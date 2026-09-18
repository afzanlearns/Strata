# Data provenance — STRATA Phase 1 (raw pulls)

## Primary: NWDP six-hourly DWLR telemetry (CGWB)
- Portal: National Water Data Portal, https://nwdp.nwic.gov.in
  (dataset page: `/dataset/ground-water-level-telemetry-daily-cgwb-as-assam`,
  dataset UUID `3782ba15-9b12-46a8-ae44-410b1f84020e`)
- Date pulled: _fill in on download day_
- Files:
  - `gwl_tel_6_hourly_cgwb_pb_2021_2025.csv` — Punjab, resource `2b3bfc59-…`, ~98 MB (portal: updated 2025-05-11)
  - `gwl_tel_6_hourly_cgwb_rj_2021_2025.csv` — Rajasthan, resource `467fe983-…`
- Licence: Other (Open), producer CGWB (`gisndc-cgwb@nic.in`).
- Verified 2026-09-18 with an HTTP Range request (first 3 KB): 22-column schema —
  `SlNo, Station, Agency, State LGD Code, State, District LGD Code, District,
  Tehsil, Block, Village, River, Basin, Tributary, Subtributary,
  SubSubtributary, Local River, Latitude, Longitude, RL_MSL,
  Data Acquisition Time (DD-MM-YYYY HH:MM), Groundwater Level Telemetry 6 Hourly (meter)`.
  Sample row: station `Akalgarh M_1`, SAS NAGAR, 6-hourly stamps, values ≈ 84.9 m.
- Access notes: bulk CSV over plain HTTPS on host `nwdp.nwic.gov.in`, byte-range
  resumable. The legacy `nwdp.nwic.in` download host does NOT resolve/connect from
  this network (DNS ok, TCP 443 timeout) — do not use old copied URLs. No API key needed.

## Labels: CGWB Dynamic Ground Water Resource Assessment 2024
- Source: https://cgwb.gov.in → National Compilation on Dynamic Ground Water
  Resources of India 2024 (+ 2023). Block/Mandal/Taluk categorization tables.
- Rule: Safe ≤70%, Semi-critical 70–90%, Critical 90–100%, Over-Exploited >100%
  stage of extraction; + Saline class. 2024 national: 73.39% Safe / 10.54% Semi-critical
  / 3.05% Critical / 11.13% Over-Exploited (6,746 units). To be scraped to CSV in Phase 4.
- Status: NOT yet pulled (PDF tables need tabula/camelot pass).

## Known limitations / gaps (honest)
1. Telemetry window is 2021–2025 only; pre-2021 baseline needs manual-quarterly series (same portal, smaller files — pull in Phase 2 if needed).
2. Value semantics unverified: ~85 m readings look like depth-to-water, not MSL level; confirm against manual series + RL_MSL in Phase 2.
3. Station IDs may shift across years; Block/Tehsil fields are `-` in the sampled rows.
4. Rainfall join will be district-month granularity (IMD), not station-hour — documented ceiling on recharge modelling.
5. "Real-time" = latest NWDP pull, not a live 15-min firehose; no such public endpoint exists.
