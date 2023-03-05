from lru_cache import LRUCache
import unittest


class TestLRUCache(unittest.TestCase):

    def test_lru_cache(self):
        # Initialize a cache with capacity 2
        cache = LRUCache(2)

        # Test inserting and retrieving keys
        cache.put('key1', 'value1')
        cache.put('key2', 'value2')
        assert cache.get('key1') == 'value1'
        assert cache.get('key2') == 'value2'

        # Test evicting the least recently used key
        cache.put('key3', 'value3')
        assert cache.get('key1') is None
        assert cache.get('key2') == 'value2'
        assert cache.get('key3') == 'value3'

        # Test updating the value of an existing key
        cache.put('key2', 'new_value')
        assert cache.get('key2') == 'new_value'

        # Test evicting the least recently used key when the cache is full
        cache.put('key4', 'value4')
        assert cache.get('key3') is None
        assert cache.get('key2') == 'new_value'
        assert cache.get('key4') == 'value4'


if __name__ == "__main__":
    unittest.main()