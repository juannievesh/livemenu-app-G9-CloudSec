from sqlalchemy import select, func
from datetime import datetime
from app.models.dish import Dish
from app.models.category import Category


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

    async def soft_delete(self, db, dish):
        dish.deleted_at = datetime.utcnow()
        await db.commit()
