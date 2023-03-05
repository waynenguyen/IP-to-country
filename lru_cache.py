# Define LRU cache for country name lookup results
from collections import OrderedDict
class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = OrderedDict()

    def get(self, key):
        if key not in self.cache:
            return None

        # Move the key to the end to mark it as recently used
        self.cache.move_to_end(key)

        return self.cache[key]

    def put(self, key, value):
        if key in self.cache:
            # Move the key to the end to mark it as recently used
            self.cache.move_to_end(key)
        else:
            if len(self.cache) >= self.capacity:
                # Remove the least recently used key
                self.cache.popitem(last=False)

        self.cache[key] = value
