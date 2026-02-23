from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime, timedelta
from typing import Dict, Any

router = APIRouter()

# Configuración del motor de plantillas Jinja2 para SSR
templates = Jinja2Templates(directory="app/templates")

# Caché en memoria: Evita golpear la base de datos si escanean el QR masivamente
MENU_CACHE: Dict[str, Dict[str, Any]] = {}
CACHE_TTL = timedelta(minutes=5)

def get_menu_from_db(slug: str):
    """Mock simulando consulta a la BD. Reemplazar con SQLAlchemy luego."""
    if slug != "mi-restaurante":
        return None
    return {
        "restaurant_name": "El Buen Sabor",
        "categories": [
            {"name": "Bebidas", "items": ["Agua", "Cerveza"]},
            {"name": "Platos Fuertes", "items": ["Hamburguesa", "Pizza"]}
        ]
    }

def get_cached_menu(slug: str):
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

@router.get("/{slug}", summary="Obtener menú en JSON puro")
async def get_menu_json(slug: str):
    return get_cached_menu(slug)

@router.get("/m/{slug}", response_class=HTMLResponse, summary="Menú SSR (HTML)")
async def get_menu_ssr(request: Request, slug: str):
    menu_data = get_cached_menu(slug)
    # Retorna la plantilla renderizada con los datos inyectados
    return templates.TemplateResponse(
        "menu_template.html", 
        {"request": request, "menu": menu_data}
    )