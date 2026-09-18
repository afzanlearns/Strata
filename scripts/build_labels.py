"""Build district labels from the GWRA-2025 block-wise categorization PDF.

Label rule (stated, defensible): within a district, the label is the most severe
quantity category covering >= 25% of assessed blocks; else the mode. Salinity-only
blocks are excluded from the quantity vote (CGWB treats salinity as a separate,
quality-based class). Severity: over_exploited > critical > semi_critical > safe.

Output: data/processed/district_labels.csv (state, district, label, n_blocks, vote detail)
Run: python scripts/build_labels.py
"""
from __future__ import annotations

import os
import re

import pandas as pd
import pymupdf

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF = os.path.join(BASE, "data", "raw", "gwra2025_blockwise.pdf")
OUT = os.path.join(BASE, "data", "processed", "district_labels.csv")
# GWRA spelling -> telemetry spelling (transliteration variants, same districts)
ALIAS = {"FIROZPUR": "FEROZEPUR", "MUKTSAR": "MUKATSAR", "RUPNAGAR": "ROPAR",
         "CHITTAURGARH": "CHITTORGARH", "DHAULPUR": "DHOLPUR", "JALOR": "JALORE"}
SEV = {"safe": 0, "semi_critical": 1, "critical": 2, "over_exploited": 3}


def norm_cat(raw: str) -> str:
    """Cells arrive as 'over exploited\\n_', 'semi critical\\n_', 'safe', ..."""
    c = re.sub(r"[\s_]+", "_", str(raw).strip().lower()).strip("_")
    return {"over_exploited": "over_exploited", "semi_critical": "semi_critical",
            "critical": "critical", "safe": "safe", "salinity": "salinity",
            "saline": "salinity"}.get(c, "")


def extract_rows() -> pd.DataFrame:
    doc = pymupdf.open(PDF)
    rows = []
    for page in doc:
        tabs = page.find_tables()
        for tab in tabs:
            for r in tab.extract():
                if len(r) >= 5 and norm_cat(r[4]):
                    rows.append([str(r[1]).strip(), str(r[2]).strip(),
                                 str(r[3]).strip(), norm_cat(r[4])])
    df = pd.DataFrame(rows, columns=["state", "district", "unit", "category"])
    # fallback sanity: table extraction must cover ~6.7k units
    print(f"extracted rows={len(df)} states={df.state.nunique()}")
    return df


def district_label(votes: pd.Series) -> tuple[str, str, str]:
    """Primary label = predominant (mode) block category.
    Sensitivity column = worst category covering >= 25% of blocks.
    Salinity-only blocks excluded from the quantity vote (separate CGWB class)."""
    qty = votes[votes != "salinity"]
    if len(qty) == 0:
        return "salinity", "all-saline", "salinity"
    frac = qty.value_counts(normalize=True)
    mode = frac.idxmax()
    worst25 = next((c for c in ["over_exploited", "critical", "semi_critical"]
                    if frac.get(c, 0) >= 0.25), mode)
    return mode, f"mode-{mode}={frac.max():.2f}", worst25


def main() -> None:
    df = extract_rows()
    df.to_csv(os.path.join(BASE, "data", "processed", "gwra2025_blocks.csv"), index=False)
    keep = df[df.state.str.upper().isin(["PUNJAB", "RAJASTHAN"])].copy()
    keep["state"] = keep.state.str.lower()
    keep["district"] = keep.district.str.upper().replace(ALIAS)
    labels = []
    for (state, district), g in keep.groupby(["state", "district"]):
        lab, how, worst25 = district_label(g.category)
        labels.append({"state": state, "district": district, "label": lab,
                       "label_worst25": worst25, "n_blocks": len(g),
                       "oe_frac": round(float((g.category == "over_exploited").mean()), 3),
                       "rule": how})
    lab = pd.DataFrame(labels)
    lab.to_csv(OUT, index=False)
    print(lab.label.value_counts().to_string())
    print(f"districts={len(lab)}")
    # join check vs telemetry districts (both sides upper-cased)
    tel = pd.read_csv(os.path.join(BASE, "data", "processed", "district_features.csv"),
                      usecols=["state", "district"])
    have = {(s.lower(), d.upper()) for s, d in lab[["state", "district"]].values}
    need = {(r.iloc[0].lower(), r.iloc[1].upper()) for _, r in tel.iterrows()}
    print("telemetry districts missing labels:",
          sorted(f"{s}/{d}" for s, d in (need - have)))


if __name__ == "__main__":
    main()
