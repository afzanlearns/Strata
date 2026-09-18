"""Phase 5 clustering: k-means vs agglomerative (Ward) vs DBSCAN.

Population: 802 stations with complete feature vectors (dropna -- clustering must
not invent points by imputation). Behaviour-only numeric features, z-scored.
  k-means: k in 2..8 via elbow (inertia) + silhouette; n_init=20, fixed seed.
  agglomerative: Ward linkage, same k; agreement with k-means by adjusted Rand index.
  DBSCAN: eps from the 5-NN k-distance elbow, min_samples=5; noise reported, not hidden.
Saves data/processed/cluster_assignments.csv + prints archetype table.
Run: python ml/cluster.py
"""
from __future__ import annotations

import os

import numpy as np
import pandas as pd
from sklearn.cluster import AgglomerativeClustering, DBSCAN, KMeans
from sklearn.metrics import adjusted_rand_score, silhouette_score
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "data", "processed")
FEATS = ["median_depth", "p10_depth", "p90_depth", "trend_30d_m_per_day",
         "trend_90d_m_per_day", "annual_decline_m_per_year", "monsoon_delta_m",
         "annual_amplitude_m", "volatility_m", "gap_fraction", "quarantine_fraction"]


def load():
    df = pd.read_csv(os.path.join(OUT, "station_features.csv"))
    df = df.dropna(subset=FEATS).reset_index(drop=True)
    Z = StandardScaler().fit_transform(df[FEATS].astype(float))
    return df, Z


def archetypes(df, col, k):
    t = df.groupby(col).agg(
        n=("station", "count"),
        punjab_frac=("state", lambda s: round(float((s == "punjab").mean()), 2)),
        med_depth=("median_depth", "median"),
        decline=("annual_decline_m_per_year", "median"),
        monsoon=("monsoon_delta_m", "median"),
        vol=("volatility_m", "median")).round(2)
    print(f"--- {col} archetypes ---")
    print(t.to_string())
    return t


if __name__ == "__main__":
    df, Z = load()
    print(f"stations={len(df)}")
    inert, sil = {}, {}
    for k in range(2, 9):
        km = KMeans(n_clusters=k, n_init=20, random_state=42).fit(Z)
        inert[k] = round(float(km.inertia_), 1)
        sil[k] = round(float(silhouette_score(Z, km.labels_)), 3)
    print("elbow(inertia):", inert)
    print("silhouette:", sil)
    K = max(sil, key=sil.get)
    print(f"chosen K={K}")
    df["kmeans"] = KMeans(n_clusters=K, n_init=20, random_state=42).fit_predict(Z)
    df["agglo"] = AgglomerativeClustering(n_clusters=K, linkage="ward").fit_predict(Z)
    print(f"kmeans vs agglo: ARI={adjusted_rand_score(df.kmeans, df.agglo):.3f} "
          f"sil_agglo={silhouette_score(Z, df.agglo):.3f}")
    d5 = np.sort(NearestNeighbors(n_neighbors=5).fit(Z)
                 .kneighbors(Z)[0][:, -1])
    print("k-distance p90/p95/p99:",
          np.round(np.percentile(d5, [90, 95, 99]), 3))
    for eps in [1.0, 1.5, 2.0]:
        lab = DBSCAN(eps=eps, min_samples=5).fit_predict(Z)
        ncl = len(set(lab)) - (1 if -1 in lab else 0)
        nz = lab[lab != -1]
        s = f"{silhouette_score(Z[nz != -1] if False else Z[lab != -1], nz):.3f}" if ncl > 1 else "n/a"
        print(f"eps={eps}: clusters={ncl} noise_frac={(lab == -1).mean():.3f} sil={s}")
    df["dbscan"] = DBSCAN(eps=1.5, min_samples=5).fit_predict(Z)
    archetypes(df, "kmeans", K)
    archetypes(df, "agglo", K)
    print("--- kmeans x agglo crosstab ---")
    print(pd.crosstab(df.kmeans, df.agglo).to_string())
    archetypes(df, "dbscan", -1)
    # DBSCAN in 11-D standardized space merges everything: retry on PCA projection
    from sklearn.decomposition import PCA
    P = PCA().fit(Z)
    npc = int(np.argmax(np.cumsum(P.explained_variance_ratio_) >= 0.80) + 1)
    Zp = P.transform(Z)[:, :npc]
    print(f"PCA: {npc} components explain 80% "
          f"(ratios={np.round(P.explained_variance_ratio_[:npc], 3).tolist()})")
    d5p = np.sort(NearestNeighbors(n_neighbors=5).fit(Zp).kneighbors(Zp)[0][:, -1])
    print("PCA k-distance p90/p95/p99:", np.round(np.percentile(d5p, [90, 95, 99]), 3))
    for eps in [0.5, 0.8, 1.0]:
        lab = DBSCAN(eps=eps, min_samples=5).fit_predict(Zp)
        ncl = len(set(lab)) - (1 if -1 in lab else 0)
        s = f"{silhouette_score(Zp[lab != -1], lab[lab != -1]):.3f}" if ncl > 1 else "n/a"
        print(f"PCA eps={eps}: clusters={ncl} noise_frac={(lab == -1).mean():.3f} sil={s}")
    df["dbscan_pca"] = DBSCAN(eps=0.8, min_samples=5).fit_predict(Zp)
    archetypes(df, "dbscan_pca", -1)
    df[["station", "state", "district", "kmeans", "agglo", "dbscan", "dbscan_pca"]].to_csv(
        os.path.join(OUT, "cluster_assignments.csv"), index=False)
