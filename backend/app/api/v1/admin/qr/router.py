from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user_only
from app.models.restaurant import Restaurant
from app.models.user import User
from app.services.qr_service import QRService

router = APIRouter()


@router.get(
    "",
    summary="Descargar código QR",
    description="Genera y descarga el código QR del menú público del restaurante. "
    "El QR apunta a la URL pública `/m/{slug}`. "
    "Se puede elegir formato (PNG o SVG) y tamaño (S, M, L, XL).",
    responses={
        200: {"description": "Imagen del QR generada", "content": {"image/png": {}, "image/svg+xml": {}}},
        400: {"description": "El usuario no tiene restaurante creado"},
    },
)
async def generate_qr_endpoint(
    request: Request,
    format: str = Query("png", pattern="^(png|svg)$", description="Formato de salida: png o svg"),
    size: str = Query("M", pattern="^(S|M|L|XL)$", description="Tamaño del QR: S (pequeño), M (mediano), L (grande), XL (extra grande)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_only),
):
    result = await db.execute(
        select(Restaurant).where(Restaurant.owner_id == current_user.id)
    )
    restaurant = result.scalar_one_or_none()
    if not restaurant:
        raise HTTPException(400, "Crea primero tu restaurante en Configuración")

    base_url = str(request.base_url).rstrip("/")
    target_url = f"{base_url}/m/{restaurant.slug}"

    qr_buffer = QRService.generate_qr(target_url, format, size)

    media_type = "image/svg+xml" if format == "svg" else "image/png"
    filename = f"qr_{restaurant.slug}.{format}"

    return StreamingResponse(
        qr_buffer,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
