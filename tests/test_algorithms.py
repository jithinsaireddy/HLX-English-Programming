import random
from english_programming.src.algorithms.lru import LRUCache
from english_programming.src.algorithms.trie import Trie
from english_programming.src.algorithms.sorting import merge_sorted_arrays
from english_programming.src.algorithms.graph import topo_sort_full_order


def test_lru_basic():
    cache = LRUCache[int, int](2)
    cache.put(1, 1)
    cache.put(2, 2)
    assert cache.get(1) == 1
    cache.put(3, 3)  # evicts key 2
    assert cache.get(2) is None
    cache.put(4, 4)  # evicts key 1
    assert cache.get(1) is None
    assert cache.get(3) == 3
    assert cache.get(4) == 4


def test_trie_search_and_prefix():
    t = Trie()
    for w in ["apple", "app", "ape", "bat"]:
        t.insert(w)
    assert t.search("app") is True
    assert t.search("ap") is False
    assert t.starts_with("ap") is True
    sugg = t.suggest("ap", limit=10)
    assert set(sugg) >= {"app", "apple", "ape"}


def test_merge_sorted_arrays():
    for _ in range(5):
        a = sorted(random.sample(range(100), 10))
        b = sorted(random.sample(range(100), 5))
        c = merge_sorted_arrays(a, b)
        assert c == sorted(a + b)


def test_topo_full_order():
    adj = {
        'a': ['b', 'c'],
        'b': ['d'],
        'c': ['d'],
        'd': [],
        'e': [],  # isolated
    }
    order = topo_sort_full_order(adj)
    # Must contain all nodes
    assert set(order) == {'a', 'b', 'c', 'd', 'e'}
    # Precedence constraints
    assert order.index('a') < order.index('b')
    assert order.index('a') < order.index('c')
    assert order.index('b') < order.index('d')
    assert order.index('c') < order.index('d')




