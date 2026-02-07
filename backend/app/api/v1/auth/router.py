from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .schemas import LoginRequest
from app.core.database import get_db
from .schemas import RegisterRequest
from .service import register_user
from .service import authenticate_user
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.core.jwt import create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])
@router.post("/register")
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    user = register_user(db, data.email, data.password)
    return {"id": str(user.id), "email": user.email}
@router.post("/login")

@router.post("/login")
def login(data: LoginRequest, db=Depends(get_db)):
    user = authenticate_user(db, data.email, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}
from app.core.deps import get_current_user

@router.get("/me")
def me(current_user=Depends(get_current_user)):
    return {"id": str(current_user.id), "email": current_user.email}
