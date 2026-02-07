from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base
from app.api.v1 import api_router
from app.api.v1.auth.router import router as auth_router
from app.api.v1.restaurants.router import router as restaurants_router
# Crear tablas (en producción usar migraciones)
# Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="LiveMenu API",
    description="API para gestión de menús digitales de restaurantes",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
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

app.include_router(auth_router, prefix="/api/v1")
app.include_router(restaurants_router, prefix="/api/v1")