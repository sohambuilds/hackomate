import os
import sys
from time import perf_counter

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request

try:
    from loguru import logger
except Exception:  # pragma: no cover - fallback if loguru unavailable
    class _NoopLogger:
        def __getattr__(self, name):
            def _noop(*args, **kwargs):
                return None

            return _noop

    logger = _NoopLogger()  # type: ignore

from .db import lifespan
from .routers.challenges import router as challenges_router
from .routers.profiles import router as profiles_router
from .routers.teams import router as teams_router


def _allowed_origins() -> list[str]:
    origins = ["http://localhost:3000"]
    frontend_origin = os.getenv("FRONTEND_ORIGIN")
    if frontend_origin:
        origins.append(frontend_origin)
    return origins


app = FastAPI(lifespan=lifespan)

# ---------------
# Logging setup
# ---------------
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
try:
    logger.remove()  # remove default handler to avoid duplicate logs
    logger.add(
        sys.stdout,
        level=LOG_LEVEL,
        enqueue=True,
        backtrace=False,
        diagnose=False,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {extra[component]: <10} | {message}",
    )
except Exception:
    # If loguru is not available, skip configuration
    pass

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Log allowed origins once at startup time (module import time is fine in server context)
try:
    logger.bind(component="startup").info("Allowed CORS origins: {}", _allowed_origins())
    host = os.getenv("HOST", "0.0.0.0")
    port = os.getenv("PORT", "8000")
    logger.bind(component="startup").info("Listening on {}:{}", host, port)
except Exception:
    pass


# ---------------
# Request logging
# ---------------
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = perf_counter()
    try:
        response = await call_next(request)
        duration_ms = (perf_counter() - start) * 1000
        try:
            logger.bind(component="request").info(
                "{method} {path} -> {status} ({duration:.2f} ms)",
                method=request.method,
                path=request.url.path,
                status=response.status_code,
                duration=duration_ms,
            )
        except Exception:
            pass
        return response
    except Exception as exc:  # Log unhandled exceptions
        duration_ms = (perf_counter() - start) * 1000
        try:
            logger.bind(component="request").exception(
                "{method} {path} -> 500 ({duration:.2f} ms): {error}",
                method=request.method,
                path=request.url.path,
                duration=duration_ms,
                error=str(exc),
            )
        except Exception:
            pass
        raise


@app.get("/health")
async def health():
    return {"status": "ok"}


app.include_router(profiles_router)
app.include_router(challenges_router)
app.include_router(teams_router)


