import pytest
import asyncio
from io import BytesIO
from PIL import Image
from unittest.mock import patch, MagicMock
import uuid

from app.workers.pool import ImageWorkerPool
from app.services.qr_service import QRService

def test_qr_generation_png():
    url = "https://livemenu.app/m/test"
    result_io = QRService.generate_qr(url, format_type='png', size='M')
    assert isinstance(result_io, BytesIO)
    result_bytes = result_io.getvalue()
    assert result_bytes.startswith(b'\x89PNG\r\n\x1a\n'), "El archivo generado no es un PNG válido"

def test_qr_generation_svg():
    url = "https://livemenu.app/m/test"
    result_io = QRService.generate_qr(url, format_type='svg', size='S')
    result_bytes = result_io.getvalue()
    assert b"<?xml" in result_bytes
    assert b"<svg" in result_bytes

def create_dummy_image_bytes() -> bytes:
    img = Image.new('RGB', (100, 100), color='blue')
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='JPEG')
    return img_byte_arr.getvalue()

@pytest.mark.asyncio
async def test_worker_pool_processing_and_upload():
    pool = ImageWorkerPool(max_workers=2)
    await pool.start()
    
    try:
        with patch('app.workers.pool.storage_service.upload_image_variant') as mock_upload, \
             patch('app.workers.pool.AsyncSessionLocal') as mock_db, \
             patch('app.workers.pool.DishRepository') as mock_repo:

            mock_upload.return_value = "https://storage.googleapis.com/fake-bucket/test.webp"

            dummy_bytes = create_dummy_image_bytes()
            test_dish_id = uuid.uuid4()
            
            await pool.add_task(dummy_bytes, "plato_test.jpg", test_dish_id)

            await asyncio.sleep(0.5)
            assert mock_upload.call_count == 3, "El worker no subió todas las variantes"
            called_filenames = [call.args[1] for call in mock_upload.call_args_list]
            assert "plato_test_thumbnail.webp" in called_filenames
            assert "plato_test_large.webp" in called_filenames

    finally:
        await pool.shutdown()