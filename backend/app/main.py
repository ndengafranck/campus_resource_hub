from fastapi import FastAPI, Depends
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.engine import Connection
from .settings import get_settings
from .db import get_connection
from .errors import ApiProblem, problem_handler, validation_handler
from .routers import auth, resources, external

app = FastAPI(title='Campus Resource Hub API', version='2.0-fastapi',
              description='IUC BTECH 3 CSE teaching project. Not production hardened.')
app.add_middleware(CORSMiddleware, allow_origins=[v.strip() for v in get_settings().cors_origins.split(',') if v.strip()],
                   allow_credentials=False, allow_methods=['GET', 'POST', 'PUT', 'DELETE'],
                   allow_headers=['Authorization', 'Content-Type'])
app.add_exception_handler(ApiProblem, problem_handler)
app.add_exception_handler(RequestValidationError, validation_handler)
app.include_router(auth.router)
app.include_router(resources.router)
app.include_router(external.router)

@app.get('/api/health', tags=['Operations'])
def health(conn: Connection = Depends(get_connection)):
    conn.execute(text('SELECT 1'))
    return {'data': {'status': 'ok'}}
