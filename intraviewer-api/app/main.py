from fastapi import FastAPI

from app.core.config import settings
from app.core.database import test_db_connection


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
)


@app.get("/")
def root():
    return {
        "message": "Intraviewer API is running"
    }


@app.get("/health")
def health():
    db_status = test_db_connection()

    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "database": "connected" if db_status == 1 else "error",
    }