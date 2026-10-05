from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.api_key import APIKey
from app.core.security import get_current_organization
from app.models.organization import Organization

router = APIRouter(tags=["API Keys"])

@router.post("/api-keys")
def create_api_key(organization_id: str, db: Session = Depends(get_db)):
    api_key = APIKey(organization_id=organization_id)
    db.add(api_key)
    db.commit()
    db.refresh(api_key)
    return {"id": api_key.id, "api_key": api_key.key, "organization_id": api_key.organization_id}

@router.get("/me")
def get_me(org: Organization = Depends(get_current_organization)):
    return {"organization_id": org.id, "name": org.name}

@router.delete("/api-keys/{id}")
def delete_api_key(id: str, db: Session = Depends(get_db), org: Organization = Depends(get_current_organization)):
    api_key = db.query(APIKey).filter(APIKey.id == id, APIKey.organization_id == org.id).first()
    if api_key:
        api_key.is_active = False
        db.commit()
    return {"success": True}
