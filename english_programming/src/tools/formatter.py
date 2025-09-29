#!/usr/bin/env python3
import sys


def format_lines(lines):
    out = []
    for line in lines:
        # normalize spaces and trim trailing spaces
        ln = line.rstrip()
        # collapse multiple spaces
        while '  ' in ln:
            ln = ln.replace('  ', ' ')
        # Ensure single space after keywords like 'if'
        if ln.lower().startswith('if') and not ln.lower().startswith('if '):
            ln = 'if ' + ln[2:]
        # lowercase control keywords
        lowers = ['if ', 'else:', 'define a function', 'return', 'call ', 'create a variable', 'set ', 'add ', 'append ', 'write ']
        for key in lowers:
            if ln.lower().startswith(key):
                # preserve rest
                ln = key + ln[len(key):]
        # normalize decorators/annotations format e.g. @route -> @route
        if ln.strip().startswith('@'):
            ln = '@' + ln.strip()[1:]
        # ensure space after commas in value lists
        ln = ln.replace(',', ', ')
        out.append(ln)
    return out


def main():
    if len(sys.argv) < 2:
        print("Usage: english-format <file.nl>")
        return 1
    path = sys.argv[1]
    with open(path, 'r') as f:
        lines = f.readlines()
    formatted = format_lines(lines)
    with open(path, 'w') as f:
        for ln in formatted:
            f.write(ln + '\n')
    print(f"Formatted {path}")
    return 0


if __name__ == '__main__':
    sys.exit(main())


