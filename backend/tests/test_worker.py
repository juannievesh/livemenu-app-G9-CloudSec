# backend/test_worker.py

import asyncio
from io import BytesIO
from PIL import Image
from app.workers.pool import image_pool
import logging

logging.basicConfig(level=logging.INFO)

def create_dummy_image() -> bytes:
    """Genera un cuadrado rojo de 1000x1000 en memoria para simular un upload pesado."""
    img = Image.new('RGB', (1000, 1000), color='red')
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='JPEG')
    return img_byte_arr.getvalue()

async def main():
    print("Iniciando pool...")
    await image_pool.start()

    print("Generando imagen de prueba...")
    dummy_bytes = create_dummy_image()

    print("Enviando 5 tareas concurrentes al worker pool...")
    for i in range(5):
        await image_pool.add_task(dummy_bytes, f"test_image_{i}.jpg")

    print("Tareas en cola. Esperando a que el pool las procese...")
    # Damos tiempo para que los workers tomen las tareas
    await asyncio.sleep(2)
    
    print("Iniciando apagado controlado (graceful shutdown)...")
    await image_pool.shutdown()
    print("Test finalizado. Si no hay errores arriba, el procesamiento de CPU funciona.")

if __name__ == "__main__":
    asyncio.run(main())