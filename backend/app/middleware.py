import time
import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.services.logging_service import LoggingService

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())[:8]
        start = time.time()

        LoggingService.info(
            f"→ {request.method} {request.url.path}",
        )

        response = await call_next(request)

        duration = round((time.time() - start) * 1000, 1)
        LoggingService.info(
            f"← {request.method} {request.url.path} | {response.status_code} | {duration}ms"
        )

        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time"] = f"{duration}ms"
        return response
