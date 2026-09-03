"""
Redis & In-Memory Hybrid Caching Engine for NEXUS-RAG (Phase 10).
Accelerates repeated retrieval operations, vector embeddings, and LLM responses with transparent TTL expiration.
"""
from typing import Any, Optional, Dict, Tuple, List
import time
import json
import hashlib
from app.core.config import settings
from app.core.logging import logger

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


class CacheManager:
    """Enterprise hybrid caching engine supporting Redis with transparent in-memory LRU fallback."""

    def __init__(self, redis_url: Optional[str] = None):
        self.redis_client = None
        self._memory_cache: Dict[str, Tuple[Any, float]] = {}  # key -> (value, expire_timestamp)
        self.hits = 0
        self.misses = 0

        # Attempt Redis connection if configured
        url = redis_url or getattr(settings, "REDIS_URL", "redis://localhost:6379/0")
        if REDIS_AVAILABLE and url:
            try:
                r = redis.Redis.from_url(url, socket_timeout=0.8, socket_connect_timeout=0.8)
                r.ping()
                self.redis_client = r
                logger.info("Connected to Redis cache backend.")
            except Exception as e:
                logger.info(f"Redis not reachable ({e}). Using high-performance in-memory cache fallback.")
                self.redis_client = None

    def _hash_key(self, prefix: str, key_data: Any) -> str:
        """Constructs a deterministic SHA-256 cache key."""
        serialized = json.dumps(key_data, sort_keys=True) if isinstance(key_data, (dict, list)) else str(key_data)
        h = hashlib.sha256(serialized.encode()).hexdigest()[:24]
        return f"nexus:{prefix}:{h}"

    def get(self, prefix: str, key_data: Any) -> Optional[Any]:
        """Retrieves cached value if present and unexpired."""
        cache_key = self._hash_key(prefix, key_data)

        if self.redis_client:
            try:
                val = self.redis_client.get(cache_key)
                if val:
                    self.hits += 1
                    return json.loads(val.decode())
            except Exception as e:
                logger.warning(f"Redis get error: {e}")

        # In-memory fallback
        item = self._memory_cache.get(cache_key)
        if item:
            val, expire_time = item
            if time.time() < expire_time:
                self.hits += 1
                return val
            else:
                del self._memory_cache[cache_key]

        self.misses += 1
        return None

    def set(self, prefix: str, key_data: Any, value: Any, ttl_seconds: int = 3600) -> bool:
        """Stores value in cache with specified TTL."""
        cache_key = self._hash_key(prefix, key_data)

        if self.redis_client:
            try:
                serialized = json.dumps(value)
                self.redis_client.setex(cache_key, ttl_seconds, serialized)
                return True
            except Exception as e:
                logger.warning(f"Redis set error: {e}")

        # In-memory fallback
        expire_time = time.time() + ttl_seconds
        self._memory_cache[cache_key] = (value, expire_time)
        return True

    def get_stats(self) -> Dict[str, Any]:
        """Returns cache telemetry stats."""
        total = self.hits + self.misses
        ratio = round(self.hits / max(1, total), 3)
        return {
            "backend": "redis" if self.redis_client else "in_memory_lru",
            "hits": self.hits,
            "misses": self.misses,
            "hit_ratio": ratio,
            "cached_items_count": len(self._memory_cache)
        }

    def clear(self):
        """Clears local in-memory cache."""
        self._memory_cache.clear()
        self.hits = 0
        self.misses = 0


cache_manager = CacheManager()
