from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.deps import get_current_user
from app.services.category_service import CategoryService
from app.schemas.category import (
    CategoryCreate,
    CategoryUpdate,
    CategoryReorder,
    CategoryInDB
)

router = APIRouter(prefix="/categories",tags=["Admin Categories"])
service = CategoryService()


@router.get("", response_model=list[CategoryInDB])
async def list_categories(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    return await service.list(db, user.restaurant_id)


@router.post("", response_model=CategoryInDB)
async def create_category(
    payload: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    return await service.create(db, user.restaurant_id, payload)


@router.put("/{category_id}", response_model=CategoryInDB)
async def update_category(
    category_id: str,
    payload: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    return await service.update(db, user.restaurant_id, category_id, payload)


@router.delete("/{category_id}")
async def delete_category(
    category_id: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    await service.delete(db, user.restaurant_id, category_id)
    return {"message": "Category deleted"}


@router.patch("/reorder")
async def reorder_categories(
    payload: CategoryReorder,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    await service.reorder(db, user.restaurant_id, payload.order)
    return {"message": "Categories reordered"}