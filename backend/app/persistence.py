from __future__ import annotations
from typing import Any
from .supabase_store import SupabaseStore
from .store import memory
from .mastery import PRIOR, update_state, parse_datetime, iso, due_record
from .config import DEMO_TIME_TRAVEL
from .cache import cache_delete_student
from datetime import datetime, timezone

class Persistence:
    """Supabase-first persistence with memory fallback."""

    def __init__(self, db: SupabaseStore | None = None):
        self.db = db or SupabaseStore()

    @property
    def enabled(self) -> bool:
        return self.db.enabled

    async def ensure_student(self, student_id: str, display_name: str = "Demo Student") -> None:
        if self.enabled:
            await self.db.upsert("students", {"id": student_id, "display_name": display_name}, on_conflict="id")

    async def ensure_concept(self, concept_id: str, concept_name: str, subject: str = "", topic: str = "") -> None:
        if self.enabled:
            await self.db.upsert(
                "concepts",
                {
                    "id": concept_id,
                    "subject": subject or "General",
                    "topic": topic or concept_name,
                    "name": concept_name,
                    "metadata": {},
                },
                on_conflict="id",
            )

    async def save_diagnosis(self, student_id: str, diagnosis: dict[str, Any], concept_name: str = "", subject: str = "", topic: str = "") -> str | None:
        memory.save_diagnosis(student_id, diagnosis)
        if not self.enabled:
            return None
        await self.ensure_student(student_id)
        cid = diagnosis.get("weakestConceptId", "unknown-topic")
        await self.ensure_concept(cid, concept_name or diagnosis.get("weakestConceptName", cid), subject, topic)
        row = await self.db.insert(
            "diagnostics",
            {
                "student_id": student_id,
                "weakest_concept_id": cid,
                "confidence": diagnosis.get("confidence", 0),
                "evidence": diagnosis.get("evidence", []),
                "diagnosis": diagnosis.get("diagnosis", ""),
                "recommendation": diagnosis.get("recommendation", ""),
                "used_fallback": bool(diagnosis.get("usedFallback", False)),
            },
            return_rows=True,
        )
        return str(row[0]["id"]) if row else None

    async def save_diagnostic_questions(self, student_id: str, concept_id: str, questions: list[dict[str, Any]], diagnostic_id: str | None = None, mode: str = "diagnostic", subject: str = "", topic: str = "") -> None:
        memory.register_diagnostic(student_id, concept_id, questions)
        if not self.enabled:
            return
        await self.ensure_student(student_id)
        concept_name = questions[0].get("conceptName", concept_id) if questions else concept_id
        await self.ensure_concept(concept_id, concept_name, subject, topic)
        for q in questions:
            await self.db.upsert(
                "diagnostic_questions",
                {
                    "student_id": student_id,
                    "diagnostic_id": diagnostic_id,
                    "concept_id": concept_id,
                    "question_id": q["questionId"],
                    "question_text": q.get("question") or q.get("questionText", ""),
                    "options": q.get("options", []),
                    "correct_answer": q["correctAnswer"],
                    "explanation": q.get("explanation", ""),
                    "difficulty": str(q.get("difficulty", "")),
                    "source_context": {"mode": mode, "subject": subject, "topic": topic, "skill": q.get("skill", "")},
                },
                on_conflict="student_id,question_id",
            )

    async def save_work_analysis(self, student_id: str, analysis: dict[str, Any], filename: str = "uploaded-work", file_type: str = "") -> str | None:
        memory_items = []
        for q in analysis.get("questions", []):
            memory_items.append({
                "question_number": str(q.get("questionNumber", "")),
                "question_text": str(q.get("questionText", "")),
                "student_answer": str(q.get("studentAnswer", "")),
                "correct_answer": str(q.get("correctAnswer", "")),
                "marks_obtained": float(q.get("marksAwarded", 0) or 0),
                "marks_total": float(q.get("marksPossible", 0) or 0),
                "concept_id": q.get("conceptId"),
                "error_type": q.get("errorType", "unknown"),
                "misconception_tag": q.get("misconceptionTag", "other"),
                "skill": q.get("skill", ""),
                "ai_confidence": float(q.get("extractionConfidence", 0) or 0),
                "grading_confidence": float(q.get("gradingConfidence", 0) or 0),
            })
        memory.save_work_items(student_id, memory_items)
        if not self.enabled:
            return None
        await self.ensure_student(student_id)
        upload_rows = await self.db.insert("uploads", {
            "student_id": student_id, "filename": filename, "file_type": file_type,
            "source_text": "",
        }, return_rows=True)
        upload_id = str(upload_rows[0]["id"]) if upload_rows else None
        for q in analysis.get("questions", []):
            row = {
                "upload_id": upload_id, "student_id": student_id,
                "question_number": str(q.get("questionNumber", "")),
                "question_text": str(q.get("questionText", "")),
                "student_answer": str(q.get("studentAnswer", "")),
                "correct_answer": str(q.get("correctAnswer", "")),
                "marks_obtained": float(q.get("marksAwarded", 0) or 0),
                "marks_total": float(q.get("marksPossible", 0) or 0),
                "concept_id": q.get("conceptId"),
                "error_type": q.get("errorType", "unknown"),
                "misconception_tag": q.get("misconceptionTag", "other"),
                "ai_confidence": float(q.get("extractionConfidence", 0) or 0),
                "grading_confidence": float(q.get("gradingConfidence", 0) or 0),
            }
            await self.db.insert("work_items", row)
        return upload_id

    async def get_diagnostic_questions(self, student_id: str, concept_id: str) -> dict[str, dict[str, Any]]:
        if self.enabled:
            rows = await self.db.select(
                "diagnostic_questions",
                {"student_id": f"eq.{student_id}", "concept_id": f"eq.{concept_id}"},
                select="question_id,question_text,options,correct_answer,explanation,difficulty,source_context",
                order="created_at.desc",
            )
            if rows:
                result: dict[str, dict[str, Any]] = {}
                for row in reversed(rows):
                    result[row["question_id"]] = row
                return result
        return memory.get_questions(student_id, concept_id)

    async def get_question(self, student_id: str, concept_id: str, question_id: str) -> dict[str, Any] | None:
        questions = await self.get_diagnostic_questions(student_id, concept_id)
        return questions.get(question_id)

    async def get_existing_question_ids(self, student_id: str, concept_id: str) -> set[str]:
        if self.enabled:
            rows = await self.db.select(
                "diagnostic_questions",
                {"student_id": f"eq.{student_id}", "concept_id": f"eq.{concept_id}"},
                select="question_id", limit=200,
            )
            return {str(r.get("question_id")) for r in rows if r.get("question_id")}
        return set(memory.get_questions(student_id, concept_id).keys())

    async def get_recent_work_context(self, student_id: str, concept_id: str, limit: int = 12) -> list[dict[str, Any]]:
        if self.enabled:
            rows = await self.db.select(
                "work_items",
                {"student_id": f"eq.{student_id}", "concept_id": f"eq.{concept_id}"},
                select="question_number,question_text,student_answer,correct_answer,marks_obtained,marks_total,error_type,ai_confidence,grading_confidence",
                order="created_at.desc", limit=limit,
            )
            if rows:
                return list(reversed(rows))
        return list(reversed(memory.get_work_items(student_id, concept_id, limit)))

    async def get_latest_diagnosis(self, student_id: str, concept_id: str | None = None) -> dict[str, Any] | None:
        if self.enabled:
            filters = {"student_id": f"eq.{student_id}"}
            if concept_id:
                filters["weakest_concept_id"] = f"eq.{concept_id}"
            rows = await self.db.select("diagnostics", filters, order="created_at.desc", limit=1)
            return rows[0] if rows else None
        diagnoses = memory.diagnoses.get(student_id, [])
        for row in reversed(diagnoses):
            if not concept_id or row.get("weakestConceptId") == concept_id:
                return row
        return None


    async def get_cached_questions(self, student_id: str, concept_id: str, mode: str = "topic") -> list[dict[str, Any]]:
        if self.enabled:
            rows = await self.db.select(
                "diagnostic_questions",
                {"student_id": f"eq.{student_id}", "concept_id": f"eq.{concept_id}"},
                select="question_id,question_text,options,correct_answer,explanation,difficulty,source_context",
                order="created_at.desc", limit=50,
            )
            return [r for r in rows if (r.get("source_context") or {}).get("mode") == mode][:10]
        questions = memory.get_questions(student_id, concept_id)
        return [q for q in questions.values() if (q.get("source_context") or {}).get("mode") == mode][-10:]

    async def get_diagnostic_key(self, student_id: str, concept_id: str) -> dict[str, str]:
        questions = await self.get_diagnostic_questions(student_id, concept_id)
        return {qid: str(q.get("correct_answer") or q.get("correctAnswer") or "") for qid, q in questions.items()}

    async def persist_quiz_question(self, student_id: str, question: dict[str, Any], mode: str = "practice", subject: str = "", topic: str = "") -> None:
        await self.save_diagnostic_questions(student_id, question["conceptId"], [question], mode=mode, subject=subject, topic=topic)

    async def record_attempt(self, student_id: str, concept_id: str, attempt: dict[str, Any]) -> float:
        now = attempt.get("as_of") if DEMO_TIME_TRAVEL else None
        if not isinstance(now, datetime):
            now = datetime.now(timezone.utc)
        previous: dict[str, Any] = memory.mastery_state.get(student_id, {}).get(concept_id, {})
        rows: list[dict[str, Any]] = []
        db_row_available = False
        if self.enabled:
            await self.ensure_student(student_id)
            await self.ensure_concept(concept_id, attempt.get("conceptName", concept_id), attempt.get("subject", ""), attempt.get("topic", ""))
            rows = await self.db.select("mastery", {"student_id": f"eq.{student_id}", "concept_id": f"eq.{concept_id}"}, select="mastery,attempts,p_known,last_practiced,next_due,confirmed", limit=1)
            db_row_available = bool(self.db.available and rows)
            if db_row_available:
                previous = rows[0]
        if not previous:
            previous = {"p_known": PRIOR, "mastery": round(PRIOR * 100, 1), "attempts": 0, "confirmed": False}
        old_state = dict(previous)
        updated = update_state(previous, bool(attempt["correct"]), str(attempt.get("mode", attempt.get("source", "practice"))), now)
        old_mastery = round(float(previous.get("p_known", float(previous.get("mastery", PRIOR * 100)) / 100)) * 100, 1)
        question_id = attempt.get("questionId") or "unknown"
        row_attempt = {
            "student_id": student_id, "concept_id": concept_id, "question_id": question_id,
            "difficulty": str(attempt.get("difficulty", "")), "correct": bool(attempt["correct"]),
            "mastery_before": old_mastery, "mastery_after": updated["mastery"],
            "student_answer": attempt.get("answer", ""), "expected_answer": attempt.get("expectedAnswer", ""),
            "session_id": attempt.get("sessionId"),
        }
        memory.record_attempt(student_id, concept_id, {**attempt, **updated, "mastery_before": old_mastery, "mastery_after": updated["mastery"], "last_practiced": updated["last_practiced"], "next_due": updated["next_due"]})
        if self.enabled and self.db.available:
            db_row = {
                "student_id": student_id, "concept_id": concept_id, "mastery": updated["mastery"],
                "p_known": updated["p_known"], "last_practiced": updated["last_practiced"],
                "next_due": updated["next_due"], "confirmed": updated["confirmed"], "attempts": updated["attempts"],
            }
            self.db.available = True
            await self.db.upsert("mastery", db_row, on_conflict="student_id,concept_id")
            if self.db.available:
                await self.db.insert("attempts", row_attempt)
                await self.db.insert("mastery_snapshots", {
                    "student_id": student_id, "concept_id": concept_id,
                    "previous_mastery": old_mastery, "new_mastery": updated["mastery"],
                    "reason": "Delayed retest passed" if updated["confirmed"] and not old_state.get("confirmed", False) else ("Correct response" if attempt["correct"] else "Incorrect response"),
                    "source": attempt.get("source", "practice"), "session_id": attempt.get("sessionId"),
                })
        return float(updated["mastery"])

    async def get_mastery_state(self, student_id: str, concept_id: str) -> dict[str, Any]:
        if self.enabled:
            rows = await self.db.select("mastery", {"student_id": f"eq.{student_id}", "concept_id": f"eq.{concept_id}"}, select="mastery,attempts,p_known,last_practiced,next_due,confirmed", limit=1)
            if self.db.available and rows:
                return rows[0]
        return dict(memory.mastery_state.get(student_id, {}).get(concept_id, {}))

    async def due(self, student_id: str, as_of: datetime | None = None) -> list[dict[str, Any]]:
        now = as_of if (DEMO_TIME_TRAVEL and as_of is not None) else datetime.now(timezone.utc)
        states = dict(memory.mastery_state.get(student_id, {}))
        if self.enabled:
            rows = await self.db.select("mastery", {"student_id": f"eq.{student_id}"}, select="concept_id,mastery,p_known,last_practiced,next_due,confirmed")
            if self.db.available:
                states = {str(r.get("concept_id")): r for r in rows if r.get("concept_id")}
        due_items = []
        for concept_id, state in states.items():
            item = due_record(concept_id, str(state.get("conceptName") or concept_id.replace("-", " ").title()), state, now)
            if item:
                due_items.append(item)
        return sorted(due_items, key=lambda d: str(d.get("dueAt", "")))

    async def delete_student_data(self, student_id: str) -> bool:
        tables = ["attempts", "mastery_snapshots", "diagnostic_questions", "diagnostics", "work_items", "uploads", "feedback", "mastery", "students"]
        db_ok = True
        if self.enabled:
            for table in tables:
                db_ok = (await self.db.delete(table, {"student_id": f"eq.{student_id}"})) and db_ok if table != "students" else (await self.db.delete(table, {"id": f"eq.{student_id}"})) and db_ok
        cache_ok = cache_delete_student(student_id)
        db_ok = db_ok and cache_ok
        memory.mastery.pop(student_id, None)
        memory.mastery_state.pop(student_id, None)
        memory.attempts.pop(student_id, None)
        memory.diagnoses.pop(student_id, None)
        memory.work_items.pop(student_id, None)
        memory.student_profiles.pop(student_id, None)
        for key in [key for key in memory.diagnostic_questions if key[0] == student_id]:
            memory.diagnostic_questions.pop(key, None)
        for code, students in list(memory.class_students.items()):
            memory.class_students[code] = [sid for sid in students if sid != student_id]
        return db_ok

    async def progress(self, student_id: str) -> dict[str, Any]:
        if not self.enabled:
            base = memory.progress(student_id)
            base["timeline"] = []
            base["persistence"] = {"source": "memory-fallback", "available": False}
            return base
        mastery_rows = await self.db.select("mastery", {"student_id": f"eq.{student_id}"}, order="updated_at.desc")
        attempts = await self.db.select("attempts", {"student_id": f"eq.{student_id}"}, order="created_at.desc")
        diagnoses = await self.db.select("diagnostics", {"student_id": f"eq.{student_id}"}, order="created_at.desc")
        if not self.db.available:
            base = memory.progress(student_id)
            base["timeline"] = []
            base["persistence"] = {"source": "memory-fallback", "available": False, "error": self.db.last_error}
            return base
        mastery = {r["concept_id"]: float(r["mastery"]) for r in mastery_rows if r.get("concept_id")}
        timeline = [
            *[{"type":"attempt", **a} for a in attempts],
            *[{"type":"diagnosis", **d} for d in diagnoses],
        ]
        timeline.sort(key=lambda x: str(x.get("created_at", "")), reverse=True)
        return {"studentId": student_id, "mastery": mastery, "attempts": attempts, "diagnoses": diagnoses, "timeline": timeline[:20], "persistence": {"source":"supabase", "available": True}}

    async def save_feedback(self, feedback: dict[str, Any]) -> None:
        if self.enabled:
            await self.ensure_student(str(feedback["student_id"]))
            await self.db.insert("feedback", feedback)
        else:
            memory.feedback.insert(0, feedback)

