from app.core.rate_limit import MemoryRateLimiter


async def test_sliding_window_blocks_then_recovers() -> None:
    now = [0.0]
    limiter = MemoryRateLimiter(clock=lambda: now[0])
    results = [await limiter.hit("k", 3, 60) for _ in range(4)]
    assert [r.allowed for r in results] == [True, True, True, False]
    assert results[3].retry_after_seconds > 0
    now[0] = 61.0
    assert (await limiter.hit("k", 3, 60)).allowed


async def test_keys_are_independent() -> None:
    limiter = MemoryRateLimiter(clock=lambda: 0.0)
    assert (await limiter.hit("a", 1, 60)).allowed
    assert (await limiter.hit("b", 1, 60)).allowed
    assert not (await limiter.hit("a", 1, 60)).allowed
