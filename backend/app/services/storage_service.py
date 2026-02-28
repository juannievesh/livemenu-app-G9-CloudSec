# backend/app/services/storage_service.py

import logging
import os

from google.cloud import storage
from google.cloud.exceptions import GoogleCloudError

logger = logging.getLogger(__name__)

class StorageService:
    def __init__(self):
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

            blob.upload_from_string(
                data=file_bytes,
                content_type=content_type
            )

            return blob.public_url

        except GoogleCloudError as e:
            logger.error(f"Error subiendo {filename} a GCS: {e}")
            raise e


    def delete_image(self, filename: str) -> bool:
        """
        Elimina un objeto del bucket de GCP.
        Retorna True si fue exitoso o False si el archivo no existía o hubo un error.
        """
        if not self.client:
            logger.error("Intento de borrado sin cliente GCP activo.")
            return False

        try:
            blob = self.bucket.blob(filename)
            blob.delete()
            logger.info(f"Archivo {filename} eliminado de GCP exitosamente.")
            return True
        except Exception as e:
            logger.warning(f"No se pudo eliminar {filename} en GCP: {e}")
            return False

storage_service = StorageService()
