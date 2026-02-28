import uuid
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.repositories.dish_repository import DishRepository
from app.services.storage_service import storage_service
from app.workers.pool import image_pool

router = APIRouter()

MAX_FILE_SIZE = 5 * 1024 * 1024
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}


@router.post(
    "/",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Subir imagen de plato",
    description="Sube una imagen para un plato existente. La imagen se procesa en segundo plano "
    "(redimensionado, optimización). Formatos aceptados: JPEG, PNG, WebP. Tamaño máximo: 5 MB.",
    responses={
        202: {
            "description": "Imagen aceptada y encolada para procesamiento",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Imagen validada y encolada para procesamiento en segundo plano.",
                        "filename": "a1b2c3d4.webp",
                        "dish_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                        "status": "processing",
                    }
                }
            },
        },
        403: {"description": "El plato no pertenece al usuario"},
        413: {"description": "La imagen supera los 5 MB"},
        415: {"description": "Formato de imagen no soportado"},
    },
)
async def upload_image(
    dish_id: UUID = Form(..., description="UUID del plato al que pertenece la imagen"),
    file: UploadFile = File(..., description="Archivo de imagen (JPEG, PNG o WebP, máx 5 MB)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = DishRepository()
    is_owner = await repo.verify_dish_ownership(db, dish_id, current_user.id)
    if not is_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operación denegada. El plato no existe o no tienes autorización para modificarlo.",
        )

    file_bytes = await file.read()
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="El archivo excede el límite permitido de 5MB.",
        )

    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Tipo de archivo no soportado: {file.content_type}.",
        )

    file_extension = file.filename.split(".")[-1].lower() if "." in file.filename else "bin"
    if file_extension not in ["jpg", "jpeg", "png", "webp"]:
        file_extension = "jpg"

    safe_filename = f"{uuid.uuid4().hex}.{file_extension}"

    await image_pool.add_task(file_bytes, safe_filename, dish_id)

    return {
        "message": "Imagen validada y encolada para procesamiento en segundo plano.",
        "filename": safe_filename,
        "dish_id": dish_id,
        "status": "processing",
    }


@router.delete(
    "/{filename}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar imagen",
    description="Elimina una imagen del almacenamiento (Google Cloud Storage). "
    "El nombre de archivo se obtiene del campo `image_urls` del plato.",
    responses={
        204: {"description": "Imagen eliminada correctamente"},
        400: {"description": "Nombre de archivo inválido"},
        404: {"description": "La imagen no existe"},
    },
)
async def delete_image_endpoint(
    filename: str,
    current_user: User = Depends(get_current_user),
):
    if "/" in filename or "\\" in filename or ".." in filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nombre de archivo inválido. Las rutas de directorios están prohibidas.",
        )

    success = storage_service.delete_image(filename)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La imagen no existe o no pudo ser eliminada.",
        )

    return
