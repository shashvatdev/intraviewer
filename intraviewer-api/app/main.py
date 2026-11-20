import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes.auth import router as auth_router
from app.api.routes.profiles import candidate_router, company_router
from app.api.routes.jobs import router as jobs_router
from app.api.routes.candidate_jobs import router as candidate_jobs_router
from app.api.routes.applications import router as applications_router
from app.api.routes.interviews import router as interviews_router
from app.core.config import settings
from app.core.errors import register_exception_handlers

logging.basicConfig(level=logging.INFO)

if settings.is_production and settings.SECRET_KEY.startswith("dev-only"):
    raise RuntimeError("SECRET_KEY must be set to a strong random value in production.")

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

register_exception_handlers(app)

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Module 1 — Authentication & Profiles
app.include_router(auth_router)
app.include_router(candidate_router)
app.include_router(company_router)
app.include_router(jobs_router)
app.include_router(candidate_jobs_router)
app.include_router(applications_router)
app.include_router(interviews_router)


@app.get("/health")
def health():
    return {"success": True, "message": "ok", "data": {"version": settings.APP_VERSION}}
