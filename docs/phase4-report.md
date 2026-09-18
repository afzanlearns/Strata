# Phase 4 — Classification report

**Date:** 2026-09-18 · `ml/classify.py` · `scripts/build_labels.py`
· outputs: `data/processed/district_labels.csv`, `gwra2025_blocks.csv`,
`classification_comparison.csv`

## 1. Labels: real CGWB categories, not proxies
Scraped the official **GWRA-2025 block-wise categorization PDF** (cgwb.gov.in, 6,762
assessment units nationally — extraction count matches exactly, validating the parse).
Two real bugs fixed en route: OE/semi-critical cells carry trailing junk
(`'over exploited\n_'`) that a naive exact-match filter silently dropped (which briefly
produced a fiction of "no over-exploitation anywhere" — caught by the national-total
checksum), plus 6 transliteration aliases (Firozpur/Ferozepur, Rupnagar/Ropar…).
District label = **predominant (mode) block category**; `label_worst25` kept as a
sensitivity column (90% agreement; all 5 disagreements are genuinely mixed districts
like Ferozepur and Udaipur). 4 extra GWRA districts have no DWLR stations — noted, not forced.
Class reality at station level (district label broadcast = stated weak supervision):
**744 OE / 65 safe / 24 semi-critical / 13 critical** (critical: Ferozepur, Udaipur;
semi: SBS Nagar, Tonk). The imbalance IS the finding — this region really is that stressed.

## 2. Protocol
Behaviour-only features (11 hydrological columns; lat/lon/state deliberately excluded so
the test is whether dynamics alone predict the official category), median imputation,
stratified 5-fold CV with identical splits, k tuned per-fold by inner CV.

## 3. Comparison (accuracy lies here — read macro-F1)
| model | accuracy | macro-F1 | weighted-F1 | OE-F1 | safe | semi | crit |
|---|---|---|---|---|---|---|---|
| kNN (k=3 all folds) | **0.865** | **0.390** | 0.841 | 0.929 | 0.216 | 0.080 | 0.333 |
| Decision tree (entropy) | 0.694 | 0.292 | 0.746 | 0.828 | 0.197 | 0.029 | 0.113 |
| Naive Bayes | 0.676 | 0.285 | 0.739 | 0.817 | 0.262 | 0.000 | 0.061 |

## 4. Why kNN won — and why none of them is "good"
- **kNN wins** because stress is *locally clustered* in behaviour space: wells behaving
  like their neighbours share their category. k=3 chosen in all 5 folds = very local
  boundaries, which suits pocketed depletion.
- **Decision tree** fragments the minorities: axis-aligned splits carve the 88%-majority
  OE mass well (OE-F1 0.83) but shatter 13 critical samples into noise (F1 0.11).
- **Naive Bayes** fails structurally: its feature-independence assumption is violated
  (median/p10/p90 depth + trends are strongly correlated), and Gaussian likelihoods fit
  to 13–24 samples collapse — semi-critical F1 = 0.000.
- **Ceiling cause (all models):** CGWB categories derive from extraction/recharge ratios;
  we predict them from water-level *dynamics* — an inherently lossy mapping — plus
  district-to-station label broadcast noise (a recovering well in Sangrur is labeled OE).
  0.39 macro-F1 is therefore a *baseline with a documented ceiling*, and beating it
  (rainfall + pumping features, block-level labels) is explicit Phase 7+ future work.

## Phase exit: ✅ 3 classifiers compared with full confusion matrices → Phase 5 unblocked
(no new inputs needed — clustering reuses the station vectors).
