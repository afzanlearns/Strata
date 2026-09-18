# Phase 5 — Clustering report (doubles as CA3 algorithm comparison)

**Date:** 2026-09-18 · `ml/cluster.py` · output: `data/processed/cluster_assignments.csv`
Population: 802 stations, 11 behaviour features, z-scored. Overall silhouettes are low
(≤0.31) — stated upfront: groundwater behaviour is a **continuum, not well-separated
blobs**, so clusters are archetype shorthands, not natural kinds.

## 1. k-means: K=3 (silhouette 0.274 beats K=2's 0.253; elbow soft at 3–5)
| cluster | n | Punjab frac | med depth | decline/yr | monsoon Δ | archetype |
|---|---|---|---|---|---|---|
| 0 | 266 | 0.19 | 53.6 m | +0.46 | 0.00 | **Deep arid stock** — mostly Rajasthan deep aquifers, slow worsening, inert seasons |
| 1 | 485 | 0.48 | 17.2 m | +0.06 | +0.02 | **Alluvial plains, holding** — shallow, near-stable, both states |
| 2 | 51 | 0.04 | 23.2 m | −8.52 | −9.64 | **Suspect pocket** — non-physical recovery rates; likely datum/short-record artefacts, referred to Phase 6 for independent confirmation |

## 2. Agglomerative (Ward, K=3): same K, different story (ARI vs k-means = **0.372**)
Ward isolates only the 20 most extreme artefact stations and folds 28 moderates into its
shallow cluster; it also re-splits k-means' big stable mass 139/346. Same data, same K,
substantially different map — the disagreement itself is the CA3 finding.

## 3. DBSCAN: the honest failure-then-fix
Raw 11-D standardized space: eps 1.5–2.0 collapse to **one blob** (curse of dimensionality;
k-distance p90 = 2.46), eps 1.0 fragments into 34% noise. Fix: PCA to 5 components (80%
variance) → eps 1.0 gives 3 clusters + 22% noise (sil 0.258): one stable core (546) plus
three 6-station micro-pockets. DBSCAN's product value here is **noise identification for
Phase 6 cross-check**, not partitioning.

## 4. Algorithm comparison (CA3)
| | k-means | Agglomerative (Ward) | DBSCAN |
|---|---|---|---|
| shape assumption | spherical, equal variance | variance-minimizing merges (balanced bias) | arbitrary density-connected shapes |
| noise | forced into nearest centroid (artefacts got their own cluster only by luck of K) | absorbed into nearest merge | explicit −1 noise label (the point) |
| parameters | K (elbow+silhouette) | K + linkage (Ward chosen: variance suits continuous features) | eps (k-distance elbow) + min_samples; needs PCA first in 11-D |
| cost | O(n·K·iter) — cheapest at scale | O(n²) memory — fine at 802, prohibitive at raw-row scale | O(n log n) with index; degrades in high-D |
| verdict on this data | best partitioner (clearest archetypes) | most sensitive to outliers (20 vs 51 split shows it) | best anomaly pre-screener |

## Phase exit: ✅ 3 clusterings compared, assignments saved → Phase 6 unblocked
(Phase 6 must test whether the 51-station suspect pocket re-emerges without supervision).
