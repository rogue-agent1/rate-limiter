#!/usr/bin/env python3
"""Rate limiter (token bucket + sliding window). Zero dependencies."""
import time, threading, sys

class TokenBucket:
    def __init__(self, rate, capacity):
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last_time = time.monotonic()
        self._lock = threading.Lock()

    def acquire(self, tokens=1):
        with self._lock:
            now = time.monotonic()
            elapsed = now - self.last_time
            self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
            self.last_time = now
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False

    def wait(self, tokens=1):
        while not self.acquire(tokens):
            time.sleep(1.0 / self.rate)

class SlidingWindow:
    def __init__(self, limit, window_seconds):
        self.limit = limit
        self.window = window_seconds
        self.timestamps = []
        self._lock = threading.Lock()

    def acquire(self):
        with self._lock:
            now = time.monotonic()
            cutoff = now - self.window
            self.timestamps = [t for t in self.timestamps if t > cutoff]
            if len(self.timestamps) < self.limit:
                self.timestamps.append(now)
                return True
            return False

    def remaining(self):
        with self._lock:
            now = time.monotonic()
            cutoff = now - self.window
            active = sum(1 for t in self.timestamps if t > cutoff)
            return max(0, self.limit - active)

class LeakyBucket:
    def __init__(self, rate, capacity):
        self.rate = rate
        self.capacity = capacity
        self.water = 0
        self.last_time = time.monotonic()
        self._lock = threading.Lock()

    def acquire(self):
        with self._lock:
            now = time.monotonic()
            elapsed = now - self.last_time
            self.water = max(0, self.water - elapsed * self.rate)
            self.last_time = now
            if self.water < self.capacity:
                self.water += 1
                return True
            return False

if __name__ == "__main__":
    tb = TokenBucket(rate=10, capacity=10)
    accepted = sum(1 for _ in range(20) if tb.acquire())
    print(f"Token bucket: {accepted}/20 accepted")
    sw = SlidingWindow(limit=5, window_seconds=1)
    accepted = sum(1 for _ in range(10) if sw.acquire())
    print(f"Sliding window: {accepted}/10 accepted")
