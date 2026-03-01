from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.core.config import settings
from app.core.database import engine, Base


from app.api.v1 import api_router
from app.api.v1.auth.router import router as auth_router
from app.api.v1.restaurants.router import router as restaurants_router
from app.api.v1.admin.categories.router import router as categories_router
from app.api.v1.admin.dishes.router import router as dishes_router
from app.api.v1.admin.qr.router import router as qr_router
from app.api.v1.menu.router import router as menu_router
from app.api.v1.admin.upload.router import router as upload_router
from app.workers.pool import image_pool

logger = logging.getLogger(__name__)

# Gestión del ciclo de vida
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Iniciando Worker Pool de imágenes...")
    await image_pool.start()
    yield
    print("Deteniendo Worker Pool limpiamente...")
    logger.info("Señal de apagado recibida. Deteniendo workers de forma segura...")
    await image_pool.shutdown()
    logger.info("Apagado completado.")

# Crear tablas (en producción usar migraciones)
# Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="LiveMenu API",
    description="API para gestión de menús digitales de restaurantes",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan  
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(api_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(restaurants_router, prefix="/api/v1")
app.include_router(categories_router, prefix="/api/v1/admin")
app.include_router(dishes_router, prefix="/api/v1/admin")
app.include_router(upload_router, prefix="/api/v1/admin/upload", tags=["upload"])
app.include_router(qr_router, prefix="/api/v1/admin/qr", tags=["qr"])
# app.include_router(menu_router, tags=["menu"])
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
