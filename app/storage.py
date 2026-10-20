from __future__ import annotations

import sqlite3
import threading
import time
import uuid
from pathlib import Path

JOB_COLUMNS = (
    "id", "original_name", "stored_path", "status", "error", "language",
    "model", "provider", "is_demo", "progress", "created_at", "updated_at",
)

_SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
    id TEXT PRIMARY KEY,
    original_name TEXT NOT NULL,
    stored_path TEXT NOT NULL,
    status TEXT NOT NULL,
    error TEXT,
    language TEXT,
    model TEXT,
    provider TEXT,
    is_demo INTEGER NOT NULL DEFAULT 0,
    progress REAL NOT NULL DEFAULT 0.0,
    created_at REAL NOT NULL,
    updated_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS segments (
    job_id TEXT NOT NULL,
    idx INTEGER NOT NULL,
    start REAL NOT NULL,
    end REAL NOT NULL,
    text TEXT NOT NULL,
    PRIMARY KEY (job_id, idx),
    FOREIGN KEY (job_id) REFERENCES jobs (id) ON DELETE CASCADE
);
"""


class JobStore:
    """Persistenza SQLite di lavori e segmenti. Thread-safe per uso locale."""

    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON")
        with self._conn:
            self._conn.executescript(_SCHEMA)

    def create_job(self, *, original_name: str, stored_path: Path, language: str, model: str, provider: str) -> dict:
        job_id = uuid.uuid4().hex
        now = time.time()
        with self._lock, self._conn:
            self._conn.execute(
                "INSERT INTO jobs (id, original_name, stored_path, status, language, model, provider, is_demo, created_at, updated_at) "
                "VALUES (?, ?, ?, 'queued', ?, ?, ?, ?, ?, ?)",
                (job_id, original_name, str(stored_path), language, model, provider, int(provider == "demo"), now, now),
            )
        return self.get_job(job_id)

    def update_job(self, job_id: str, **fields) -> dict | None:
        allowed = set(JOB_COLUMNS) - {"id", "created_at"}
        updates = {k: v for k, v in fields.items() if k in allowed}
        if not updates:
            return self.get_job(job_id)
        updates["updated_at"] = time.time()
        set_clause = ", ".join(f"{k} = ?" for k in updates)
        with self._lock, self._conn:
            self._conn.execute(f"UPDATE jobs SET {set_clause} WHERE id = ?", (*updates.values(), job_id))
        return self.get_job(job_id)

    def get_job(self, job_id: str) -> dict | None:
        with self._lock:
            row = self._conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
        return dict(row) if row else None

    def list_jobs(self) -> list[dict]:
        with self._lock:
            rows = self._conn.execute("SELECT * FROM jobs ORDER BY created_at DESC").fetchall()
        return [dict(r) for r in rows]

    def next_queued_job(self) -> dict | None:
        with self._lock:
            row = self._conn.execute(
                "SELECT * FROM jobs WHERE status = 'queued' ORDER BY created_at LIMIT 1"
            ).fetchone()
        return dict(row) if row else None

    def save_segments(self, job_id: str, segments) -> None:
        rows = [(job_id, i, s.start, s.end, s.text) for i, s in enumerate(segments)]
        with self._lock, self._conn:
            self._conn.execute("DELETE FROM segments WHERE job_id = ?", (job_id,))
            self._conn.executemany(
                "INSERT INTO segments (job_id, idx, start, end, text) VALUES (?, ?, ?, ?, ?)",
                rows,
            )

    def get_segments(self, job_id: str) -> list[dict]:
        with self._lock:
            rows = self._conn.execute(
                "SELECT idx, start, end, text FROM segments WHERE job_id = ? ORDER BY idx",
                (job_id,),
            ).fetchall()
        return [dict(r) for r in rows]

    def delete_job(self, job_id: str) -> bool:
        with self._lock, self._conn:
            cur = self._conn.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
        return cur.rowcount > 0

    def close(self) -> None:
        with self._lock:
            self._conn.close()
