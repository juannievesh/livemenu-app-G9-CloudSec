import pytest
from unittest.mock import AsyncMock
from uuid import uuid4
from fastapi import HTTPException
from app.services.dish_service import DishService


class FakeCategory:
    def __init__(self, restaurant_id):
        self.id = uuid4()
        self.restaurant_id = restaurant_id


class FakeDish:
    def __init__(self, restaurant_id):
        self.id = uuid4()
        self.available = True
        self.category = FakeCategory(restaurant_id)
        self.price = 10


class FakeRepo:
    def __init__(self):
        self.dish = None

    async def list(self, db, restaurant_id, filters):
        return []

    async def get(self, db, dish_id):
        return self.dish

    async def get_max_position(self, db, category_id):
        return 2

    async def create(self, db, **kwargs):
        return kwargs

    async def soft_delete(self, db, dish):
        dish.deleted_at = "now"
        return True


class FakeCategoryRepo:
    def __init__(self, category):
        self.category = category

    async def get(self, db, category_id):
        return self.category


@pytest.fixture
def fake_db():
    """Fixture que devuelve un objeto con métodos commit y refresh simulados."""
    db = AsyncMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    return db


@pytest.mark.asyncio
async def test_create_dish_success(fake_db):
    restaurant_id = uuid4()
    category = FakeCategory(restaurant_id)

    service = DishService()
    service.repo = FakeRepo()
    service.category_repo = FakeCategoryRepo(category)

    class Payload:
        category_id = category.id
        name = "Pizza"
        description = None
        price = 20
        offer_price = 15
        featured = False
        tags = []

    result = await service.create(fake_db, restaurant_id, Payload())

    assert result["name"] == "Pizza"
    assert result["position"] == 3  # 2 + 1


@pytest.mark.asyncio
async def test_create_dish_invalid_offer_price(fake_db):
    restaurant_id = uuid4()
    category = FakeCategory(restaurant_id)

    service = DishService()
    service.repo = FakeRepo()
    service.category_repo = FakeCategoryRepo(category)

    class Payload:
        category_id = category.id
        name = "Pizza"
        description = None
        price = 10
        offer_price = 15
        featured = False
        tags = []

    with pytest.raises(HTTPException):
        await service.create(fake_db, restaurant_id, Payload())


@pytest.mark.asyncio
async def test_toggle_availability(fake_db):
    restaurant_id = uuid4()
    dish = FakeDish(restaurant_id)

    service = DishService()
    fake_repo = FakeRepo()
    fake_repo.dish = dish
    service.repo = fake_repo

    result = await service.toggle_availability(fake_db, restaurant_id, dish.id)

    assert result.available is False
    fake_db.commit.assert_awaited_once()
    fake_db.refresh.assert_awaited_once_with(dish)


@pytest.mark.asyncio
async def test_delete_soft_delete(fake_db):
    restaurant_id = uuid4()
    dish = FakeDish(restaurant_id)

    service = DishService()
    fake_repo = FakeRepo()
    fake_repo.dish = dish
    service.repo = fake_repo

    await service.delete(fake_db, restaurant_id, dish.id)

    assert hasattr(dish, "deleted_at")