from __future__ import annotations

import hashlib
import secrets
import string
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Header, HTTPException

from ..config import demo_data_enabled, is_hosted_environment, supabase_configured
from ..schemas import CreateClassRequest
from ..persistence import persistence
from ..store import memory
from ..notes import get_misconception
from ..openrouter import client

router = APIRouter(tags=["Teacher classroom"])

DB_UNAVAILABLE = "The classroom database is unavailable. No sample data was loaded; check the Supabase connection and try again."
DB_REQUIRED = "Persistent Supabase storage must be configured for teacher classrooms on the hosted website. No sample data is available here."


async def _select_live(
    table: str,
    filters: dict[str, str] | None = None,
    *,
    select: str = "*",
    order: str | None = None,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    rows = await persistence.db.select(table, filters, select=select, order=order, limit=limit)
    if persistence.enabled and not persistence.db.available:
        raise HTTPException(status_code=503, detail=DB_UNAVAILABLE)
    return rows


async def _ensure_class_storage() -> None:
    """Hosted class data must be durable; configured-but-broken storage fails closed."""
    if is_hosted_environment() and not persistence.enabled:
        raise HTTPException(status_code=503, detail=DB_REQUIRED)
    if persistence.enabled and not await persistence.db.ping():
        raise HTTPException(status_code=503, detail=DB_UNAVAILABLE)


async def _get_class(code: str) -> dict | None:
    code = code.upper().strip()
    row = None
    if persistence.enabled:
        rows = await _select_live(
            "classes",
            {"code": f"eq.{code}"},
            select="code,name,teacher_name,teacher_key_hash,synthetic,created_at",
            limit=1,
        )
        row = rows[0] if rows else None
    else:
        row = memory.classes.get(code)

    if not row:
        return None
    # A legacy synthetic row must never be surfaced in a configured or hosted app.
    if row.get("synthetic") and (code != "CSE-A" or not demo_data_enabled()):
        return None
    return row


def _authorized(class_row: dict, code: str, supplied: str | None) -> bool:
    if not supplied:
        return False
    if class_row.get("synthetic") and code.upper() == "CSE-A":
        return demo_data_enabled() and secrets.compare_digest(supplied, "demo-teacher-key")
    digest = hashlib.sha256(supplied.encode()).hexdigest()
    return secrets.compare_digest(digest, str(class_row.get("teacher_key_hash", "")))


async def class_member_ids(code: str) -> set[str]:
    code = code.upper()
    if persistence.enabled:
        rows = await _select_live("students", {"class_code": f"eq.{code}"}, select="id,synthetic")
        return {
            str(row["id"])
            for row in rows
            if row.get("id") and not bool(row.get("synthetic", False))
        }
    return {
        sid for sid in memory.class_students.get(code, [])
        if not bool(memory.student_profiles.get(sid, {}).get("synthetic", False))
    }


def _concept_catalog() -> list[dict[str, str]]:
    # This is the column catalogue, not a collection of student measurements.
    return [
        {"id": "sets-types", "name": "Types of sets"},
        {"id": "sets-builder", "name": "Set-builder notation"},
        {"id": "sets-operations", "name": "Set operations and intervals"},
        {"id": "algebra-linear", "name": "Linear equations and signs"},
        {"id": "matrices", "name": "Matrices and row operations"},
    ]


@router.post("/teacher/classes")
async def create_class(req: CreateClassRequest):
    await _ensure_class_storage()
    alphabet = string.ascii_uppercase + string.digits
    code = "LL-" + "".join(secrets.choice(alphabet) for _ in range(5))
    teacher_key = secrets.token_urlsafe(24)
    row = {
        "code": code,
        "name": req.className.strip(),
        "teacher_name": req.teacherName.strip(),
        "teacher_key_hash": hashlib.sha256(teacher_key.encode()).hexdigest(),
        "synthetic": False,
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }

    if persistence.enabled:
        saved = await persistence.db.upsert(
            "classes",
            {
                "code": code,
                "name": row["name"],
                "teacher_name": row["teacher_name"],
                "teacher_key_hash": row["teacher_key_hash"],
                "synthetic": False,
            },
            on_conflict="code",
        )
        if not persistence.db.available or not saved:
            raise HTTPException(status_code=503, detail=DB_UNAVAILABLE)
    else:
        memory.classes[code] = row

    return {
        "classCode": code,
        "className": row["name"],
        "teacherKey": teacher_key,
        "teacherKeyShownOnce": True,
        "synthetic": False,
    }


async def _build_heatmap(class_row: dict, code: str) -> dict:
    code = code.upper()
    concepts = _concept_catalog()

    if class_row.get("synthetic"):
        if not demo_data_enabled() or code != "CSE-A":
            raise HTTPException(status_code=404, detail="Class not found")
        roster = class_row.get("demoRoster", [])
        tags = [tag for student in roster for tag in student.get("tags", [])]
        counts = Counter(tags)
        top = [
            {
                "tag": tag,
                "label": (get_misconception(tag) or {}).get("label", tag),
                "count": count,
            }
            for tag, count in counts.items()
        ]
        top.sort(key=lambda item: item["count"], reverse=True)
        return {
            "students": roster,
            "concepts": concepts,
            "topMisconceptions": top[:3],
            "synthetic": True,
            "dataMode": "local-demo",
            "classCode": code,
            "className": class_row.get("name"),
            "sampleNotice": "Illustrative synthetic data only; not measurements from real students.",
            "persistence": {"source": "bundled demo", "configured": False, "available": False},
        }

    # When Supabase is configured, its student roster is authoritative. In
    # memory-only local mode, the current process is the real-data store.
    profiles: dict[str, dict[str, Any]] = {}
    if persistence.enabled:
        profile_rows = await _select_live(
            "students",
            {"class_code": f"eq.{code}"},
            select="id,display_name,language,synthetic,consented_at",
        )
        for item in profile_rows:
            if not item.get("id") or bool(item.get("synthetic", False)):
                continue
            sid = str(item["id"])
            profiles[sid] = {
                "studentId": sid,
                "name": item.get("display_name") or "Student",
                "classCode": code,
                "language": item.get("language") or "en",
                "consentedAt": item.get("consented_at"),
                "synthetic": False,
            }
    else:
        for sid in memory.class_students.get(code, []):
            profile = memory.student_profiles.get(sid, {})
            if not profile.get("synthetic", False):
                profiles[sid] = profile

    class_ids = list(profiles.keys())
    students_by_id: dict[str, dict[str, Any]] = {
        sid: {
            "id": sid,
            "label": profile.get("name", "Student"),
            "mastery": {},
            "provisional": {},
            "synthetic": False,
        }
        for sid, profile in profiles.items()
    }

    attempts_by_student: Counter[str] = Counter()
    last_active: dict[str, str] = {}
    tag_students: dict[str, set[str]] = defaultdict(set)

    if persistence.enabled and class_ids:
        ids_filter = "in.(" + ",".join(class_ids) + ")"
        mastery_rows = await _select_live(
            "mastery",
            {"student_id": ids_filter},
            select="student_id,concept_id,mastery,confirmed",
        )
        for item in mastery_rows:
            sid = str(item.get("student_id") or "")
            cid = str(item.get("concept_id") or "")
            if sid not in students_by_id or not cid:
                continue
            students_by_id[sid]["mastery"][cid] = float(item.get("mastery") or 0)
            students_by_id[sid]["provisional"][cid] = not bool(item.get("confirmed", False))

        attempt_rows = await _select_live(
            "attempts",
            {"student_id": ids_filter},
            select="student_id,created_at",
            order="created_at.desc",
        )
        for item in attempt_rows:
            sid = str(item.get("student_id") or "")
            if sid not in students_by_id:
                continue
            attempts_by_student[sid] += 1
            created_at = str(item.get("created_at") or "")
            if created_at and (sid not in last_active or created_at > last_active[sid]):
                last_active[sid] = created_at

        work_rows = await _select_live(
            "work_items",
            {"student_id": ids_filter},
            select="student_id,misconception_tag",
        )
        for item in work_rows:
            sid = str(item.get("student_id") or "")
            tag = str(item.get("misconception_tag") or "")
            if sid in students_by_id and tag and tag != "other":
                tag_students[tag].add(sid)
    else:
        for sid in class_ids:
            profile = profiles[sid]
            mastery = {cid: float(value) for cid, value in memory.mastery.get(sid, {}).items()}
            states = memory.mastery_state.get(sid, {})
            students_by_id[sid]["mastery"].update(mastery)
            students_by_id[sid]["provisional"].update({cid: not bool(states.get(cid, {}).get("confirmed", False)) for cid in mastery})
            attempts = memory.attempts.get(sid, [])
            attempts_by_student[sid] = len(attempts)
            timestamps = [str(a.get("last_practiced") or a.get("created_at") or "") for a in attempts]
            if timestamps and max(timestamps):
                last_active[sid] = max(timestamps)
            for item in memory.work_items.get(sid, []):
                tag = str(item.get("misconception_tag") or "")
                if tag and tag != "other":
                    tag_students[tag].add(sid)

    # Add any genuinely observed topics that are outside the starter catalogue.
    known = {item["id"] for item in concepts}
    for cid in dict.fromkeys(cid for student in students_by_id.values() for cid in student["mastery"]):
        if cid not in known:
            concepts.append({"id": cid, "name": cid.replace("-", " ").replace("_", " ").title()})
            known.add(cid)

    students = list(students_by_id.values())
    for student in students:
        sid = student["id"]
        profile = profiles.get(sid, {})
        mastery_values = list(student["mastery"].values())
        student["joinedAt"] = profile.get("consentedAt")
        student["language"] = profile.get("language", "en")
        student["attempts"] = attempts_by_student.get(sid, 0)
        student["lastActive"] = last_active.get(sid)
        student["average"] = round(sum(mastery_values) / len(mastery_values), 1) if mastery_values else None

    students.sort(key=lambda student: str(student.get("joinedAt") or ""), reverse=True)
    averages = [student["average"] for student in students if student["average"] is not None]
    summary = {
        "joined": len(students),
        "started": sum(1 for student in students if student["attempts"] or student["mastery"]),
        "attempts": sum(attempts_by_student.values()),
        "averageMastery": round(sum(averages) / len(averages), 1) if averages else None,
    }
    top = [
        {
            "tag": tag,
            "label": (get_misconception(tag) or {}).get("label", tag),
            "count": len(sids),
        }
        for tag, sids in tag_students.items()
    ]
    top.sort(key=lambda item: item["count"], reverse=True)

    return {
        "students": students,
        "concepts": concepts,
        "topMisconceptions": top[:3],
        "synthetic": False,
        "dataMode": "real",
        "classCode": code,
        "className": class_row.get("name"),
        "summary": summary,
        "sampleNotice": "Only real class nicknames and saved learning signals are included. Empty cells mean no saved evidence.",
        "persistence": {
            "source": "supabase" if persistence.enabled else "local-memory",
            "configured": persistence.enabled,
            "available": bool(persistence.enabled and persistence.db.available),
        },
    }


@router.get("/teacher/classes/{code}/heatmap")
async def class_heatmap(code: str, x_teacher_key: str | None = Header(default=None, alias="X-Teacher-Key")):
    if is_hosted_environment() or persistence.enabled:
        await _ensure_class_storage()
    if demo_data_enabled():
        from .student import _ensure_demo_class
        _ensure_demo_class()
    row = await _get_class(code)
    if not row:
        raise HTTPException(404, "Class not found. No synthetic classroom is available in real-data mode.")
    if not _authorized(row, code, x_teacher_key):
        raise HTTPException(403, "A valid X-Teacher-Key is required")
    return await _build_heatmap(row, code)


@router.post("/teacher/classes/{code}/reteach-plan")
async def reteach_plan(code: str, x_teacher_key: str | None = Header(default=None, alias="X-Teacher-Key")):
    if is_hosted_environment() or persistence.enabled:
        await _ensure_class_storage()
    if demo_data_enabled():
        from .student import _ensure_demo_class
        _ensure_demo_class()
    row = await _get_class(code)
    if not row:
        raise HTTPException(404, "Class not found. No synthetic classroom is available in real-data mode.")
    if not _authorized(row, code, x_teacher_key):
        raise HTTPException(403, "A valid X-Teacher-Key is required")

    heatmap = await _build_heatmap(row, code)
    top = heatmap.get("topMisconceptions", [])[:3]
    prompt = (
        "Create a practical 10-minute reteach plan for a first-year engineering mathematics class. "
        "Use only these observed misconception tags; do not invent student results. Return JSON with "
        "minutes, steps [{t,what}], groups [{misconception,studentLabels,activity}], and checkQuestion. "
        "Keep minutes at 10.\n"
        + str(top)
        + "\nRoster labels: "
        + str([student["label"] for student in heatmap.get("students", [])])
    )
    try:
        raw = await client.complete_json("You are a careful teacher-support assistant. Output valid JSON only.", prompt)
        steps = raw.get("steps") if isinstance(raw.get("steps"), list) else []
        groups = raw.get("groups") if isinstance(raw.get("groups"), list) else []
        if not steps:
            raise ValueError("No valid steps returned")
        plan = {
            "minutes": 10,
            "steps": [{"t": str(step.get("t", "")), "what": str(step.get("what", ""))} for step in steps[:5] if isinstance(step, dict)],
            "groups": [
                {
                    "misconception": str(group.get("misconception", "")),
                    "studentLabels": [str(value) for value in group.get("studentLabels", []) if isinstance(value, str)],
                    "activity": str(group.get("activity", "")),
                }
                for group in groups[:3] if isinstance(group, dict)
            ],
            "checkQuestion": str(raw.get("checkQuestion", "Ask students to explain the target misconception in their own words.")),
        }
        return {"plan": plan, "provider": raw.get("_learnlens_provider", "AI provider"), "generatedByAI": True, "synthetic": bool(heatmap.get("synthetic"))}
    except Exception:
        steps = [
            {"t": "0-2 min", "what": "Show one short worked example and ask students to predict the next step."},
            {"t": "2-5 min", "what": "Model the highest-frequency misconception and contrast it with the correct rule."},
            {"t": "5-8 min", "what": "Pair students to solve a fresh example; ask them to explain why each step is valid."},
            {"t": "8-10 min", "what": "Use the exit question below and group students for follow-up practice."},
        ]
        groups = []
        for item in top:
            misconception = get_misconception(item.get("tag", "other")) or {}
            groups.append({
                "misconception": item.get("label", "Review needed"),
                "studentLabels": [],
                "activity": misconception.get("reteach", "Teacher-led review and a short example."),
            })
        return {
            "plan": {
                "minutes": 10,
                "steps": steps,
                "groups": groups,
                "checkQuestion": "For the highest-priority misconception, solve a new example and explain why the endpoints/operations are included or excluded.",
            },
            "provider": "rule-based fallback",
            "generatedByAI": False,
            "synthetic": bool(heatmap.get("synthetic")),
        }


@router.get("/api/teacher/analytics")
@router.get("/teacher/analytics")
async def teacher_analytics(
    classCode: str | None = None,
    x_teacher_key: str | None = Header(default=None, alias="X-Teacher-Key"),
):
    """Return mode/status by default; return learning analytics only for an authorized class."""
    supabase_available = False
    if persistence.enabled:
        supabase_available = await persistence.db.ping()
    meta: dict[str, Any] = {
        "concepts": [],
        "studentsTracked": 0,
        "demoDataEnabled": demo_data_enabled(),
        "dataMode": "local-demo" if demo_data_enabled() else "real",
        "hosted": is_hosted_environment(),
        "persistence": {
            "source": "supabase" if persistence.enabled else "local-memory",
            "configured": supabase_configured(),
            "available": supabase_available,
        },
    }
    if not classCode:
        return meta

    if is_hosted_environment() or persistence.enabled:
        await _ensure_class_storage()
    if demo_data_enabled():
        from .student import _ensure_demo_class
        _ensure_demo_class()
    row = await _get_class(classCode)
    if not row:
        raise HTTPException(404, "Class not found")
    if not _authorized(row, classCode, x_teacher_key):
        raise HTTPException(403, "A valid X-Teacher-Key is required")
    heatmap = await _build_heatmap(row, classCode)

    concepts_summary = []
    for concept in heatmap["concepts"]:
        scores = [
            float(student["mastery"][concept["id"]])
            for student in heatmap["students"]
            if concept["id"] in student.get("mastery", {})
        ]
        if scores:
            concepts_summary.append({
                "conceptId": concept["id"],
                "conceptName": concept["name"],
                "averageMastery": round(sum(scores) / len(scores), 1),
                "students": len(scores),
            })
    meta.update({"concepts": concepts_summary, "studentsTracked": len(heatmap["students"])})
    return meta
