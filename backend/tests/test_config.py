from app.core.config import settings


def test_settings_defaults():
    assert settings.ALGORITHM == "HS256"
    assert settings.ACCESS_TOKEN_EXPIRE_MINUTES > 0
    assert settings.RATE_LIMIT_REQUESTS_PER_MINUTE > 0
    assert settings.WORKER_POOL_SIZE > 0


def test_cors_origins_is_list():
    assert isinstance(settings.CORS_ORIGINS, list)
    assert len(settings.CORS_ORIGINS) >= 1
