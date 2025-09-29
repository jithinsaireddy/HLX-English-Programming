#!/usr/bin/env python3
import sys
from english_programming.bin.nlbc_disassembler import disassemble


def main():
    if len(sys.argv) != 2:
        print("Usage: english-disasm <file.nlbc>")
        return 1
    path = sys.argv[1]
    with open(path, 'rb') as f:
        buf = f.read()
    print(disassemble(buf))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


