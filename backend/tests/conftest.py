from unittest.mock import AsyncMock

import pytest


@pytest.fixture
def fake_db():
    """Mock de sesión async de base de datos para unit tests."""
    db = AsyncMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    db.add = AsyncMock()
    db.delete = AsyncMock()
    return db
