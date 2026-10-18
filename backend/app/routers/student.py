from __future__ import annotations
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from ..schemas import ProgressResponse, FeedbackRequest, FeedbackSummaryResponse, JoinRequest, DeleteDataRequest
from ..config import AI_ENABLED, DEMO_MODE, DEMO_TIME_TRAVEL, MAX_UPLOAD_MB, ai_configured, openrouter_configured, gemini_configured, OPENROUTER_MODEL, supabase_configured
from ..persistence import persistence
from ..store import memory
from ..supabase_store import SupabaseStore
from ..notes import NOTES, MISCONCEPTIONS
from ..cache import DB_PATH
from ..mastery import parse_datetime

router = APIRouter(tags=["Student, privacy and system"])

def _ensure_demo_class() -> dict:
    code = "CSE-A"
    if code not in memory.classes:
        roster = [
            {"id":"sample-01","label":"Sample student 1","mastery":{"sets-types":82,"sets-builder":48,"sets-operations":55,"algebra-linear":74,"matrices":63},"provisional":{"sets-types":False,"sets-builder":True,"sets-operations":True,"algebra-linear":False,"matrices":True},"tags":["interval_endpoint_inclusion"]},
            {"id":"sample-02","label":"Sample student 2","mastery":{"sets-types":65,"sets-builder":41,"sets-operations":52,"algebra-linear":58,"matrices":71},"provisional":{"sets-types":True,"sets-builder":True,"sets-operations":True,"algebra-linear":True,"matrices":False},"tags":["interval_endpoint_inclusion","set_builder_domain_ignored"]},
            {"id":"sample-03","label":"Sample student 3","mastery":{"sets-types":88,"sets-builder":73,"sets-operations":38,"algebra-linear":69,"matrices":61},"provisional":{"sets-types":False,"sets-builder":True,"sets-operations":True,"algebra-linear":False,"matrices":True},"tags":["union_overlap_double_count"]},
            {"id":"sample-04","label":"Sample student 4","mastery":{"sets-types":54,"sets-builder":48,"sets-operations":46,"algebra-linear":51,"matrices":44},"provisional":{"sets-types":True,"sets-builder":True,"sets-operations":True,"algebra-linear":True,"matrices":True},"tags":["interval_endpoint_inclusion","set_builder_domain_ignored"]},
            {"id":"sample-05","label":"Sample student 5","mastery":{"sets-types":91,"sets-builder":68,"sets-operations":73,"algebra-linear":83,"matrices":80},"provisional":{"sets-types":False,"sets-builder":False,"sets-operations":True,"algebra-linear":False,"matrices":False},"tags":[]},
            {"id":"sample-06","label":"Sample student 6","mastery":{"sets-types":63,"sets-builder":34,"sets-operations":48,"algebra-linear":62,"matrices":57},"provisional":{"sets-types":True,"sets-builder":True,"sets-operations":True,"algebra-linear":True,"matrices":True},"tags":["interval_endpoint_inclusion","union_overlap_double_count"]},
            {"id":"sample-07","label":"Sample student 7","mastery":{"sets-types":76,"sets-builder":56,"sets-operations":62,"algebra-linear":77,"matrices":65},"provisional":{"sets-types":False,"sets-builder":True,"sets-operations":True,"algebra-linear":False,"matrices":True},"tags":["set_builder_domain_ignored"]},
            {"id":"sample-08","label":"Sample student 8","mastery":{"sets-types":43,"sets-builder":29,"sets-operations":42,"algebra-linear":49,"matrices":52},"provisional":{"sets-types":True,"sets-builder":True,"sets-operations":True,"algebra-linear":True,"matrices":True},"tags":["interval_endpoint_inclusion","union_overlap_double_count"]},
        ]
        memory.classes[code] = {"code": code, "name": "CSE A - Sample classroom", "teacher_name": "LearnLens Demo Teacher", "teacher_key_hash": "demo-key-hash", "synthetic": True, "demoRoster": roster, "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")}
    return memory.classes[code]

def _concept_catalog() -> list[dict]:
    return [
      {"id":"sets-types","name":"Types of sets"},
      {"id":"sets-builder","name":"Set-builder notation"},
      {"id":"sets-operations","name":"Set operations and intervals"},
      {"id":"algebra-linear","name":"Linear equations and signs"},
      {"id":"matrices","name":"Matrices and row operations"},
    ]

