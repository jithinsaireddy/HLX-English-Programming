from typing import List


def lint_lines(lines: List[str]) -> List[str]:
    warnings: List[str] = []
    known_starters = [
        'create a variable', 'set ', 'add ', 'subtract ', 'multiply ', 'divide ', 'concatenate ', 'print',
        'define a function', 'call ', 'return', 'if ', 'else', 'write ', 'read file', 'append ', 'http get',
        'http post', 'parse json', 'stringify json', 'get json', 'make ', 'trim ', 'format ', 'capture group',
        'set http header', 'import module'
    ]
    for i, raw in enumerate(lines, start=1):
        line = raw.strip().lower()
        if not line or line.startswith('#'):
            continue
        if not any(line.startswith(k) for k in known_starters):
            warnings.append(f"Line {i}: Unknown phrase start; consider rephrasing -> {raw.strip()}")
    return warnings



