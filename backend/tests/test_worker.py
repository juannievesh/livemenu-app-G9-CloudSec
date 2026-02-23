# backend/tests/test_worker.py
import pytest
import asyncio
from io import BytesIO
from PIL import Image
from unittest.mock import patch, MagicMock

from app.workers.pool import ImageWorkerPool
from app.services.qr_service import QRService

# --- TESTS DEL SERVICIO QR ---

def test_qr_generation_png():
    """Valida que el servicio genere bytes válidos de una imagen PNG con alta corrección."""
    url = "https://livemenu.app/m/test"
    result_io = QRService.generate_qr(url, format_type='png', size='M')
    
    assert isinstance(result_io, BytesIO)
    result_bytes = result_io.getvalue()
    
    # Validar Magic Number de PNG (\x89PNG\r\n\x1a\n)
    assert result_bytes.startswith(b'\x89PNG\r\n\x1a\n'), "El archivo generado no es un PNG válido"

def test_qr_generation_svg():
    """Valida que el formato alternativo vectorial funcione correctamente."""
    url = "https://livemenu.app/m/test"
    result_io = QRService.generate_qr(url, format_type='svg', size='S')
    
    result_bytes = result_io.getvalue()
    # Validar que contenga el tag XML de SVG
    assert b"<?xml" in result_bytes
    assert b"<svg" in result_bytes

# --- TESTS DEL WORKER POOL (ASYNC & MOCKING) ---

def create_dummy_image_bytes() -> bytes:
    """Crea una imagen sintética en memoria para las pruebas."""
    img = Image.new('RGB', (100, 100), color='blue')
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='JPEG')
    return img_byte_arr.getvalue()

@pytest.mark.asyncio
async def test_worker_pool_processing_and_upload():
    """
    Prueba el ciclo de vida completo del Worker Pool simulando el procesamiento CPU-bound
    y aislando la subida a GCP mediante un Mock para evitar peticiones de red.
    """
    # 1. Instanciar un pool pequeño y aislado solo para este test
    pool = ImageWorkerPool(max_workers=2)
    
    # 2. Mockear el StorageService para que no envíe datos a Google Cloud
    # Esto simula un entorno seguro y rápido
    with patch('app.workers.pool.storage_service.upload_image_variant') as mock_upload:
        # Configurar el mock para que devuelva una URL falsa en lugar de hacer la petición
        mock_upload.return_value = "https://storage.googleapis.com/fake-bucket/test.webp"
        
        # 3. Iniciar el pool y encolar la tarea
        asyncio.create_task(pool.start())
        dummy_bytes = create_dummy_image_bytes()
        await pool.add_task(dummy_bytes, "plato_test.jpg")
        
        # 4. Dar un margen de tiempo ínfimo para que el event loop procese la cola
        await asyncio.sleep(0.5)
        
        # 5. Apagar limpiamente
        await pool.shutdown()
        
        # 6. Aserciones críticas
        # Si la imagen se redimensionó a thumbnail, medium y large, el mock debió ser llamado 3 veces
        assert mock_upload.call_count == 3, "El worker no subió todas las variantes de la imagen"
        
        # Validar que los nombres de los archivos enviados a GCP sean correctos y sanitizados
        called_filenames = [call.args[1] for call in mock_upload.call_args_list]
        assert "plato_test_thumbnail.webp" in called_filenames
        assert "plato_test_large.webp" in called_filenames