# backend/seed.py
import asyncio
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
# IMPORTACIONES NUEVAS PARA FORZAR CREACIÓN:
from app.core.database import AsyncSessionLocal, engine, Base
import app.models # Obliga a cargar los metadatos de todos los modelos

from app.models.user import User
from app.models.restaurant import Restaurant
from app.models.category import Category
from app.models.dish import Dish

async def seed_database():
    # 1. FUERZA BRUTA ARQUITECTÓNICA: Crear tablas faltantes directamente
    print("Verificando e inicializando tablas en PostgreSQL...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    # 2. Inyección de datos
    async with AsyncSessionLocal() as db:
        try:
            print("Iniciando inyección de datos de prueba...")

            user_id = uuid.uuid4()
            test_user = User(
                id=user_id,
                email=f"admin_{user_id.hex[:6]}@livemenu.app", # Email dinámico por si repites el script
                password_hash="hashed_mock_password" 
            )
            db.add(test_user)
            await db.flush()

            restaurant_id = uuid.uuid4()
            test_restaurant = Restaurant(
                id=restaurant_id,
                owner_id=user_id,
                name="El Buen Sabor",
                slug="mi-restaurante",
                description="Comida local e internacional"
            )
            db.add(test_restaurant)
            await db.flush()

            cat_bebidas_id = uuid.uuid4()
            cat_platos_id = uuid.uuid4()
            
            cat_bebidas = Category(id=cat_bebidas_id, restaurant_id=restaurant_id, name="Bebidas", position=1, active=True)
            cat_platos = Category(id=cat_platos_id, restaurant_id=restaurant_id, name="Platos Fuertes", position=2, active=True)
            
            db.add_all([cat_bebidas, cat_platos])
            await db.flush()

            mock_image_urls = {
                "thumbnail": "https://storage.googleapis.com/livemenu-images-prod/mock_thumbnail.webp",
                "medium": "https://storage.googleapis.com/livemenu-images-prod/mock_medium.webp",
                "large": "https://storage.googleapis.com/livemenu-images-prod/mock_large.webp"
            }

            plato_1 = Dish(
                category_id=cat_platos_id,
                name="Hamburguesa Artesanal",
                description="Carne Angus 200g, queso cheddar, tocineta y pan brioche.",
                price=25000.00,
                image_urls=mock_image_urls,
                available=True,
                position=1
            )

            plato_2 = Dish(
                category_id=cat_platos_id,
                name="Pizza Margarita",
                description="Masa madre, pomodoro San Marzano, mozzarella fresca y albahaca.",
                price=32000.00,
                image_urls=mock_image_urls,
                available=True,
                position=2
            )

            bebida_1 = Dish(
                category_id=cat_bebidas_id,
                name="Cerveza Artesanal IPA",
                description="Cerveza local con notas cítricas.",
                price=12000.00,
                image_urls=None,
                available=True,
                position=1
            )

            db.add_all([plato_1, plato_2, bebida_1])
            await db.commit()
            print("Datos de prueba inyectados exitosamente.")

        except Exception as e:
            await db.rollback()
            print(f"Error crítico inyectando datos: {e}")

if __name__ == "__main__":
    asyncio.run(seed_database())