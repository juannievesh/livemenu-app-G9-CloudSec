from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user

from app.models.user import User

router = APIRouter(prefix="/restaurants", tags=["restaurants"])

@router.get("")
def list_restaurants(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # TODO: consulta DB
    return []
