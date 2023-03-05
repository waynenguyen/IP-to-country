import time
import threading
from functools import wraps

# Define leaky bucket rate limiting algorithm
class LeakyBucket:
    def __init__(self, rate_limit):
        self.rate_limit = rate_limit
        self.last_check_time = time.monotonic()
        self.tokens = rate_limit
        self.rate_limit_lock = threading.Lock()

    def acquire(self, amount=1):
        with self.rate_limit_lock:
            # Check if enough tokens are available
            self._add_tokens()
            if self.tokens >= amount:
                self.tokens -= amount
                return True
            else:
                return False

    def _add_tokens(self):
        # Calculate time elapsed since last check
        now = time.monotonic()
        time_elapsed = now - self.last_check_time
        self.last_check_time = now

        # Add new tokens based on elapsed time
        new_tokens = time_elapsed * self.rate_limit / 3600

        self.tokens = min(self.tokens + new_tokens, self.rate_limit)

