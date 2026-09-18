"""NWDP bulk downloader for STRATA (Phase 1).

Downloads CGWB six-hourly telemetry CSVs for the scoped states (Punjab + Rajasthan)
from the National Water Data Portal. Uses plain HTTPS range-capable GETs so a
dropped connection can resume with --resume.

Discovered 2026-09-18: the canonical host is https://nwdp.nwic.gov.in
(the older nwdp.nwic.in download host is unreachable from this network).
Resource UUIDs were scraped from the dataset page
  https://nwdp.nwic.gov.in/dataset/ground-water-level-telemetry-daily-cgwb-as-assam
(dataset UUID 3782ba15-9b12-46a8-ae44-410b1f84020e).

Usage:
    python scripts/fetch_nwdp.py
    python scripts/fetch_nwdp.py --resume
"""
from __future__ import annotations

import argparse
import hashlib
import os
import sys
import urllib.request

BASE = "https://nwdp.nwic.gov.in/dataset/3782ba15-9b12-46a8-ae44-410b1f84020e"
FILES = {
    # Punjab telemetry 2021-2025 (~98 MB per portal metadata 2025-05-11)
    "gwl_tel_6_hourly_cgwb_pb_2021_2025.csv":
        f"{BASE}/resource/2b3bfc59-e5ca-419b-b3c8-6133da16f2f7/download/gwl_tel_6_hourly_cgwb_pb_2021_2025.csv",
    # Rajasthan telemetry 2021-2025
    "gwl_tel_6_hourly_cgwb_rj_2021_2025.csv":
        f"{BASE}/resource/467fe983-e1f0-4428-91b7-0ade87b39f6d/download/gwl_tel_6_hourly_cgwb_rj_2021_2025.csv",
}

RAW = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "raw")


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fetch(name: str, url: str, resume: bool = False) -> str:
    os.makedirs(RAW, exist_ok=True)
    dest = os.path.join(RAW, name)
    existing = os.path.getsize(dest) if os.path.exists(dest) else 0
    req = urllib.request.Request(url)
    if resume and existing:
        req.add_header("Range", f"bytes={existing}-")
        print(f"[resume] {name} from byte {existing}")
    else:
        existing = 0
        print(f"[fetch] {name}")
    try:
        with urllib.request.urlopen(req, timeout=120) as r, open(dest, "ab" if existing else "wb") as f:
            while True:
                chunk = r.read(1 << 20)
                if not chunk:
                    break
                f.write(chunk)
    except Exception as e:  # noqa: BLE001 - network flakes are expected on 100MB pulls
        print(f"[warn] {name} interrupted after {os.path.getsize(dest)} bytes: {e}")
        print("       re-run with --resume to continue.")
        return dest
    print(f"[done] {name} bytes={os.path.getsize(dest)} sha256={sha256(dest)[:16]}...")
    return dest


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--resume", action="store_true")
    args = ap.parse_args()
    for name, url in FILES.items():
        fetch(name, url, resume=args.resume)
    return 0


if __name__ == "__main__":
    sys.exit(main())
