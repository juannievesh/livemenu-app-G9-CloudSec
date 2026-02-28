# backend/app/api/v1/menu/router.py

from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

MENU_CACHE: dict[str, dict[str, Any]] = {}
CACHE_TTL = timedelta(minutes=5)

def get_menu_from_db(slug: str):
    """Mock de la consulta a BD. Aquí usarías tu Session de SQLAlchemy."""
    if slug != "mi-restaurante":
        return None
    return {
        "restaurant_name": "El Buen Sabor",
        "categories": [{"name": "Bebidas", "items": ["Agua", "Cerveza"]}]
    }

def get_cached_menu(slug: str):
    """Busca en caché antes de golpear la base de datos."""
    cached_data = MENU_CACHE.get(slug)
    if cached_data and datetime.now() < cached_data["expires_at"]:
        return cached_data["data"]

    menu_data = get_menu_from_db(slug)
    if not menu_data:
        raise HTTPException(status_code=404, detail="Menú no encontrado")

    MENU_CACHE[slug] = {
        "data": menu_data,
        "expires_at": datetime.now() + CACHE_TTL
    }
    return menu_data

@router.get("/api/v1/menu/{slug}", summary="Obtener menú en JSON")
async def get_menu_json(slug: str):
    """Endpoint consumido por el frontend en modo SPA/PWA."""
    return get_cached_menu(slug)

@router.get("/m/{slug}", response_class=HTMLResponse, summary="Server-Side Rendering del menú")
async def get_menu_ssr(request: Request, slug: str):
    """Genera el HTML desde el servidor para SEO y carga rápida inicial."""
    menu_data = get_cached_menu(slug)
    return templates.TemplateResponse(
        "menu_template.html",
        {"request": request, "menu": menu_data}
    )
