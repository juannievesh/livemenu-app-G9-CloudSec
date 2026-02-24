# backend/app/api/v1/menu/router.py
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from datetime import datetime, timedelta
from typing import Dict, Any

# Ajusta estas importaciones a la ruta real de tu proyecto
from app.core.database import get_db 
from app.models.restaurant import Restaurant
from app.models.category import Category
from app.models.dish import Dish

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

MENU_CACHE: Dict[str, Dict[str, Any]] = {}
CACHE_TTL = timedelta(minutes=5)

async def get_menu_from_db(slug: str, db: AsyncSession):
    """Consulta la base de datos usando Eager Loading para evitar el problema N+1."""
    
    stmt = (
        select(Restaurant)
        # Trae el restaurante, sus categorías, y los platos de esas categorías de un solo golpe
        .options(selectinload(Restaurant.categories).selectinload(Category.dishes))
        .where(Restaurant.slug == slug)
    )
    result = await db.execute(stmt)
    restaurant = result.scalar_one_or_none()

    if not restaurant:
        return None

    # Serializamos a un diccionario nativo de Python para que pueda ser almacenado 
    # en caché de forma segura sin generar errores de "Detached Instance" en SQLAlchemy.
    menu_data = {
        "restaurant_name": restaurant.name,
        "categories": []
    }

    # Ordenamos y filtramos en memoria
    for category in restaurant.categories:
        cat_data = {"name": category.name, "items": []}
        
        # Filtramos platos eliminados o no disponibles (Soft Delete)
        active_dishes = [d for d in category.dishes if d.available and d.deleted_at is None]
        # Ordenamos por la posición definida por el restaurante
        active_dishes.sort(key=lambda x: x.position)
        
        for dish in active_dishes:
            cat_data["items"].append({
                "name": dish.name,
                "description": dish.description,
                "price": float(dish.price),
                # El campo JSONB que definimos antes entra en acción aquí
                "image_urls": dish.image_urls or {},
                "offer_price": float(dish.offer_price) if dish.offer_price else None
            })
            
        # Solo agregamos categorías que tengan platos activos
        if cat_data["items"]:
            menu_data["categories"].append(cat_data)

    return menu_data

async def get_cached_menu(slug: str, db: AsyncSession):
    cached_data = MENU_CACHE.get(slug)
    if cached_data and datetime.now() < cached_data["expires_at"]:
        return cached_data["data"]
    
    menu_data = await get_menu_from_db(slug, db)
    if not menu_data:
        raise HTTPException(status_code=404, detail="Menú no encontrado o restaurante inactivo")
        
    MENU_CACHE[slug] = {
        "data": menu_data,
        "expires_at": datetime.now() + CACHE_TTL
    }
    return menu_data

@router.get("/{slug}", summary="Obtener menú en JSON puro")
async def get_menu_json(slug: str, db: AsyncSession = Depends(get_db)):
    return await get_cached_menu(slug, db)

@router.get("/m/{slug}", response_class=HTMLResponse, summary="Menú SSR (HTML)")
async def get_menu_ssr(request: Request, slug: str, db: AsyncSession = Depends(get_db)):
    menu_data = await get_cached_menu(slug, db)
    return templates.TemplateResponse(
        "menu_template.html", 
        {"request": request, "menu": menu_data}
    )