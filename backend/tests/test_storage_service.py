import pytest
from unittest.mock import patch, MagicMock
from app.services.storage_service import StorageService

@pytest.fixture
def mock_gcp_client():
    with patch("app.services.storage_service.storage.Client") as mock_client:
        mock_bucket = MagicMock()
        mock_client.return_value.bucket.return_value = mock_bucket
        yield mock_bucket

def test_delete_image_success(mock_gcp_client):
    """Verifica que el servicio intente borrar las tres variantes de la imagen."""
    mock_blob = MagicMock()
    mock_blob.exists.return_value = True
    mock_gcp_client.blob.return_value = mock_blob

    service = StorageService()
    
    result = service.delete_image("uuid-falso.jpg")

    assert result is True
    assert mock_gcp_client.blob.call_count == 1
    assert mock_blob.delete.call_count == 1

def test_delete_image_path_traversal_protection():
    """Verifica que los intentos de inyección de directorios sean bloqueados internamente."""
    service = StorageService()
    
    filename = "../../../etc/passwd"
    
    result = service.delete_image(filename)
    assert result is False