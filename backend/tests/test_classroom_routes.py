from fastapi.testclient import TestClient
from app.main import app
from app.store import memory

client = TestClient(app)


def test_health_exposes_notes_and_tag_counts():
    response = client.get('/health')
    assert response.status_code == 200
    body = response.json()
    assert body['notesCount'] >= 30
    assert body['misconceptionCount'] >= 20
    assert 'providers' in body


def test_demo_class_join_requires_consent_and_nickname_only():
    from app.config import demo_data_enabled
    no_consent = client.post('/auth/join', json={'name':'Green Owl','classCode':'CSE-A','language':'en','consent':False})
    assert no_consent.status_code == 400
    email_like = client.post('/auth/join', json={'name':'student@example.com','classCode':'CSE-A','language':'en','consent':True})
    assert email_like.status_code == 422
    joined = client.post('/auth/join', json={'name':'Green Owl','classCode':'CSE-A','language':'kn','consent':True})
    if demo_data_enabled():
        assert joined.status_code == 200
        assert joined.json()['studentId'].startswith('stu_')
        assert joined.json()['language'] == 'kn'
    else:
        assert joined.status_code == 404


def test_teacher_demo_heatmap_is_only_available_in_local_demo_mode():
    from app.config import demo_data_enabled
    denied = client.get('/teacher/classes/CSE-A/heatmap')
    if demo_data_enabled():
        assert denied.status_code == 403
        response = client.get('/teacher/classes/CSE-A/heatmap', headers={'X-Teacher-Key':'demo-teacher-key'})
        assert response.status_code == 200
        body = response.json()
        assert body['synthetic'] is True
        assert body['dataMode'] == 'local-demo'
        assert len(body['students']) == 8
        assert body['sampleNotice']
    else:
        assert denied.status_code == 404
        blocked = client.get('/teacher/classes/CSE-A/heatmap', headers={'X-Teacher-Key':'demo-teacher-key'})
        assert blocked.status_code == 404


def test_class_create_returns_one_time_teacher_key():
    result = client.post('/teacher/classes', json={'className':'Test Class','teacherName':'Reviewer'})
    assert result.status_code == 200
    body = result.json()
    assert body['classCode'].startswith('LL-')
    assert len(body['teacherKey']) >= 20
    assert body['teacherKeyShownOnce'] is True
    # Test isolation: remove the in-memory-only class created by this test.
    memory.classes.pop(body['classCode'], None)


def test_real_class_shows_joined_student_and_their_progress():
    made = client.post('/teacher/classes', json={'className':'Real Class','teacherName':'T'}).json()
    code, key = made['classCode'], made['teacherKey']
    joined = client.post('/auth/join', json={'name':'Blue Falcon','classCode':code,'language':'en','consent':True}).json()
    body = client.get(f'/teacher/classes/{code}/heatmap', headers={'X-Teacher-Key':key}).json()
    assert body['synthetic'] is False and body['summary']['joined'] == 1
    row = body['students'][0]
    assert row['label'] == 'Blue Falcon' and row['joinedAt'] and row['attempts'] == 0 and row['mastery'] == {}
    assert row['id'] == joined['studentId']


def test_feedback_summary_is_teacher_only_and_class_scoped():
    mine = client.post('/teacher/classes', json={'className':'Class A','teacherName':'Teacher'}).json()
    other = client.post('/teacher/classes', json={'className':'Class B','teacherName':'Teacher'}).json()
    sid = client.post('/auth/join', json={'name':'Fox','classCode':mine['classCode'],'language':'en','consent':True}).json()['studentId']
    client.post('/feedback', json={'studentId':sid,'sessionId':'s','rating':5,'helpfulAspects':[],'confusingAspects':[],'wouldUseAgain':'yes','comment':'great lesson'})
    assert client.get(f"/feedback/summary?classCode={mine['classCode']}").status_code == 403
    ok = client.get(f"/feedback/summary?classCode={mine['classCode']}", headers={'X-Teacher-Key':mine['teacherKey']}).json()
    assert ok['responses'] == 1 and ok['recentComments'] == ['great lesson']
    none = client.get(f"/feedback/summary?classCode={other['classCode']}", headers={'X-Teacher-Key':other['teacherKey']}).json()
    assert none['responses'] == 0


def test_upload_must_be_a_real_pdf_or_image():
    r = client.post('/work/analyze', files={'files': ('evil.pdf', b'MZ not a pdf', 'application/pdf')}, data={'studentId':'x'})
    assert r.status_code == 415


def test_rate_limit_returns_429(monkeypatch):
    import app.main as m
    m._hits.clear(); monkeypatch.setattr(m, 'RATE_LIMIT_PER_MIN', 3)
    codes = [client.get('/teacher/analytics').status_code for _ in range(5)]
    assert codes[:3] == [200, 200, 200] and codes[3:] == [429, 429]
    m._hits.clear()


def test_teacher_analytics_is_authorized_and_scoped_to_one_class():
    first = client.post('/teacher/classes', json={'className':'Analytics A','teacherName':'Teacher'}).json()
    second = client.post('/teacher/classes', json={'className':'Analytics B','teacherName':'Teacher'}).json()
    client.post('/auth/join', json={'name':'Red Kite','classCode':first['classCode'],'language':'en','consent':True})

    unauthorized = client.get(f"/teacher/analytics?classCode={first['classCode']}")
    assert unauthorized.status_code == 403

    first_response = client.get(
        f"/teacher/analytics?classCode={first['classCode']}",
        headers={'X-Teacher-Key': first['teacherKey']},
    )
    second_response = client.get(
        f"/teacher/analytics?classCode={second['classCode']}",
        headers={'X-Teacher-Key': second['teacherKey']},
    )
    assert first_response.status_code == second_response.status_code == 200
    assert first_response.json()['studentsTracked'] == 1
    assert second_response.json()['studentsTracked'] == 0


def test_teacher_analytics_without_class_credentials_never_returns_global_student_data():
    client.post('/teacher/classes', json={'className':'Private Class','teacherName':'Teacher'})
    response = client.get('/teacher/analytics')
    assert response.status_code == 200
    body = response.json()
    assert body['concepts'] == []
    assert body['studentsTracked'] == 0
    assert body['dataMode'] in {'local-demo', 'real'}
    assert 'demoDataEnabled' in body


def test_hosted_teacher_pages_fail_closed_without_supabase(monkeypatch):
    from app.routers import student as student_router
    from app.routers import teacher as teacher_router
    monkeypatch.setattr(teacher_router, "is_hosted_environment", lambda: True)
    monkeypatch.setattr(student_router, "is_hosted_environment", lambda: True)
    monkeypatch.setattr(teacher_router, "demo_data_enabled", lambda: False)
    monkeypatch.setattr(student_router, "demo_data_enabled", lambda: False)

    heatmap = client.get('/teacher/classes/CSE-A/heatmap', headers={'X-Teacher-Key': 'demo-teacher-key'})
    assert heatmap.status_code == 503
    assert 'No sample data' in heatmap.json()['detail']

    create = client.post('/teacher/classes', json={'className':'Hosted Class','teacherName':'Teacher'})
    assert create.status_code == 503

    join = client.post('/auth/join', json={'name':'Green Owl','classCode':'CSE-A','language':'en','consent':True})
    assert join.status_code == 503