@router.get("/health")
async def health():
    supabase_available = await persistence.db.ping() if supabase_configured() else False
    return {
      "status":"ok", "aiEnabled":AI_ENABLED, "demoMode":DEMO_MODE, "aiConfigured":ai_configured(),
      "model":OPENROUTER_MODEL if openrouter_configured() else ("Gemini (configured)" if gemini_configured() else "offline fallback"),
      "supabaseConfigured":supabase_configured(), "supabaseAvailable":supabase_available,
      "providers":[
        {"name":"OpenRouter", "ok":openrouter_configured(), "configured":openrouter_configured(), "freeModelOnly":True},
        {"name":"Gemini", "ok":gemini_configured(), "configured":gemini_configured(), "freeTierRequired":True},
      ],
      "cache":{"enabled":True,"kind":"SQLite","pathConfigured":bool(str(DB_PATH))},
      "notesCount":len(NOTES), "misconceptionCount":len(MISCONCEPTIONS), "maxUploadMB":MAX_UPLOAD_MB,
      "demoTimeTravelEnabled":DEMO_TIME_TRAVEL,
    }

@router.get("/api/student/progress", response_model=ProgressResponse)
@router.get("/student/progress", response_model=ProgressResponse)
async def student_progress(studentId: str = "demo-student"):
    return ProgressResponse(**(await persistence.progress(studentId)))

@router.get("/student/due")
async def student_due(studentId: str, asOf: datetime | None = None):
    if asOf is not None and not DEMO_TIME_TRAVEL:
        raise HTTPException(400, "Time travel is disabled outside demo mode")
    return {"items": await persistence.due(studentId, asOf), "demoTimeTravelEnabled": DEMO_TIME_TRAVEL}

@router.post("/auth/join")
async def join_class(req: JoinRequest):
    name = " ".join(req.name.split()).strip()
    if not name or "@" in name or len(name) > 50:
        raise HTTPException(422, "Use a nickname only; do not enter an email address.")
    code = req.classCode.strip().upper()
    demo = _ensure_demo_class()
    class_row = memory.classes.get(code)
    if not class_row and persistence.enabled:
        rows = await persistence.db.select("classes", {"code": f"eq.{code}"}, select="code,name,synthetic", limit=1)
        if rows:
            class_row = rows[0]
    if not class_row:
        raise HTTPException(404, "Class code not found. Ask your teacher to share the code.")
    if not req.consent:
        raise HTTPException(400, "Consent is required before learning data is saved.")
    student_id = "stu_" + uuid.uuid4().hex
    profile = {"studentId": student_id, "name": name, "classCode": code, "language": req.language, "consentedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"), "synthetic": False}
    memory.student_profiles[student_id] = profile
    if student_id not in memory.class_students[code]:
        memory.class_students[code].append(student_id)
    if persistence.enabled:
        await persistence.db.upsert("students", {"id": student_id, "display_name": name, "class_code": code, "language": req.language, "consented_at": profile["consentedAt"], "synthetic": False}, on_conflict="id")
    return {"studentId":student_id,"name":name,"classCode":code,"language":req.language,"consentedAt":profile["consentedAt"],"synthetic":False}

@router.post("/student/delete-data")
async def delete_student_data(req: DeleteDataRequest):
    student_id = req.studentId.strip()
    if student_id == "demo-student":
        raise HTTPException(400, "The shared demo profile cannot be deleted. Join with your own class nickname first.")
    db_ok = await persistence.delete_student_data(student_id)
    return {"deleted":True,"studentId":student_id,"databaseCleanupComplete":db_ok,"note":"Browser-local session data should also be cleared on this device."}

@router.post("/feedback")
async def feedback_submit(req: FeedbackRequest):
    await persistence.save_feedback({"student_id":req.studentId,"session_id":req.sessionId,"rating":req.rating,"helpful_aspects":req.helpfulAspects,"confusing_aspects":req.confusingAspects,"would_use_again":req.wouldUseAgain,"comment":req.comment})
    return {"ok":True}

@router.get("/feedback/summary", response_model=FeedbackSummaryResponse)
async def feedback_summary():
    return FeedbackSummaryResponse(**(await persistence.feedback_summary()))
