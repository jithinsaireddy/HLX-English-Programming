def tokenize(nl_lines):
    tokens = []
    for line in nl_lines:
        line = line.lower().strip()
        words = line.split()
        tokens.append(words)
    return tokens