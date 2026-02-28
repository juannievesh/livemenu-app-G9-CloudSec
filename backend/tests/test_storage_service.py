from unittest.mock import MagicMock, patch

from app.services.storage_service import StorageService


def _make_service_with_mock_client():
    with patch("app.services.storage_service.storage"):
        svc = StorageService()
        svc.client = MagicMock()
        svc.bucket = MagicMock()
        return svc


def test_upload_image_variant_success():
    svc = _make_service_with_mock_client()
    blob = MagicMock()
    blob.public_url = "https://storage.googleapis.com/bucket/img.webp"
    svc.bucket.blob.return_value = blob

    url = svc.upload_image_variant(b"\x00", "img.webp")
    assert url == "https://storage.googleapis.com/bucket/img.webp"
    blob.upload_from_string.assert_called_once_with(data=b"\x00", content_type="image/webp")


def test_upload_image_variant_no_client():
    svc = StorageService.__new__(StorageService)
    svc.client = None
    try:
        svc.upload_image_variant(b"\x00", "x.webp")
        assert False, "Expected RuntimeError"
    except RuntimeError as e:
        assert "GCP Client" in str(e)


def test_delete_image_success():
    svc = _make_service_with_mock_client()
    blob = MagicMock()
    svc.bucket.blob.return_value = blob
    assert svc.delete_image("old.webp") is True
    blob.delete.assert_called_once()


def test_delete_image_no_client():
    svc = StorageService.__new__(StorageService)
    svc.client = None
    assert svc.delete_image("x.webp") is False
