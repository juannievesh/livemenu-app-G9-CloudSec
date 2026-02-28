from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.models.restaurant import Restaurant
from app.models.user import User

# HTTPBearer: Swagger pide el JWT generado en POST /auth/login (enunciado: Authorization: Bearer <JWT_TOKEN>)
security = HTTPBearer(
    auto_error=True,
    description="Pega el access_token obtenido de POST /auth/login (email + contraseña)",
)


async def get_current_user_only(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Valida JWT y retorna el usuario sin requerir restaurante."""
    token = credentials.credentials
    cred_exc = HTTPException(status_code=401, detail="Invalid or expired token")
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str | None = payload.get("sub")
        if not user_id:
            raise cred_exc
    except JWTError:
        raise cred_exc from None

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise cred_exc

    result = await db.execute(select(Restaurant).where(Restaurant.owner_id == user.id))
    restaurant = result.scalar_one_or_none()
    if restaurant:
        user.restaurant_id = restaurant.id
    return user


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Valida JWT y retorna el usuario. Requiere que tenga restaurante asociado."""
    user = await get_current_user_only(credentials, db)
    if not hasattr(user, "restaurant_id") or user.restaurant_id is None:
        raise HTTPException(status_code=400, detail="User has no restaurant associated")
    return user
