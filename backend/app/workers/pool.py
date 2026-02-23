# backend/app/workers/pool.py

import asyncio
from concurrent.futures import ProcessPoolExecutor
import logging
import os
from io import BytesIO
from PIL import Image

# Configuración de log y lectura de variable de entorno
logger = logging.getLogger(__name__)
WORKER_POOL_SIZE = int(os.getenv("WORKER_POOL_SIZE", 4))

# LÓGICA CPU-BOUND
def process_image_cpu_bound(image_bytes: bytes, filename: str) -> dict:
    """Transformación de imágenes. Bloquea la CPU, por lo que corre en un proceso separado."""
    try:
        with Image.open(BytesIO(image_bytes)) as img:
            # Normalización estricta de canales alpha
            if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])
                img = background

            variants = {}
            configs = {
                'thumbnail': ((150, 150), 80),
                'medium': ((400, 400), 85),
                'large': ((800, 800), 90)
            }

            for size_name, (dimensions, quality) in configs.items():
                img_copy = img.copy()
                img_copy.thumbnail(dimensions, Image.Resampling.LANCZOS)
                
                output_io = BytesIO()
                img_copy.save(output_io, format='WEBP', quality=quality)
                variants[size_name] = output_io.getvalue()

            return {"status": "success", "variants": variants, "filename": filename}
    except Exception as e:
        return {"status": "error", "message": str(e), "filename": filename}

# ORQUESTADOR I/O-BOUND
class ImageWorkerPool:
    def __init__(self, max_workers: int = WORKER_POOL_SIZE):
        self.queue = asyncio.Queue()
        self.executor = ProcessPoolExecutor(max_workers=max_workers)
        self.workers = []
        self._shutdown_event = asyncio.Event()

    async def start(self):
        """Inicializa los workers que consumirán la cola."""
        for i in range(self.executor._max_workers):
            task = asyncio.create_task(self._worker_loop(i))
            self.workers.append(task)
        logger.info(f"Worker pool iniciado con {self.executor._max_workers} procesos.")

    async def _worker_loop(self, worker_id: int):
        loop = asyncio.get_running_loop()
        while not self._shutdown_event.is_set():
            try:
                task_data = await asyncio.wait_for(self.queue.get(), timeout=1.0)
                
                # Ejecución en proceso paralelo
                result = await loop.run_in_executor(
                    self.executor, 
                    process_image_cpu_bound, 
                    task_data['bytes'], 
                    task_data['filename']
                )

                if result['status'] == 'success':
                    # TODO: Aquí se inyecta la subida al Object Storage (S3/GCS)
                    logger.info(f"Imagen {result['filename']} procesada. Variantes generadas: {list(result['variants'].keys())}")
                else:
                    logger.error(f"Fallo críico procesando {result['filename']}: {result['message']}")

                self.queue.task_done()
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break

    async def add_task(self, image_bytes: bytes, filename: str):
        """Punto de entrada para que el endpoint agregue trabajos."""
        await self.queue.put({'bytes': image_bytes, 'filename': filename})

    async def shutdown(self):
        """Apagado estricto para no perder imágenes en memoria."""
        self._shutdown_event.set()
        await self.queue.join()
        for w in self.workers:
            w.cancel()
        self.executor.shutdown(wait=True)
        logger.info("Worker pool detenido.")

# Instancia global para ser importada por los endpoints
image_pool = ImageWorkerPool()