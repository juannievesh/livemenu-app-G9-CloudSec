import pytest
from fastapi.testclient import TestClient
from uuid import uuid4
from unittest.mock import patch, AsyncMock

from app.main import app
from app.core.deps import get_current_user
from app.core.database import get_db
from app.models.user import User

def override_get_current_user():
    return User(id=uuid4(), email="test_admin@livemenu.app")

async def override_get_db():
    yield AsyncMock()

app.dependency_overrides[get_current_user] = override_get_current_user
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture
def mock_dish_repo():
    with patch("app.api.v1.admin.upload.router.DishRepository.verify_dish_ownership", new_callable=AsyncMock) as mock:
        mock.return_value = True
        yield mock

@pytest.fixture
def mock_worker_pool():
    with patch("app.api.v1.admin.upload.router.image_pool.add_task", new_callable=AsyncMock) as mock:
        yield mock

def test_upload_image_rejects_invalid_mime_type(mock_dish_repo, mock_worker_pool):
    """Prueba que el servidor rechace ejecutables camuflados o archivos no permitidos."""
    dish_id = str(uuid4())
    
    files = {"file": ("malicious.pdf", b"fake pdf content", "application/pdf")}
    data = {"dish_id": dish_id}

    response = client.post("/api/v1/admin/upload/", files=files, data=data)

    assert response.status_code == 415
    assert "Tipo de archivo no soportado" in response.json()["detail"]
    mock_worker_pool.assert_not_called()

def test_upload_image_accepts_valid_image(mock_dish_repo, mock_worker_pool):
    """Prueba el camino feliz con una imagen legítima."""
    dish_id = str(uuid4())
    
    files = {"file": ("burger.jpg", b"fake image bytes", "image/jpeg")}
    data = {"dish_id": dish_id}

    response = client.post("/api/v1/admin/upload/", files=files, data=data)

    assert response.status_code == 202
    assert response.json()["status"] == "processing"
    mock_worker_pool.assert_called_once()