<<<<<<< HEAD
    async def feedback_summary(self, student_ids: set[str]) -> dict[str, Any]:
        if self.enabled:
            rows = await self.db.select("feedback", {}, select="student_id,rating,comment,created_at", order="created_at.desc", limit=500)
        else:
            rows = memory.feedback
        rows = [r for r in rows if str(r.get("student_id")) in student_ids][:100]
=======
    async def feedback_summary(self) -> dict[str, Any]:
        if self.enabled:
            rows = await self.db.select("feedback", {}, select="rating,comment,created_at", order="created_at.desc", limit=100)
        else:
            rows = memory.feedback[:100]
>>>>>>> b9d02d34e42932237d9f91969848006efc59b2b1
        ratings = [int(r.get("rating", 0)) for r in rows if r.get("rating") is not None]
        comments = [str(r.get("comment")) for r in rows if r.get("comment")]
        return {
            "responses": len(ratings),
            "averageRating": round(sum(ratings) / len(ratings), 2) if ratings else 0,
            "recentComments": comments[:10],
        }

    async def teacher(self) -> tuple[list[dict[str, Any]], int]:
        if not self.enabled:
            return memory.teacher(), len(memory.mastery)
        rows = await self.db.select("mastery", {}, order="updated_at.desc")
        concepts_rows = await self.db.select("concepts", {}, select="id,name")
        names = {r["id"]: r.get("name", r["id"]) for r in concepts_rows if r.get("id")}
        agg: dict[str, list[float]] = {}
        for row in rows:
            cid = row.get("concept_id")
            if cid:
                agg.setdefault(cid, []).append(float(row.get("mastery", 0)))
        concepts = [
            {"conceptId": cid, "conceptName": names.get(cid, cid), "averageMastery": round(sum(v) / len(v), 1), "students": len(v)}
            for cid, v in agg.items()
        ]
        students = len({r.get("student_id") for r in rows if r.get("student_id")})
        return concepts, students

persistence = Persistence()
