import asyncio
from app import services
from app.schemas import DiagnosticGenerateRequest, QuizGenerateRequest

class FailingClient:
    async def complete_json(self, *args, **kwargs):
        raise RuntimeError('simulated provider outage')


def test_known_topic_fallback_is_domain_specific(monkeypatch):
    monkeypatch.setattr(services, 'client', FailingClient())
    req = DiagnosticGenerateRequest(
        studentId='demo-student', conceptId='physics-projectile-motion', conceptName='Projectile Motion',
        subject='Physics', topic='Projectile Motion', count=4, mode='topic'
    )
    result = asyncio.run(services.generate_diagnostic(req))
    assert len(result.questions) == 4
    assert any('projectile' in q.question.lower() for q in result.questions)
    assert all(q.skill for q in result.questions)
    assert all('best way to learn' not in q.question.lower() for q in result.questions)


def test_unknown_topic_fallback_is_rejected_without_trusted_content(monkeypatch):
    monkeypatch.setattr(services, 'client', FailingClient())
    req = DiagnosticGenerateRequest(
        studentId='demo-student', conceptId='history-industrial-revolution', conceptName='Industrial Revolution',
        subject='History', topic='Industrial Revolution', count=4, mode='topic'
    )
    try:
        asyncio.run(services.generate_diagnostic(req))
    except services.TopicContentUnavailable as exc:
        assert 'no trusted offline content' in str(exc).lower()
    else:
        raise AssertionError('unknown topic should not receive fabricated offline questions')


def test_practice_fallback_does_not_repeat_previous_question_id(monkeypatch):
    monkeypatch.setattr(services, 'client', FailingClient())
    req = QuizGenerateRequest(
        studentId='demo-student', conceptId='math-sets', conceptName='Sets', subject='Mathematics', topic='Sets',
        mode='retest', mastery=60, previousQuestionIds=['fallback-practice-math-sets-1']
    )
    result = asyncio.run(services.quiz(req))
    assert result.question.questionId not in req.previousQuestionIds
