# backend/app/api/v1/admin/upload/router.py
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from app.workers.pool import image_pool
from app.services.storage_service import storage_service
import uuid

router = APIRouter()

# Restricciones estrictas de seguridad
MAX_FILE_SIZE = 5 * 1024 * 1024  # Límite duro de 5 MB
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}

@router.post("/", status_code=status.HTTP_202_ACCEPTED, summary="Subir imagen de plato/categoría")
async def upload_image(file: UploadFile = File(...)):
    """
    Recibe una imagen, valida su integridad y la encola para procesamiento CPU-bound.
    """
    # Validación de tamaño
    file_bytes = await file.read()
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, 
            detail="El archivo excede el límite permitido de 5MB."
        )

    # Validación de Content-Type
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, 
            detail=f"Tipo de archivo no soportado: {file.content_type}."
        )

    # Sanitización de nombre de archivo (Prevención de ejecución remota)
    file_extension = file.filename.split(".")[-1].lower() if "." in file.filename else "bin"
    if file_extension not in ["jpg", "jpeg", "png", "webp"]:
        file_extension = "jpg"
        
    safe_filename = f"{uuid.uuid4().hex}.{file_extension}"

    # Encolar tarea al Worker Pool
    await image_pool.add_task(file_bytes, safe_filename)

    return {
        "message": "Imagen validada y encolada para procesamiento en segundo plano.",
        "filename": safe_filename,
        "status": "processing"
    }

@router.delete("/{filename}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar imagen de GCP")
async def delete_image_endpoint(filename: str):
    """
    Elimina una imagen del almacenamiento en la nube de Google Cloud.
    """
    # Validación contra Path Traversal
    # Ejemplos bloqueados: "../../../etc/passwd", "carpeta/secreta.jpg"
    if "/" in filename or "\\" in filename or ".." in filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Nombre de archivo inválido. Las rutas de directorios están prohibidas."
        )

    # Ejecutar borrado en Google Cloud Storage
    success = storage_service.delete_image(filename)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="La imagen no existe en el Object Storage o no pudo ser eliminada."
        )
        
    return