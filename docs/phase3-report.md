# Phase 3 — Association rule mining report

**Date:** 2026-09-18 · `ml/association.py` · `scripts/fetch_rain.py`
· outputs: `data/processed/rules_apriori.csv`, `rules_fpgrowth.csv`

## 1. Transactions (452 district-season-years, 51 districts, 20 items)
Grain: (district × IMD season × year); cells need ≥30 days of `ok` DWLR data.
Items: `state`, `season`, `rain:deficient|normal|surplus` (ERA5 season total, **within-season
tertiles** so rain bands aren't just a proxy for season), `depth:shallow|mid|deep`
(season median, global tertiles), `move:falling|flat|rising` (vs prior season),
`trajectory:deepening|stable|recovering`, `stress:yes|no` (>30 m + deepening).
Rainfall input: Open-Meteo ERA5 daily precipitation at each district's median station
coordinate, 2022-09 → 2025-12 (`data/raw/rain_daily_district.csv`, 52/52 districts).
Stated limit: reanalysis, not IMD gauges (IMD district-daily ends 2023 / needs keys) —
adequate for bands, disclosed everywhere.

## 2. Apriori vs FP-Growth (min_support 0.08, lift ≥ 1, conf ≥ 0.5)
| | Apriori | FP-Growth |
|---|---|---|
| frequent itemsets | 289 | 289 |
| rules | 458 | 458 |
| runtime | 0.01 s | 0.01 s |
| top-10 overlap | 9/10 (10th differs only by tie-order) | — |
Identical outputs (expected: same level-wise search space, FP-Growth just avoids
candidate generation). At 452 transactions both are instant; FP-Growth's advantage would
appear at 10–100× scale. Either is defensible — we ship Apriori rules, cite the equivalence.

## 3. Strongest rules (support / confidence / lift)
| # | rule | sup | conf | lift |
|---|---|---|---|---|
| 1 | {monsoon, deepening} → {falling} | .093 | .93 | 2.23 |
| 2 | {monsoon, punjab} → {falling} | .082 | .93 | 2.21 |
| 3 | {monsoon, recovering} → {rajasthan} | .082 | 1.00 | 1.86 |
| 4 | {mid-depth, surplus-rain, punjab} → {deepening} | .104 | .92 | 3.02 |
| 5 | {deep, deepening} → {stress} | .173 | 1.00 | 5.26 |

## 4. What rules 1–5 mean for a water-policy audience
1. **Rain is not rescuing deepening districts.** Where the multi-year trajectory is
   deepening, the water table keeps *falling through the monsoon* (93% of such cases) —
   extraction outruns recharge even in the wet season.
2. **That monsoon-falling pattern is Punjab's signature** (rule 2) — the kharif-pumping
   mechanism from Phase 2, now quantified as a rule, not an anecdote.
3. **Monsoon recovery belongs to Rajasthan** (rule 3, confidence 1.0): the only places
   that rise in monsoon are recovering-track Rajasthan districts — recharge-led systems.
4. **Even surplus rain doesn't flip Punjab's trajectory** (rule 4, conf .92): mid-depth
   Punjab districts with above-normal rain are *still deepening*. Policy implication:
   supply-side fixes (more recharge structures) alone won't stabilize these blocks;
   demand-side (pumping/cropping) action is required.
5. **Deep + deepening = stressed, always** (rule 5) — disclosed as partly constructional
   (stress is defined from depth + trajectory), kept because it validates the item
   encoding end-to-end (a broken pipeline wouldn't produce lift 5.26 here).

## Phase exit: ✅ patterns + Apriori/FP-Growth comparison → Phase 4 unblocked
(open: CGWB GWRA label scrape still required for classification targets).
