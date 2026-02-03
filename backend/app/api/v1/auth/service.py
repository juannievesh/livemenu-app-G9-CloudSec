from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.user import User
from app.core.security import hash_password  # asegúrate que exista

def register_user(db: Session, email: str, password: str):
    result = db.execute(select(User).where(User.email == email))
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    print("DEBUG password repr:", repr(password))
    print("DEBUG password len:", len(password))
    user = User(email=email, password_hash=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
