# Phases 9–10 — Backend API + dashboard report

**Date:** 2026-09-18 · `backend/` (app, models, db, seed) · `frontend/` (React+TS, brutalist)
Demo: `python backend/seed.py && python -m uvicorn backend.app:app --port 8000` → open
http://127.0.0.1:8000. **One process**: API + built static frontend (`backend/static`).

## Decisions (as locked)
- **SQLite default, MySQL switch:** `DATABASE_URL` env var (`sqlite:///strata.db` default;
  `mysql+pymysql://…` for production). Schema uses only MySQL-compatible generic types;
  no SQLite-isms. Rationale: zero setup friction at demo time; "production-ready for
  MySQL" stays an honest writeup line.
- **Static build served by FastAPI**, not Vite dev server: one terminal, no sync failures,
  closer to real deployment. (`npm run dev` remains the iteration loop; the demo runs
  `npm run build` output copied to `backend/static`.)
- **Dashboard never re-runs the pipeline:** seed materializes stations (features + label +
  cluster + anomaly), districts, top-100 rules, forecast sample, tuned-threshold risks
  (≥0.235), weekly series (72K points). Similarity is the one live computation (z-scored
  Euclidean over stored vectors — milliseconds).

## Endpoints (all verified live)
`/api/summary` · `/api/districts[?state]` · `/api/districts/{st}/{d}` (with stations) ·
`/api/stations/{name}` (features, forecast, risk, series) · `…/similar` · `/api/rules` ·
`/api/alerts`. Bug caught in verification: `{name:path}` greedily swallowed `/similar` —
fixed by route ordering, re-verified (Akalgarh M_1 → 5 neighbours + full series).

## Dashboard surfaces (checklist-linked)
District picker with CGWB label chips → station table (depth, Δ/yr, anomaly/cluster flags)
→ station view: status, **trend chart with 30-day forecast overlay**, 90-day crossing-risk
badge, similar stations, anomaly flag → side panels: top association rules with lift,
anomaly alerts. Footer states the depth convention and model thresholds on-screen —
no hidden semantics during a demo.

## Phase exit: ✅ demoable product → Phase 11 (mapping writeups) unblocked
