import unittest
import time
from leaky_bucket import LeakyBucket

class TestLeakyBucket(unittest.TestCase):

    def test_acquire_token(self):
        bucket = LeakyBucket(rate_limit=10)
        self.assertTrue(bucket.acquire())
        self.assertTrue(bucket.acquire(5))
        self.assertFalse(bucket.acquire(10))

    def test_rate_limit(self):
        bucket = LeakyBucket(rate_limit=10)
        for i in range(10):
            self.assertTrue(bucket.acquire())
        self.assertFalse(bucket.acquire())

    def test_add_tokens(self):
        bucket = LeakyBucket(rate_limit=10)
        bucket.last_check_time = time.monotonic() - 3600
        self.assertTrue(bucket.acquire())
        self.assertTrue(bucket.acquire(5))
        self.assertFalse(bucket.acquire(5))
        self.assertTrue(bucket.acquire(4))
        time.sleep(2)
        self.assertTrue(bucket.acquire())


if __name__ == "__main__":
    unittest.main()