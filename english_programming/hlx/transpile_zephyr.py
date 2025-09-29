from english_programming.hlx.grammar import HLXSpec


def generate_zephyr_c(spec: HLXSpec) -> str:
    thing = spec.thing
    sensor = spec.sensors[0] if spec.sensors else None
    policy = spec.policies[0] if spec.policies else None
    period_ms = sensor.period_ms if sensor else 200
    window_ms = policy.duration_ms if policy else 10000
    ring_len = max(64, int((window_ms // period_ms) * 2) or 64)
    sensor_name = sensor.name if sensor else 'sensor'
    return f"""
/* Auto-generated HLX-Zephyr skeleton for {thing.name} */
#include <zephyr/kernel.h>

#define PERIOD_MS {period_ms}
#define RING_LEN {ring_len}

K_THREAD_STACK_DEFINE(sensor_stack, 2048);
K_THREAD_STACK_DEFINE(policy_stack, 2048);
struct k_thread sensor_thread;
struct k_thread policy_thread;

static float ring[RING_LEN];
static volatile int ring_idx = 0;
static struct k_mutex ring_mu;

void sensor_entry(void *a, void *b, void *c) {{
    while (1) {{
        float val = 0.0f; /* TODO: read {sensor_name} */
        k_mutex_lock(&ring_mu, K_FOREVER);
        ring[ring_idx] = val; ring_idx = (ring_idx + 1) % RING_LEN;
        k_mutex_unlock(&ring_mu);
        k_msleep(PERIOD_MS);
    }}
}}

void policy_entry(void *a, void *b, void *c) {{
    while (1) {{
        /* TODO: walk ring with time-based windows; apply hysteresis/cooldown; actuate */
        k_msleep(100);
    }}
}}

int main(void) {{
    k_mutex_init(&ring_mu);
    k_tid_t st = k_thread_create(&sensor_thread, sensor_stack, K_THREAD_STACK_SIZEOF(sensor_stack),
                                 sensor_entry, NULL, NULL, NULL, 5, 0, K_NO_WAIT);
    k_tid_t pt = k_thread_create(&policy_thread, policy_stack, K_THREAD_STACK_SIZEOF(policy_stack),
                                 policy_entry, NULL, NULL, NULL, 5, 0, K_NO_WAIT);
    ARG_UNUSED(st); ARG_UNUSED(pt);
    return 0;
}}
"""


