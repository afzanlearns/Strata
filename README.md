# STRATA — Groundwater Resource Evaluation System

**SIH25068** · Ministry of Jal Shakti 

STRATA turns raw DWLR (Digital Water Level Recorder) telemetry into actionable groundwater intelligence — answering Smart India Hackathon problem statement SIH25068. One shared data pipeline powers two university submissions (Data Mining pattern discovery, Machine Learning prediction) behind a single working dashboard. No LLMs, no notebooks-only output — real data, a real product.

## Scope

- **Coverage**: Punjab + Rajasthan, 846 DWLR stations, 52 districts
- **Data**: ~2M readings, Sep 2022 – Dec 2025, 6-hourly, sourced from NWDP bulk telemetry
- **Ground truth**: CGWB GWRA-2025 official block/district stress categorization (Safe / Semi-critical / Critical / Over-exploited)
- **Covariate**: ERA5 rainfall data

## What it does

- Browse all 52 districts with official CGWB stress category, median depth, annual decline rate
- Drill into any station: historical trend, 30-day forecast overlay, 90-day critical-crossing risk score, 5 most similar stations, anomaly flags
- Explore mined association rules (support/confidence/lift) explaining what conditions co-occur with depletion
- Review a live anomaly feed — each flagged station manually diagnosable as sensor fault, datum artefact, or real depletion event

## Techniques implemented

| Area | Techniques |
|---|---|
| Preprocessing & similarity | Euclidean, cosine, Jaccard distance; `find_similar` station search |
| Association rule mining | Apriori, FP-Growth — 289 itemsets, 458 rules over district-season transactions |
| Classification | Decision tree, Naive Bayes, kNN — compared via confusion matrix, precision/recall/F1 |
| Clustering | k-means, hierarchical (Ward), DBSCAN — compared on the same station feature vectors |
| Outlier detection | Isolation Forest vs. z-score baseline |
| Regression | Linear regression with from-scratch gradient descent (matches scikit-learn to 5e-6) |
| Classification (ML) | Logistic regression with explicit sigmoid + gradient descent, ROC-AUC; MLP comparison |

Full syllabus-to-implementation mapping: see `docs/dm-mapping.md` and `docs/ml-mapping.md`.

## Stack

- **Pipeline**: Python, pandas, scikit-learn
- **Backend**: FastAPI, serving precomputed results — SQLite by default, MySQL via `DATABASE_URL`
- **Frontend**: React + TypeScript, built to a static bundle served by the backend
- **Storage**: one process for the full demo — no separate dev servers to keep in sync

## Setup

```bash
# Clone and enter the repo
git clone https://github.com/afzanlearns/Strata.git
cd Strata

# Backend
pip install -r requirements.txt
python backend/seed.py        # builds/loads the database from processed data
python -m uvicorn backend.app:app --port 8000  # serves the API + static frontend

# Frontend (only needed if rebuilding the UI)
cd frontend
npm install
npm run build                 # output copied to backend/static/
```

Open `http://127.0.0.1:8000` after seeding.

To use MySQL instead of the SQLite default:

```bash
export DATABASE_URL=mysql+pymysql://user:password@host/dbname
python backend/seed.py
```

## Project structure

```
data/           raw + processed telemetry, provenance notes
ml/             preprocessing, similarity, mining, classification,
                 clustering, anomaly detection, regression, logistic/MLP
backend/        FastAPI app, seed script, static frontend build
frontend/       React + TypeScript source
docs/           phase reports, DM/ML syllabus mapping writeups
scripts/        data acquisition, diagnostics
```

## Honest limitations

- Effective telemetry window is ~3.3 years (3 monsoon cycles) — seasonality is sound, decade-scale depletion claims are not
- Forecast/risk coverage runs over the full station set via batch inference; a small number of stations may still show sparse history in edge cases
- Block-level metadata is unreliable in the source data — classification labels are joined at district level from CGWB GWRA reports instead
- Linear models fail to anticipate regime changes in the 30-day forecast (see the SAS Nagar case study in `docs/ml-mapping.md`) — framed in-product as a persistence-baseline comparison, not hidden
