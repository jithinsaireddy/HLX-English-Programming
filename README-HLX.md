# HLX (Controlled-English for IoT/Edge)

HLX is a strict, machine‑verifiable subset of English that specifies sensors, actuators, timing constraints, and safety/policy logic. HLX compiles into deployable artifacts for embedded MCUs and edge gateways while preserving an auditable, natural‑language source of truth.

## 2-minute Quickstart

1) Create outputs (RTOS/Edge/WoT):
```bash
python -m english_programming.hlx.cli english_programming/examples/boiler_a.hlx --out hlx_out
```
- `hlx_out/rtos.rs` (Rust/FreeRTOS skeleton)
- `hlx_out/edge_manifest.json` (Edge manifest)
- `hlx_out/thing_description.json` (W3C WoT TD)

2) Run a local demo (simulated sensor + policy):
```bash
python -m english_programming.hlx.run_demo english_programming/examples/boiler_a.hlx
```

3) Run edge module (simulated or MQTT):
```bash
# simulate locally
python -m english_programming.hlx.edge_module --spec english_programming/examples/boiler_a.hlx
# or with MQTT if paho-mqtt installed and broker available
python -m english_programming.hlx.edge_module --spec english_programming/examples/boiler_a.hlx --endpoint mqtt://localhost
```

## What this does
- HLX compiles to:
  - FreeRTOS Rust skeleton for MCUs (`hlx_out/rtos.rs`)
  - Edge container manifest for gateways (`hlx_out/edge_manifest.json`)
  - W3C WoT Thing Description (`hlx_out/thing_description.json`)
- The demo simulates sensor readings to show policy triggers and safety actions.

## Why HLX is different

- Deterministic semantics for control loops and policy evaluation
- Explicit timing (period, deadline, jitter budgets) and unit‑safe checks
- Capability‑scoped I/O and network access (principle of least authority)
- Portable artifacts and standards alignment (W3C WoT)

## Safety and real‑time model

- Watchdogs and dead‑man switches as first‑class constructs
- Bounded ISR work, queue handoff to tasks, and rate‑monotonic patterns
- Bounds checks for sensor ranges and actuator limits

## Real‑time streaming

- Event‑time vs processing‑time semantics and window operators
- Backpressure strategies for lossy networks
- Idempotent actuator command patterns

## Marketing message
"Write your factory/hospital/city rules in English. We generate verified, multi-target code for microcontrollers and edge gateways—plus a Thing Description for instant interoperability."

## Next steps
- Wire `rtos.rs` into a Rust FreeRTOS project (board-specific HAL)
- Use the edge manifest to containerize `english_programming.hlx.edge_module` and connect to MQTT/CoAP
- Add more HLX verbs (publish/subscribe/store) and device drivers
