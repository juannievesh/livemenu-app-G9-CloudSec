from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from .schemas import RegisterRequest
from .service import register_user

router = APIRouter(prefix="/auth", tags=["auth"])
from sqlalchemy.orm import Session
@router.post("/register")
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    user = register_user(db, data.email, data.password)
    return {"id": str(user.id), "email": user.email}
