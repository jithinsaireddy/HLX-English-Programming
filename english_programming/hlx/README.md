# HLX: Controlled‑English for Real‑Time IoT and Edge Systems

HLX is a strict, machine‑verifiable subset of English for specifying sensors, actuators, timing constraints, and safety/policy logic. HLX compiles to artifacts suitable for embedded MCUs and edge gateways while preserving a high‑level, auditable specification.

## Design Goals
- Deterministic semantics for control loops and policies
- Explicit timing (periods, deadlines, jitter budgets)
- Capability‑scoped I/O and networking (principle of least authority)
- Portable outputs and standards alignment (W3C WoT)

## Toolchain Outputs
- `hlx_out/rtos.rs`: Rust/FreeRTOS skeleton with tasks, timers, and queues
- `hlx_out/edge_manifest.json`: Container manifest for gateway deployment
- `hlx_out/thing_description.json`: W3C WoT Thing Description

## Execution and Connectivity
- Local simulation for rapid testing
- MQTT/CoAP connectors for telemetry and command/control
- Pluggable drivers for sensors/actuators; HAL binding is board‑specific

## Example (Sketch)
```
DEVICE boiler_a
SENSOR temperature EVERY 1000 ms
ACTUATOR valve

POLICY overheat_protection:
  IF temperature > 95 C FOR 5 s THEN
    SET valve TO CLOSED
    EMIT alert "overheat"
  ELSE
    SET valve TO OPEN
```
Generated code wires this policy into a periodic task and safe actuator updates. The WoT TD exposes readable/writable properties and actions.

## Safety and Timing Model
- Rate‑monotonic task hints with bounded ISR work
- Watchdogs and dead‑man switches as first‑class constructs
- Bounds checks for sensor ranges and actuator limits

## Real‑Time Data Semantics
- Event‑time vs processing‑time distinctions and window operators
- Backpressure strategies for lossy networks
- Idempotent command patterns for actuators

## spaCy in HLX
- spaCy normalization (mandatory) canonicalizes phrasing and comparison language, improving compile‑time robustness.

## Next Steps
- Expand HLX verbs (publish/subscribe/store/aggregate)
- Add formal contracts for units, ranges, and failure modes
- Provide reference HAL bindings for popular MCU boards

See the root `README.md` for system overview and use cases.
