# English Programming VS Code Extension

## Install (Local)
- Open this folder in VS Code: `nlvm_phase11_vscode_extension/`.
- Run the VS Code command “Developer: Install Extension from Location…”, select this folder.
- Alternatively, run `F5` to launch an Extension Development Host.

## Features
- Syntax highlighting for `.nl` files.
- Commands:
  - “English: Format File” (runs `english-format` on the current file)
  - “English: Lint File” (runs `english-lint` on the current file)

Ensure the CLI tools are installed (from the repo root):
```
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
```
This provides the `english-format` and `english-lint` commands.

## Suggested Keybindings
Open “Keyboard Shortcuts (JSON)” and add:
```
[
  {
    "key": "ctrl+alt+f",
    "command": "english.format",
    "when": "editorLangId == english"
  },
  {
    "key": "ctrl+alt+l",
    "command": "english.lint",
    "when": "editorLangId == english"
  }
]
```

## Notes
- Formatting modifies the file in place.
- Lint shows warnings for lines that don’t start with known phrases.

