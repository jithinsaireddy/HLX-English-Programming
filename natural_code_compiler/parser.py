def parse(token_lists):
    parsed = []
    for tokens in token_lists:
        if "create" in tokens and "variable" in tokens and "set" in tokens:
            var_name = tokens[tokens.index("called") + 1]
            value = tokens[-1]
            parsed.append(("assign", var_name, value))
        elif "add" in tokens and "and" in tokens and "store" in tokens:
            var1 = tokens[tokens.index("add") + 1]
            var2 = tokens[tokens.index("and") + 1]
            result = tokens[-1]
            parsed.append(("add", var1, var2, result))
        elif "print" in tokens:
            var_name = tokens[-1]
            parsed.append(("print", var_name))
    return parsed