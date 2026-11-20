"""Small in-process sliding-window rate limiter.

Good enough for a single-instance MVP. Swap the backend for Redis when the API
runs on multiple workers/instances (same interface).
"""
import threading
import time
from collections import defaultdict, deque
from typing import Deque, Dict, Optional

from fastapi import Request

from app.core.config import settings
from app.core.errors import ApiError


class SlidingWindowLimiter:
    def __init__(self) -> None:
        self._hits: Dict[str, Deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def _prune(self, key: str, window: int, now: float) -> Deque[float]:
        q = self._hits[key]
        while q and now - q[0] >= window:
            q.popleft()
        return q

    def count(self, key: str, window: int) -> int:
        with self._lock:
            return len(self._prune(key, window, time.monotonic()))

    def retry_after(self, key: str, window: int) -> int:
        with self._lock:
            q = self._prune(key, window, time.monotonic())
            if not q:
                return 0
            return max(1, int(window - (time.monotonic() - q[0])) + 1)

    def hit(self, key: str) -> None:
        with self._lock:
            self._hits[key].append(time.monotonic())

    def check_and_hit(self, key: str, limit: int, window: int, message: str) -> None:
        with self._lock:
            now = time.monotonic()
            q = self._prune(key, window, now)
            if len(q) >= limit:
                retry = max(1, int(window - (now - q[0])) + 1)
                raise ApiError(
                    429, message, "RATE_LIMITED",
                    headers={"Retry-After": str(retry)},
                )
            q.append(now)

    def reset(self, key: str) -> None:
        with self._lock:
            self._hits.pop(key, None)

    def clear_all(self) -> None:
        with self._lock:
            self._hits.clear()


limiter = SlidingWindowLimiter()


def client_ip(request: Request) -> str:
    if settings.TRUST_PROXY_HEADERS:
        fwd: Optional[str] = request.headers.get("x-forwarded-for")
        if fwd:
            return fwd.split(",")[0].strip()
    return request.client.host if request.client else "unknown"
