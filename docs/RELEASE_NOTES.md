# Release Notes
Release 1.1.0 (2025-09-28)
- Security hardening: network disabled by default (enable via EP_ENABLE_NET=1); sandbox IMPORTURL/HTTP; op-count/time guards in VM (EP_MAX_OPS/EP_MAX_MS)
- Compiler: zero-warning support for short forms: "length of X store in Y" and "pop from list X store in Y"
- VM: LIST_POP operation; FOR_EACH block execution; improved list append semantics
- Web: simple per-IP rate limiting (EP_RATE_WINDOW_S/EP_RATE_LIMIT)
- Disassembler: richer output with byte offsets and decoded operands/targets
- Algorithms: added `LRUCache`, `Trie` with prefix search, `topo_sort_full_order`, and `merge_sorted_arrays`
- Tests: property-style tests for algorithms and VM list ops

## v0.2.0
- NLBC v1.0: header/sections/opcodes frozen; verifier updated (stack/type).
- SSA hooks active (CSE/LICM/inliner analysis) with gated feedback.
- Async stdlib (sleep, sockets, scheduler) and richer stdlib (sets, CSV/YAML, regex, JSON, dates).
- OOP (classes/fields/methods), exceptions (typed), iterators, pattern matching.
- Optimizer: peephole const-folding; JIT hot-loop stub; profiler counters.
- Tools: disassembler, formatter, linter, LSP stub; CI configured.
- Sandbox: module cache with env-gated network and registry lock; semver resolver + lockfile.
- Explainable traces for key ops (print/call/attr/method) for debugging.

