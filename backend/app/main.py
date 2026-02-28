import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.v1 import api_router
from app.api.v1.admin.categories.router import router as categories_router
from app.api.v1.admin.dishes.router import router as dishes_router
from app.api.v1.admin.qr.router import router as qr_router
from app.api.v1.admin.upload.router import router as upload_router
from app.api.v1.auth.router import router as auth_router
from app.api.v1.menu.router import get_cached_menu
from app.api.v1.menu.router import router as menu_router
from app.api.v1.restaurants.router import router as restaurants_router
from app.core.config import settings
from app.core.database import Base, engine, get_db
from app.core.rate_limit import RateLimitMiddleware
from app.core.request_logging import RequestLoggingMiddleware
from app.workers.pool import image_pool

templates = Jinja2Templates(directory="app/templates")

tags_metadata = [
    {
        "name": "Autenticación",
        "description": "Registro, login y gestión de sesión. Obtén un JWT token con `/login` "
        "y úsalo en el header `Authorization: Bearer <token>` para los demás endpoints.",
    },
    {
        "name": "Restaurante",
        "description": "CRUD del restaurante del usuario. Cada usuario puede tener **un solo restaurante**. "
        "El slug se genera automáticamente a partir del nombre.",
    },
    {
        "name": "Categorías",
        "description": "Gestión de las categorías del menú (ej: Entrantes, Principales, Postres). "
        "Las categorías se ordenan por posición y pueden activarse/desactivarse.",
    },
    {
        "name": "Platos",
        "description": "CRUD de platos dentro de las categorías. Soporta precios de oferta, "
        "etiquetas, destacados y control de disponibilidad.",
    },
    {
        "name": "Imágenes",
        "description": "Subida y eliminación de imágenes de platos. Las imágenes se procesan "
        "en segundo plano (redimensionado y optimización) y se almacenan en Google Cloud Storage.",
    },
    {
        "name": "Código QR",
        "description": "Generación del código QR del menú público del restaurante. "
        "Disponible en formato PNG y SVG con varios tamaños.",
    },
    {
        "name": "Menú Público",
        "description": "Endpoints públicos (sin autenticación) para consultar el menú de un restaurante "
        "por su slug. Disponible en JSON y HTML (SSR).",
    },
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Iniciando Worker Pool de imágenes...")
    await image_pool.start()
    yield
    print("Deteniendo Worker Pool limpiamente...")
    await image_pool.shutdown()


app = FastAPI(
    title="LiveMenu API",
    description=(
        "API para gestión de menús digitales de restaurantes.\n\n"
        "## Autenticación\n"
        "1. Crea una cuenta con `POST /api/v1/auth/register`\n"
        "2. Inicia sesión con `POST /api/v1/auth/login` para obtener un JWT token\n"
        "3. Haz clic en **Authorize** (candado arriba a la derecha) y pega el token\n"
        "4. Ya puedes usar todos los endpoints protegidos\n\n"
        "## Flujo típico\n"
        "1. **Registrarse** → **Login** → Obtener token\n"
        "2. **Crear restaurante** con nombre, dirección, horarios...\n"
        "3. **Crear categorías** (Entrantes, Principales, Postres...)\n"
        "4. **Crear platos** en cada categoría con precios e información\n"
        "5. **Subir imágenes** para los platos\n"
        "6. **Descargar QR** para colocarlo en las mesas del restaurante\n"
        "7. Los clientes escanean el QR y ven el **menú público**"
    ),
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_tags=tags_metadata,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(
    RateLimitMiddleware,
    requests_per_minute=settings.RATE_LIMIT_REQUESTS_PER_MINUTE,
)
app.add_middleware(RequestLoggingMiddleware)

logging.getLogger("livemenu.requests").setLevel(logging.INFO)
if not logging.getLogger("livemenu.requests").handlers:
    h = logging.StreamHandler()
    h.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logging.getLogger("livemenu.requests").addHandler(h)

if settings.STORAGE_TYPE == "local":
    uploads_dir = Path(settings.STORAGE_PATH)
    uploads_dir.mkdir(parents=True, exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")

app.include_router(api_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(restaurants_router, prefix="/api/v1")
app.include_router(categories_router, prefix="/api/v1/admin")
app.include_router(dishes_router, prefix="/api/v1/admin")
app.include_router(upload_router, prefix="/api/v1/admin/upload", tags=["Imágenes"])
app.include_router(qr_router, prefix="/api/v1/admin/qr", tags=["Código QR"])
app.include_router(menu_router, prefix="/api/v1/menu", tags=["Menú Público"])


@app.get("/", tags=["General"], summary="Información de la API")
async def root():
    return {
        "message": "LiveMenu API",
        "version": "1.0.0",
        "docs": "/api/docs",
    }


@app.get("/health", tags=["General"], summary="Health check")
async def health_check():
    """Verifica que la API está funcionando correctamente."""
    return {"status": "healthy"}


@app.get("/m/{slug}", response_class=HTMLResponse, tags=["Menú Público"], summary="Menú público (URL del QR)")
async def menu_publico_slug(request: Request, slug: str, db=Depends(get_db)):
    """Ruta pública SSR: https://{domain}/m/{slug} — esta es la URL que escanean los clientes."""
    menu_data = await get_cached_menu(slug, db)
    return templates.TemplateResponse(
        "menu_template.html", {"request": request, "menu": menu_data}
    )
