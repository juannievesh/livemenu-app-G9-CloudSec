from datetime import UTC, datetime

from sqlalchemy import func, select, update

from app.models.category import Category
from app.models.dish import Dish


class DishRepository:

    async def list(self, db, restaurant_id, filters):

        query = (
            select(Dish)
            .join(Category)
            .where(
                Category.restaurant_id == restaurant_id,
                Dish.deleted_at.is_(None)
            )
        )

        if filters.get("category_id"):
            query = query.where(Dish.category_id == filters["category_id"])

        if filters.get("available") is not None:
            query = query.where(Dish.available == filters["available"])

        if filters.get("featured") is not None:
            query = query.where(Dish.featured == filters["featured"])

        result = await db.execute(query.order_by(Dish.position))
        return result.scalars().all()

    async def get(self, db, dish_id):
        result = await db.execute(
            select(Dish).where(Dish.id == dish_id)
        )
        return result.scalar_one_or_none()

    async def get_max_position(self, db, category_id):
        result = await db.execute(
            select(func.max(Dish.position))
            .where(Dish.category_id == category_id)
        )
        return result.scalar() or 0

    async def create(self, db, **kwargs):
        dish = Dish(**kwargs)
        db.add(dish)
        await db.commit()
        await db.refresh(dish)
        return dish

    async def update_image_urls(self, db, dish_id, urls: dict):
        """Actualiza el campo JSONB con las nuevas URLs generadas en la nube."""
        await db.execute(
            update(Dish).where(Dish.id == dish_id).values(image_urls=urls)
        )
        await db.commit()

    async def soft_delete(self, db, dish):
        dish.deleted_at = datetime.now(UTC)
        await db.commit()

    async def verify_dish_ownership(self, db, dish_id, owner_id) -> bool:
        """
        Verifica que el plato pertenezca a la jerarquía
        de un restaurante cuyo owner_id coincida con el usuario autenticado.
        """
        from sqlalchemy import select

        from app.models.category import Category
        from app.models.restaurant import Restaurant

        stmt = (
            select(Dish.id)
            .join(Category, Dish.category_id == Category.id)
            .join(Restaurant, Category.restaurant_id == Restaurant.id)
            .where(
                Dish.id == dish_id,
                Restaurant.owner_id == owner_id
            )
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none() is not None
