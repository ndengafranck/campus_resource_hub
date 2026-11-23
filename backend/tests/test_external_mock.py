from fastapi.testclient import TestClient
from app.main import app
from app.routers import external

client = TestClient(app)

def test_open_library_adapter(monkeypatch):
    async def fake_get_json(url, params):
        assert url == 'https://openlibrary.org/search.json'
        assert params['limit'] == 5
        return {'docs': [{'key': '/works/OL1W', 'title': 'Algorithms',
                          'author_name': ['A. Example'], 'first_publish_year': 2020}]}
    monkeypatch.setattr(external, 'get_json', fake_get_json)
    res = client.get('/api/external/books', params={'title': 'algorithms'})
    assert res.status_code == 200
    assert res.json()['data'][0]['authors'] == ['A. Example']

def test_crossref_adapter(monkeypatch):
    async def fake_get_json(url, params):
        assert url == 'https://api.crossref.org/works'
        assert params['query.bibliographic'] == 'machine learning'
        return {'message': {'items': [{'DOI': '10.1234/demo', 'title': ['Learning'],
                  'author': [{'given': 'A', 'family': 'Scholar'}],
                  'published': {'date-parts': [[2025, 5]]}, 'URL': 'https://doi.org/10.1234/demo'}]}}
    monkeypatch.setattr(external, 'get_json', fake_get_json)
    res = client.get('/api/external/papers', params={'query': 'machine learning'})
    assert res.status_code == 200
    assert res.json()['data'][0]['year'] == 2025
