from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user_only
from app.schemas.category import CategoryCreate, CategoryInDB, CategoryReorder, CategoryUpdate
from app.services.category_service import CategoryService

router = APIRouter(prefix="/categories", tags=["Categorías"])
service = CategoryService()


@router.get(
    "",
    response_model=list[CategoryInDB],
    summary="Listar categorías",
    description="Devuelve todas las categorías del restaurante del usuario autenticado, "
    "ordenadas por posición. Si el usuario aún no tiene restaurante, retorna una lista vacía.",
)
async def list_categories(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user_only),
):
    if not getattr(user, "restaurant_id", None):
        return []
    return await service.list(db, user.restaurant_id)


@router.post(
    "",
    response_model=CategoryInDB,
    status_code=201,
    summary="Crear categoría",
    description="Crea una nueva categoría en el menú del restaurante. "
    "La posición se asigna automáticamente al final.",
    responses={
        400: {"description": "El usuario no tiene restaurante creado"},
    },
)
async def create_category(
    payload: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user_only),
):
    if not getattr(user, "restaurant_id", None):
        raise HTTPException(400, "Crea primero tu restaurante en Configuración")
    return await service.create(db, user.restaurant_id, payload)


@router.put(
    "/{category_id}",
    response_model=CategoryInDB,
    summary="Actualizar categoría",
    description="Actualiza los datos de una categoría existente. "
    "Solo se modifican los campos incluidos en el body.",
    responses={
        404: {"description": "Categoría no encontrada"},
    },
)
async def update_category(
    category_id: UUID,
    payload: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user_only),
):
    if not getattr(user, "restaurant_id", None):
        raise HTTPException(400, "Crea primero tu restaurante en Configuración")
    return await service.update(db, user.restaurant_id, category_id, payload)


@router.delete(
    "/{category_id}",
    summary="Eliminar categoría",
    description="Elimina una categoría y todos sus platos asociados.",
    responses={
        200: {"description": "Categoría eliminada", "content": {"application/json": {"example": {"message": "Category deleted"}}}},
        404: {"description": "Categoría no encontrada"},
    },
)
async def delete_category(
    category_id: UUID,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user_only),
):
    if not getattr(user, "restaurant_id", None):
        raise HTTPException(400, "Crea primero tu restaurante en Configuración")
    await service.delete(db, user.restaurant_id, category_id)
    return {"message": "Category deleted"}


@router.patch(
    "/reorder",
    summary="Reordenar categorías",
    description="Reordena las categorías del menú. Envía la lista completa de categorías "
    "con su nueva posición. Las posiciones empiezan en 0.",
    responses={
        200: {"description": "Categorías reordenadas", "content": {"application/json": {"example": {"message": "Categories reordered"}}}},
    },
)
async def reorder_categories(
    payload: CategoryReorder,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user_only),
):
    if not getattr(user, "restaurant_id", None):
        raise HTTPException(400, "Crea primero tu restaurante en Configuración")
    await service.reorder(db, user.restaurant_id, payload.order)
    return {"message": "Categories reordered"}
