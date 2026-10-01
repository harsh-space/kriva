"""Step 5: SQLite run log (subset of the Section 4.6 schema).

DB lives at ~/.router/runs.db (override with ROUTER_DB env var).
"""
import os
import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at  TEXT DEFAULT CURRENT_TIMESTAMP,
    repo        TEXT,
    commit_sha  TEXT,
    provider    TEXT,
    model       TEXT,
    prompt      TEXT,
    output      TEXT,
    tokens_in   INTEGER,
    tokens_out  INTEGER,
    latency_ms  INTEGER,
    success     INTEGER,   -- Phase 1: 1 = model responded, 0 = call failed
    error       TEXT
);
"""


def db_path() -> Path:
    override = os.environ.get("ROUTER_DB")
    return Path(override) if override else Path.home() / ".router" / "runs.db"


def _conn() -> sqlite3.Connection:
    path = db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.execute(SCHEMA)
    return conn


def log_run(**fields) -> None:
    with _conn() as conn:
        conn.execute(
            """INSERT INTO runs (repo, commit_sha, provider, model, prompt, output,
                                 tokens_in, tokens_out, latency_ms, success, error)
               VALUES (:repo, :commit_sha, :provider, :model, :prompt, :output,
                       :tokens_in, :tokens_out, :latency_ms, :success, :error)""",
            fields,
        )


def recent_runs(n: int = 10):
    with _conn() as conn:
        return conn.execute(
            "SELECT id, created_at, provider, model, tokens_in, tokens_out, "
            "latency_ms, success FROM runs ORDER BY id DESC LIMIT ?",
            (n,),
        ).fetchall()
