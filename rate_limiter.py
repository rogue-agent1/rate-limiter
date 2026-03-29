#!/usr/bin/env python3
"""rate_limiter - Token bucket and sliding window rate limiters."""
import sys, time

class TokenBucket:
    def __init__(self, rate, capacity):
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last = time.monotonic()
    def _refill(self):
        now = time.monotonic()
        elapsed = now - self.last
        self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
        self.last = now
    def allow(self, tokens=1):
        self._refill()
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False
    def wait_time(self, tokens=1):
        self._refill()
        if self.tokens >= tokens:
            return 0.0
        return (tokens - self.tokens) / self.rate

class SlidingWindowCounter:
    def __init__(self, limit, window_sec):
        self.limit = limit
        self.window = window_sec
        self.counts = {}  # bucket -> count
        self.bucket_size = max(1, window_sec // 10)
    def _bucket(self, t=None):
        if t is None:
            t = time.monotonic()
        return int(t / self.bucket_size)
    def _clean(self, now_bucket):
        cutoff = now_bucket - int(self.window / self.bucket_size) - 1
        for k in list(self.counts):
            if k <= cutoff:
                del self.counts[k]
    def allow(self):
        now = time.monotonic()
        b = self._bucket(now)
        self._clean(b)
        total = sum(self.counts.values())
        if total >= self.limit:
            return False
        self.counts[b] = self.counts.get(b, 0) + 1
        return True

class FixedWindow:
    def __init__(self, limit, window_sec):
        self.limit = limit
        self.window = window_sec
        self.count = 0
        self.window_start = time.monotonic()
    def allow(self):
        now = time.monotonic()
        if now - self.window_start >= self.window:
            self.window_start = now
            self.count = 0
        if self.count < self.limit:
            self.count += 1
            return True
        return False

def test():
    # token bucket
    tb = TokenBucket(rate=10, capacity=5)
    # should allow 5 requests immediately
    for _ in range(5):
        assert tb.allow()
    assert not tb.allow()  # bucket empty
    # fixed window
    fw = FixedWindow(3, 1.0)
    assert fw.allow() and fw.allow() and fw.allow()
    assert not fw.allow()
    # sliding window
    sw = SlidingWindowCounter(5, 1.0)
    for _ in range(5):
        assert sw.allow()
    assert not sw.allow()
    print("OK: rate_limiter")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test()
    else:
        print("Usage: rate_limiter.py test")
