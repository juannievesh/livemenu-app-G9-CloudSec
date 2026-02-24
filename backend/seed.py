# backend/seed.py
import asyncio
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.user import User
from app.models.restaurant import Restaurant
from app.models.category import Category
from app.models.dish import Dish

async def seed_database():
    async with AsyncSessionLocal() as db:
        try:
            print("Iniciando inyección de datos de prueba...")

            # 1. Crear Usuario (Dueño)
            # Revisa si tu modelo User exige otros campos obligatorios
            user_id = uuid.uuid4()
            test_user = User(
                id=user_id,
                email="admin@livemenu.app",
                hashed_password="hashed_mock_password", 
                is_active=True
            )
            db.add(test_user)
            await db.flush() # Flush para obtener el ID sin hacer commit final

            # 2. Crear Restaurante
            # CRÍTICO: El router busca por el campo 'slug'. Si Persona 2 no lo creó,
            # el modelo fallará aquí.
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

            # 3. Crear Categorías
            cat_bebidas_id = uuid.uuid4()
            cat_platos_id = uuid.uuid4()
            
            cat_bebidas = Category(id=cat_bebidas_id, restaurant_id=restaurant_id, name="Bebidas", position=1)
            cat_platos = Category(id=cat_platos_id, restaurant_id=restaurant_id, name="Platos Fuertes", position=2)
            
            db.add_all([cat_bebidas, cat_platos])
            await db.flush()

            # 4. Crear Platos con estructura JSONB simulando GCP
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
                description="Cerveza local con notas cítricas y amargor moderado.",
                price=12000.00,
                image_urls=None, # Simulando un producto sin imagen
                available=True,
                position=1
            )

            db.add_all([plato_1, plato_2, bebida_1])
            
            # Confirmar transacción
            await db.commit()
            print("Datos de prueba inyectados exitosamente.")

        except Exception as e:
            await db.rollback()
            print(f"Error crítico inyectando datos: {e}")

if __name__ == "__main__":
    asyncio.run(seed_database())