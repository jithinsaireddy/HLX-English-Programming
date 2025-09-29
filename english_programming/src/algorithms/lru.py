from collections import OrderedDict
from typing import Generic, TypeVar, Optional


K = TypeVar("K")
V = TypeVar("V")


class LRUCache(Generic[K, V]):
    """
    Simple LRU cache with O(1) get/put using OrderedDict.
    Evicts least recently used item upon capacity overflow.
    """

    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        self.capacity = int(capacity)
        self._store: OrderedDict[K, V] = OrderedDict()

    def get(self, key: K) -> Optional[V]:
        if key not in self._store:
            return None
        # Move to end (most recently used)
        self._store.move_to_end(key)
        return self._store[key]

    def put(self, key: K, value: V) -> None:
        if key in self._store:
            # Update and move to end
            self._store[key] = value
            self._store.move_to_end(key)
        else:
            self._store[key] = value
        # Evict if over capacity
        while len(self._store) > self.capacity:
            self._store.popitem(last=False)

    def __len__(self) -> int:
        return len(self._store)

    def __contains__(self, key: K) -> bool:
        return key in self._store




