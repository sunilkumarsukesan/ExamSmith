from __future__ import annotations

from functools import lru_cache

from app.settings import settings
from app.storage.inmemory import InMemoryRunRepository
from app.storage.mongo import MongoRunRepository
from app.storage.repo import RunRepository


@lru_cache
def get_repo() -> RunRepository:
    backend = (settings.storage_backend or "inmemory").lower()
    if backend == "mongo":
        return MongoRunRepository(settings.mongodb_uri, settings.mongodb_db)
    return InMemoryRunRepository()
