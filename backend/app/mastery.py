from __future__ import annotations
from datetime import datetime, timezone, timedelta
import math
from typing import Any

PRIOR = 0.30
GUESS = 0.20
SLIP = 0.10
LEARN = 0.08
FORGETTING_HALF_LIFE_DAYS = 14.0
RETEST_DELAY_HOURS = 24

def parse_datetime(value: Any) -> datetime | None:
    if not value:
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    try:
        raw = str(value).replace("Z", "+00:00")
        dt = datetime.fromisoformat(raw)
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except (ValueError, TypeError):
        return None

def iso(dt: datetime | None) -> str | None:
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z") if dt else None

def decay_probability(p_known: float, last_practiced: Any, now: datetime | None = None) -> float:
    now = now or datetime.now(timezone.utc)
    last = parse_datetime(last_practiced)
    p = min(1.0, max(0.0, float(p_known if p_known is not None else PRIOR)))
    if not last:
        return p
    elapsed = max(0.0, (now - last).total_seconds() / 86400)
    retention = 0.5 ** (elapsed / FORGETTING_HALF_LIFE_DAYS)
    return min(1.0, max(0.0, PRIOR + (p - PRIOR) * retention))

def update_probability(p_known: float, correct: bool) -> float:
    p = min(1.0, max(0.0, float(p_known)))
    likelihood_known = 1 - SLIP if correct else SLIP
    likelihood_unknown = GUESS if correct else 1 - GUESS
    denom = p * likelihood_known + (1 - p) * likelihood_unknown
    posterior = (p * likelihood_known / denom) if denom > 0 else p
    return min(1.0, max(0.0, posterior + (1 - posterior) * LEARN))

def update_state(previous: dict[str, Any] | None, correct: bool, mode: str, now: datetime | None = None) -> dict[str, Any]:
    now = now or datetime.now(timezone.utc)
    previous = previous or {}
    p0 = float(previous.get("p_known", PRIOR))
    decayed = decay_probability(p0, previous.get("last_practiced"), now)
    p1 = update_probability(decayed, correct)
    was_due = parse_datetime(previous.get("next_due"))
    delayed_enough = bool(was_due and now >= was_due)
    confirmed = bool(previous.get("confirmed", False))
    if mode == "retest" and correct and delayed_enough:
        confirmed = True
    # Any new practice resets a spaced-retrieval window, including an unsuccessful retest.
    next_due = now + timedelta(hours=RETEST_DELAY_HOURS)
    attempts = int(previous.get("attempts", 0)) + 1
    return {
        "p_known": round(p1, 6),
        "mastery": round(p1 * 100, 1),
        "last_practiced": iso(now),
        "next_due": iso(next_due),
        "confirmed": confirmed,
        "attempts": attempts,
        "retestWasDue": delayed_enough,
        "provisional": not confirmed,
    }

def due_record(concept_id: str, concept_name: str, state: dict[str, Any], now: datetime | None = None) -> dict[str, Any] | None:
    now = now or datetime.now(timezone.utc)
    next_due = parse_datetime(state.get("next_due"))
    if not next_due or next_due > now or state.get("confirmed"):
        return None
    return {"conceptId": concept_id, "conceptName": concept_name, "dueAt": iso(next_due), "reason": "Spaced retest due; mastery remains provisional until a delayed retest is passed."}
