
import asyncio
import json

from app import services
from app.schemas import QuizEvaluateRequest, QuizGenerateRequest


class CaptureQuizClient:
    def __init__(self):
        self.prompts = []

    async def complete_json(self, system, user, images=None):
        self.prompts.append(user)
        return {
            "question": {
                "questionId": "fresh-retest-ai-001",
                "conceptId": "quadratic-equations",
                "conceptName": "Quadratic Equations",
                "question": "A quadratic has roots 2 and -3. Which equation has exactly these roots?",
                "options": ["x²-x-6=0", "x²+x-6=0", "x²-5x+6=0", "x²+5x+6=0"],
                "correctAnswer": "x²+x-6=0",
                "difficulty": 3,
                "explanation": "The sum of roots is -1 and the product is -6, giving x²+x-6=0."
            }
        }


def test_retest_prompt_contains_original_work_and_is_fresh(monkeypatch):
    client = CaptureQuizClient()
    monkeypatch.setattr(services, "client", client)

    async def cached(*args, **kwargs):
        return []

    async def work(*args, **kwargs):
        return [{
            "question_number": "2",
            "question_text": "Solve 2x²+5x-3=0",
            "student_answer": "x=1/2, -3",
            "correct_answer": "x=1/2, -3/2",
            "marks_obtained": 2,
            "marks_total": 3,
            "error_type": "sign_error",
            "skill": "Factor and solve a quadratic equation",
        }]

    async def diagnosis(*args, **kwargs):
        return {
            "diagnosis": "Repeated sign handling issue while factoring.",
            "recommendation": "Verify factor signs with a new problem.",
            "confidence": 0.91,
            "evidence": ["Q2 lost a mark after a sign error."],
        }

    monkeypatch.setattr(services.persistence, "get_cached_questions", cached)
    monkeypatch.setattr(services.persistence, "get_recent_work_context", work)
    monkeypatch.setattr(services.persistence, "get_latest_diagnosis", diagnosis)

    async def persist(*args, **kwargs):
        return None
    monkeypatch.setattr(services.persistence, "persist_quiz_question", persist)

    req = QuizGenerateRequest(
        studentId="student-1",
        conceptId="quadratic-equations",
        conceptName="Quadratic Equations",
        subject="Mathematics",
        topic="Quadratic Equations",
        mode="retest",
        mastery=68,
        previousQuestionIds=["old-question"],
        skill="Factor and solve a quadratic equation",
        evidenceContext=[],
    )
    result = asyncio.run(services.quiz(req))
    assert result.question.questionId == "fresh-retest-ai-001"
    assert len(client.prompts) == 1
    prompt = client.prompts[0]
    assert "Solve 2x²+5x-3=0" in prompt
    assert "sign_error" in prompt
    assert "RETEST RULE" in prompt


def test_quiz_evaluation_does_not_call_ai(monkeypatch):
    async def fail(*args, **kwargs):
        raise AssertionError("AI must never be called to check an MCQ answer")

    monkeypatch.setattr(services, "client", type("NoAI", (), {"complete_json": fail})())

    async def get_question(*args, **kwargs):
        return {
            "question_id": "q-fast",
            "correct_answer": "Option A",
        }

    async def record(*args, **kwargs):
        return 80.0

    monkeypatch.setattr(services.persistence, "get_question", get_question)
    monkeypatch.setattr(services.persistence, "record_attempt", record)

    result = asyncio.run(services.evaluate_quiz(QuizEvaluateRequest(
        studentId="student-1",
        questionId="q-fast",
        conceptId="concept-1",
        answer="Option A",
        correctAnswer="Option A",
        mode="retest",
    )))
    assert result.correct is True
    assert result.mastery == 80.0
