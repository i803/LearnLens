from __future__ import annotations
import json, os, sqlite3
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if os.getenv("LEARNLENS_CACHE_PATH"):
    DB_PATH = Path(os.environ["LEARNLENS_CACHE_PATH"])
elif os.getenv("VERCEL") == "1":
    # Serverless filesystems are not durable; /tmp only provides a best-effort
    # per-instance cache. Use Supabase for persistent student learning records.
    DB_PATH = Path("/tmp/learnlens_ai_cache.sqlite3")
else:
    DB_PATH = ROOT / "data" / "ai_cache.sqlite3"


def _connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=5)
    conn.execute("""CREATE TABLE IF NOT EXISTS cache (
        key TEXT NOT NULL, kind TEXT NOT NULL, payload TEXT NOT NULL,
        owner_student_id TEXT NOT NULL DEFAULT '',
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (key, owner_student_id))""")
    # Upgrade an existing local cache schema without deleting cached data.
    cols = {row[1] for row in conn.execute("PRAGMA table_info(cache)").fetchall()}
    if "owner_student_id" not in cols:
        conn.execute("ALTER TABLE cache ADD COLUMN owner_student_id TEXT NOT NULL DEFAULT ''")
    conn.commit()
    return conn


def cache_get(key: str, kind: str, student_id: str = "demo-student") -> dict[str, Any] | None:
    try:
        with _connect() as conn:
            row = conn.execute("SELECT payload FROM cache WHERE key=? AND kind=? AND owner_student_id=?", (key, kind, student_id)).fetchone()
        value = json.loads(row[0]) if row else None
        return value if isinstance(value, dict) else None
    except (sqlite3.Error, json.JSONDecodeError, OSError):
        return None


def cache_put(key: str, kind: str, payload: dict[str, Any], student_id: str = "demo-student") -> None:
    try:
        with _connect() as conn:
            conn.execute("""INSERT INTO cache(key,kind,payload,owner_student_id)
                VALUES(?,?,?,?) ON CONFLICT(key,owner_student_id) DO UPDATE SET
                kind=excluded.kind,payload=excluded.payload,created_at=CURRENT_TIMESTAMP""",
                (key, kind, json.dumps(payload, ensure_ascii=False), student_id))
            conn.commit()
    except (sqlite3.Error, TypeError, OSError):
        # Cache is an optimization; a cache failure must not break learning.
        return


def cache_delete_student(student_id: str) -> bool:
    """Purge this student's result cache plus unowned legacy entries from old versions."""
    try:
        with _connect() as conn:
            conn.execute("DELETE FROM cache WHERE owner_student_id IN (?, '')", (student_id,))
            conn.commit()
        return True
    except (sqlite3.Error, OSError):
        return False
