# Phase 1 — Data acquisition report

**Date:** 2026-09-18 · `scripts/fetch_nwdp.py` + `scripts/profile_phase1.py`

## What was pulled
| State | File | Size | Rows | Stations | Districts | Time range |
|---|---|---|---|---|---|---|
| Punjab | `gwl_tel_6_hourly_cgwb_pb_2021_2025.csv` | 130.5 MB | 940,158 | 289 | 21 | 2022-09-07 → 2025-12-11 |
| Rajasthan | `gwl_tel_6_hourly_cgwb_rj_2021_2025.csv` | 131.9 MB | 1,100,757 | 557 | 31 | 2022-12-07 → 2025-11-14 |
| **Total** | | **≈262 MB** | **2,040,915** | **846** | **52** | **~3.3 yr @ 6-hourly** |

Access method: plain-HTTPS bulk CSV from `nwdp.nwic.gov.in` (byte-range resumable).
Provenance: `data/raw/PROVENANCE.md`. Re-run pulls with `python scripts/fetch_nwdp.py --resume`.

## Data quality issues (shape Phase 2)
1. **Extreme sensor outliers:** Punjab range −857…+242 m; Rajasthan −2015…+145 m.
   Negative and 100 m+ readings are non-physical for depth-to-water → Phase 2 must
   clip/flag via per-station MAD or hard hydrogeological bounds + Isolation Forest cross-check (Phase 6).
2. **No missing values** (0.00%) — but that likely means gaps are *absent rows*, not NaNs.
   Phase 2 must reindex each station to a regular 6H grid and measure gap fraction.
3. **Block metadata unusable:** `-` in 93% (PB) / 100% (RJ) of rows. District-level joins
   only; block labels for classification must come from the CGWB GWRA report, not this file.
4. **Window is ~3.3 yr, not 2021–2025:** effective start Sep/Dec 2022. Seasonal amplitude
   still estimable (3 monsoon cycles); 10-yr depletion trends are NOT — years-to-depletion
   claims are out of scope until manual-quarterly baseline is added.
5. **Value semantics open:** ~85 m typical readings suggest depth-to-water (larger = worse).
   Confirm vs manual series in Phase 2; every downstream sign convention depends on it.

## Not yet pulled (tracked, non-blocking)
- Manual-quarterly series (pre-2021 baseline cross-check) — Phase 2 if needed.
- CGWB GWRA 2023/2024 block-category tables → CSV — required input to Phase 4.
- IMD district-month rainfall — required input to Phase 7.

## Phase exit: ✅ data on disk, schema + gaps known → Phase 2 unblocked.
