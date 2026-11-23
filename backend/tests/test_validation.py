import pytest
from pydantic import ValidationError
from fastapi.testclient import TestClient
from app.schemas import ResourceBody, Registration
from app.main import app

client = TestClient(app)

def test_schema_rejects_unsafe_scheme():
    with pytest.raises(ValidationError):
        ResourceBody(title='Example', url='file:///etc/passwd', category='lecture')

def test_schema_rejects_unknown_property():
    with pytest.raises(ValidationError):
        Registration(fullName='Ada', email='ada@example.edu', password='long-enough-password', role='admin')

def test_docs_exist_without_database_connection():
    response = client.get('/openapi.json')
    assert response.status_code == 200
    assert '/api/resources' in response.json()['paths']

def test_invalid_book_query_has_consistent_error_envelope():
    response = client.get('/api/external/books', params={'title': 'x'})
    assert response.status_code == 422
    assert response.json()['error']['code'] == 'INVALID_INPUT'

def test_no_token_blocks_write_without_database():
    response = client.post('/api/resources', json={'title':'New lecture', 'url':'https://example.org'})
    assert response.status_code == 401
    assert response.json()['error']['code'] == 'UNAUTHENTICATED'
