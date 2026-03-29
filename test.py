from rate_limiter import TokenBucket, SlidingWindow, LeakyBucket
tb = TokenBucket(rate=100, capacity=5)
accepted = sum(1 for _ in range(10) if tb.acquire())
assert accepted == 5
sw = SlidingWindow(limit=3, window_seconds=1)
accepted = sum(1 for _ in range(5) if sw.acquire())
assert accepted == 3
lb = LeakyBucket(rate=100, capacity=3)
accepted = sum(1 for _ in range(5) if lb.acquire())
assert accepted == 3
print("Rate limiter tests passed")