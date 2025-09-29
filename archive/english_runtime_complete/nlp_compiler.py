import spacy, re

def compile_nl_to_nlc(input_file, output_file):
    try:
        nlp = spacy.load("en_core_web_sm")
    except:
        print("Please install spaCy model: python -m spacy download en_core_web_sm")
        return
    with open(input_file) as f:
        raw_lines = [l.rstrip() for l in f if l.strip()]
    lines = raw_lines
    bytecode = []
    i = 0
    while i < len(lines):
        line = lines[i]
        lower = line.strip().lower()
        # function definition
        m = re.match(r"define a function called (\w+) with inputs (.+):", lower)
        if m:
            name = m.group(1)
            params = [p.strip() for p in m.group(2).split("and")]
            bytecode.append(f"FUNC_DEF {name} {' '.join(params)}")
            i += 1
            while i < len(lines) and lines[i].startswith("    "):
                cmd = normalize_line(lines[i].strip())
                if cmd: bytecode.append(cmd)
                i += 1
            bytecode.append("END_FUNC")
            continue
        # if/else
        m = re.match(r"if (\w+) is (greater than|less than|equal to) (\w+):", lower)
        if m:
            var, op_text, val = m.group(1), m.group(2), m.group(3)
            ops = {"greater than":">", "less than":"<", "equal to":"=="}
            bytecode.append(f"IF {var} {ops[op_text]} {val}")
            i += 1
            while i < len(lines) and lines[i].startswith("    ") and not lines[i].strip().lower().startswith("else"):
                cmd = normalize_line(lines[i].strip())
                if cmd: bytecode.append(cmd)
                i += 1
            if i < len(lines) and lines[i].strip().lower().startswith("else"):
                bytecode.append("ELSE")
                i += 1
                while i < len(lines) and lines[i].startswith("    "):
                    cmd = normalize_line(lines[i].strip())
                    if cmd: bytecode.append(cmd)
                    i += 1
            bytecode.append("END_IF")
            continue
        # repeat
        m = re.match(r"repeat (\d+) times:", lower)
        if m:
            count = m.group(1)
            bytecode.append(f"REPEAT {count}")
            i += 1
            while i < len(lines) and lines[i].startswith("    "):
                cmd = normalize_line(lines[i].strip())
                if cmd: bytecode.append(cmd)
                i += 1
            bytecode.append("END_REPEAT")
            continue
        # normal line
        cmd = normalize_line(lower)
        if cmd:
            bytecode.append(cmd)
        i += 1
    with open(output_file, "w") as fw:
        for bc in bytecode:
            fw.write(bc + "\n")

def normalize_line(line):
    # variable
    m = re.match(r"(?:create a variable called|set) (\w+) (?:and set it to|to|as) (.+)", line)
    if m: return f"SET {m.group(1)} {m.group(2)}"
    # list
    m = re.match(r"create a list called (\w+) with values (.+)", line)
    if m:
        items = [x.strip() for x in m.group(2).split(",")]
        return "LIST " + m.group(1) + " " + " ".join(items)
    # dict
    m = re.match(r"create a dictionary called (\w+) with (.+)", line)
    if m:
        parts = [p.strip() for p in m.group(2).split("and")]
        kvs = []
        for part in parts:
            k,v = part.split("as")
            kvs.append(f"{k.strip()}:{v.strip()}")
        return "DICT " + m.group(1) + " " + ",".join(kvs)
    # add
    m = re.match(r"add (\w+) and (\w+) and store (?:the )?(?:result|outcome) in (\w+)", line)
    if m: return f"ADD {m.group(1)} {m.group(2)} {m.group(3)}"
    # concat
    m = re.match(r"concatenate (\w+) and (\w+) and store in (\w+)", line)
    if m: return f"CONCAT {m.group(1)} {m.group(2)} {m.group(3)}"
    # builtin length
    m = re.match(r"get the length of list (\w+) and store (?:it )?in (\w+)", line)
    if m: return f"BUILTIN LENGTH {m.group(1)} {m.group(2)}"
    # builtin sum
    m = re.match(r"get the sum of list (\w+) and store it in (\w+)", line)
    if m: return f"BUILTIN SUM {m.group(1)} {m.group(2)}"
    # index
    m = re.match(r"get item at index (\d+) from list (\w+) and store in (\w+)", line)
    if m: return f"INDEX {m.group(2)} {m.group(1)} {m.group(3)}"
    # get
    m = re.match(r"get (\w+) (\w+) and store it in (\w+)", line)
    if m: return f"GET {m.group(1)} {m.group(2)} {m.group(3)}"
    # print
    m = re.match(r"(?:print|show|display) "?([^\"]+)"?", line)
    if m: return f"PRINT {m.group(1)}"
    # read
    m = re.match(r"read file (\S+) and store lines in (\w+)", line)
    if m: return f"READ {m.group(1)} {m.group(2)}"
    # write
    m = re.match(r"write "?(.+?)"? to file (\S+)", line)
    if m: return f"WRITE {m.group(1)} {m.group(2)}"
    # api
    m = re.match(r"call openweather api with city as (\w+) and store .* in (\w+)", line)
    if m: return f"API openweather {m.group(1)} {m.group(2)}"
    return None
