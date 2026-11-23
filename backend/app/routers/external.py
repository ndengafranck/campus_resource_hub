from fastapi import APIRouter, Query
import httpx
from ..errors import ApiProblem
from ..settings import get_settings

router = APIRouter(prefix='/api/external', tags=['External integrations'])
USER_AGENT = 'IUC-Campus-Hub-Lab/1.0 (educational exercise)'

async def get_json(url: str, params: dict) -> dict:
    try:
        async with httpx.AsyncClient(timeout=5.0, follow_redirects=False) as client:
            response = await client.get(url, params=params, headers={'User-Agent': USER_AGENT})
            response.raise_for_status()
            return response.json()
    except httpx.TimeoutException:
        raise ApiProblem(503, 'SERVICE_UNAVAILABLE', 'External provider request timed out')
    except (httpx.HTTPError, ValueError):
        raise ApiProblem(502, 'UPSTREAM_ERROR', 'External provider is unavailable')

@router.get('/books')
async def books(title: str = Query(min_length=2, max_length=80)):
    payload = await get_json('https://openlibrary.org/search.json',
                             {'title': title, 'limit': 5,
                              'fields': 'key,title,author_name,first_publish_year'})
    docs = payload.get('docs', [])
    if not isinstance(docs, list):
        raise ApiProblem(502, 'UPSTREAM_ERROR', 'Invalid book provider response')
    return {'data': [{'key': doc.get('key'), 'title': doc.get('title'),
                      'authors': doc.get('author_name', []),
                      'firstPublished': doc.get('first_publish_year')}
                     for doc in docs if isinstance(doc, dict)]}

@router.get('/papers')
async def papers(query: str = Query(min_length=2, max_length=100)):
    settings = get_settings()
    params = {'query.bibliographic': query, 'rows': 5,
              'select': 'DOI,title,author,published,URL'}
    if settings.crossref_contact:
        params['mailto'] = settings.crossref_contact
    payload = await get_json('https://api.crossref.org/works', params)
    items = payload.get('message', {}).get('items', [])
    if not isinstance(items, list):
        raise ApiProblem(502, 'UPSTREAM_ERROR', 'Invalid paper provider response')
    results = []
    for p in items:
        if not isinstance(p, dict):
            continue
        titles = p.get('title') or []
        authors = p.get('author') or []
        published = p.get('published') or {}
        parts = published.get('date-parts', [[]]) if isinstance(published, dict) else [[]]
        year = parts[0][0] if parts and parts[0] else None
        results.append({'doi': p.get('DOI'), 'title': titles[0] if titles else '',
                        'authors': [((a.get('given','') + ' ' + a.get('family','')).strip())
                                    for a in authors if isinstance(a, dict)],
                        'year': year, 'url': p.get('URL')})
    return {'data': results}
