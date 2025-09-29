import argparse
import random
import time
from english_programming.hlx.grammar import HLXParser


def simulate_pressure_sequence(n: int, base: float = 150.0, spike_after: int = 10, spike_value: float = 185.0):
    vals = []
    for i in range(n):
        if i >= spike_after:
            vals.append(spike_value)
        else:
            vals.append(base + random.uniform(-2.0, 2.0))
    return vals


def main():
    ap = argparse.ArgumentParser(description='HLX local demo runner')
    ap.add_argument('spec', help='HLX spec file')
    ap.add_argument('--realtime', action='store_true', help='Sleep according to sensor period')
    args = ap.parse_args()

    spec = HLXParser().parse(open(args.spec).read())
    thing = spec.thing
    sensor = spec.sensors[0]
    policy = spec.policies[0]

    period_ms = sensor.period_ms
    need_consecutive = max(1, policy.duration_ms // period_ms)
    hysteresis = policy.hysteresis_pct / 100.0
    cool_until = -1

    print(f"Demo starting for {thing.name} at {thing.endpoint}")
    print(f"Sensor {sensor.name} every {period_ms} ms; policy: {policy.metric} {policy.comparator} {policy.threshold} for {policy.duration_ms} ms")

    # Generate 50 samples with a spike that will trigger the policy
    vals = simulate_pressure_sequence(50, base=150.0, spike_after=10, spike_value=max(policy.threshold + 5.0, 185.0))
    consec = 0
    for idx, v in enumerate(vals):
        cond = False
        if policy.comparator == '>':
            thr = policy.threshold * (1.0 + hysteresis) if cool_until >= 0 and idx*period_ms < cool_until else policy.threshold
            cond = v > thr
        elif policy.comparator == '>=':
            thr = policy.threshold * (1.0 + hysteresis) if cool_until >= 0 and idx*period_ms < cool_until else policy.threshold
            cond = v >= thr
        elif policy.comparator == '<':
            cond = v < policy.threshold
        elif policy.comparator == '<=':
            cond = v <= policy.threshold
        elif policy.comparator == '==':
            cond = abs(v - policy.threshold) < 1e-9
        consec = consec + 1 if cond else 0
        print(f"t={idx*period_ms:04d}ms {sensor.name}={v:.1f}")
        if consec >= need_consecutive:
            print("-- POLICY TRIGGERED --")
            for act in policy.actions:
                print(f"ACTION: {act}")
            if policy.cooldown_ms > 0:
                cool_until = idx*period_ms + policy.cooldown_ms
            break
        if args.realtime:
            time.sleep(period_ms / 1000.0)

    print("Demo complete.")


if __name__ == '__main__':
    main()


