# STRATA

**Groundwater Resource Evaluation System**

Real-time groundwater monitoring dashboard for Punjab and Rajasthan, India. Built for the Smart India Hackathon (SIH25068), Ministry of Jal Shakti.

STRATA ingests telemetry from CGWB Deep Water Level Recorders, applies machine learning for forecasting, classification, anomaly detection, and association mining, and presents everything in a single browser-based dashboard.

---

## Quick start

```bash
# 1. Clone and install
git clone https://github.com/afzanlearns/Strata.git
cd Strata
python -m venv .venv && .venv\Scripts\activate   # Windows
pip install -r requirements.txt
cd frontend && npm install && cd ..

# 2. Seed database and start server
python backend/seed.py
python -m uvicorn backend.app:app --port 8000
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000). The landing page loads first; click **Open dashboard** to enter.

---

## What it does

| Capability | Technique | Key result |
|---|---|---|
| **Water-level tracking** | Sign unification, per-station z-score audit, quarantine flags | 802 stations, ~2M rows, sensor issues flagged without deletion |
| **30-day forecast** | Linear trend projection vs persistence baseline | R² 0.994 (persistence mirage — water levels change slowly) |
| **Crossing-risk score** | MLP neural network | P(depth crosses 35 m in 90 days); alert threshold 0.235 |
| **Groundwater classification** | k-NN, Decision Tree, Naive Bayes | GWRA-2025 labels; k-NN best macro-F1 0.39 |
| **Anomaly detection** | Isolation Forest | 49 flags; 63% independent of sensor quarantine |
| **Association mining** | Apriori algorithm | 458 rules from 452 district-season transactions |
| **Behaviour clustering** | k-means (K=3), Ward hierarchical, DBSCAN + PCA | ARI 0.372 vs hierarchical; 3 depth archetypes |

---

## Project structure

```
Strata/
├── backend/
│   ├── app.py              # FastAPI server
│   ├── seed.py             # Database seeder (SQLite / MySQL)
│   ├── models.py           # SQLAlchemy models
│   └── static/             # Built frontend (served at /)
├── frontend/
│   ├── src/
│   │   ├── App.tsx         # Dashboard (district/station/forecast/risk)
│   │   ├── Landing.tsx     # Landing page (hero, about, FAQ)
│   │   ├── api.ts          # API client
│   │   ├── index.css       # Dashboard theme + green accent system
│   │   └── landing.css     # Landing page styles
│   └── package.json
├── ml/
│   ├── similarity.py       # Euclidean / Cosine / Jaccard similarity
│   ├── association.py      # Apriori rule mining
│   ├── classify.py         # DT / NB / kNN classification
│   ├── cluster.py          # k-means / Ward / DBSCAN
│   ├── anomalies.py        # Isolation Forest
│   ├── regress.py          # Linear regression + scratch GD
│   ├── logistic.py         # Logistic regression + MLP
│   └── batch_infer.py      # Full-station batch inference
├── scripts/
│   ├── fetch_nwdp.py       # NWDP telemetry bulk downloader
│   └── audit_sign.py       # Per-station sign convention audit
├── data/
│   ├── raw/                # Source telemetry + GWRA PDFs
│   └── processed/          # Cleaned series, feature vectors, forecasts
├── docs/
│   ├── phase0-scoping.md   # Scope, users, technique map
│   ├── phase1-report.md    # Data acquisition
│   ├── phase2-report.md    # Preprocessing + similarity
│   ├── phase3-report.md    # Association mining
│   ├── phase4-report.md    # Classification
│   ├── phase5-report.md    # Clustering
│   ├── phase6-report.md    # Anomaly detection
│   ├── phase78-report.md   # Regression + logistic/MLP
│   ├── phase910-report.md  # Backend + frontend
│   ├── dm-mapping.md       # Data Mining syllabus mapping
│   ├── ml-mapping.md       # Machine Learning syllabus mapping
│   └── data-dictionary.md  # Column definitions, sign convention
└── requirements.txt
```

---

## Data

- **Source:** NWDP CGWB six-hourly DWLR telemetry
- **Coverage:** Punjab + Rajasthan, September 2022 – December 2025
- **Stations:** 802 active (846 originally ingested)
- **Rows:** ~2 million raw observations
- **Labels:** GWRA-2025 block categories (Safe / Semi-critical / Critical / Over-exploited) from Ministry of Jal Shakti PDFs

### Sign convention

Depth-to-water: **larger = deeper = worse.** Raw negative values are sensor convention, not actual negative depths. Per-station audit via `scripts/audit_sign.py`.

### Quarantine flags

Sensor-level issues are flagged in the `qflag` column (`ok` / `mad_outlier` / `nonphysical` / `datum_shift` / `gap`) — rows are never deleted.

---

## Tech stack

| Layer | Technology |
|---|---|
| Frontend | React 18, TypeScript, Vite, Geist Mono |
| Backend | FastAPI, SQLAlchemy, SQLite (default) / MySQL (switch via `DATABASE_URL`) |
| ML/DM | Python, pandas, scikit-learn, mlxtend |
| Fonts | Geist Sans + Geist Mono (bundled woff2) |

---

## API endpoints

| Endpoint | Description |
|---|---|
| `GET /api/summary` | Station count, district count, anomaly count |
| `GET /api/districts?state=` | District list with labels and station counts |
| `GET /api/district/{state}/{district}` | District detail with station table |
| `GET /api/station/{name}` | Station detail, series, forecast, risk |
| `GET /api/similar/{name}` | Nearest neighbours (Euclidean) |
| `GET /api/rules` | Association rules (support, confidence, lift) |
| `GET /api/alerts` | Anomaly alerts (Isolation Forest flags) |

---

## Dashboard

The dashboard has three columns:

1. **Left** — District list, filterable by state. Status pills (Safe / Semi-critical / Critical / Over-exploited) with station counts.
2. **Centre** — District overview or station detail. Shows depth trend chart, 30-day forecast (dashed blue), crossing-risk badge, annual decline, monsoon response, behaviour cluster, and similar stations.
3. **Right** — Association rules (antecedent → consequent with metrics) and anomaly alerts.

Landing page sections: hero, about, pipeline diagram, features, how-to-use with mockups, FAQ.

Dark mode toggle in both landing nav and dashboard header. Preference persists in localStorage.

---

## Production data refresh

```bash
# Full batch inference (forecasts + crossing risk for all stations)
python ml/batch_infer.py

# Use MySQL instead of SQLite
DATABASE_URL=mysql+pymysql://user:pw@host/strata python backend/seed.py

# After frontend changes
cd frontend && npm run build
Remove-Item -Recurse -Force ..\backend\static
Copy-Item -Recurse dist ..\backend\static
```

---

## Docs

- `docs/dm-mapping.md` — Data Mining syllabus technique mapping
- `docs/ml-mapping.md` — Machine Learning syllabus technique mapping
- `docs/data-dictionary.md` — Full column definitions and conventions

---

## License

Built for Smart India Hackathon 2025 (SIH25068). Ministry of Jal Shakti.
