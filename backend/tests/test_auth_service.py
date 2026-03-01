from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from app.api.v1.auth.service import authenticate_user, register_user
from app.core.security import hash_password, verify_password

# ── Security (bcrypt) ──────────────────────────────────────────

def test_hash_password_returns_hash():
    h = hash_password("secret123")
    assert h != "secret123"
    assert h.startswith("$2b$")


def test_verify_password_correct():
    h = hash_password("secret123")
    assert verify_password("secret123", h) is True


def test_verify_password_wrong():
    h = hash_password("secret123")
    assert verify_password("wrong", h) is False


# ── JWT ────────────────────────────────────────────────────────

def test_create_access_token():
    from jose import jwt

    from app.core.config import settings
    from app.core.jwt import create_access_token

    token = create_access_token({"sub": "user-123"})
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert payload["sub"] == "user-123"
    assert "exp" in payload


def test_create_access_token_custom_expiry():
    from jose import jwt

    from app.core.config import settings
    from app.core.jwt import create_access_token

    token = create_access_token({"sub": "u1"}, expires_minutes=1)
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert payload["sub"] == "u1"


# ── Register ───────────────────────────────────────────────────

def _mock_db(existing_user=None):
    db = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = existing_user
    db.execute.return_value = result
    db.refresh = AsyncMock()
    return db


@pytest.mark.asyncio
async def test_register_success():
    db = _mock_db(existing_user=None)
    await register_user(db, "new@test.com", "password123")
    db.add.assert_called_once()
    db.commit.assert_awaited_once()
    db.refresh.assert_awaited_once()


@pytest.mark.asyncio
async def test_register_duplicate_email():
    fake_user = MagicMock()
    db = _mock_db(existing_user=fake_user)
    with pytest.raises(HTTPException) as exc:
        await register_user(db, "dup@test.com", "pass123")
    assert exc.value.status_code == 400
    assert "already registered" in exc.value.detail


# ── Authenticate ───────────────────────────────────────────────

@pytest.mark.asyncio
async def test_authenticate_email_not_found():
    db = _mock_db(existing_user=None)
    with pytest.raises(HTTPException) as exc:
        await authenticate_user(db, "no@exist.com", "pass")
    assert exc.value.status_code == 401
    assert "no registrado" in exc.value.detail


@pytest.mark.asyncio
async def test_authenticate_wrong_password():
    fake_user = MagicMock()
    fake_user.password_hash = hash_password("correct")
    db = _mock_db(existing_user=fake_user)
    with pytest.raises(HTTPException) as exc:
        await authenticate_user(db, "u@test.com", "wrong")
    assert exc.value.status_code == 401
    assert "Contraseña incorrecta" in exc.value.detail


@pytest.mark.asyncio
async def test_authenticate_success():
    fake_user = MagicMock()
    fake_user.password_hash = hash_password("correct")
    db = _mock_db(existing_user=fake_user)
    result = await authenticate_user(db, "u@test.com", "correct")
    assert result == fake_user
