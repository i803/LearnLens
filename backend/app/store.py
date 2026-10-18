from __future__ import annotations
from collections import defaultdict
from typing import Any

class MemoryStore:
    def __init__(self):
        self.mastery = defaultdict(dict)
        self.attempts: dict[str, list[dict[str, Any]]] = defaultdict(list)
        self.diagnoses: dict[str, list[dict[str, Any]]] = defaultdict(list)
        self.diagnostic_questions: dict[tuple[str, str], dict[str, dict[str, Any]]] = {}
        self.work_items: dict[str, list[dict[str, Any]]] = defaultdict(list)
        self.mastery_state: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
        self.student_profiles: dict[str, dict[str, Any]] = {}
        self.classes: dict[str, dict[str, Any]] = {}
        self.class_students: dict[str, list[str]] = defaultdict(list)
        self.class_attempts: dict[str, list[dict[str, Any]]] = defaultdict(list)
        self.feedback: list[dict[str, Any]] = []

    def save_diagnosis(self, student_id: str, diagnosis: dict[str, Any]):
        self.diagnoses[student_id].append(diagnosis)

    def register_diagnostic(self, student_id: str, concept_id: str, questions: list[dict[str, Any]]):
        bucket = self.diagnostic_questions.setdefault((student_id, concept_id), {})
        for q in questions:
            bucket[q["questionId"]] = q

    def get_questions(self, student_id: str, concept_id: str) -> dict[str, dict[str, Any]]:
        return self.diagnostic_questions.get((student_id, concept_id), {})

    def get_key(self, student_id: str, concept_id: str) -> dict[str, str]:
        return {qid: q["correctAnswer"] for qid, q in self.get_questions(student_id, concept_id).items()}

    def save_work_items(self, student_id: str, items: list[dict[str, Any]]):
        self.work_items[student_id].extend(items)

    def get_work_items(self, student_id: str, concept_id: str | None = None, limit: int = 12) -> list[dict[str, Any]]:
        rows = self.work_items[student_id]
        if concept_id:
            rows = [r for r in rows if r.get("concept_id") == concept_id]
        return rows[-limit:]

    def record_attempt(self, student_id: str, concept_id: str, attempt: dict[str, Any]):
        self.attempts[student_id].append(attempt)
        new_value = float(attempt.get("mastery_after", self.mastery[student_id].get(concept_id, 30.0)))
        self.mastery[student_id][concept_id] = round(max(0, min(100, new_value)), 1)
        self.mastery_state[student_id][concept_id] = {
            "p_known": round(float(attempt.get("p_known", self.mastery[student_id][concept_id] / 100)), 6),
            "mastery": self.mastery[student_id][concept_id],
            "last_practiced": attempt.get("last_practiced"),
            "next_due": attempt.get("next_due"),
            "confirmed": bool(attempt.get("confirmed", False)),
            "attempts": int(attempt.get("attempts", 1)),
        }
        profile = self.student_profiles.get(student_id, {})
        class_code = profile.get("classCode")
        if class_code:
            self.class_attempts[class_code].append({**attempt, "studentId": student_id, "conceptId": concept_id})
        return self.mastery[student_id][concept_id]

    def progress(self, student_id: str) -> dict[str, Any]:
        return {
            "studentId": student_id,
            "mastery": dict(self.mastery[student_id]),
            "attempts": self.attempts[student_id],
            "diagnoses": self.diagnoses[student_id],
        }

    def teacher(self) -> list[dict[str, Any]]:
        agg: dict[str, list[float]] = defaultdict(list)
        for student in self.mastery.values():
            for concept, score in student.items():
                agg[concept].append(score)
        return [
            {"conceptId": c, "averageMastery": round(sum(v) / len(v), 1), "students": len(v)}
            for c, v in agg.items()
        ]

memory = MemoryStore()
