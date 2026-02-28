from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user_only
from app.schemas.dish import DishCreate, DishInDB, DishUpdate
from app.services.dish_service import DishService

router = APIRouter(prefix="/dishes", tags=["Platos"])
service = DishService()


@router.get(
    "",
    response_model=list[DishInDB],
    summary="Listar platos",
    description="Devuelve los platos del restaurante del usuario autenticado. "
    "Se pueden aplicar filtros opcionales por categoría, disponibilidad, destacados y texto de búsqueda.",
)
async def list_dishes(
    category_id: str | None = Query(None, description="Filtrar por UUID de categoría"),
    available: bool | None = Query(None, description="Filtrar por disponibilidad"),
    featured: bool | None = Query(None, description="Filtrar solo platos destacados"),
    search: str | None = Query(None, description="Buscar por nombre o descripción"),
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


@router.get(
    "/{dish_id}",
    response_model=DishInDB,
    summary="Obtener plato por ID",
    description="Devuelve los detalles completos de un plato específico.",
    responses={
        404: {"description": "Plato no encontrado"},
    },
)
async def get_dish(
    dish_id: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user_only),
):
    if not getattr(user, "restaurant_id", None):
        raise HTTPException(400, "Crea primero tu restaurante en Configuración")
    return await service.get(db, user.restaurant_id, dish_id)


@router.post(
    "",
    response_model=DishInDB,
    status_code=201,
    summary="Crear plato",
    description="Crea un nuevo plato dentro de una categoría. "
    "La posición se asigna automáticamente al final de la categoría. "
    "Para añadir imágenes, usa el endpoint POST /api/v1/admin/upload/ después de crear el plato.",
    responses={
        400: {"description": "El usuario no tiene restaurante creado"},
    },
)
async def create_dish(
    payload: DishCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user_only),
):
    if not getattr(user, "restaurant_id", None):
        raise HTTPException(400, "Crea primero tu restaurante en Configuración")
    return await service.create(db, user.restaurant_id, payload)


@router.put(
    "/{dish_id}",
    response_model=DishInDB,
    summary="Actualizar plato",
    description="Actualiza los datos de un plato existente. "
    "Solo se modifican los campos incluidos en el body.",
    responses={
        404: {"description": "Plato no encontrado"},
    },
)
async def update_dish(
    dish_id: str,
    payload: DishUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user_only),
):
    if not getattr(user, "restaurant_id", None):
        raise HTTPException(400, "Crea primero tu restaurante en Configuración")
    return await service.update(db, user.restaurant_id, dish_id, payload)


@router.delete(
    "/{dish_id}",
    summary="Eliminar plato",
    description="Elimina un plato (soft delete). El plato no se borra de la base de datos, "
    "se marca con `deleted_at` para mantener historial.",
    responses={
        200: {"description": "Plato eliminado", "content": {"application/json": {"example": {"message": "Dish deleted"}}}},
        404: {"description": "Plato no encontrado"},
    },
)
async def delete_dish(
    dish_id: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user_only),
):
    if not getattr(user, "restaurant_id", None):
        raise HTTPException(400, "Crea primero tu restaurante en Configuración")
    await service.delete(db, user.restaurant_id, dish_id)
    return {"message": "Dish deleted"}


@router.patch(
    "/{dish_id}/availability",
    response_model=DishInDB,
    summary="Alternar disponibilidad",
    description="Cambia el estado de disponibilidad del plato (disponible ↔ no disponible). "
    "Útil para marcar rápidamente un plato como agotado.",
)
async def toggle_availability(
    dish_id: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user_only),
):
    if not getattr(user, "restaurant_id", None):
        raise HTTPException(400, "Crea primero tu restaurante en Configuración")
    return await service.toggle_availability(db, user.restaurant_id, dish_id)
