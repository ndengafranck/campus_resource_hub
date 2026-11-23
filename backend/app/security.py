from datetime import datetime, timedelta, timezone
import jwt
from jwt import InvalidTokenError
from argon2 import PasswordHasher, exceptions as argon_errors
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from .errors import ApiProblem
from .settings import get_settings

hasher = PasswordHasher()
bearer = HTTPBearer(auto_error=False)

def hash_password(password: str) -> str:
    return hasher.hash(password)

def verify_password(password: str, stored_hash: str) -> bool:
    try:
        return hasher.verify(stored_hash, password)
    except (argon_errors.VerificationError, argon_errors.InvalidHashError):
        return False

def make_token(user_id: int) -> str:
    expiration = datetime.now(timezone.utc) + timedelta(hours=1)
    return jwt.encode({'sub': str(user_id), 'exp': expiration}, get_settings().jwt_secret, algorithm='HS256')

def current_user_id(credentials: HTTPAuthorizationCredentials | None = Depends(bearer)) -> int:
    if credentials is None or credentials.scheme.lower() != 'bearer':
        raise ApiProblem(401, 'UNAUTHENTICATED', 'Authentication required')
    try:
        payload = jwt.decode(credentials.credentials, get_settings().jwt_secret,
                             algorithms=['HS256'], options={'require': ['exp', 'sub']})
        user_id = int(payload['sub'])
        if user_id <= 0:
            raise ValueError('Invalid user ID')
        return user_id
    except (InvalidTokenError, ValueError, TypeError, KeyError):
        raise ApiProblem(401, 'UNAUTHENTICATED', 'Invalid or expired access token')
