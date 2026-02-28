# backend/app/core/rate_limit.py
"""Rate limiting middleware - 100 req/min por IP (RNF04)."""

import time
from collections import defaultdict

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

# Ventana de 60 segundos, máx 100 requests por IP
RATE_LIMIT_REQUESTS = 100
RATE_LIMIT_WINDOW = 60  # segundos


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Limita a 100 requests por minuto por IP."""

    EXCLUDED_PATHS = {"/health", "/"}

    def __init__(self, app, requests_per_minute: int = RATE_LIMIT_REQUESTS):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self._storage: dict[str, list[float]] = defaultdict(list)

    def _get_client_ip(self, request: Request) -> str:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        if request.client:
            return request.client.host
        return "unknown"

    def _is_allowed(self, ip: str) -> bool:
        now = time.time()
        window_start = now - RATE_LIMIT_WINDOW
        timestamps = self._storage[ip]
        # Eliminar timestamps fuera de la ventana
        timestamps[:] = [t for t in timestamps if t > window_start]
        if len(timestamps) >= self.requests_per_minute:
            return False
        timestamps.append(now)
        return True

    async def dispatch(self, request: Request, call_next):
        if request.url.path in self.EXCLUDED_PATHS:
            return await call_next(request)
        ip = self._get_client_ip(request)
        if not self._is_allowed(ip):
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Try again later."},
            )
        return await call_next(request)
