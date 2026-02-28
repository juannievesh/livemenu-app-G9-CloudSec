# backend/app/workers/pool.py

import asyncio
import logging
import os
from concurrent.futures import ProcessPoolExecutor
from io import BytesIO
from uuid import UUID

from PIL import Image

from app.core.database import AsyncSessionLocal
from app.repositories.dish_repository import DishRepository
from app.services.storage_service import storage_service

logger = logging.getLogger(__name__)
WORKER_POOL_SIZE = int(os.getenv("WORKER_POOL_SIZE", 4))

def process_image_cpu_bound(image_bytes: bytes, filename: str) -> dict:
    try:
        with Image.open(BytesIO(image_bytes)) as img:
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


class ImageWorkerPool:
    def __init__(self, max_workers: int = WORKER_POOL_SIZE):
        self.queue = asyncio.Queue()
        self.executor = ProcessPoolExecutor(max_workers=max_workers)
        self.workers = []
        self._shutdown_event = asyncio.Event()

    async def start(self):
        for i in range(self.executor._max_workers):
            task = asyncio.create_task(self._worker_loop(i))
            self.workers.append(task)
        logger.info(f"Worker pool iniciado con {self.executor._max_workers} procesos.")

    async def _worker_loop(self, worker_id: int):
        loop = asyncio.get_running_loop()
        while not self._shutdown_event.is_set():
            try:
                task_data = await asyncio.wait_for(self.queue.get(), timeout=1.0)

                dish_id = task_data['dish_id']

                result = await loop.run_in_executor(
                    self.executor,
                    process_image_cpu_bound,
                    task_data['bytes'],
                    task_data['filename']
                )

                if result['status'] == 'success':
                    base_name = result['filename'].split('.')[0]
                    urls_generadas = {}

                    for variant_name, img_bytes in result['variants'].items():
                        cloud_filename = f"{base_name}_{variant_name}.webp"
                        try:
                            url = await loop.run_in_executor(
                                None,
                                storage_service.upload_image_variant,
                                img_bytes,
                                cloud_filename
                            )
                            urls_generadas[variant_name] = url
                        except Exception as e:
                            logger.error(f"GCP Upload fallido para {cloud_filename}: {e}")

                    logger.info(f"Variantes subidas a GCP: {urls_generadas}")

                    try:
                        async with AsyncSessionLocal() as db:
                            repo = DishRepository()
                            await repo.update_image_urls(db, dish_id, urls_generadas)
                        logger.info(f"Base de datos actualizada para dish_id {dish_id}")
                    except Exception as db_error:
                        logger.error(f"Error de base de datos actualizando URLs: {db_error}")

                else:
                    logger.error(f"Error procesando {result['filename']}: {result['message']}")

                self.queue.task_done()
            except TimeoutError:
                continue
            except asyncio.CancelledError:
                break

    async def add_task(self, image_bytes: bytes, filename: str, dish_id: UUID):
        await self.queue.put({'bytes': image_bytes, 'filename': filename, 'dish_id': dish_id})

    async def shutdown(self):
        self._shutdown_event.set()
        await self.queue.join()
        for w in self.workers:
            w.cancel()
        self.executor.shutdown(wait=True)
        logger.info("Worker pool detenido.")

image_pool = ImageWorkerPool()
