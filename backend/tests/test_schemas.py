import pytest
from pydantic import ValidationError

from app.api.v1.auth.schemas import LoginRequest, RegisterRequest
from app.schemas.category import CategoryCreate
from app.schemas.dish import DishCreate, DishUpdate

# ── Auth schemas ───────────────────────────────────────────────

def test_register_valid():
    r = RegisterRequest(email="test@test.com", password="123456")
    assert r.email == "test@test.com"


def test_register_short_password():
    with pytest.raises(ValidationError):
        RegisterRequest(email="t@t.com", password="123")


def test_register_invalid_email():
    with pytest.raises(ValidationError):
        RegisterRequest(email="not-an-email", password="123456")


def test_login_valid():
    login = LoginRequest(email="test@test.com", password="pass")
    assert login.email == "test@test.com"


# ── Dish schemas ───────────────────────────────────────────────

def test_dish_create_valid():
    d = DishCreate(
        name="Pizza",
        price=10.50,
        category_id="00000000-0000-0000-0000-000000000001",
    )
    assert d.name == "Pizza"
    assert d.tags == []
    assert d.available is True


def test_dish_create_with_tags():
    d = DishCreate(
        name="Salad",
        price=8,
        category_id="00000000-0000-0000-0000-000000000001",
        tags=["vegetariano", "sin gluten"],
    )
    assert len(d.tags) == 2


def test_dish_create_negative_price():
    with pytest.raises(ValidationError):
        DishCreate(
            name="X",
            price=-1,
            category_id="00000000-0000-0000-0000-000000000001",
        )


def test_dish_update_partial():
    d = DishUpdate(name="Renamed")
    assert d.name == "Renamed"
    assert d.price is None


# ── Category schemas ───────────────────────────────────────────

def test_category_create():
    c = CategoryCreate(name="Bebidas")
    assert c.name == "Bebidas"
