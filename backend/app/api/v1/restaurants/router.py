from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import re
import uuid as uuid_module

from app.core.database import get_db
from app.core.deps import get_current_user, get_current_user_only
from app.models.user import User
from app.models.restaurant import Restaurant

router = APIRouter(prefix="/restaurants", tags=["restaurants"])


def _slugify(name: str) -> str:
    s = name.lower().strip()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[-\s]+", "-", s).strip("-")
    return s or "restaurant"


async def _make_unique_slug(db: AsyncSession, base_slug: str) -> str:
    slug = base_slug
    for i in range(100):
        result = await db.execute(select(Restaurant).where(Restaurant.slug == slug))
        if result.scalar_one_or_none() is None:
            return slug
        slug = f"{base_slug}-{uuid_module.uuid4().hex[:6]}"
    return slug


@router.post("/")
async def create_restaurant(
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_only),
):
    base_slug = _slugify(data.get("name", "restaurant"))
    slug = await _make_unique_slug(db, base_slug)
    restaurant = Restaurant(
        name=data["name"],
        address=data.get("address"),
        slug=slug,
        owner_id=current_user.id,
    )
    db.add(restaurant)
    await db.commit()
    await db.refresh(restaurant)
    return restaurant


@router.get("/")
async def list_restaurants(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_only),
):
    result = await db.execute(
        select(Restaurant).where(Restaurant.owner_id == current_user.id)
    )
    return list(result.scalars().all())


@router.put("/{restaurant_id}")
async def update_restaurant(
    restaurant_id: str,
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Restaurant).where(
            Restaurant.id == restaurant_id,
            Restaurant.owner_id == current_user.id,
        )
    )
    restaurant = result.scalar_one_or_none()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Not found")

    restaurant.name = data.get("name", restaurant.name)
    restaurant.address = data.get("address", restaurant.address)
    await db.commit()
    await db.refresh(restaurant)
    return restaurant


@router.delete("/{restaurant_id}")
async def delete_restaurant(
    restaurant_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Restaurant).where(
            Restaurant.id == restaurant_id,
            Restaurant.owner_id == current_user.id,
        )
    )
    restaurant = result.scalar_one_or_none()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Not found")

    db.delete(restaurant)
    await db.commit()
    return {"message": "deleted"}
