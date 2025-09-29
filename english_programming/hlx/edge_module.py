"""
HLX Edge Module (stub)
- If paho-mqtt is available and endpoint is mqtt://host, connect and subscribe.
- Otherwise, simulate readings like the local demo and apply the policy.
"""

import argparse
import time
import random
from urllib.parse import urlparse
from english_programming.hlx.grammar import HLXParser


def apply_policy_loop(spec, realtime: bool):
    sensor = spec.sensors[0]
    policy = spec.policies[0]
    period_ms = sensor.period_ms
    need_consecutive = max(1, policy.duration_ms // period_ms)
    consec = 0
    # simulate stream
    while True:
        v = 150.0 + (0 if consec > 0 else random.uniform(-2.0, 2.0))
        if consec == 0 and random.random() < 0.05:
            v = policy.threshold + 5.0
        cond = False
        if policy.comparator == '>':
            cond = v > policy.threshold
        elif policy.comparator == '>=':
            cond = v >= policy.threshold
        elif policy.comparator == '<':
            cond = v < policy.threshold
        elif policy.comparator == '<=':
            cond = v <= policy.threshold
        elif policy.comparator == '==':
            cond = abs(v - policy.threshold) < 1e-9
        consec = consec + 1 if cond else 0
        print(f"edge: {sensor.name}={v:.1f} cond={cond} consec={consec}")
        if consec >= need_consecutive:
            print("-- EDGE POLICY TRIGGERED --")
            for act in policy.actions:
                print(f"EDGE ACTION: {act}")
            consec = 0
        if realtime:
            time.sleep(period_ms / 1000.0)
        else:
            time.sleep(0.05)


def main():
    ap = argparse.ArgumentParser(description='HLX edge module')
    ap.add_argument('--spec', required=True, help='HLX spec file')
    ap.add_argument('--endpoint', help='Override endpoint (e.g., mqtt://host)')
    ap.add_argument('--realtime', action='store_true', help='Use sensor period for pacing')
    args = ap.parse_args()

    spec = HLXParser().parse(open(args.spec).read())
    endpoint = args.endpoint or spec.thing.endpoint
    print(f"edge starting: {spec.thing.name} endpoint={endpoint}")
    url = urlparse(endpoint)
    if url.scheme == 'mqtt':
        try:
            import paho.mqtt.client as mqtt
            client = mqtt.Client()
            client.connect(url.hostname, url.port or 1883, 60)
            topic = f"{spec.thing.name}/sensor/{spec.sensors[0].name}"
            state = {'consec': 0}
            policy = spec.policies[0]
            period_ms = spec.sensors[0].period_ms
            need_consecutive = max(1, policy.duration_ms // period_ms)

            def on_message(client, userdata, msg):
                try:
                    v = float(msg.payload.decode('utf-8'))
                except Exception:
                    return
                cond = False
                if policy.comparator == '>':
                    cond = v > policy.threshold
                elif policy.comparator == '>=':
                    cond = v >= policy.threshold
                elif policy.comparator == '<':
                    cond = v < policy.threshold
                elif policy.comparator == '<=':
                    cond = v <= policy.threshold
                elif policy.comparator == '==':
                    cond = abs(v - policy.threshold) < 1e-9
                state['consec'] = state['consec'] + 1 if cond else 0
                if state['consec'] >= need_consecutive:
                    print("-- MQTT POLICY TRIGGERED --")
                    for act in policy.actions:
                        print(f"EDGE ACTION: {act}")
                    state['consec'] = 0

            client.on_message = on_message
            client.subscribe(topic)
            client.loop_forever()
            return
        except Exception as e:
            print(f"mqtt unavailable, simulating locally: {e}")

    apply_policy_loop(spec, args.realtime)


if __name__ == '__main__':
    main()


