"""DB layer: SQLite by default, MySQL via DATABASE_URL.

Demo rule: zero setup friction -- `python backend/seed.py && uvicorn backend.app:app`
just works on SQLite. For MySQL: set DATABASE_URL=mysql+pymysql://user:pw@host/strata
(all column types are MySQL-compatible; no SQLite-isms in the schema).
"""
from __future__ import annotations

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

URL = os.environ.get("DATABASE_URL", "sqlite:///strata.db")
CONNECT_ARGS = {"check_same_thread": False} if URL.startswith("sqlite") else {}
engine = create_engine(URL, connect_args=CONNECT_ARGS)
Session = sessionmaker(bind=engine)
Base = declarative_base()
