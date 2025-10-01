
/* Auto-generated HLX-Zephyr skeleton for HVAC-Unit-42 */
#include <zephyr/kernel.h>

#define PERIOD_MS 1000
#define RING_LEN 64

K_THREAD_STACK_DEFINE(sensor_stack, 2048);
K_THREAD_STACK_DEFINE(policy_stack, 2048);
struct k_thread sensor_thread;
struct k_thread policy_thread;

static float ring[RING_LEN];
static volatile int ring_idx = 0;
static struct k_mutex ring_mu;

void sensor_entry(void *a, void *b, void *c) {
    while (1) {
        float val = 0.0f; /* TODO: read temp */
        k_mutex_lock(&ring_mu, K_FOREVER);
        ring[ring_idx] = val; ring_idx = (ring_idx + 1) % RING_LEN;
        k_mutex_unlock(&ring_mu);
        k_msleep(PERIOD_MS);
    }
}

void policy_entry(void *a, void *b, void *c) {
    while (1) {
        /* TODO: walk ring with time-based windows; apply hysteresis/cooldown; actuate */
        k_msleep(100);
    }
}

int main(void) {
    k_mutex_init(&ring_mu);
    k_tid_t st = k_thread_create(&sensor_thread, sensor_stack, K_THREAD_STACK_SIZEOF(sensor_stack),
                                 sensor_entry, NULL, NULL, NULL, 5, 0, K_NO_WAIT);
    k_tid_t pt = k_thread_create(&policy_thread, policy_stack, K_THREAD_STACK_SIZEOF(policy_stack),
                                 policy_entry, NULL, NULL, NULL, 5, 0, K_NO_WAIT);
    ARG_UNUSED(st); ARG_UNUSED(pt);
    return 0;
}
