from typing import Dict, List, Hashable
from collections import deque, defaultdict


def topo_sort_full_order(adj: Dict[Hashable, List[Hashable]]) -> List[Hashable]:
    """
    Kahn's algorithm returning a full topological order containing all vertices.
    Includes isolated vertices and handles multiple components.
    Raises ValueError if a cycle is detected.
    """
    indeg: Dict[Hashable, int] = defaultdict(int)
    nodes = set(adj.keys())
    for u, vs in adj.items():
        for v in vs:
            indeg[v] += 1
            nodes.add(v)
    # add isolated nodes with zero indegree
    for n in nodes:
        indeg.setdefault(n, 0)
    q = deque([n for n in nodes if indeg[n] == 0])
    order: List[Hashable] = []
    while q:
        u = q.popleft()
        order.append(u)
        for v in adj.get(u, []):
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
    if len(order) != len(nodes):
        raise ValueError("graph contains a cycle")
    return order




