# Data dictionary — STRATA (locks Phase 2 conventions)

## 1. Core sign convention (LOCKED 2026-09-18, evidence below)
- Raw column `Groundwater Level Telemetry 6 Hourly (meter)` mixes **two per-station
  sensor/datum conventions**: ~85% of stations report water level as negative-down
  (e.g. −17 = water table 17 m below surface), ~15% report depth-to-water positive-down.
- Canonical quantity everywhere downstream: **`depth_to_water_m` — metres below ground
  surface, LARGER = DEEPER = WORSE.** Rule: `depth = raw * s` where `s = −1` for
  neg-majority stations (negfrac > 0.8), `s = +1` for pos-majority (negfrac < 0.2).
- Evidence (per-station seasonal audit, `scripts/audit_sign.py`, all 846 stations):
  Punjab neg-majority stations move −1.42 m (away from zero) in monsoon while
  pos-majority move +2.41 m (away from zero) — same physical direction (paddy-season
  deepening), opposite raw signs. Rajasthan neg-majority moves +0.44 m toward zero
  (monsoon recovery). Only 23/846 stations are mixed-sign (datum shift mid-history).
- Consequences: every trend/feature/chart uses `depth_to_water_m`. Positive slope =
  deepening = worsening. Dashboard copy must say "water table falling", never "levels
  rising", when depth increases.

## 2. Quarantine flags (queryable column `qflag`; rows NEVER deleted)
| flag | meaning | rule |
|---|---|---|
| `ok` | usable observation | passes all gates |
| `mad_outlier` | per-station spike | modified z-score (MAD) > 3.5 on depth series |
| `nonphysical` | impossible value | depth < 0 or > 100 m after sign unification |
| `datum_shift` | mixed-sign station segment | station negfrac in [0.2, 0.8]; series split at zero-crossings of 30-day rolling median, each segment oriented by its own median sign |
| `gap` | absent telemetry | grid cell with no observation after 6H reindex (value NaN) |

Phase 6 overlap metric: `frac_anomalies_precaught = P(qflag != ok | isoforest=anomaly)`.

## 3. Time grain
- Raw: irregular 6-hourly. Canonical grid: regular **6H** per station over its active span
  (`clean_6h.csv`: `station, time_utc, depth_to_water_m, qflag`).
- Feature grain: **daily medians** of `ok` rows → station feature vector
  (`station_features.csv`); **district medians** of station vectors
  (`district_features.csv`) — district grain is what Phase 4 labels (CGWB GWRA) join to.

## 4. Station feature vector (shared input: clustering, classification, similarity)
`state, district, lat, lon, n_days, gap_fraction, quarantine_fraction, median_depth,
p10_depth, p90_depth, trend_30d_m_per_day, trend_90d_m_per_day,
annual_decline_m_per_year (+ = worsening), monsoon_delta_m (monsoon−premonsoon median;
− = recovery), annual_amplitude_m, volatility_m (std of daily diffs), datum_shift (bool)`

## 5. Known limits
Block-level joins impossible (Block=`-` in 93–100% of raw rows). No aquifer-type column
in telemetry → Jaccard runs on discretized archetype tokens until NAQUIM metadata joins.
Window ≈3.3 yr (late 2022 → late 2025): 3 monsoon cycles, no decadal trends.
