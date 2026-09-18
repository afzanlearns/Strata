"""Phase 4 classification: DT (entropy/C4.5-style) vs Naive Bayes vs kNN.

Target: district CGWB-2025 predominant block category (safe / semi_critical /
critical / over_exploited), broadcast to stations (weak supervision, stated).
Features: hydrological behaviour ONLY -- lat/lon/state/district excluded on purpose,
so the test is whether behaviour alone predicts the official category.
NaNs (short-record stations) median-imputed, documented.

Protocol: stratified 5-fold CV, identical splits for all models; k for kNN chosen by
inner 5-fold CV over {3,5,7,11,15} on each training fold. Metrics: accuracy, macro +
weighted precision/recall/F1, per-class F1, summed confusion matrix.
Run: python ml/classify.py
"""
from __future__ import annotations

import os

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.metrics import confusion_matrix, precision_recall_fscore_support
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "data", "processed")
FEATS = ["median_depth", "p10_depth", "p90_depth", "trend_30d_m_per_day",
         "trend_90d_m_per_day", "annual_decline_m_per_year", "monsoon_delta_m",
         "annual_amplitude_m", "volatility_m", "gap_fraction", "quarantine_fraction"]
ORDER = ["safe", "semi_critical", "critical", "over_exploited"]


def load():
    st = pd.read_csv(os.path.join(OUT, "station_features.csv"))
    lab = pd.read_csv(os.path.join(OUT, "district_labels.csv"))
    df = st.merge(lab[["state", "district", "label"]], on=["state", "district"])
    df = df[df.label.isin(ORDER)].reset_index(drop=True)
    X = SimpleImputer(strategy="median").fit_transform(df[FEATS])
    return X, df.label.to_numpy(), df


def evaluate(name, make, X, y):
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cm = np.zeros((len(ORDER), len(ORDER)), int)
    yt_all, yp_all = [], []
    for tr, te in skf.split(X, y):
        clf = make(X[tr], y[tr])
        p = clf.predict(X[te])
        cm += confusion_matrix(y[te], p, labels=ORDER)
        yt_all.extend(y[te]); yp_all.extend(p)
    acc = float(np.mean(np.array(yt_all) == np.array(yp_all)))
    prec, rec, f1, _ = precision_recall_fscore_support(
        yt_all, yp_all, labels=ORDER, zero_division=0)
    macro = [float(np.mean(prec)), float(np.mean(rec)), float(np.mean(f1))]
    w = [round(float(v), 3) for v in
         precision_recall_fscore_support(yt_all, yp_all, average="weighted", zero_division=0)[:3]]
    per = {c: round(float(f), 3) for c, f in zip(ORDER, f1)}
    print(f"{name}: acc={acc:.3f} macroP/R/F1={[round(v,3) for v in macro]} "
          f"weightedP/R/F1={w} per-class-F1={per}")
    return {"model": name, "accuracy": round(acc, 3),
            "macro_P": round(macro[0], 3), "macro_R": round(macro[1], 3),
            "macro_F1": round(macro[2], 3), "per_class_F1": per}, cm


def tune_k(Xtr, ytr):
    best, bestk = -1.0, 5
    inner = StratifiedKFold(n_splits=5, shuffle=True, random_state=7)
    for k in [3, 5, 7, 11, 15]:
        s = cross_val_score(KNeighborsClassifier(n_neighbors=k), Xtr, ytr,
                            cv=inner, scoring="f1_macro").mean()
        if s > best:
            best, bestk = s, k
    return bestk


if __name__ == "__main__":
    X, y, df = load()
    print("samples:", len(y), "class_counts:",
          {c: int((y == c).sum()) for c in ORDER})
    ks = []
    res, cm_dt = evaluate(
        "decision_tree",
        lambda Xt, yt: DecisionTreeClassifier(criterion="entropy", min_samples_leaf=5,
                                              class_weight="balanced", random_state=42
                                              ).fit(Xt, yt), X, y)

    def make_knn(Xt, yt):
        k = tune_k(Xt, yt)
        ks.append(k)
        return KNeighborsClassifier(n_neighbors=k).fit(Xt, yt)

    res_knn, cm_knn = evaluate("knn", make_knn, X, y)
    res_nb, cm_nb = evaluate("naive_bayes", lambda Xt, yt: GaussianNB().fit(Xt, yt), X, y)
    print("knn chosen k per fold:", ks)
    comp = pd.DataFrame([{k: v for k, v in r.items() if k != "per_class_F1"}
                         for r in [res, res_knn, res_nb]])
    comp.to_csv(os.path.join(OUT, "classification_comparison.csv"), index=False)
    print("\nconfusion matrices (rows=true, cols=pred; order safe/semi/crit/OE):")
    for n, cm in [("DT", cm_dt), ("kNN", cm_knn), ("NB", cm_nb)]:
        print(n, ":\n", cm)
    print("\ncritical-class districts:",
          sorted(df[df.label == "critical"].district.unique()))
    print("semi_critical-class districts:",
          sorted(df[df.label == "semi_critical"].district.unique()))
