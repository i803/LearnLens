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
    no_consent = client.post('/auth/join', json={'name':'Green Owl','classCode':'CSE-A','language':'en','consent':False})
    assert no_consent.status_code == 400
    email_like = client.post('/auth/join', json={'name':'student@example.com','classCode':'CSE-A','language':'en','consent':True})
    assert email_like.status_code == 422
    joined = client.post('/auth/join', json={'name':'Green Owl','classCode':'CSE-A','language':'kn','consent':True})
    assert joined.status_code == 200
    assert joined.json()['studentId'].startswith('stu_')
    assert joined.json()['language'] == 'kn'


def test_teacher_demo_heatmap_requires_key_and_is_marked_synthetic():
    denied = client.get('/teacher/classes/CSE-A/heatmap')
    assert denied.status_code == 403
    response = client.get('/teacher/classes/CSE-A/heatmap', headers={'X-Teacher-Key':'demo-teacher-key'})
    assert response.status_code == 200
    body = response.json()
    assert body['synthetic'] is True
    assert len(body['students']) == 8
    assert body['sampleNotice']


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
