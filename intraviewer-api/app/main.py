from fastapi import FastAPI

from app.api.v1.organizations import router as organizations_router
from app.core.config import settings
from app.api.v1.api_keys import router as api_keys_router

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
)

app.include_router(
    organizations_router,
    prefix="/v1",
)

app.include_router(
    api_keys_router,
    prefix="/v1",
)


@app.get("/")
def root():
    return {"message": "Intraviewer API is running"}