import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.exceptions import RequestValidationError
from loguru import logger

from app.core.config import settings
from app.core.logging import setup_logging
from app.schemas.base import StandardResponse
from app.middleware.error_handler import (
    validation_exception_handler,
    internal_server_error_handler,
    not_found_error_handler
)

# Initialize logging
setup_logging()

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json"
    )

    # Middleware Registration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # Request Performance Logging Middleware
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        logger.info(f"{request.method} {request.url.path} - Status: {response.status_code} - Time: {process_time:.4f}s")
        return response

    # Exception Handlers
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, internal_server_error_handler)
    app.add_exception_handler(404, not_found_error_handler)

    # Router Registration
    from app.api.v1.auth.router import router as auth_router
    from app.api.v1.users.router import router as users_router
    from app.api.v1.aptitude.router import router as aptitude_router
    from app.api.v1.ai.router import router as ai_router
    from app.api.v1.resume.router import router as resume_router
    from app.api.v1.admin.router import router as admin_router
    from app.api.v1.analytics.router import router as analytics_router
    from app.api.v1.companies.router import router as companies_router
    from app.api.v1.dsa.router import router as dsa_router
    from app.api.v1.interview.router import router as interview_router
    from app.api.v1.roadmap.router import router as roadmap_router
    
    app.include_router(auth_router, prefix=settings.API_V1_STR)
    app.include_router(users_router, prefix=settings.API_V1_STR)
    app.include_router(aptitude_router, prefix=settings.API_V1_STR)
    app.include_router(ai_router, prefix=settings.API_V1_STR)
    app.include_router(resume_router, prefix=settings.API_V1_STR)
    app.include_router(admin_router, prefix=settings.API_V1_STR)
    app.include_router(analytics_router, prefix=settings.API_V1_STR)
    app.include_router(companies_router, prefix=settings.API_V1_STR)
    app.include_router(dsa_router, prefix=settings.API_V1_STR)
    app.include_router(interview_router, prefix=settings.API_V1_STR)
    app.include_router(roadmap_router, prefix=settings.API_V1_STR)
    
    # Automatically create tables on startup
    from app.database.connection import engine, Base
    import app.models.ai as ai_models
    import app.models.dsa as dsa_models
    import app.models.interview as interview_models
    import app.models.roadmap as roadmap_models
    Base.metadata.create_all(bind=engine)
    
    # --- Health Check ---
    @app.get("/health", tags=["System"])
    def health_check():
        return {"status": "ok", "service": "PlacementPrep AI Backend"}

    @app.get("/", response_model=StandardResponse)
    def root():
        return StandardResponse(
            success=True,
            message="Welcome to PlacementPrep AI Backend",
            data=None
        )

    @app.get("/health", response_model=StandardResponse)
    def health_check():
        return StandardResponse(
            success=True,
            message="System is healthy",
            data={"status": "UP"}
        )

    @app.get("/version", response_model=StandardResponse)
    def get_version():
        return StandardResponse(
            success=True,
            message="Current version",
            data={"version": settings.VERSION}
        )

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=1111, reload=True)
