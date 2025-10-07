import sys
from pathlib import Path

# Ensure project root is on sys.path
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Import Flask app as WSGI application
from english_programming.src.interfaces.web.web_app import app as application  # noqa: E402
