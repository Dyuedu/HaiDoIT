"""One way to connect to Postgres, for ingest.py and extract.py.

Which Supabase endpoint to use, measured from the VPS:
  * direct   db.<ref>.supabase.co:5432   AAAA only, unreachable: the VPS has no global IPv6.
  * session  pooler:5432                 IPv4, prepared statements supported. Use this one.
  * trans.   pooler:6543                 IPv4, no prepared statements, turned off below.
"""

from __future__ import annotations

import os
import sys

import psycopg
from psycopg.rows import dict_row


def connect(dsn: str | None = None) -> psycopg.Connection:
    dsn = dsn or os.environ.get("DATABASE_URL")
    if not dsn:
        sys.exit("DATABASE_URL not set")
    opts = {"prepare_threshold": None} if ":6543" in dsn else {}
    return psycopg.connect(dsn, row_factory=dict_row, connect_timeout=30, **opts)
