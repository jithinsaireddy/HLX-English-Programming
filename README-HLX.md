# HLX (Controlled-English for IoT/Edge)

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
- HLX is a strict English layer that compiles to:
  - FreeRTOS Rust skeleton for MCUs
  - Edge container manifest for gateways
  - W3C WoT Thing Description for interoperability
- The demo fakes sensor readings to show the policy triggering.

## Marketing message
"Write your factory/hospital/city rules in English. We generate verified, multi-target code for microcontrollers and edge gateways—plus a Thing Description for instant interoperability."

## Next steps
- Wire `rtos.rs` into a Rust FreeRTOS project (board-specific HAL)
- Use the edge manifest to containerize `english_programming.hlx.edge_module` and connect to MQTT/CoAP
- Add more HLX verbs (publish/subscribe/store) and device drivers
