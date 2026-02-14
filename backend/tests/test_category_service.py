import pytest
from uuid import uuid4
from fastapi import HTTPException
from app.services.category_service import CategoryService


class FakeCategory:
    def __init__(self, restaurant_id):
        self.id = uuid4()
        self.restaurant_id = restaurant_id
        self.position = 1


class FakeRepo:
    def __init__(self):
        self.category = None
        self.has_dishes_value = False

    async def list(self, db, restaurant_id):
        return []

    async def get(self, db, category_id):
        return self.category

    async def get_max_position(self, db, restaurant_id):
        return 3

    async def has_dishes(self, db, category_id):
        return self.has_dishes_value

    async def create(self, db, **kwargs):
        return kwargs

    async def update(self, db, category, data):
        return data

    async def delete(self, db, category):
        return True


@pytest.mark.asyncio
async def test_create_category_success():

    service = CategoryService()
    service.repo = FakeRepo()

    class Payload:
        name = "Entradas"
        description = "Desc"

    result = await service.create(None, uuid4(), Payload())

    assert result["name"] == "Entradas"
    assert result["position"] == 4  # 3 + 1


@pytest.mark.asyncio
async def test_create_category_without_name():

    service = CategoryService()
    service.repo = FakeRepo()

    class Payload:
        name = None
        description = None

    with pytest.raises(HTTPException):
        await service.create(None, uuid4(), Payload())


@pytest.mark.asyncio
async def test_delete_category_with_dishes_should_fail():

    service = CategoryService()
    fake_repo = FakeRepo()
    fake_repo.category = FakeCategory(uuid4())
    fake_repo.has_dishes_value = True

    service.repo = fake_repo

    with pytest.raises(HTTPException):
        await service.delete(None, fake_repo.category.restaurant_id, fake_repo.category.id)


@pytest.mark.asyncio
async def test_delete_category_success():

    service = CategoryService()
    fake_repo = FakeRepo()
    fake_repo.category = FakeCategory(uuid4())
    fake_repo.has_dishes_value = False

    service.repo = fake_repo

    result = await service.delete(None, fake_repo.category.restaurant_id, fake_repo.category.id)

    assert result is None
