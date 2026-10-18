from datetime import datetime, timezone, timedelta
from app.mastery import PRIOR, update_state, decay_probability, due_record
from app.notes import NOTES, MISCONCEPTIONS, search_notes, infer_misconception


def test_notes_library_has_expected_minimum_and_ids_are_unique():
    assert len(NOTES) >= 30
    assert len(MISCONCEPTIONS) >= 20
    assert len({n['id'] for n in NOTES}) == len(NOTES)
    assert len({m['id'] for m in MISCONCEPTIONS}) == len(MISCONCEPTIONS)


def test_retrieval_returns_relevant_interval_note():
    results = search_notes('interval endpoint included square bracket', limit=3)
    assert results
    assert any('interval' in f'{r.get("title", "")} {r.get("content", "")}'.lower() for r in results)
    assert all('score' in r and r['score'] > 0 for r in results)


def test_misconception_rule_smoke():
    q = {'questionText':'Write interval in set-builder form', 'studentAnswer':'I excluded the right endpoint', 'teacherFeedback':'Right endpoint should be included', 'errorType':'conceptual'}
    assert infer_misconception(q) == 'interval_endpoint_inclusion'


def test_retest_remains_provisional_until_due_then_confirms():
    start = datetime(2026, 1, 1, 10, tzinfo=timezone.utc)
    first = update_state({'p_known':PRIOR,'attempts':0,'confirmed':False}, True, 'practice', start)
    too_early = update_state(first, True, 'retest', start + timedelta(hours=23))
    due = update_state(first, True, 'retest', start + timedelta(hours=25))
    assert not first['confirmed'] and first['provisional']
    assert not too_early['confirmed']
    assert due['confirmed'] and not due['provisional']


def test_forgetting_moves_probability_toward_prior():
    now = datetime(2026, 2, 1, tzinfo=timezone.utc)
    after = decay_probability(0.95, now - timedelta(days=14), now)
    assert PRIOR < after < 0.95


def test_due_record_only_for_due_unconfirmed_mastery():
    now = datetime(2026, 1, 2, tzinfo=timezone.utc)
    record = {'next_due':(now - timedelta(minutes=1)).isoformat(), 'confirmed':False, 'p_known':0.4}
    assert due_record('sets-types','Types of sets',record,now)
    record['confirmed'] = True
    assert due_record('sets-types','Types of sets',record,now) is None
