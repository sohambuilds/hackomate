from contextlib import asynccontextmanager
from typing import AsyncIterator
import os

from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from .config import get_settings
from .utils.indexes import ensure_indexes

try:
    from loguru import logger
except Exception:  # pragma: no cover
    class _NoopLogger:
        def __getattr__(self, name):
            def _noop(*args, **kwargs):
                return None

            return _noop

    logger = _NoopLogger()  # type: ignore


_mongo_client: AsyncIOMotorClient | None = None


def get_mongo_client() -> AsyncIOMotorClient:
    """Return a singleton AsyncIOMotorClient instance."""
    global _mongo_client
    if _mongo_client is None:
        settings = get_settings()
        _mongo_client = AsyncIOMotorClient(settings.mongodb_uri)
    return _mongo_client


def get_database() -> AsyncIOMotorDatabase:
    """FastAPI dependency that returns the configured database."""
    settings = get_settings()
    client = get_mongo_client()
    return client[settings.db_name]


@asynccontextmanager
async def lifespan(app) -> AsyncIterator[None]:
    """FastAPI lifespan handler to manage MongoDB client lifecycle."""
    try:
        # Log startup with host/port and DB
        settings = get_settings()
        host = os.getenv("HOST", "0.0.0.0")
        port = os.getenv("PORT", "8000")
        try:
            logger.bind(component="startup").info(
                "Starting up. Listening on {}:{} | DB: {}",
                host,
                port,
                settings.db_name,
            )
        except Exception:
            pass

        # Ensure indexes/collections on startup
        db = get_database()
        await ensure_indexes(db)
        try:
            logger.bind(component="startup").info("Mongo indexes ensured")
        except Exception:
            pass
        yield
    finally:
        global _mongo_client
        if _mongo_client is not None:
            _mongo_client.close()
            _mongo_client = None
            try:
                logger.bind(component="shutdown").info("Mongo client closed; application shutdown complete")
            except Exception:
                pass


__all__ = ["get_database", "get_mongo_client", "lifespan"]


