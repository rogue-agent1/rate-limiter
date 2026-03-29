#!/usr/bin/env python3
"""Rate limiter — token bucket, sliding window, fixed window."""
import sys, time

class TokenBucket:
    def __init__(self, capacity, refill_rate):
        self.capacity, self.refill_rate = capacity, refill_rate
        self.tokens, self.last_refill = float(capacity), time.time()
    def _refill(self):
        now = time.time(); elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now
    def allow(self, tokens=1):
        self._refill()
        if self.tokens >= tokens: self.tokens -= tokens; return True
        return False

class FixedWindow:
    def __init__(self, max_requests, window_seconds):
        self.max, self.window = max_requests, window_seconds
        self.counts = {}  # window_key -> count
    def _key(self, t=None): return int((t or time.time()) // self.window)
    def allow(self, t=None):
        k = self._key(t)
        self.counts[k] = self.counts.get(k, 0) + 1
        return self.counts[k] <= self.max

class SlidingWindow:
    def __init__(self, max_requests, window_seconds):
        self.max, self.window = max_requests, window_seconds
        self.timestamps = []
    def allow(self, t=None):
        now = t or time.time()
        self.timestamps = [ts for ts in self.timestamps if now - ts < self.window]
        if len(self.timestamps) < self.max:
            self.timestamps.append(now); return True
        return False

def main():
    if len(sys.argv) < 2: print("Usage: rate_limiter.py <demo|test>"); return
    if sys.argv[1] == "test":
        tb = TokenBucket(5, 1)
        for _ in range(5): assert tb.allow()
        assert not tb.allow()  # exhausted
        tb.tokens = 2; assert tb.allow(); assert tb.allow(); assert not tb.allow()
        # Fixed window
        fw = FixedWindow(3, 60)
        t = 1000.0
        assert fw.allow(t); assert fw.allow(t); assert fw.allow(t)
        assert not fw.allow(t)  # 4th in same window
        assert fw.allow(t + 60)  # new window
        # Sliding window
        sw = SlidingWindow(3, 10)
        t2 = 100.0
        assert sw.allow(t2); assert sw.allow(t2+1); assert sw.allow(t2+2)
        assert not sw.allow(t2+3)  # 4th within 10s
        assert sw.allow(t2+11)  # first one expired
        print("All tests passed!")
    else:
        tb = TokenBucket(10, 2)
        for i in range(15):
            print(f"Request {i}: {'OK' if tb.allow() else 'DENIED'}")

if __name__ == "__main__": main()
