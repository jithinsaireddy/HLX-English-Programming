from typing import Dict, Optional, List


class TrieNode:
    __slots__ = ("children", "is_end")

    def __init__(self) -> None:
        self.children: Dict[str, "TrieNode"] = {}
        self.is_end: bool = False


class Trie:
    """Prefix tree with insert, search, and starts_with."""

    def __init__(self) -> None:
        self.root = TrieNode()

    def insert(self, word: str) -> None:
        node = self.root
        for ch in word:
            node = node.children.setdefault(ch, TrieNode())
        node.is_end = True

    def search(self, word: str) -> bool:
        node = self._walk(word)
        return bool(node and node.is_end)

    def starts_with(self, prefix: str) -> bool:
        return self._walk(prefix) is not None

    def suggest(self, prefix: str, limit: int = 10) -> List[str]:
        node = self._walk(prefix)
        if not node:
            return []
        out: List[str] = []
        self._dfs(node, prefix, out, limit)
        return out

    def _walk(self, s: str) -> Optional[TrieNode]:
        node = self.root
        for ch in s:
            node = node.children.get(ch)
            if node is None:
                return None
        return node

    def _dfs(self, node: TrieNode, path: str, out: List[str], limit: int) -> None:
        if len(out) >= limit:
            return
        if node.is_end:
            out.append(path)
            if len(out) >= limit:
                return
        for ch, nxt in node.children.items():
            self._dfs(nxt, path + ch, out, limit)




