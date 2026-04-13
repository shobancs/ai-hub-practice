"""
storage/database.py - SQLite persistence layer

Stores: operation history, cumulative cost, and optional result cache.

Reusable pattern: a lightweight DB class that any interface (CLI, API,
web UI) can share.  Swap to PostgreSQL by changing the connection string.
"""
from __future__ import annotations

import hashlib
import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class Database:
    """
    Thread-safe SQLite wrapper for Text Processor history and caching.

    Usage:
        db = Database("text_processor.db")
        db.save_result(operation, source, result_text, tokens_in, tokens_out, cost)
        rows = db.get_history(limit=10)
        cached = db.get_cached("sha256-of-input")
    """

    def __init__(self, db_path: str = "text_processor.db") -> None:
        self.db_path = Path(db_path)
        self._conn: Optional[sqlite3.Connection] = None
        self._init_db()
        logger.info("Database ready at %s", self.db_path)

    # ── Lifecycle ──────────────────────────────────────────────────────────────

    def _get_conn(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
            self._conn.row_factory = sqlite3.Row
        return self._conn

    def _init_db(self) -> None:
        conn = self._get_conn()
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS history (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at   TEXT    NOT NULL,
                operation    TEXT    NOT NULL,
                source       TEXT    NOT NULL,
                source_type  TEXT    NOT NULL DEFAULT 'text',
                input_hash   TEXT,
                result       TEXT    NOT NULL,
                model        TEXT,
                input_tokens INTEGER DEFAULT 0,
                output_tokens INTEGER DEFAULT 0,
                cost_usd     REAL    DEFAULT 0.0,
                latency_ms   REAL    DEFAULT 0.0
            );

            CREATE TABLE IF NOT EXISTS cache (
                input_hash TEXT PRIMARY KEY,
                operation  TEXT NOT NULL,
                result     TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS session_costs (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                recorded_at TEXT NOT NULL,
                cost_usd   REAL NOT NULL,
                tokens     INTEGER NOT NULL,
                model      TEXT NOT NULL
            );
        """)
        conn.commit()

    def close(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None

    # ── Write operations ───────────────────────────────────────────────────────

    def save_result(
        self,
        operation: str,
        source: str,
        result: str,
        *,
        source_type: str = "text",
        input_text: str = "",
        model: str = "",
        input_tokens: int = 0,
        output_tokens: int = 0,
        cost_usd: float = 0.0,
        latency_ms: float = 0.0,
    ) -> int:
        """Persist a completed operation to the history table."""
        input_hash = self._hash(input_text + operation) if input_text else None
        conn = self._get_conn()
        cur = conn.execute(
            """
            INSERT INTO history
              (created_at, operation, source, source_type, input_hash, result,
               model, input_tokens, output_tokens, cost_usd, latency_ms)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.utcnow().isoformat(),
                operation, source, source_type, input_hash, result,
                model, input_tokens, output_tokens, cost_usd, latency_ms,
            ),
        )
        conn.commit()
        logger.debug("Saved result id=%d operation=%s", cur.lastrowid, operation)
        return cur.lastrowid

    def cache_result(self, input_text: str, operation: str, result: str) -> None:
        """Store a result in the cache table for future reuse."""
        key = self._hash(input_text + operation)
        conn = self._get_conn()
        conn.execute(
            "INSERT OR REPLACE INTO cache (input_hash, operation, result, created_at) VALUES (?, ?, ?, ?)",
            (key, operation, result, datetime.utcnow().isoformat()),
        )
        conn.commit()

    def record_session_cost(self, cost_usd: float, tokens: int, model: str) -> None:
        conn = self._get_conn()
        conn.execute(
            "INSERT INTO session_costs (recorded_at, cost_usd, tokens, model) VALUES (?, ?, ?, ?)",
            (datetime.utcnow().isoformat(), cost_usd, tokens, model),
        )
        conn.commit()

    # ── Read operations ────────────────────────────────────────────────────────

    def get_cached(self, input_text: str, operation: str) -> Optional[str]:
        """Return a cached result or None."""
        key = self._hash(input_text + operation)
        conn = self._get_conn()
        row = conn.execute(
            "SELECT result FROM cache WHERE input_hash = ? AND operation = ?", (key, operation)
        ).fetchone()
        if row:
            logger.info("Cache hit for operation=%s", operation)
            return row["result"]
        return None

    def get_history(self, limit: int = 20, operation: Optional[str] = None) -> list[dict]:
        """Return recent history rows as plain dicts."""
        conn = self._get_conn()
        if operation:
            rows = conn.execute(
                "SELECT * FROM history WHERE operation = ? ORDER BY id DESC LIMIT ?",
                (operation, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM history ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
        return [dict(r) for r in rows]

    def get_total_cost(self) -> float:
        """Return cumulative cost across all recorded sessions."""
        conn = self._get_conn()
        row = conn.execute("SELECT COALESCE(SUM(cost_usd), 0) as total FROM history").fetchone()
        return round(row["total"], 6)

    def get_stats(self) -> dict:
        """Return a summary statistics dict."""
        conn = self._get_conn()
        stats = conn.execute(
            """
            SELECT
                COUNT(*)                        AS total_operations,
                COALESCE(SUM(cost_usd), 0)      AS total_cost_usd,
                COALESCE(SUM(input_tokens + output_tokens), 0) AS total_tokens,
                COALESCE(AVG(latency_ms), 0)    AS avg_latency_ms
            FROM history
            """
        ).fetchone()
        ops = conn.execute(
            "SELECT operation, COUNT(*) as cnt FROM history GROUP BY operation ORDER BY cnt DESC"
        ).fetchall()
        return {
            "total_operations": stats["total_operations"],
            "total_cost_usd": round(stats["total_cost_usd"], 4),
            "total_tokens": stats["total_tokens"],
            "avg_latency_ms": round(stats["avg_latency_ms"], 1),
            "operations_breakdown": {r["operation"]: r["cnt"] for r in ops},
        }

    # ── Internal ───────────────────────────────────────────────────────────────

    @staticmethod
    def _hash(text: str) -> str:
        return hashlib.sha256(text.encode()).hexdigest()
