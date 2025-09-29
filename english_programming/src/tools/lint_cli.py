#!/usr/bin/env python3
import sys
from pathlib import Path
from english_programming.src.compiler.linter import lint_lines


def main():
    if len(sys.argv) < 2:
        print("Usage: english-lint <file.nl>")
        return 1
    path = Path(sys.argv[1])
    if not path.exists():
        print(f"File not found: {path}")
        return 1
    lines = path.read_text().splitlines()
    warnings = lint_lines(lines)
    if warnings:
        print("\n".join(warnings))
        return 2
    print("No issues found.")
    return 0


if __name__ == '__main__':
    sys.exit(main())



