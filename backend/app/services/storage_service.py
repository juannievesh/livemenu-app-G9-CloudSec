# backend/app/services/storage_service.py
from google.cloud import storage
from google.cloud.exceptions import GoogleCloudError
import logging
import os

logger = logging.getLogger(__name__)

class StorageService:
    def __init__(self):
        # La autenticación ocurre automáticamente debajo de la mesa 
        # usando la variable GOOGLE_APPLICATION_CREDENTIALS
        try:
            self.client = storage.Client()
            self.bucket_name = os.getenv("GCP_BUCKET_NAME", "livemenu-images-prod")
            self.bucket = self.client.bucket(self.bucket_name)
        except Exception as e:
            logger.error(f"Fallo al inicializar el cliente de GCP: {e}")
            self.client = None

    def upload_image_variant(self, file_bytes: bytes, filename: str, content_type: str = "image/webp") -> str:
        """Sube un archivo a GCS y retorna la URL pública."""
        if not self.client:
            raise RuntimeError("GCP Client inactivo. Revisa tus credenciales.")
            
        try:
            blob = self.bucket.blob(filename)
            
            # Subida directa del binario desde la memoria RAM del Worker
            blob.upload_from_string(
                data=file_bytes,
                content_type=content_type
            )
            
            # Retorna el enlace directo hacia la infraestructura de Google
            return blob.public_url
            
        except GoogleCloudError as e:
            logger.error(f"Error subiendo {filename} a GCS: {e}")
            raise e

storage_service = StorageService()