from typing import List, Any


def merge_sorted_arrays(a: List[Any], b: List[Any]) -> List[Any]:
    """Merge two sorted arrays into a single sorted array (stable)."""
    i = j = 0
    out: List[Any] = []
    while i < len(a) and j < len(b):
        if a[i] <= b[j]:
            out.append(a[i])
            i += 1
        else:
            out.append(b[j])
            j += 1
    if i < len(a):
        out.extend(a[i:])
    if j < len(b):
        out.extend(b[j:])
    return out




