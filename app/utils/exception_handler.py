from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY, HTTP_401_UNAUTHORIZED

from app.utils.response import error


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Check if Authorization header is missing
    missing_auth = any(
        err["loc"][-1].lower() == "authorization" and err["type"] == "missing"
        for err in exc.errors()
    )

    if missing_auth:
        response = error(
            msg="Authorization header is required",
            response_type="AUTH",
            status_code=HTTP_401_UNAUTHORIZED
        )
        return JSONResponse(
            status_code=HTTP_401_UNAUTHORIZED,
            content=response
        )

    # Other validation errors
    response = error(
        msg="Validation error",
        data=exc.errors(),
        response_type="VALIDATION",
        status_code=HTTP_422_UNPROCESSABLE_ENTITY
    )
    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        content=response
    )
