from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.engine import Connection
from sqlalchemy.exc import IntegrityError
from ..db import get_connection
from ..schemas import Registration, Credentials
from ..security import hash_password, verify_password, make_token, current_user_id
from ..errors import ApiProblem

router = APIRouter(prefix='/api/auth', tags=['Authentication'])

@router.post('/register', status_code=201)
def register(body: Registration, conn: Connection = Depends(get_connection)):
    try:
        with conn.begin():
            user = conn.execute(text("""
                INSERT INTO app_users (full_name, email, password_hash)
                VALUES (:name, :email, :password_hash)
                RETURNING id, full_name, email
            """), {'name': body.fullName, 'email': str(body.email).lower(),
                   'password_hash': hash_password(body.password)}).mappings().one()
        account = dict(user)
    except IntegrityError:
        raise ApiProblem(409, 'EMAIL_EXISTS', 'Email already registered')
    return {'data': {'user': account, 'accessToken': make_token(account['id'])}}

@router.post('/login')
def login(body: Credentials, conn: Connection = Depends(get_connection)):
    user = conn.execute(text("""
        SELECT id, full_name, email, password_hash FROM app_users WHERE email = :email
    """), {'email': str(body.email).lower()}).mappings().first()
    if not user or not verify_password(body.password, user['password_hash']):
        raise ApiProblem(401, 'BAD_CREDENTIALS', 'Invalid email or password')
    account = {key: user[key] for key in ('id', 'full_name', 'email')}
    return {'data': {'user': account, 'accessToken': make_token(account['id'])}}

@router.get('/me')
def me(user_id: int = Depends(current_user_id), conn: Connection = Depends(get_connection)):
    user = conn.execute(text("""
        SELECT id, full_name, email FROM app_users WHERE id = :uid
    """), {'uid': user_id}).mappings().first()
    if user is None:
        raise ApiProblem(401, 'ACCOUNT_NOT_FOUND', 'User no longer exists')
    return {'data': dict(user)}
