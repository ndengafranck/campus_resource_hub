from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy import text
from sqlalchemy.engine import Connection
from ..db import get_connection
from ..schemas import ResourceBody
from ..security import current_user_id
from ..errors import ApiProblem

router = APIRouter(prefix='/api/resources', tags=['Resources'])

@router.get('')
def list_resources(q: str = Query('', max_length=100), page: int = Query(1, ge=1, le=10000),
                   conn: Connection = Depends(get_connection)):
    limit = 10
    rows = conn.execute(text("""
        SELECT r.id, r.title, r.description, r.url, r.category, r.owner_id, r.created_at,
               u.full_name AS owner_name
        FROM resources r JOIN app_users u ON u.id = r.owner_id
        WHERE (:q = '' OR LOWER(r.title) LIKE '%' || LOWER(:q) || '%' OR LOWER(r.description) LIKE '%' || LOWER(:q) || '%')
        ORDER BY r.created_at DESC, r.id DESC LIMIT :limit OFFSET :offset
    """), {'q': q.strip(), 'limit': limit, 'offset': (page - 1) * limit}).mappings().all()
    return {'data': [dict(r) for r in rows], 'meta': {'page': page, 'limit': limit, 'hasMore': len(rows) == limit}}

@router.get('/{resource_id}')
def get_resource(resource_id: int, conn: Connection = Depends(get_connection)):
    row = conn.execute(text("""SELECT r.*, u.full_name AS owner_name FROM resources r
                              JOIN app_users u ON u.id=r.owner_id WHERE r.id=:rid"""),
                       {'rid': resource_id}).mappings().first()
    if row is None:
        raise ApiProblem(404, 'NOT_FOUND', 'Resource not found')
    return {'data': dict(row)}

@router.post('', status_code=201)
def create_resource(body: ResourceBody, user_id: int = Depends(current_user_id),
                    conn: Connection = Depends(get_connection)):
    with conn.begin():
        row = conn.execute(text("""
            INSERT INTO resources (title,description,url,category,owner_id)
            VALUES (:title,:description,:url,:category,:owner_id) RETURNING *
        """), {**body.model_dump(exclude={'url'}), 'url': str(body.url), 'owner_id': user_id}).mappings().one()
    return {'data': dict(row)}

@router.put('/{resource_id}')
def update_resource(resource_id: int, body: ResourceBody,
                    user_id: int = Depends(current_user_id), conn: Connection = Depends(get_connection)):
    with conn.begin():
        row = conn.execute(text("""
            UPDATE resources SET title=:title, description=:description, url=:url,
                category=:category, updated_at=CURRENT_TIMESTAMP
            WHERE id=:rid AND owner_id=:uid RETURNING *
        """), {**body.model_dump(exclude={'url'}), 'url': str(body.url),
               'rid': resource_id, 'uid': user_id}).mappings().first()
    if row is None:
        raise ApiProblem(404, 'NOT_FOUND', 'Not found or not owned by you')
    return {'data': dict(row)}

@router.delete('/{resource_id}', status_code=204)
def delete_resource(resource_id: int, user_id: int = Depends(current_user_id),
                    conn: Connection = Depends(get_connection)):
    with conn.begin():
        result = conn.execute(text("""DELETE FROM resources WHERE id=:rid AND owner_id=:uid"""),
                              {'rid': resource_id, 'uid': user_id})
    if result.rowcount == 0:
        raise ApiProblem(404, 'NOT_FOUND', 'Not found or not owned by you')
    return Response(status_code=204)
