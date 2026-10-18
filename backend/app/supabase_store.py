from __future__ import annotations
from typing import Any
import httpx
from urllib.parse import urlencode
from .config import SUPABASE_URL, SUPABASE_SECRET_KEY, supabase_configured


class SupabaseStore:
    def __init__(self):
        self.enabled = supabase_configured()
        self.available = False if self.enabled else False
        self.last_error = ""
        self.headers = {
            "apikey": SUPABASE_SECRET_KEY,
            "Authorization": f"Bearer {SUPABASE_SECRET_KEY}",
            "Content-Type": "application/json",
        }

    def _ok(self):
        self.available = True
        self.last_error = ""

    def _fail(self, exc: Exception):
        self.available = False
        self.last_error = str(exc)[:300]

    async def ping(self) -> bool:
        if not self.enabled:
            self.available = False
            return False
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                r = await client.get(f"{SUPABASE_URL}/rest/v1/students?select=id&limit=1", headers=self.headers)
                r.raise_for_status()
            self._ok()
            return True
        except Exception as exc:
            self._fail(exc)
            return False

    async def insert(self, table: str, row: dict[str, Any], return_rows: bool = False) -> list[dict[str, Any]]:
        if not self.enabled:
            return []
        headers = {**self.headers, "Prefer": "return=representation" if return_rows else "return=minimal"}
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                r = await client.post(f"{SUPABASE_URL}/rest/v1/{table}", headers=headers, json=row)
                r.raise_for_status()
                self._ok()
                return r.json() if return_rows and r.content else []
        except Exception as exc:
            self._fail(exc)
            return []

    async def upsert(self, table: str, row: dict[str, Any], on_conflict: str, ignore_duplicates: bool = False) -> list[dict[str, Any]]:
        if not self.enabled:
            return []
        resolution = "ignore-duplicates" if ignore_duplicates else "merge-duplicates"
        headers = {**self.headers, "Prefer": f"resolution={resolution},return=representation"}
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                r = await client.post(f"{SUPABASE_URL}/rest/v1/{table}?on_conflict={on_conflict}", headers=headers, json=row)
                r.raise_for_status()
                self._ok()
                return r.json() if r.content else []
        except Exception as exc:
            self._fail(exc)
            return []

    async def select(self, table: str, filters: dict[str, str] | None = None, select: str = "*", order: str | None = None, limit: int | None = None) -> list[dict[str, Any]]:
        if not self.enabled:
            return []
        params: list[tuple[str, str]] = [("select", select)]
        for key, value in (filters or {}).items():
            params.append((key, value))
        if order:
            params.append(("order", order))
        if limit:
            params.append(("limit", str(limit)))
        query = urlencode(params)
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                r = await client.get(f"{SUPABASE_URL}/rest/v1/{table}?{query}", headers=self.headers)
                r.raise_for_status()
                data = r.json()
                self._ok()
                return data if isinstance(data, list) else []
        except Exception as exc:
            self._fail(exc)
            return []

    async def delete(self, table: str, filters: dict[str, str]) -> bool:
        if not self.enabled:
            return False
        params = urlencode(list(filters.items()))
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                r = await client.delete(f"{SUPABASE_URL}/rest/v1/{table}?{params}", headers=self.headers)
                r.raise_for_status()
                self._ok()
                return True
        except Exception as exc:
            self._fail(exc)
            return False
