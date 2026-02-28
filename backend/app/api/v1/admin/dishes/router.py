
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user_only
from app.schemas.dish import DishCreate, DishInDB, DishUpdate
from app.services.dish_service import DishService

router = APIRouter(prefix="/dishes",tags=["Admin Dishes"])
service = DishService()


@router.get("", response_model=list[DishInDB])
async def list_dishes(
    category_id: str | None = None,
    available: bool | None = None,
    featured: bool | None = None,
    search: str | None = None,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user_only),
):
    if not getattr(user, "restaurant_id", None):
        return []
    filters = {
        "category_id": category_id,
        "available": available,
        "featured": featured,
        "search": search,
    }
    return await service.list(db, user.restaurant_id, filters)


@router.get("/{dish_id}", response_model=DishInDB)
async def get_dish(
    dish_id: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user_only),
):
    if not getattr(user, "restaurant_id", None):
        raise HTTPException(400, "Crea primero tu restaurante en Configuración")
    return await service.get(db, user.restaurant_id, dish_id)


@router.post("", response_model=DishInDB)
async def create_dish(
    payload: DishCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user_only),
):
    if not getattr(user, "restaurant_id", None):
        raise HTTPException(400, "Crea primero tu restaurante en Configuración")
    return await service.create(db, user.restaurant_id, payload)


@router.put("/{dish_id}", response_model=DishInDB)
async def update_dish(
    dish_id: str,
    payload: DishUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user_only),
):
    if not getattr(user, "restaurant_id", None):
        raise HTTPException(400, "Crea primero tu restaurante en Configuración")
    return await service.update(db, user.restaurant_id, dish_id, payload)


@router.delete("/{dish_id}")
async def delete_dish(
    dish_id: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user_only),
):
    if not getattr(user, "restaurant_id", None):
        raise HTTPException(400, "Crea primero tu restaurante en Configuración")
    await service.delete(db, user.restaurant_id, dish_id)
    return {"message": "Dish deleted"}


@router.patch("/{dish_id}/availability", response_model=DishInDB)
async def toggle_availability(
    dish_id: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user_only),
):
    if not getattr(user, "restaurant_id", None):
        raise HTTPException(400, "Crea primero tu restaurante en Configuración")
    return await service.toggle_availability(db, user.restaurant_id, dish_id)
