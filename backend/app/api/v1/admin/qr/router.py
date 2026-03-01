from fastapi import APIRouter, Query, Depends, Request, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.services.qr_service import QRService
from app.core.database import get_db
from app.models.restaurant import Restaurant
from app.models.user import User
from app.core.deps import get_current_user

router = APIRouter()

@router.get("/", summary="Generar y descargar código QR del Restaurante")
async def generate_qr_endpoint(
    request: Request,
    format: str = Query("png", pattern="^(png|svg)$", description="Formato de salida"),
    size: str = Query("M", pattern="^(S|M|L|XL)$", description="Tamaño del QR"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Genera el QR dinámico apuntando a la ruta pública SSR del restaurante del usuario autenticado.
    """
    result = await db.execute(
        select(Restaurant).where(Restaurant.owner_id == current_user.id)
    )
    restaurant = result.scalar_one()

    base_url = str(request.base_url).rstrip("/")
    target_url = f"{base_url}/api/v1/menu/m/{restaurant.slug}"
    
    qr_buffer = QRService.generate_qr(target_url, format, size)
    
    media_type = "image/svg+xml" if format == "svg" else "image/png"
    filename = f"qr_{restaurant.slug}.{format}"
    
    return StreamingResponse(
        qr_buffer, 
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )