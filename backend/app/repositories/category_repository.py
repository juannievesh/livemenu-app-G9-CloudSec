from sqlalchemy import select, func, update, delete
from app.models.category import Category
from app.models.dish import Dish


class CategoryRepository:

    async def list(self, db, restaurant_id):
        result = await db.execute(
            select(Category)
            .where(Category.restaurant_id == restaurant_id)
            .order_by(Category.position)
        )
        return result.scalars().all()

    async def get(self, db, category_id):
        result = await db.execute(
            select(Category).where(Category.id == category_id)
        )
        return result.scalar_one_or_none()

    async def get_max_position(self, db, restaurant_id):
        result = await db.execute(
            select(func.max(Category.position))
            .where(Category.restaurant_id == restaurant_id)
        )
        return result.scalar() or 0

    async def has_dishes(self, db, category_id):
        result = await db.execute(
            select(Dish).where(
                Dish.category_id == category_id,
                Dish.deleted_at.is_(None)
            )
        )
        return result.first() is not None

    async def create(self, db, **kwargs):
        category = Category(**kwargs)
        db.add(category)
        await db.commit()
        await db.refresh(category)
        return category

    async def update(self, db, category, data):
        for key, value in data.items():
            setattr(category, key, value)

        await db.commit()
        await db.refresh(category)
        return category

    async def delete(self, db, category):
        await db.delete(category)
        await db.commit()
