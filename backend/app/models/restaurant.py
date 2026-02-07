from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.core.database import Base

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User

class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    address = Column(String, nullable=True)
router = APIRouter(prefix="/restaurants", tags=["restaurants"])

@router.get("/")
def list_restaurants(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    restaurants = (
        db.query(Restaurant)
        .filter(Restaurant.owner_id == current_user.id)
        .all()
    )
    return restaurants

