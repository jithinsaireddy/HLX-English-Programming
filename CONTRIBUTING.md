# Contributing to English Programming

## Development Setup
- Use a virtualenv:
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e .[nlp]
pip install -r requirements.txt
```

## Running Tests
```bash
pytest -q
```

## Code Style
- Python 3.9+.
- Prefer explicit, readable code and small functions.
- Avoid deep nesting; add guard clauses.
- Keep debug prints behind `debug` flags.

## Pull Requests
- Include tests for new features.
- Update docs (`README.md`) if behavior changes.
- Keep edits minimal and focused.
