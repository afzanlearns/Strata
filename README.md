# STRATA — Groundwater Resource Evaluation System (SIH25068)

Real-time groundwater resource evaluation on DWLR telemetry (Ministry of Jal Shakti
problem statement), built as one shared pipeline serving two university deliverables:
**Data Mining** (pattern discovery) and **Machine Learning** (predictive functions).

Scope: **Punjab + Rajasthan**, NWDP CGWB six-hourly telemetry 2021–2025, CGWB GWRA
block categories as labels. See `docs/phase0-scoping.md`.

## Layout
- `docs/` — phase reports (`phase0-scoping.md`, …), `dm-mapping.md` + `ml-mapping.md` (Phase 11)
- `scripts/fetch_nwdp.py` — bulk downloader (Phase 1)
- `data/raw/PROVENANCE.md` — sources, URLs, limitations
- `data/processed/` — cleaned series + station feature vectors (Phase 2+)
- `ml/` — similarity, association, classification, clustering, anomalies, regression (Phases 2–8)
- `backend/` — Python API over MySQL-persisted results (Phase 9)
- `frontend/` — React/TypeScript dashboard, brutalist-minimal (Phase 10)

## Phase log
- [x] Phase 0 — scoping (Punjab + Rajasthan; NWDP-first access; technique map)
- [x] Phase 1 — raw pulls done (846 stations, ~2M rows; see `docs/phase1-report.md`)
- [x] Phase 2 — preprocessing + similarity done (sign convention locked, 846 feature
  vectors + 52 district aggregates, Euclidean/Cosine/Jaccard; see `docs/phase2-report.md`)
- [x] Phase 3 — association mining done (452 district-season transactions, ERA5 rainfall,
  Apriori ≡ FP-Growth, 458 rules; see `docs/phase3-report.md`)
- [x] Phase 4 — classification done (real GWRA-2025 labels, DT vs kNN vs NB with
  confusion matrices; kNN best, macro-F1 0.39; see `docs/phase4-report.md`)
- [x] Phase 5 — clustering done (k-means K=3 archetypes, Ward comparison ARI 0.372,
  DBSCAN+PCA noise screening; see `docs/phase5-report.md`)
- [x] Phase 6 — anomaly detection done (IF 49 flags, 63% independent of quarantine,
  sensor faults vs one real depletion event; see `docs/phase6-report.md`)
- [x] Phases 7–8 — ML layer done (regression = persistence mirage, GD matches sklearn;
  logistic fails linearly AUC 0.57, MLP 0.98; see `docs/phase78-report.md`)
- [x] Phases 9–10 — product done (FastAPI + SQLite/MySQL-switch, static React build,
  one-process demo; see `docs/phase910-report.md`)

## Demo
`python backend/seed.py && python -m uvicorn backend.app:app --port 8000` → open
http://127.0.0.1:8000

## Writeups
- `docs/dm-mapping.md` — Data Mining syllabus mapping
- `docs/ml-mapping.md` — Machine Learning syllabus mapping
