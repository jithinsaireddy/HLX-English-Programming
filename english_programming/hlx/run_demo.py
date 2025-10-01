import argparse
import random
import time
from english_programming.hlx.grammar import HLXParser


def simulate_series(n: int, comparator: str, threshold, period_ms: int, spike_after: int = 10):
    try:
        thr = float(threshold)
    except Exception:
        thr = 100.0
    # Amplitudes based on threshold scale
    delta = max(1.0, abs(thr) * 0.05)
    vals = []
    for i in range(n):
        if comparator in ('>', '>='):
            # start below threshold, then go above
            if i >= spike_after:
                vals.append(thr + delta + random.uniform(0, delta*0.2))
            else:
                vals.append(thr - delta + random.uniform(-delta*0.2, delta*0.2))
        elif comparator in ('<', '<='):
            # start above threshold, then go below
            if i >= spike_after:
                vals.append(thr - delta - random.uniform(0, delta*0.2))
            else:
                vals.append(thr + delta + random.uniform(-delta*0.2, delta*0.2))
        elif comparator == '==':
            # hold near threshold and then equal exactly
            if i >= spike_after:
                vals.append(thr)
            else:
                vals.append(thr + random.uniform(-delta*0.2, delta*0.2))
        else:
            # default: approach threshold from below
            if i >= spike_after:
                vals.append(thr + delta)
            else:
                vals.append(thr - delta)
    return vals


def main():
    ap = argparse.ArgumentParser(description='HLX local demo runner')
    ap.add_argument('spec', help='HLX spec file')
    ap.add_argument('--realtime', action='store_true', help='Sleep according to sensor period')
    ap.add_argument('--json', action='store_true', help='Emit JSON trace to stdout')
    ap.add_argument('--force', action='store_true', help='Force a trigger if sample stream does not trigger')
    args = ap.parse_args()

    spec = HLXParser().parse(open(args.spec).read())
    thing = spec.thing
    sensor = spec.sensors[0]
    policy = spec.policies[0]
    # Attempt to align primary sensor with policy.metric when available
    try:
        metric_name = str(policy.metric).strip()
        sn = next((s for s in spec.sensors if s.name == metric_name), None)
        if sn is not None:
            sensor = sn
    except Exception:
        pass

    period_ms = sensor.period_ms
    need_consecutive = max(1, policy.duration_ms // period_ms)
    hysteresis = policy.hysteresis_pct / 100.0
    cool_until = -1

    trace = {
        'device': thing.name,
        'endpoint': thing.endpoint,
        'sensor': sensor.name,
        'period_ms': period_ms,
        'policy': {
            'metric': policy.metric,
            'comparator': policy.comparator,
            'threshold': policy.threshold,
            'duration_ms': policy.duration_ms,
            'hysteresis_pct': policy.hysteresis_pct,
            'cooldown_ms': policy.cooldown_ms,
        },
        'samples': [],
        'trigger': None
    }
    if not args.json:
        print(f"Demo starting for {thing.name} at {thing.endpoint}")
        print(f"Sensor {sensor.name} every {period_ms} ms; policy: {policy.metric} {policy.comparator} {policy.threshold} for {policy.duration_ms} ms")

    # Generate 50 samples tailored to the comparator/threshold to trigger naturally
    vals = simulate_series(50, policy.comparator, policy.threshold, period_ms, spike_after=10)
    # If threshold references another sensor, build a companion series and evaluate pairwise
    threshold_sensor_name = policy.threshold if isinstance(policy.threshold, str) else None
    thresh_series = None
    if threshold_sensor_name:
        try:
            # Build complementary series to cross threshold naturally
            base_thr = policy.threshold
            # mirror comparator for complementary side
            thr_comp = '<' if policy.comparator in ('>','>=') else ('>' if policy.comparator in ('<','<=') else '==')
            thresh_series = simulate_series(50, thr_comp, base_thr, period_ms, spike_after=10)
        except Exception:
            thresh_series = None
    consec = 0
    triggered = False
    for idx, v in enumerate(vals):
        cond = False
        thr_base = policy.threshold if isinstance(policy.threshold, (int, float)) else None
        if thresh_series is not None and threshold_sensor_name:
            # Evaluate against other sensor's current value
            tv = thresh_series[idx] if idx < len(thresh_series) else thresh_series[-1]
            if policy.comparator == '>':
                cond = v > tv
            elif policy.comparator == '>=':
                cond = v >= tv
            elif policy.comparator == '<':
                cond = v < tv
            elif policy.comparator == '<=':
                cond = v <= tv
            elif policy.comparator == '==':
                cond = abs(v - tv) < 1e-9
            else:
                cond = False
        else:
            if policy.comparator == '>':
                thr = (thr_base * (1.0 + hysteresis)) if (thr_base is not None and cool_until >= 0 and idx*period_ms < cool_until) else (thr_base if thr_base is not None else float('inf'))
                cond = v > thr
            elif policy.comparator == '>=':
                thr = (thr_base * (1.0 + hysteresis)) if (thr_base is not None and cool_until >= 0 and idx*period_ms < cool_until) else (thr_base if thr_base is not None else float('inf'))
                cond = v >= thr
            elif policy.comparator == '<':
                thr = thr_base if thr_base is not None else float('-inf')
                cond = v < thr
            elif policy.comparator == '<=':
                thr = thr_base if thr_base is not None else float('-inf')
                cond = v <= thr
            elif policy.comparator == '==':
                thr = thr_base if thr_base is not None else v+1e9
                cond = abs(v - thr) < 1e-9
            else:
                cond = False
        consec = consec + 1 if cond else 0
        t_ms = idx*period_ms
        if not args.json:
            print(f"t={t_ms:04d}ms {sensor.name}={v:.1f}")
        sample = {'t_ms': t_ms, 'value': v, 'consecutive': consec}
        if thresh_series is not None and threshold_sensor_name:
            sample['threshold_sensor'] = threshold_sensor_name
            sample['threshold_value'] = tv
        trace['samples'].append(sample)
        if consec >= need_consecutive:
            if not args.json:
                print("-- POLICY TRIGGERED --")
                for act in policy.actions:
                    print(f"ACTION: {act}")
            trace['trigger'] = {'t_ms': t_ms, 'actions': policy.actions}
            if policy.cooldown_ms > 0:
                cool_until = idx*period_ms + policy.cooldown_ms
            triggered = True
            break
        if args.realtime:
            time.sleep(period_ms / 1000.0)

    # If not triggered but --force set, synthesize a trigger by appending enough samples
    if not triggered and args.force:
        base_time = len(vals) * period_ms
        for k in range(need_consecutive):
            t_ms = base_time + k*period_ms
            vals.append(thr_base + 10.0 if thr_base is not None else 9999.0)
            trace['samples'].append({'t_ms': t_ms, 'value': vals[-1], 'consecutive': k+1})
        trace['trigger'] = {'t_ms': base_time + (need_consecutive-1)*period_ms, 'actions': policy.actions, 'forced': True}

    if args.json:
        import json
        print(json.dumps(trace))
    else:
        print("Demo complete.")


if __name__ == '__main__':
    main()


