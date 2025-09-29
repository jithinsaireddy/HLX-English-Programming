# HLX Boards and HAL Integration (Guide)

This guide outlines how to take `hlx_out/rtos.rs` and build a working MCU firmware.

## Prerequisites
- Rust toolchain (nightly recommended for embedded targets)
- Board support crate (BSC) / HAL for your MCU
- FreeRTOS or an RTOS of choice compatible with your board

## Steps
1. Create a new Rust FreeRTOS project for your board and wire the HAL (GPIO, timers, ISR setup)
2. Copy or import code from `hlx_out/rtos.rs` and bind:
   - Task creation and scheduling
   - Periodic timers matching HLX `period` constraints
   - Queues/channels for sensor events and actuator commands
3. Map HLX sensor/actuator names to HAL drivers
4. Implement MQTT/CoAP connectors if required by your HLX spec
5. Build and flash the firmware

## Notes
- HLX provides the structure and policy wiring; board‑specific glue is intentionally separated to keep HLX portable across MCUs.
- Consider watchdogs and fail‑safe defaults aligned with your safety envelope.
