import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
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



# Gestión del ciclo de vida
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
    description="API para gestión de menús digitales de restaurantes. **Autenticación:** 1) Llama a POST /api/v1/auth/login con email y contraseña. 2) Copia el `access_token` de la respuesta. 3) Haz clic en Authorize y pega el token.",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
)

# Middlewares (orden: último añadido = primero en ejecutar)
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

# Configurar logging de requests
logging.getLogger("livemenu.requests").setLevel(logging.INFO)
if not logging.getLogger("livemenu.requests").handlers:
    h = logging.StreamHandler()
    h.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logging.getLogger("livemenu.requests").addHandler(h)

# Incluir routers
app.include_router(api_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(restaurants_router, prefix="/api/v1")
app.include_router(categories_router, prefix="/api/v1/admin")
app.include_router(dishes_router, prefix="/api/v1/admin")
app.include_router(upload_router, prefix="/api/v1/admin/upload", tags=["upload"])
app.include_router(qr_router, prefix="/api/v1/admin/qr", tags=["qr"])
app.include_router(menu_router, prefix="/api/v1/menu", tags=["Menu Público"])

@app.get("/")
async def root():
    return {
        "message": "LiveMenu API",
        "version": "1.0.0",
        "docs": "/api/docs"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/m/{slug}", response_class=HTMLResponse, summary="Menú público (URL del QR)")
async def menu_publico_slug(request: Request, slug: str, db=Depends(get_db)):
    """Ruta pública según enunciado: https://{domain}/m/{slug}"""
    menu_data = await get_cached_menu(slug, db)
    return templates.TemplateResponse(
        "menu_template.html",
        {"request": request, "menu": menu_data}
    )
