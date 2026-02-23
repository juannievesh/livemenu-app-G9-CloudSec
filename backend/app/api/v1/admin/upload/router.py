from fastapi import APIRouter, UploadFile, File, HTTPException, status
from app.workers.pool import image_pool
import uuid

router = APIRouter()

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}

@router.post("/", status_code=status.HTTP_202_ACCEPTED, summary="Subir imagen de plato/categoría")
async def upload_image(file: UploadFile = File(...)):
    # 1. Validación de tamaño
    file_bytes = await file.read()
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, 
            detail="El archivo excede el límite permitido de 5MB."
        )

    # 2. Validación de Content-Type
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, 
            detail=f"Tipo de archivo no soportado: {file.content_type}."
        )

    # 3. Sanitización (Prevención de Path Traversal)
    file_extension = file.filename.split(".")[-1].lower() if "." in file.filename else "bin"
    if file_extension not in ["jpg", "jpeg", "png", "webp"]:
        file_extension = "jpg"
        
    safe_filename = f"{uuid.uuid4().hex}.{file_extension}"

    # 4. Encolar tarea al Worker Pool
    await image_pool.add_task(file_bytes, safe_filename)

    return {
        "message": "Imagen encolada para procesamiento",
        "filename": safe_filename,
        "status": "processing"
    }