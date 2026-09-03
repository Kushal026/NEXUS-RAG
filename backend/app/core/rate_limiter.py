"""
Rate Limiter Middleware & Token Bucket Engine for NEXUS-RAG (Phase 10).
Protects API endpoints against denial-of-service, abusive scraping, and brute-force attacks.
"""
from typing import Dict, Tuple
import time
from fastapi import Request, HTTPException, status
from app.core.logging import logger


class TokenBucketRateLimiter:
    """Sliding-window token bucket rate limiter."""

    def __init__(self, default_rate_limit: int = 120, time_window_seconds: int = 60):
        self.default_rate_limit = default_rate_limit
        self.time_window_seconds = time_window_seconds
        # key: client_id -> list of request timestamps
        self._request_history: Dict[str, list] = {}

    def is_allowed(self, client_id: str, max_requests: int = None) -> Tuple[bool, int, int]:
        """
        Checks if client request is within allowed quota.
        Returns: (is_allowed, remaining_requests, reset_seconds)
        """
        limit = max_requests or self.default_rate_limit
        now = time.time()
        window_start = now - self.time_window_seconds

        history = self._request_history.setdefault(client_id, [])
        # Prune timestamps older than window
        self._request_history[client_id] = [t for t in history if t > window_start]
        current_count = len(self._request_history[client_id])

        if current_count >= limit:
            oldest_timestamp = self._request_history[client_id][0]
            reset_sec = max(1, int(self.time_window_seconds - (now - oldest_timestamp)))
            return False, 0, reset_sec

        self._request_history[client_id].append(now)
        remaining = limit - (current_count + 1)
        return True, remaining, self.time_window_seconds


rate_limiter = TokenBucketRateLimiter(default_rate_limit=150, time_window_seconds=60)


async def rate_limit_dependency(request: Request):
    """FastAPI dependency to enforce rate limiting on incoming requests."""
    client_ip = request.client.host if request.client else "127.0.0.1"
    auth_header = request.headers.get("Authorization", "")
    client_key = f"{client_ip}:{auth_header[:16]}" if auth_header else client_ip

    allowed, remaining, reset_time = rate_limiter.is_allowed(client_key)
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Try again in {reset_time} seconds.",
            headers={"Retry-After": str(reset_time), "X-RateLimit-Remaining": "0"}
        )
