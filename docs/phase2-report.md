# Phase 2 — Preprocessing + similarity report

**Date:** 2026-09-18 · `ml/preprocess.py` · `ml/similarity.py` · `docs/data-dictionary.md`

## 1. Sign convention — RESOLVED (was the open question)
Raw telemetry mixes two per-station datum conventions (audit: `scripts/audit_sign.py`).
Locked rule, documented in `docs/data-dictionary.md`:
**`depth_to_water_m`, larger = deeper = worse.** Neg-majority stations flipped (×−1);
23 mixed-sign stations split at rolling-median zero-crossings, segments oriented
individually, flagged `datum_shift`. Post-flip medians (PB 22.8 m, RJ 30.7 m) match
CGWB-published depth ranges — independent plausibility check passed.

## 2. What was built
- `clean_6h_pb.csv` (1.04M grid rows) + `clean_6h_rj.csv` (1.48M): regular 6H grid,
  duplicate stamps deduped (median depth, worst-flag-wins), quarantine flags kept as a
  **queryable column** — nothing deleted.
- `station_features.csv` (846 stations × 18 cols): trends (30/90-day, annual),
  monsoon delta, amplitude, volatility, gap/quarantine fractions, lat/lon.
- `district_features.csv` (52 districts): medians of station vectors + `frac_deepening`.

## 3. Quarantine census (the Phase 6 overlap baseline)
| | ok | gap | mad_outlier | nonphysical |
|---|---|---|---|---|
| Punjab | 87.1% | 10.7% | 1.9% | 0.3% |
| Rajasthan | 68.5% | 26.0% | 3.4% | 2.1% |
Rajasthan is gappier and spikier — imputation/robustness there matters more.
24 stations carry `datum_shift`. 44 short-record stations lack full features
(similarity indexes 802/846).

## 4. Headline patterns (preview, not conclusions)
- **Monsoon response splits by state:** PB median monsoon_delta **+1.49 m** (deepens —
  kharif paddy pumping beats recharge) vs RJ **−0.39 m** (recovers). The scope contrast
  is real and measurable.
- **Deepening gradient:** Sangrur/Ludhiana/Barnala/Faridkot 100% of stations deepening
  (~1–2 m/yr); eastern RJ districts recovering. Matches CGWB's OE geography.
- **Watch-out:** a few annual declines ≈ −12 m/yr (Bundi, Dungarpur) — likely short-record
  or datum artefacts; downstream models must be robust (median-based, or winsorized).

## 5. Similarity measures (checklist: 2+, all three demonstrated)
| measure | captures | prefer when | demo behaviour |
|---|---|---|---|
| Euclidean (z-scored) | absolute behavioural distance | magnitude matters (how deep/how fast) | nearest: same-district Patiala/Sangrur wells |
| Cosine (z-scored) | profile shape, magnitude-free | same stress shape at different depths | near-identical ranking, one swap — shape≈magnitude here |
| Jaccard (archetype tokens) | categorical trait overlap | explainability ("shares 6/6 traits") | exact-trait matches across Barnala/Ludhiana/Sangrur |

Honest limit documented: no aquifer/land-use column exists in telemetry, so Jaccard tokens
are behaviour bins; true aquifer-type Jaccard waits for the NAQUIM join (Phase 3 input).
`find_similar(station_id, metric, k)` is the shared function the dashboard will call.

## Phase exit: ✅ conventions locked, features + district grain ready → Phase 3 unblocked
(needs: district-season transactions; rainfall join + aquifer metadata still open inputs).
Deviation: hard gate applied post-flip on depth [0,100], not on raw values — the raw gate
would have discarded the majority of the data (raw medians are negative by convention).
