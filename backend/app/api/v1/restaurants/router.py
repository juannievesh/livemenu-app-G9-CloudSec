import re
import uuid as uuid_module

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user, get_current_user_only
from app.models.restaurant import Restaurant
from app.models.user import User
from app.schemas.restaurant import RestaurantCreate, RestaurantInDB, RestaurantUpdate

router = APIRouter(prefix="/admin/restaurant", tags=["Restaurante"])


def _slugify(name: str) -> str:
    s = name.lower().strip()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[-\s]+", "-", s).strip("-")
    return s or "restaurant"


async def _make_unique_slug(db: AsyncSession, base_slug: str) -> str:
    slug = base_slug
    for _i in range(100):
        result = await db.execute(select(Restaurant).where(Restaurant.slug == slug))
        if result.scalar_one_or_none() is None:
            return slug
        slug = f"{base_slug}-{uuid_module.uuid4().hex[:6]}"
    return slug


@router.post(
    "",
    response_model=RestaurantInDB,
    status_code=201,
    summary="Crear restaurante",
    description="Crea un nuevo restaurante asociado al usuario autenticado. "
    "Se genera automáticamente un **slug** único a partir del nombre para la URL pública del menú.",
)
async def create_restaurant(
    data: RestaurantCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_only),
):
    base_slug = _slugify(data.name)
    slug = await _make_unique_slug(db, base_slug)
    restaurant = Restaurant(
        name=data.name,
        address=data.address,
        description=data.description,
        logo_url=data.logo_url,
        phone=data.phone,
        horarios=data.horarios,
        slug=slug,
        owner_id=current_user.id,
    )
    db.add(restaurant)
    await db.commit()
    await db.refresh(restaurant)
    return restaurant


@router.get(
    "",
    response_model=RestaurantInDB | None,
    summary="Obtener mi restaurante",
    description="Devuelve el restaurante del usuario autenticado. "
    "Retorna `null` si aún no ha creado uno (el frontend usa esto para mostrar el onboarding).",
)
async def get_restaurant(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_only),
):
    result = await db.execute(
        select(Restaurant).where(Restaurant.owner_id == current_user.id)
    )
    return result.scalar_one_or_none()


@router.put(
    "",
    response_model=RestaurantInDB,
    summary="Actualizar mi restaurante",
    description="Actualiza los datos del restaurante del usuario autenticado. "
    "Solo se modifican los campos incluidos en el body; los demás se mantienen sin cambios.",
)
async def update_restaurant(
    data: RestaurantUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Restaurant).where(Restaurant.owner_id == current_user.id)
    )
    restaurant = result.scalar_one_or_none()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(restaurant, field, value)

    await db.commit()
    await db.refresh(restaurant)
    return restaurant


@router.delete(
    "",
    summary="Eliminar mi restaurante",
    description="Elimina permanentemente el restaurante del usuario autenticado, "
    "incluyendo todas sus categorías y platos (cascade).",
    responses={
        200: {"description": "Restaurante eliminado correctamente", "content": {"application/json": {"example": {"message": "deleted"}}}},
        404: {"description": "El usuario no tiene restaurante"},
    },
)
async def delete_restaurant(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Restaurant).where(Restaurant.owner_id == current_user.id)
    )
    restaurant = result.scalar_one_or_none()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    db.delete(restaurant)
    await db.commit()
    return {"message": "deleted"}
