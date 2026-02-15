from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.models.restaurant import Restaurant

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    cred_exc = HTTPException(status_code=401, detail="Invalid or expired token")

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str | None = payload.get("sub")
        if not user_id:
            raise cred_exc
    except JWTError:
        raise cred_exc

   
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise cred_exc

   
    result = await db.execute(select(Restaurant).where(Restaurant.owner_id == user.id))
    restaurant = result.scalar_one_or_none()
    if not restaurant:
        raise HTTPException(status_code=400, detail="User has no restaurant associated")

   
    user.restaurant_id = restaurant.id
    return user