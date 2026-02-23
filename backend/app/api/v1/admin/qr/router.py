# backend/app/api/v1/admin/qr/router.py
from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
from app.services.qr_service import QRService

router = APIRouter()

@router.get("/", summary="Generar y descargar código QR")
async def generate_qr_endpoint(
    format: str = Query("png", regex="^(png|svg)$", description="Formato de salida"),
    size: str = Query("M", regex="^(S|M|L|XL)$", description="Tamaño del QR")
):
    """
    Genera el QR apuntando a la ruta pública SSR del restaurante.
    Requiere inyección de dependencias para obtener el usuario autenticado (Omitido por ahora).
    """
    # En producción, este slug debe venir de la base de datos asociado al usuario JWT
    mock_slug = "mi-restaurante"
    
    # Construir la URL absoluta hacia el endpoint SSR (/m/:slug)
    # Debes cambiar 'localhost:8000' por el dominio de producción
    target_url = f"http://localhost:8000/m/{mock_slug}"
    
    qr_buffer = QRService.generate_qr(target_url, format, size)
    
    media_type = "image/svg+xml" if format == "svg" else "image/png"
    filename = f"qr_{mock_slug}.{format}"
    
    return StreamingResponse(
        qr_buffer, 
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )