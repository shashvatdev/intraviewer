from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.api_key import APIKey

router = APIRouter(
    prefix="/api-keys",
    tags=["API Keys"],
)


@router.post("")
def create_api_key(
    organization_id: str,
    db: Session = Depends(get_db),
):
    api_key = APIKey(
        organization_id=organization_id,
    )

    db.add(api_key)
    db.commit()
    db.refresh(api_key)

    return {
        "id": api_key.id,
        "api_key": api_key.key,
        "organization_id": api_key.organization_id,
    }