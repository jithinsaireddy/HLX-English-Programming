# HLX (Human Language eXecution): Controlled‑English for Real‑Time IoT/Edge

HLX specifies sensors, actuators, timing constraints, and safety/policy logic in controlled English. It compiles to deployable artifacts for embedded MCUs and edge gateways while keeping an auditable, human‑readable source of truth.

## Quickstart
```bash
python -m english_programming.hlx.cli english_programming/examples/boiler_a.hlx --out hlx_out
python -m english_programming.hlx.run_demo english_programming/examples/boiler_a.hlx
# Optional
python -m english_programming.hlx.edge_module --spec english_programming/examples/boiler_a.hlx --endpoint mqtt://localhost
```
Outputs:
- `hlx_out/rtos.rs` (Rust/FreeRTOS skeleton)
- `hlx_out/edge_manifest.json` (edge manifest)
- `hlx_out/thing_description.json` (W3C WoT TD)

## Why it’s different
- Deterministic semantics for control policies
- Explicit timing (period/deadline/jitter) and unit‑safe bounds
- Capability‑scoped I/O; principle of least authority
- Portable artifacts and standards alignment (W3C WoT)

## Safety/Timing Model (Sketch)
- Watchdogs and dead‑man switches as first‑class constructs
- Bounded ISR work; queue handoff to tasks; rate‑monotonic hints
- Bounds checks for sensor ranges and actuator limits

## Real‑Time Streaming
- Event‑time vs processing‑time and window operators
- Backpressure strategies for lossy networks
- Idempotent actuator command patterns

## spaCy and HLX
- spaCy normalization (mandatory) improves robustness to phrasing variations (e.g., synonyms of thresholds, comparisons) before compilation.

## Next Steps
- Wire `rtos.rs` to board HALs (see `english_programming/hlx/README_boards.md`)
- Package `edge_module` into containers; connect to MQTT/CoAP
- Expand HLX verbs (publish/subscribe/store/aggregate)
