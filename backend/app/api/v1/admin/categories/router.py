from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.services.category_service import CategoryService
from app.schemas.category import (
    CategoryCreate,
    CategoryUpdate,
    CategoryReorder
)

router = APIRouter(prefix="/categories", tags=["Admin Categories"])
service = CategoryService()


@router.get("")
async def list_categories(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    return await service.list(db, user.restaurant_id)


@router.post("")
async def create_category(
    payload: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    return await service.create(db, user.restaurant_id, payload)


@router.put("/{category_id}")
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
    return await service.delete(db, user.restaurant_id, category_id)


@router.patch("/reorder")
async def reorder_categories(
    payload: CategoryReorder,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    return await service.reorder(db, user.restaurant_id, payload.order)
