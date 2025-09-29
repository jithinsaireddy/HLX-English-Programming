#!/usr/bin/env bash
set -euo pipefail

# Root of repo
ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Ensure venv
if [ ! -d "$ROOT_DIR/.venv" ]; then
  python3 -m venv "$ROOT_DIR/.venv"
fi
source "$ROOT_DIR/.venv/bin/activate"

# Install backend (editable)
pip install --upgrade pip >/dev/null
pip install -e . >/dev/null

# Optional: install spaCy model if missing
python - <<'PY' || true
try:
    import spacy
    try:
        spacy.load('en_core_web_sm')
    except Exception:
        import os
        os.system('python -m spacy download en_core_web_sm')
except Exception:
    pass
PY

# Start Flask backend
export FLASK_APP="english_programming/src/interfaces/web/web_app.py"
export EP_ENABLE_NET=0

flask run --port 5000 &
FLASK_PID=$!

# Start UI
pushd "$ROOT_DIR/ui/english-ui" >/dev/null
npm i >/dev/null
npm run dev &
UI_PID=$!
popd >/dev/null

echo "Backend PID: $FLASK_PID"
echo "UI PID: $UI_PID"
echo "Open UI at: http://localhost:5173"
echo "Press Ctrl+C to stop."

trap 'kill $FLASK_PID $UI_PID >/dev/null 2>&1 || true' INT TERM
wait


