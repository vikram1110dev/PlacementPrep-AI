from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from loguru import logger
from app.schemas.base import StandardResponse

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    logger.warning(f"Validation Error: {errors}")
    content = StandardResponse(
        success=False,
        message="Validation failed for the request payload.",
        data=None,
        errors=[{"loc": err["loc"], "msg": err["msg"], "type": err["type"]} for err in errors]
    ).model_dump()
    return JSONResponse(status_code=422, content=content)

async def internal_server_error_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled Exception: {exc}")
    content = StandardResponse(
        success=False,
        message="An internal server error occurred.",
        data=None,
        errors=str(exc)
    ).model_dump()
    return JSONResponse(status_code=500, content=content)

async def not_found_error_handler(request: Request, exc: Exception):
    content = StandardResponse(
        success=False,
        message="The requested resource was not found.",
        data=None,
        errors=None
    ).model_dump()
    return JSONResponse(status_code=404, content=content)
