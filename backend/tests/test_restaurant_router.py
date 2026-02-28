from unittest.mock import AsyncMock, MagicMock

import pytest

from app.api.v1.restaurants.router import _make_unique_slug, _slugify

# ── Slugify ────────────────────────────────────────────────────

def test_slugify_basic():
    assert _slugify("Mi Restaurante") == "mi-restaurante"


def test_slugify_accents_and_symbols():
    assert _slugify("  Café & Bar!  ") == "café-bar"


def test_slugify_empty():
    assert _slugify("") == "restaurant"


def test_slugify_only_special():
    assert _slugify("!!!") == "restaurant"


def test_slugify_dashes():
    assert _slugify("a--b") == "a-b"


# ── Unique slug ────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_make_unique_slug_first_available():
    db = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = None
    db.execute.return_value = result

    slug = await _make_unique_slug(db, "pizza-house")
    assert slug == "pizza-house"
    db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_make_unique_slug_collision():
    db = AsyncMock()
    existing = MagicMock()
    none_result = MagicMock()
    none_result.scalar_one_or_none.return_value = None
    existing_result = MagicMock()
    existing_result.scalar_one_or_none.return_value = existing

    db.execute.side_effect = [existing_result, none_result]
    slug = await _make_unique_slug(db, "taken")
    assert slug.startswith("taken-")
    assert len(slug) > len("taken-")
