import argparse
import time
import random
from urllib.parse import urlparse


def main():
    ap = argparse.ArgumentParser(description='HLX MQTT publisher demo')
    ap.add_argument('--endpoint', default='mqtt://localhost', help='MQTT URL')
    ap.add_argument('--topic', default='Boiler-A/sensor/pressure')
    args = ap.parse_args()
    try:
        import paho.mqtt.client as mqtt
    except Exception:
        print('Install paho-mqtt or pip install -e .[iot]')
        return
    url = urlparse(args.endpoint)
    client = mqtt.Client()
    client.connect(url.hostname, url.port or 1883, 60)
    client.loop_start()
    print(f'Publishing random pressure values to {args.topic}... Ctrl+C to stop')
    try:
        while True:
            v = 150.0 + random.uniform(-2.0, 2.0)
            # Occasionally spike
            if random.random() < 0.1:
                v = 185.0
            client.publish(args.topic, f"{v}")
            time.sleep(0.2)
    except KeyboardInterrupt:
        pass
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == '__main__':
    main()


