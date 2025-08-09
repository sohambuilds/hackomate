from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from .config import get_settings
from .utils.indexes import ensure_indexes


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
        # Ensure indexes/collections on startup
        db = get_database()
        await ensure_indexes(db)
        yield
    finally:
        global _mongo_client
        if _mongo_client is not None:
            _mongo_client.close()
            _mongo_client = None


__all__ = ["get_database", "get_mongo_client", "lifespan"]


