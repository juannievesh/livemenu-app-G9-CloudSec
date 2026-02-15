from fastapi import HTTPException
from app.repositories.dish_repository import DishRepository
from app.repositories.category_repository import CategoryRepository


class DishService:

    def __init__(self):
        self.repo = DishRepository()
        self.category_repo = CategoryRepository()

    async def list(self, db, restaurant_id, filters):
        return await self.repo.list(db, restaurant_id, filters)

    async def get(self, db, restaurant_id, dish_id):

        dish = await self.repo.get(db, dish_id)

        if not dish or dish.category.restaurant_id != restaurant_id:
            raise HTTPException(404, "Dish not found")

        return dish

    async def create(self, db, restaurant_id, data):

        category = await self.category_repo.get(db, data.category_id)

        if not category or category.restaurant_id != restaurant_id:
            raise HTTPException(400, "Invalid category")

        if data.offer_price and data.offer_price >= data.price:
            raise HTTPException(400, "Offer price must be lower than price")

        position = await self.repo.get_max_position(db, data.category_id)

        return await self.repo.create(
            db,
            category_id=data.category_id,
            name=data.name,
            description=data.description,
            price=data.price,
            offer_price=data.offer_price,
            featured=data.featured,
            tags=data.tags,
            position=position + 1
        )

    async def update(self, db, restaurant_id, dish_id, data):

        dish = await self.get(db, restaurant_id, dish_id)

        update_data = data.dict(exclude_unset=True)

        # Validar offer_price después de posible cambio de precio
        if "offer_price" in update_data:
            price_to_check = update_data.get("price", dish.price)
            if update_data["offer_price"] >= price_to_check:
                raise HTTPException(400, "Offer price must be lower than price")

        for key, value in update_data.items():
            setattr(dish, key, value)

        await db.commit()
        await db.refresh(dish)

        return dish

    async def delete(self, db, restaurant_id, dish_id):

        dish = await self.get(db, restaurant_id, dish_id)
        await self.repo.soft_delete(db, dish)

    async def toggle_availability(self, db, restaurant_id, dish_id):

        dish = await self.get(db, restaurant_id, dish_id)

        dish.available = not dish.available
        await db.commit()
        await db.refresh(dish)
        return dish