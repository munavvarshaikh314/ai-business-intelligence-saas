import json
import hashlib
from typing import Any, Optional
from datetime import datetime, timedelta

# In-memory cache — swap for Redis in production
_cache: dict = {}

class CacheService:

    @staticmethod
    def _make_key(prefix: str, *args) -> str:
        raw = prefix + "::" + "::".join(str(a) for a in args)
        return hashlib.md5(raw.encode()).hexdigest()

    @staticmethod
    def get(prefix: str, *args) -> Optional[Any]:
        key = CacheService._make_key(prefix, *args)
        entry = _cache.get(key)
        if entry is None:
            return None
        if entry["expires_at"] and datetime.utcnow() > entry["expires_at"]:
            del _cache[key]
            return None
        return entry["value"]

    @staticmethod
    def set(prefix: str, *args, value: Any, ttl_seconds: int = 300) -> None:
        key = CacheService._make_key(prefix, *args)
        _cache[key] = {
            "value": value,
            "expires_at": datetime.utcnow() + timedelta(seconds=ttl_seconds)
        }

    @staticmethod
    def invalidate(prefix: str, *args) -> None:
        key = CacheService._make_key(prefix, *args)
        _cache.pop(key, None)

    @staticmethod
    def clear_all() -> None:
        _cache.clear()
