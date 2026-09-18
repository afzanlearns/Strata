"""Phase 8 logistic regression: P(cross above 35 m within 90 days).

Syllabus core: sigmoid + gradient descent implemented from scratch (log-loss curve
printed), compared against sklearn; metrics accuracy/precision/recall/ROC-AUC on the
future holdout. Stretch: 1-hidden-layer MLP -- is the complexity worth it?
Run: python ml/logistic.py
"""
from __future__ import annotations

import os

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, roc_auc_score
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler

from supervised import FEAT_COLS, build_supervised, time_split

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "data", "processed")


def sigmoid(z: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(z, -500, 500)))


def gd_logreg(X: np.ndarray, y: np.ndarray, lr: float = 0.5,
              iters: int = 3000) -> tuple[np.ndarray, list[float]]:
    """Batch GD on binary log-loss: grad = X'(sigmoid(Xw) - y)/n."""
    n = len(y)
    w = np.zeros(X.shape[1])
    costs = []
    for it in range(iters + 1):
        ph = sigmoid(X @ w)
        eps = 1e-12
        costs.append(float(-(y * np.log(ph + eps) + (1 - y) * np.log(1 - ph + eps)).mean()))
        w -= lr * (X.T @ (ph - y)) / n
        if it > 0 and abs(costs[-2] - costs[-1]) < 1e-12:
            break
    return w, costs


def report(name: str, y: np.ndarray, prob: np.ndarray) -> dict:
    pred = (prob >= 0.5).astype(int)
    p, r, f, _ = precision_recall_fscore_support(y, pred, average="binary", zero_division=0)
    out = {"model": name, "acc": round(float(accuracy_score(y, pred)), 3),
           "prec": round(float(p), 3), "rec": round(float(r), 3),
           "f1": round(float(f), 3),
           "auc": round(float(roc_auc_score(y, prob)), 3)}
    print(f"{name}: " + " ".join(f"{k}={v}" for k, v in out.items() if k != "model"))
    return out


if __name__ == "__main__":
    sup = build_supervised(horizon=90, task="classify")
    tr, te, cut = time_split(sup)
    print(f"time split at {cut}: train={len(tr):,} test={len(te):,} "
          f"train_pos={tr.target.mean():.4f} test_pos={te.target.mean():.4f}")
    sc = StandardScaler().fit(tr[FEAT_COLS])
    Xtr, Xte = sc.transform(tr[FEAT_COLS]), sc.transform(te[FEAT_COLS])
    ytr, yte = tr.target.to_numpy(), te.target.to_numpy()

    sk = LogisticRegression(penalty=None, max_iter=5000).fit(Xtr, ytr)
    r_sk = report("sklearn_logreg", yte, sk.predict_proba(Xte)[:, 1])

    Xtr1 = np.column_stack([np.ones(len(Xtr)), Xtr])
    Xte1 = np.column_stack([np.ones(len(Xte)), Xte])
    w, costs = gd_logreg(Xtr1, ytr)
    print(f"scratch GD: logloss {costs[0]:.3f} -> {costs[-1]:.3f} "
          f"weight_gap={np.abs(w[1:] - sk.coef_[0]).max():.2e}")
    r_gd = report("scratch_GD", yte, sigmoid(Xte1 @ w))

    mlp = MLPClassifier(hidden_layer_sizes=(16,), max_iter=2000,
                        random_state=42).fit(Xtr, ytr)
    r_mlp = report("mlp_16", yte, mlp.predict_proba(Xte)[:, 1])

    skb = LogisticRegression(max_iter=5000, class_weight="balanced").fit(Xtr, ytr)
    r_skb = report("logreg_balanced", yte, skb.predict_proba(Xte)[:, 1])

    def best_thresh(y, prob):
        ths = np.quantile(prob[prob > 0], np.linspace(0.01, 0.99, 60))
        best = max(((t, 2 * ((prob >= t) & (y == 1)).sum() /
                     max(1, 2 * ((prob >= t) & (y == 1)).sum()
                         + ((prob >= t) & (y == 0)).sum() + ((prob < t) & (y == 1)).sum()))
                    for t in ths), key=lambda kv: kv[1])
        return round(float(best[0]), 3), round(float(best[1]), 3)

    print("best-F1 thresholds: logreg", best_thresh(yte, sk.predict_proba(Xte)[:, 1]),
          "balanced", best_thresh(yte, skb.predict_proba(Xte)[:, 1]),
          "mlp", best_thresh(yte, mlp.predict_proba(Xte)[:, 1]))
    pd.DataFrame([r_sk, r_gd, r_mlp, r_skb]).to_csv(
        os.path.join(OUT, "logistic_comparison.csv"), index=False)
    # per-row crossing probabilities for the dashboard (test window only)
    probs = te[["state", "district", "station", "date"]].copy()
    probs["cross_prob"] = np.round(mlp.predict_proba(Xte)[:, 1], 4)
    probs.to_csv(os.path.join(OUT, "crossing_probs.csv"), index=False)
    print(f"saved crossing_probs: {len(probs):,} rows")
