from fastapi import FastAPI
from app.api.v1.organizations import router as organizations_router
from app.api.v1.api_keys import router as api_keys_router
from app.api.v1.interviews import router as interviews_router
from app.api.v1.questions import router as questions_router
from app.api.v1.candidates import router as candidates_router
from app.api.v1.sessions import router as sessions_router
from app.api.v1.answers import router as answers_router
from app.api.v1.evaluations import router as evaluations_router
from app.api.v1.public import router as public_router
from app.api.v1.ai import router as ai_router
from app.core.config import settings

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)

app.include_router(organizations_router, prefix="/v1")
app.include_router(api_keys_router, prefix="/v1")
app.include_router(interviews_router, prefix="/v1")
app.include_router(questions_router, prefix="/v1")
app.include_router(candidates_router, prefix="/v1")
app.include_router(sessions_router, prefix="/v1")
app.include_router(answers_router, prefix="/v1")
app.include_router(evaluations_router, prefix="/v1")
app.include_router(public_router, prefix="/v1")
app.include_router(ai_router, prefix="/v1")

@app.get("/")
def root():
    return {"message": "Intraviewer API is running"}
