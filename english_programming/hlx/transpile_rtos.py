from typing import List
from english_programming.hlx.grammar import HLXSpec


def generate_rust_freertos(spec: HLXSpec) -> str:
    # Minimal Rust FreeRTOS skeleton with tasks (escaped braces)
    thing = spec.thing
    sens = spec.sensors[0] if spec.sensors else None
    poll_ms = sens.period_ms if sens else 200
    sensor_name = sens.name if sens else 'sensor'
    tpl = """
// Auto-generated HLX-RTOS skeleton for {thing_name}
#![no_std]
#![no_main]

use freertos_rust::{{Duration, FreeRtosUtils, FreeRtosBaseTicks, Task}};

#[no_mangle]
pub extern "C" fn app_main() {{
    let _sensor_task = Task::new().name("sensor").stack_size(1024).start(move || {{
        // Ring buffer: 1200 samples for 600000 ms @ 500 ms (adjust at codegen)
        const N: usize = 1200;
        let mut buf: [f32; N] = [0.0; N];
        let mut idx: usize = 0;
        let mut ts_ms: u64 = 0;
        loop {{
            // TODO: read sensor '{sensor_name}' into val
            let val: f32 = 0.0;
            buf[idx] = val; idx = (idx + 1) % N; ts_ms += {poll_ms} as u64;
            FreeRtosUtils::delay(Duration::ms({poll_ms}));
        }}
    }});

    let _policy_task = Task::new().name("policy").stack_size(1024).start(move || {{
        // TODO: compute over ring buffer with time-based windows; apply hysteresis/cooldown
        loop {{
            FreeRtosUtils::delay(Duration::ms(100));
        }}
    }});
}}
"""
    return tpl.format(thing_name=thing.name, sensor_name=sensor_name, poll_ms=poll_ms)


