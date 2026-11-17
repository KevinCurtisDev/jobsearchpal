"""Sliding-window rate limiting with Redis (production) or memory (tests, single process)."""

import time
import uuid
from collections import defaultdict, deque
from collections.abc import Callable
from dataclasses import dataclass
from typing import Protocol

from redis.asyncio import Redis


@dataclass(frozen=True)
class RateLimitResult:
    allowed: bool
    remaining: int
    retry_after_seconds: int


class RateLimiter(Protocol):
    async def hit(self, key: str, limit: int, window_seconds: int) -> RateLimitResult: ...


class MemoryRateLimiter:
    """In-process limiter. Fine for tests and local development only."""

    def __init__(self, clock: Callable[[], float] = time.monotonic) -> None:
        self._clock = clock
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    async def hit(self, key: str, limit: int, window_seconds: int) -> RateLimitResult:
        now = self._clock()
        window = self._hits[key]
        while window and window[0] <= now - window_seconds:
            window.popleft()
        if len(window) >= limit:
            retry = int(window[0] + window_seconds - now) + 1
            return RateLimitResult(False, 0, max(retry, 1))
        window.append(now)
        return RateLimitResult(True, limit - len(window), 0)


class RedisRateLimiter:
    """Sliding window using a sorted set per key."""

    def __init__(self, redis: Redis, prefix: str = "rl:") -> None:
        self._redis = redis
        self._prefix = prefix

    async def hit(self, key: str, limit: int, window_seconds: int) -> RateLimitResult:
        now = time.time()
        redis_key = self._prefix + key
        async with self._redis.pipeline(transaction=True) as pipe:
            pipe.zremrangebyscore(redis_key, 0, now - window_seconds)
            pipe.zcard(redis_key)
            pipe.zrange(redis_key, 0, 0, withscores=True)
            count_before, oldest = (await pipe.execute())[1:]
        if count_before >= limit:
            oldest_ts = oldest[0][1] if oldest else now
            retry = int(oldest_ts + window_seconds - now) + 1
            return RateLimitResult(False, 0, max(retry, 1))
        async with self._redis.pipeline(transaction=True) as pipe:
            pipe.zadd(redis_key, {f"{now}:{uuid.uuid4().hex}": now})
            pipe.expire(redis_key, window_seconds)
            await pipe.execute()
        return RateLimitResult(True, limit - count_before - 1, 0)
