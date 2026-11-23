from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def register(email):
    res = client.post('/api/auth/register', json={'fullName': 'Test Learner', 'email': email,
                          'password': 'long-test-password'})
    assert res.status_code == 201, res.text
    return res.json()['data']['accessToken']

def test_two_users_ownership_and_login():
    first = register('owner@example.edu')
    second = register('guest@example.edu')
    payload = {'title': 'Course slides', 'description': 'Introduction',
               'url': 'https://example.com/course', 'category': 'lecture'}
    result = client.post('/api/resources', json=payload, headers={'Authorization': f'Bearer {first}'})
    assert result.status_code == 201, result.text
    rid = result.json()['data']['id']

    visible = client.get('/api/resources', params={'q': 'course'})
    assert visible.status_code == 200
    assert any(row['id'] == rid for row in visible.json()['data'])

    blocked = client.put(f'/api/resources/{rid}', json={**payload, 'title': 'Hacked'},
                         headers={'Authorization': f'Bearer {second}'})
    assert blocked.status_code == 404
    blocked_del = client.delete(f'/api/resources/{rid}', headers={'Authorization': f'Bearer {second}'})
    assert blocked_del.status_code == 404
    assert client.get(f'/api/resources/{rid}').json()['data']['title'] == 'Course slides'

    signed_in = client.post('/api/auth/login', json={'email': 'OWNER@example.edu',
                                               'password': 'long-test-password'})
    assert signed_in.status_code == 200
    assert signed_in.json()['data']['user']['email'] == 'owner@example.edu'
    assert client.get('/api/auth/me', headers={'Authorization': f'Bearer {first}'}).status_code == 200

    assert client.delete(f'/api/resources/{rid}', headers={'Authorization': f'Bearer {first}'}).status_code == 204
    assert client.get(f'/api/resources/{rid}').status_code == 404
