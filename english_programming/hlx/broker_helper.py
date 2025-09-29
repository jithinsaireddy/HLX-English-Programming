"""
Start a local MQTT broker using Docker (eclipse-mosquitto) if available.
If Docker is not available, print manual instructions.
"""

import subprocess
import sys


def have(cmd: str) -> bool:
    try:
        subprocess.run([cmd, "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
        return True
    except Exception:
        return False


def main():
    if have("docker"):
        print("Starting MQTT broker via Docker (eclipse-mosquitto) on port 1883...")
        try:
            # Remove if already exists
            subprocess.run(["docker", "rm", "-f", "hlx-mosquitto"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
            subprocess.check_call(["docker", "run", "-d", "--name", "hlx-mosquitto", "-p", "1883:1883", "eclipse-mosquitto:2"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("Broker started. Use endpoint mqtt://localhost")
            print("Stop with: docker rm -f hlx-mosquitto")
            return
        except Exception as e:
            print(f"Docker run failed: {e}")
    print("Could not start broker automatically.")
    print("Install Docker and run: docker run -d --name hlx-mosquitto -p 1883:1883 eclipse-mosquitto:2")
    print("Or install mosquitto locally and run: mosquitto -p 1883")


if __name__ == '__main__':
    main()


