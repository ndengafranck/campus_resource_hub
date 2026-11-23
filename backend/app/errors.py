from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

class ApiProblem(Exception):
    def __init__(self, status: int, code: str, message: str):
        self.status = status
        self.code = code
        self.message = message

async def problem_handler(_request: Request, exc: ApiProblem):
    return JSONResponse(status_code=exc.status, content={'error': {'code': exc.code, 'message': exc.message}})

async def validation_handler(_request: Request, _exc: RequestValidationError):
    # FastAPI's default is 422; preserve the existing React error envelope.
    return JSONResponse(status_code=422, content={'error': {'code': 'INVALID_INPUT', 'message': 'Validate request fields and types'}})
