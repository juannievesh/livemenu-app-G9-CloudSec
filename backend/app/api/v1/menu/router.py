# backend/app/api/v1/menu/router.py

from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from datetime import datetime, timedelta
from typing import Dict, Any


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
        .options(selectinload(Restaurant.categories).selectinload(Category.dishes))
        .where(Restaurant.slug == slug)
    )
    result = await db.execute(stmt)
    restaurant = result.scalar_one_or_none()

    if not restaurant:
        return None

    menu_data = {
        "restaurant_name": restaurant.name,
        "restaurant_logo": restaurant.logo_url,
        "restaurant_phone": restaurant.phone,
        "restaurant_horarios": restaurant.horarios,
        "categories": []
    }

    for category in restaurant.categories:
        if not category.active:
            continue
        cat_data = {"name": category.name, "items": []}
        
        dishes = [d for d in category.dishes if d.deleted_at is None]
        dishes.sort(key=lambda x: x.position)
        
        for dish in dishes:
            cat_data["items"].append({
                "name": dish.name,
                "description": dish.description,
                "price": float(dish.price),
                "image_urls": dish.image_urls or {},
                "offer_price": float(dish.offer_price) if dish.offer_price else None,
                "available": dish.available,
                "tags": dish.tags or []
            })
            
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