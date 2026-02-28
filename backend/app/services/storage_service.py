import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)


class StorageService:
    def __init__(self):
        self.storage_type = os.getenv("STORAGE_TYPE", "auto")
        self.client = None

        if self.storage_type == "auto":
            self._auto_detect()
        elif self.storage_type == "gcs":
            self._init_gcs()
        else:
            self._init_local()

    def _auto_detect(self):
        creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if creds_path and Path(creds_path).exists():
            try:
                import json
                with open(creds_path) as f:
                    data = json.load(f)
                if data.get("private_key"):
                    self._init_gcs()
                    if self.client:
                        self.storage_type = "gcs"
                        return
            except Exception:
                pass
        self._init_local()
        self.storage_type = "local"

    # ── GCS ──────────────────────────────────────────────────────

    def _init_gcs(self):
        try:
            from google.cloud import storage
            self.client = storage.Client()
            self.bucket_name = os.getenv("GCP_BUCKET_NAME", "livemenu-images-prod")
            self.bucket = self.client.bucket(self.bucket_name)
            logger.info(f"GCS inicializado: bucket={self.bucket_name}")
        except Exception as e:
            logger.error(f"Fallo al inicializar GCS, usando almacenamiento local: {e}")
            self.client = None
            self._init_local()
            self.storage_type = "local"

    # ── Local ────────────────────────────────────────────────────

    def _init_local(self):
        self.upload_dir = Path(os.getenv("STORAGE_PATH", "./uploads"))
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Almacenamiento local: {self.upload_dir.resolve()}")

    # ── Upload ───────────────────────────────────────────────────

    def upload_image_variant(self, file_bytes: bytes, filename: str, content_type: str = "image/webp") -> str:
        if self.storage_type == "gcs":
            return self._upload_gcs(file_bytes, filename, content_type)
        return self._upload_local(file_bytes, filename)

    def _upload_gcs(self, file_bytes: bytes, filename: str, content_type: str) -> str:
        if not self.client:
            raise RuntimeError("GCP Client inactivo. Revisa tus credenciales.")
        from google.cloud.exceptions import GoogleCloudError
        try:
            blob = self.bucket.blob(filename)
            blob.upload_from_string(data=file_bytes, content_type=content_type)
            return blob.public_url
        except GoogleCloudError as e:
            logger.error(f"Error subiendo {filename} a GCS: {e}")
            raise

    def _upload_local(self, file_bytes: bytes, filename: str) -> str:
        filepath = self.upload_dir / filename
        filepath.write_bytes(file_bytes)
        return f"/uploads/{filename}"

    # ── Delete ───────────────────────────────────────────────────

    def delete_image(self, filename: str) -> bool:
        if self.storage_type == "gcs":
            return self._delete_gcs(filename)
        return self._delete_local(filename)

    def _delete_gcs(self, filename: str) -> bool:
        if not self.client:
            return False
        try:
            blob = self.bucket.blob(filename)
            blob.delete()
            return True
        except Exception as e:
            logger.warning(f"No se pudo eliminar {filename} en GCP: {e}")
            return False

    def _delete_local(self, filename: str) -> bool:
        filepath = self.upload_dir / filename
        if filepath.exists():
            filepath.unlink()
            return True
        return False


storage_service = StorageService()
