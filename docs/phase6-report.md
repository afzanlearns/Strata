# Phase 6 — Outlier detection report

**Date:** 2026-09-18 · `ml/anomalies.py` · output: `data/processed/anomaly_flags.csv`
IF trained on quarantine-inclusive vectors (802 stations), contamination 0.06.

## 1. Headline overlap metrics (the quarantine-honesty audit)
| metric | value | reading |
|---|---|---|
| IF flags | 49/802 (6%) | by construction |
| robust-z baseline (≥2 of 4 keys > 3.5 MAD) | 122 | univariate thresholds over-flag heavy-tailed data |
| IF overlap baseline | 38/49 | IF is the stricter multivariate subset — the refinement story |
| IF pre-caught by Phase 2 quarantine (quar_frac > 5%) | **37%** | 63% found *independently* — quarantine did not pre-empt the forest |
| suspect pocket (k-means=2) recaptured | 28/51 | pocket confirmed anomalous, but IF splits it — some members are multivariately normal |
| DBSCAN-noise recaptured | 49/238 | low: isolation ≠ local sparsity; the two methods mean different things by "odd" |

## 2. Manual inspection (8 top anomalies, raw 6H series)
| station | evidence | verdict |
|---|---|---|
| Baswa1_1 (RJ) | 78 m single jump, 48% stuck readings, −42 m/yr | **sensor fault** |
| Sundran D_1 (PB) | 61 m jump, 36% stuck, 51% quarantined | **sensor fault** |
| Kotadi_1 (RJ) | 65 m jump, p99 jump 17 m | **sensor fault** |
| Bhooriyawas (RJ) | −39 m/yr, smooth, 59% quarantined | **suspect artefact** (datum drift) |
| Chirwa_1 (RJ) | −18 m/yr, −44 monsoon Δ | **suspect artefact** |
| Kala khuta (RJ) | −48 m/yr on 597 ok-readings | **suspect artefact** |
| SAS NAGAR MAJRI AKALGARH D (PB) | **+2.8 m/yr, smooth (max jump 1.9 m), deepening monsoon +20** | **real depletion event** — fast, clean, urban-fringe signal |
| Gowa Kalan (RJ) | flat, 75% gaps | **unexplained/unverifiable** — flagged for gappiness, correctly surfaced as "cannot assess" |

## 3. Method contrast (for the writeup)
Isolation Forest (multivariate isolation depth) vs robust-z counting (marginal extremes):
the baseline flags 2.5× more because heavy-tailed hydrology trips single-feature
thresholds constantly; IF requires *joint* weirdness. Cost: IF O(n log n) both fit fast
at this scale; the baseline is O(n) but buys false positives. IF wins on precision,
baseline wins on transparency — keep both, show the overlap number.

## Phase exit: ✅ IF + baseline + inspection → Phases 7–8 unblocked
(regression must exclude sensor-fault stations from training; depletion_event station is
a showcase forecast case).
