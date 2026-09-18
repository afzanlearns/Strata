# Data Mining — Syllabus Technique Mapping (STRATA)

Shared pipeline/product with the ML submission; this document lists only what the
Data Mining rubric grades, mapped to implementation + dashboard surface + result.

## 1. Similarity measures (Module 2) — `ml/similarity.py`, Phase 2
| measure | what it captures | when preferred |
|---|---|---|
| Euclidean (z-scored station vectors) | absolute behavioural distance | magnitude matters (how deep / how fast) |
| Cosine (z-scored) | profile shape, magnitude-free | same stress shape at different depths |
| Jaccard (archetype tokens) | categorical trait overlap, explainable ("shares 6/6 traits") | policy explanations |
`find_similar(station, metric, k)` powers the dashboard's SIMILAR STATIONS panel.
Stated limit: telemetry has no aquifer/land-use column, so Jaccard tokens are behaviour
bins; true aquifer-type Jaccard awaits the NAQUIM join.

## 2. Frequent pattern mining (Module 3) — `ml/association.py`, Phase 3
- Transactions: 452 district-season-years × 20 items (rain bands from concurrent ERA5,
  within-season tertiles; `docs/phase3-report.md`).
- **Apriori vs FP-Growth**: identical — 289 itemsets, 458 rules, 9/10 top-rule overlap
  (10th = tie-order). Same search space, different enumeration; equivalent at this scale.
- Key rules with support/confidence/lift: {monsoon, deepening}→{falling} (.093/.93/2.23);
  {monsoon, recovering}→{Rajasthan} (.082/1.00/1.86); {mid-depth, surplus-rain,
  Punjab}→{still deepening} (.104/.92/3.02) — supply-side fixes alone won't stabilize
  these blocks. Dashboard: CRITICAL RULES panel with lift badges.

## 3. Classification (Module 4) — `ml/classify.py`, Phase 4
Target: real **CGWB GWRA-2025 predominant block category** per district (scraped from the
official PDF; 6,762-unit checksum; transliteration aliases), broadcast to 846 stations.
| model | accuracy | macro-F1 | OE-F1 | minor-class F1 |
|---|---|---|---|---|
| kNN (k=3) | 0.865 | **0.390** | 0.929 | safe .216 / semi .080 / crit .333 |
| Decision tree (entropy/C4.5-style) | 0.694 | 0.292 | 0.828 | .197 / .029 / .113 |
| Naive Bayes | 0.676 | 0.285 | 0.817 | .262 / .000 / .061 |
Stratified 5-fold CV, confusion matrices in `docs/phase4-report.md`. **Why kNN:**
depletion is pocketed (neighbours share fate); trees shatter n=13 minorities; NB's
independence assumption breaks on correlated depth features. Accuracy is reported but
macro-F1 is the honest metric (88% OE base rate); the ceiling (labels come from
extraction ratios, features from level dynamics) is documented.

## 4. Clustering (Module 4 + CA3) — `ml/cluster.py`, Phase 5
- **k-means K=3** (silhouette 0.274; elbow 3–5): deep arid stock (266) / alluvial plains
  holding (485) / suspect artefact pocket (51, −8.5 m/yr — referred to Phase 6).
- **Agglomerative Ward K=3**: ARI vs k-means **0.372** — same K, different map (Ward
  isolates only the 20 most extreme, re-splits the stable mass). The disagreement is the
  CA3 finding.
- **DBSCAN**: fails in raw 11-D (one blob / 34% noise — curse of dimensionality),
  works after PCA→5 dims (eps 1.0: 3 clusters + 22% noise). Verdict table —
  shape assumptions, noise handling, cost — in `docs/phase5-report.md`.
  Dashboard: cluster archetype per station.

## 5. Outlier detection (Module 5) — `ml/anomalies.py`, Phase 6
- **Isolation Forest** (49 flags, contamination 0.06) vs robust-z baseline (122 flags):
  IF is the stricter multivariate subset (38/49 overlap).
- **Quarantine-honesty audit: 37% pre-caught → 63% found independently.**
- Manual inspection of top 8: 3 sensor faults (61–78 m jumps, stuck readings),
  3 datum artefacts, **1 real depletion event** (SAS Nagar +2.8 m/yr, clean),
  1 unverifiable (75% gaps). Dashboard: ANOMALY ALERTS panel + per-station flags.

## Checklist status: all five DM techniques demonstrated, measured, and visible in the product.
