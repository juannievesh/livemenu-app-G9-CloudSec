from fastapi import HTTPException
from app.repositories.category_repository import CategoryRepository


class CategoryService:

    def __init__(self):
        self.repo = CategoryRepository()

    async def list(self, db, restaurant_id):
        return await self.repo.list(db, restaurant_id)

    async def create(self, db, restaurant_id, data):

        if not data.name:
            raise HTTPException(400, "Name is required")

        position = await self.repo.get_max_position(db, restaurant_id)

        return await self.repo.create(
            db,
            restaurant_id=restaurant_id,
            name=data.name,
            description=data.description,
            position=position + 1
        )

    async def update(self, db, restaurant_id, category_id, data):

        category = await self.repo.get(db, category_id)

        if not category or category.restaurant_id != restaurant_id:
            raise HTTPException(404, "Category not found")

        return await self.repo.update(db, category, data.dict(exclude_unset=True))

    async def delete(self, db, restaurant_id, category_id):

        category = await self.repo.get(db, category_id)

        if not category or category.restaurant_id != restaurant_id:
            raise HTTPException(404, "Category not found")

        if await self.repo.has_dishes(db, category_id):
            raise HTTPException(400, "Cannot delete category with dishes")

        await self.repo.delete(db, category)

    async def reorder(self, db, restaurant_id, order_list):

        for item in order_list:
            category = await self.repo.get(db, item.id)

            if not category or category.restaurant_id != restaurant_id:
                raise HTTPException(404, "Invalid category in reorder")

            category.position = item.position

        await db.commit()
