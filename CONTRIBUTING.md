# Contributing to HLX‑English‑Programming

Thanks for your interest in contributing! This guide explains how to propose changes.

## Development Setup

- Python 3.9+
- Create a virtualenv and install dev deps:
  ```bash
  python3 -m venv .venv && source .venv/bin/activate
  pip install -r requirements.txt
  ```

## Workflow

1. Fork and create a feature branch
2. Write tests (see `tests/` and `english_programming/tests/`)
3. Run tests locally
4. Submit a PR with a clear description and rationale

## Coding Guidelines

- Prefer clear, explicit code and descriptive names
- Keep functions small; avoid deep nesting
- Add focused docstrings for non‑obvious logic
- Match existing formatting; run linters where applicable

## Documentation

- Update `README.md` and module READMEs when behavior changes
- Document public CLI flags and environment variables

## Security

- Do not include secrets in PRs
- Report vulnerabilities via `SECURITY.md`

## DCO/License

- Contributions are licensed under the project’s MIT License
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
