from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from app.api.v1.menu.router import MENU_CACHE, get_cached_menu, get_menu_from_db

# ── Helpers ────────────────────────────────────────────────────

def _make_dish(name, price, available=True, deleted_at=None, position=0, offer_price=None, tags=None):
    d = MagicMock()
    d.name = name
    d.price = price
    d.description = f"Desc {name}"
    d.available = available
    d.deleted_at = deleted_at
    d.position = position
    d.offer_price = offer_price
    d.image_urls = {}
    d.tags = tags or []
    return d


def _make_category(name, dishes, active=True):
    c = MagicMock()
    c.name = name
    c.active = active
    c.dishes = dishes
    return c


def _make_restaurant(name, slug, logo_url=None, phone=None, horarios=None, categories=None):
    r = MagicMock()
    r.name = name
    r.slug = slug
    r.logo_url = logo_url
    r.phone = phone
    r.horarios = horarios
    r.categories = categories or []
    return r


def _mock_db(restaurant=None):
    db = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = restaurant
    db.execute.return_value = result
    return db


# ── get_menu_from_db ───────────────────────────────────────────

@pytest.mark.asyncio
async def test_menu_from_db_not_found():
    db = _mock_db(restaurant=None)
    result = await get_menu_from_db("no-existe", db)
    assert result is None


@pytest.mark.asyncio
async def test_menu_from_db_filters_unavailable():
    dish_ok = _make_dish("Burger", 10.0, available=True, position=0)
    dish_off = _make_dish("Salad", 8.0, available=False, position=1)
    dish_deleted = _make_dish("Old", 5.0, available=True, deleted_at=datetime.now(), position=2)
    cat = _make_category("Comida", [dish_ok, dish_off, dish_deleted])
    rest = _make_restaurant("Test", "test", categories=[cat])
    db = _mock_db(restaurant=rest)

    menu = await get_menu_from_db("test", db)
    assert menu is not None
    assert menu["restaurant_name"] == "Test"
    items = menu["categories"][0]["items"]
    names = [i["name"] for i in items]
    assert "Burger" in names
    assert "Salad" in names  # all dishes included now (available flag passed)
    assert "Old" not in names  # deleted excluded


@pytest.mark.asyncio
async def test_menu_from_db_includes_offer_price():
    dish = _make_dish("Pizza", 15.0, offer_price=12.0, position=0)
    cat = _make_category("Main", [dish])
    rest = _make_restaurant("R", "r", categories=[cat])
    db = _mock_db(restaurant=rest)

    menu = await get_menu_from_db("r", db)
    item = menu["categories"][0]["items"][0]
    assert item["offer_price"] == 12.0
    assert item["price"] == 15.0


@pytest.mark.asyncio
async def test_menu_from_db_includes_tags():
    dish = _make_dish("Veggie", 10.0, tags=["vegetariano", "sin gluten"], position=0)
    cat = _make_category("Main", [dish])
    rest = _make_restaurant("R", "r", categories=[cat])
    db = _mock_db(restaurant=rest)

    menu = await get_menu_from_db("r", db)
    item = menu["categories"][0]["items"][0]
    assert "vegetariano" in item["tags"]


@pytest.mark.asyncio
async def test_menu_from_db_includes_logo():
    rest = _make_restaurant("R", "r", logo_url="https://img.com/logo.png", categories=[])
    db = _mock_db(restaurant=rest)
    menu = await get_menu_from_db("r", db)
    assert menu["restaurant_logo"] == "https://img.com/logo.png"


@pytest.mark.asyncio
async def test_menu_from_db_skips_inactive_category():
    cat_active = _make_category("Active", [_make_dish("A", 10, position=0)], active=True)
    cat_inactive = _make_category("Hidden", [_make_dish("B", 10, position=0)], active=False)
    rest = _make_restaurant("R", "r", categories=[cat_active, cat_inactive])
    db = _mock_db(restaurant=rest)

    menu = await get_menu_from_db("r", db)
    cat_names = [c["name"] for c in menu["categories"]]
    assert "Active" in cat_names
    assert "Hidden" not in cat_names


# ── get_cached_menu (cache) ────────────────────────────────────

@pytest.mark.asyncio
async def test_cache_hit():
    MENU_CACHE["cached-slug"] = {
        "data": {"restaurant_name": "Cached", "categories": []},
        "expires_at": datetime.now() + timedelta(minutes=10),
    }
    db = AsyncMock()
    result = await get_cached_menu("cached-slug", db)
    assert result["restaurant_name"] == "Cached"
    db.execute.assert_not_awaited()
    del MENU_CACHE["cached-slug"]


@pytest.mark.asyncio
async def test_cache_miss_not_found():
    MENU_CACHE.pop("miss-slug", None)
    db = _mock_db(restaurant=None)
    with pytest.raises(HTTPException) as exc:
        await get_cached_menu("miss-slug", db)
    assert exc.value.status_code == 404
