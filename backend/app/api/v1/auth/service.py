from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password
from app.models.user import User


async def register_user(db: AsyncSession, email: str, password: str):
    result = await db.execute(select(User).where(User.email == email))
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(email=email, password_hash=hash_password(password))
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def authenticate_user(db: AsyncSession, email: str, password: str):
    """Returns user or raises HTTPException with specific message."""
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Email no registrado. Crea tu cuenta para continuar.",
        )
    if not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Contraseña incorrecta.",
        )
    return user
