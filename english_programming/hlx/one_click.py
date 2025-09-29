import subprocess
import sys
import webbrowser
from pathlib import Path


def run(cmd: list[str]):
    return subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def main():
    root = Path(__file__).resolve().parents[2]
    # Start broker if possible
    try:
        subprocess.run([sys.executable, '-m', 'english_programming.hlx.broker_helper'])
    except Exception:
        pass
    # Start Flask
    env = dict(**os.environ)
    env['FLASK_APP'] = str(root / 'english_programming' / 'src' / 'interfaces' / 'web' / 'web_app.py')
    flask = subprocess.Popen(['flask', 'run'], env=env)
    # Open browser
    try:
        webbrowser.open_new('http://127.0.0.1:5000/hlx')
    except Exception:
        pass
    flask.wait()


if __name__ == '__main__':
    import os
    main()


