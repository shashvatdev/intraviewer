from fastapi import Security, HTTPException, status, Depends
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.api_key import APIKey
from app.models.organization import Organization

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)

def get_current_organization(
    key: str = Security(api_key_header),
    db: Session = Depends(get_db)
) -> Organization:
    api_key = db.query(APIKey).filter(APIKey.key == key, APIKey.is_active == True).first()
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or inactive API Key"
        )
    organization = db.query(Organization).filter(Organization.id == api_key.organization_id).first()
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Organization not found"
        )
    return organization
