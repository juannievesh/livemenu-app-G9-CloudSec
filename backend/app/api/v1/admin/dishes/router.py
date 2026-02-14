from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.services.dish_service import DishService
from app.schemas.dish import DishCreate, DishUpdate

router = APIRouter(prefix="/dishes", tags=["Admin Dishes"])
service = DishService()


@router.get("")
async def list_dishes(
    category_id: str | None = None,
    available: bool | None = None,
    featured: bool | None = None,
    search: str | None = None,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    filters = {
        "category_id": category_id,
        "available": available,
        "featured": featured,
        "search": search,
    }

    return await service.list(db, user.restaurant_id, filters)


@router.get("/{dish_id}")
async def get_dish(
    dish_id: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    return await service.get(db, user.restaurant_id, dish_id)


@router.post("")
async def create_dish(
    payload: DishCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    return await service.create(db, user.restaurant_id, payload)


@router.put("/{dish_id}")
async def update_dish(
    dish_id: str,
    payload: DishUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    return await service.update(db, user.restaurant_id, dish_id, payload)


@router.delete("/{dish_id}")
async def delete_dish(
    dish_id: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    return await service.delete(db, user.restaurant_id, dish_id)


@router.patch("/{dish_id}/availability")
async def toggle_availability(
    dish_id: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    return await service.toggle_availability(db, user.restaurant_id, dish_id)
