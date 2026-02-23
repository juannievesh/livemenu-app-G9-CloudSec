# backend/app/api/v1/menu/router.py
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime, timedelta
from typing import Dict, Any

router = APIRouter()
# Si usas SSR, FastAPI requiere configurar el directorio de templates
templates = Jinja2Templates(directory="app/templates")

# Implementación rústica pero efectiva de Caché en memoria (TTL de 5 minutos)
MENU_CACHE: Dict[str, Dict[str, Any]] = {}
CACHE_TTL = timedelta(minutes=5)

def get_menu_from_db(slug: str):
    """Mock de la consulta a BD. Aquí usarías tu Session de SQLAlchemy."""
    # Falla intencionalmente si el slug no existe para simular el comportamiento real
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
    
    # Cache miss - Consultar BD
    menu_data = get_menu_from_db(slug)
    if not menu_data:
        raise HTTPException(status_code=404, detail="Menú no encontrado")
        
    # Guardar en caché
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
    # Debes crear el archivo menu_template.html en backend/app/templates/
    return templates.TemplateResponse(
        "menu_template.html", 
        {"request": request, "menu": menu_data}
    )