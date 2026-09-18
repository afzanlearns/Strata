# Phase 0 — Scoping Document: STRATA
### Groundwater Resource Evaluation System (SIH25068)

**Date:** 2026-09-18 · **Status:** approved scope, Phase 1 unblocked

---

## 1. Problem statement (in our own words)

India monitors groundwater through ~5,260 DWLR (Digital Water Level Recorder) telemetry
stations that transmit water-level readings as often as every 15 minutes / six-hourly.
This high-frequency data exists, but it is not usable by the people who must act on it:
a district officer cannot see which blocks are sliding toward over-exploitation, a policy
analyst cannot quantify recharge vs. extraction, and a citizen has no readable local picture.

**SIH25068 (Ministry of Jal Shakti / CGWB)** asks for a *real-time groundwater resource
evaluation system on DWLR data*: ingest water-level time series, quantify fluctuation and
recharge, classify resource health, forecast risk, and present it in an actionable dashboard.
STRATA answers that, and doubles as the shared product for two university subjects —
Data Mining (pattern discovery) and Machine Learning (predictive functions) — on one
dataset and one pipeline.

Out of scope (explicit): no LLM, no OCR, no synthetic "real-time streaming" claims.
"Real-time" here means *evaluation on the latest available telemetry*, refreshed on
download/schedule — honest and demoable.

## 2. Geographic scope: PUNJAB + RAJASTHAN

**Decision: two states — Punjab and Rajasthan.** Investigated before deciding:

| Source checked | Finding |
|---|---|
| CGWB Dynamic Ground Water Resources Assessment 2024 (national compilation, public PDF) | OE+Critical units >25% concentrated in Delhi, Haryana, **Punjab, Rajasthan**, Tamil Nadu, DNH&DD. Punjab = extraction-driven stress; Rajasthan = aridity-driven stress (CGWB's own two archetypes). |
| NWDP — National Water Data Portal (`nwdp.nwic.gov.in`) | State-wise bulk CSV + API confirmed: `gwl_tel_6_hourly_cgwb_pb_2021_2025.csv` (~98 MB, Punjab), plus Haryana / Rajasthan / Delhi equivalents, 2021–2025 six-hourly telemetry + manual quarterly sets. Open licence, no scraping needed. |
| India-WRIS time-series portal | Exists but geo-fenced (India IP), session-based, unreliable for automated pulls — documented as fallback only, not primary. |
| QGIS WRIS-extractor plugin reports | Confirms WRIS blocks non-Indian IPs; reinforces NWDP-first choice. |

**Why these two (justification for viva):**
1. **Richest open data:** both states have full 2021–2025 telemetry + manual-quarterly series on NWDP with state GW-department supplements (Punjab GW, Rajasthan GW).
2. **Compelling contrast, same endpoint:** Punjab = alluvial, abundant recharge, *over-exploited by indiscriminate pumping* (paddy). Rajasthan = arid, *low recharge by climate*. Both end "Over-Exploited" per CGWB — so the project shows two *different causal paths to the same category*, which makes clustering, rules, and classification genuinely interesting instead of trivially separable.
3. **All four CGWB categories present** across the two states' blocks (Safe through Over-Exploited), so classification/clustering targets are non-degenerate.
4. **Bounded cost:** two states keep the 6-hourly data volume manageable (~100–200 MB raw) on a student machine.

## 3. Target users + core user stories

1. **District water officer (primary).** "As a district officer, I want to see my district's
   current stress category, 30/60/90-day critical-crossing risk, and flagged anomalies, so I
   can prioritise field verification and extraction control."
2. **Policy analyst (state/CGWB).** "As an analyst, I want block-level category maps, recharge
   estimates, and the top association rules (which condition combos co-occur with critical
   depletion), so I can target conservation funds and cropping advisories."
3. **Citizen / farmer.** "As a citizen, I want to pick my district/station and see a plain-language
   status, trend chart, and forecast — not raw metres-below-ground — so I know whether my
   area's water is stable or declining."
4. **Student / evaluator (viva).** "As an evaluator, I want every syllabus technique mapped to a
   visible product surface with metrics, so I can verify coverage without reading notebooks."

## 4. Technique checklist → where each lives in the product

**Data Mining deliverable (pattern discovery):**

| Syllabus technique | Implementation | Product surface |
|---|---|---|
| Similarity (Euclidean + Cosine, + Jaccard on aquifer/land-use) | `ml/similarity.py` on station feature vectors (Phase 2) | "Most similar stations" panel |
| Frequent patterns (Apriori, FP-Growth comparison; support/confidence/lift) | `ml/association.py` on district-season transactions (Phase 3) | "What co-occurs with critical depletion" rules card + analyst view |
| Classification: Decision Tree (C4.5-style) + Naive Bayes + kNN; confusion matrix, P/R/F1 | `ml/classify.py` on CGWB-category labels (Phase 4) | Category predictor + comparison table |
| Clustering: k-means + agglomerative + DBSCAN; elbow/silhouette, eps tuning | `ml/cluster.py` (Phase 5) | Aquifer-archetype map + CA3 comparison writeup |
| Outlier detection: Isolation Forest (+ z-score baseline) | `ml/anomalies.py` (Phase 6) | Anomaly flags on charts + alerts list |

**ML deliverable (predictive functions):**

| Syllabus technique | Implementation | Product surface |
|---|---|---|
| Linear (+ polynomial compare) regression, RMSE/R², explicit from-scratch gradient descent | `ml/regression.py` (Phase 7) | Forecasted water-level chart (N-days ahead) |
| Logistic regression, sigmoid + gradient descent shown explicitly, accuracy/P/R/ROC-AUC | `ml/logistic.py` (Phase 8) | Critical-crossing probability badge |
| Optional 1–2-layer MLP comparison | `ml/mlp_compare.py` (Phase 8 stretch) | "Was complexity worth it?" note |

**Shared:** MySQL-persisted results + Python API (`backend/`) → React/TypeScript brutalist-minimal
dashboard (`frontend/`) → two separate mapping writeups (`docs/dm-mapping.md`, `docs/ml-mapping.md`).

## 5. Data plan + known limitations (input to Phase 1)

- **Primary:** NWDP CGWB six-hourly telemetry 2021–2025 (Punjab, Rajasthan) + manual quarterly
  series (longer baseline, cross-check). Bulk CSV download + documented API (`/dataset_api/home_api_page`, 546 APIs).
- **Labels:** CGWB GWRA 2023/2024 block-wise categorization tables (Safe ≤70%, Semi-critical 70–90%,
  Critical 90–100%, Over-Exploited >100% extraction stage) — scraped from public PDFs into a CSV.
- **Expected quality issues:** missing intervals, sensor spikes, inconsistent station IDs across
  years, coarse rainfall join (district-month, not station-hour). Handled in Phase 2; nothing here
  blocks Phase 1.
- **Honest flags:** no public 15-min live firehose; "live" = latest NWDP pull. India-WRIS direct
  station API not assumed — NWDP only until proven otherwise.

## 6. Phase exit criteria

- [x] Scope (states, users, technique map) written and committed
- [ ] Phase 1: raw pulls + `data/raw/PROVENANCE.md` with URLs, dates, station counts, gaps
- Next phase depends on: confirmed CSV schemas (column names) so Phase 2 cleaning code matches reality.

*Deviation risk accepted:* if NWDP blocks bulk download at pull time, fallback is manual-quarterly
CSV (smaller) + documented attempt log — technique coverage unchanged, only resolution reduced.
