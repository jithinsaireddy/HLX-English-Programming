import spacy
import re

def normalize_line(line):
    line_lower = line.lower()
    # variable assignment
    match = re.search(r"(?:create a variable called|set) (\w+) (?:and set it to|to|as) (.+)", line_lower)
    if match:
        return f"SET {match.group(1)} {match.group(2)}"
    # list creation
    match = re.search(r"create a list called (\w+) with values (.+)", line_lower)
    if match:
        items = [v.strip() for v in match.group(2).split(",")]
        return "LIST " + match.group(1) + " " + " ".join(items)
    # dict creation
    match = re.search(r"create a dictionary called (\w+) with (.+)", line_lower)
    if match:
        entries = [e.strip() for e in match.group(2).split("and")]
        kvs = []
        for entry in entries:
            parts = entry.split("as")
            if len(parts)==2:
                k = parts[0].strip()
                v = parts[1].strip()
                kvs.append(f"{k}:{v}")
        return "DICT " + match.group(1) + " " + ",".join(kvs)
    # addition
    match = re.search(r"add (\w+) and (\w+) and store (?:the )?(?:result|outcome) in (\w+)", line_lower)
    if match:
        return f"ADD {match.group(1)} {match.group(2)} {match.group(3)}"
    # print
    match = re.search(r"(?:print|show|display) "?([^\"]+)"?", line_lower)
    if match:
        return f"PRINT {match.group(1)}"
    # read file
    match = re.search(r"read file (\S+) and store lines in (\w+)", line_lower)
    if match:
        return f"READ {match.group(1)} {match.group(2)}"
    # write file
    match = re.search(r"write "?(.+?)"? to file (\S+)", line_lower)
    if match:
        return f"WRITE {match.group(1)} {match.group(2)}"
    # API call
    match = re.search(r"call (\w+) api with city as (\w+) and store .*? in (\w+)", line_lower)
    if match:
        return f"API {match.group(1)} {match.group(2)} {match.group(3)}"
    # repeat loop
    match = re.search(r"repeat (\d+) times:", line_lower)
    if match:
        return f"REPEAT {match.group(1)}"
    # if condition
    match = re.search(r"if (\w+) is (greater|less|equal) to (\w+):", line_lower)
    if match:
        op = {"greater":">","less":"<","equal":"=="}.get(match.group(2),"==")
        return f"IF {match.group(1)} {op} {match.group(3)}"
    # else
    if line_lower.strip()=="else:":
        return "ELSE"
    return None

def compile_nl_to_nlc(input_file, output_file):
    try:
        nlp = spacy.load("en_core_web_sm")
    except:
        print("Please install spaCy model: python -m spacy download en_core_web_sm")
        return
    with open(input_file) as f:
        lines = [l.strip() for l in f if l.strip()]
    bytecode = []
    for line in lines:
        cmd = normalize_line(line)
        if cmd:
            bytecode.append(cmd)
    with open(output_file,"w") as fw:
        for bc in bytecode:
            fw.write(bc+"\n")

if __name__=="__main__":
    compile_nl_to_nlc("program.nl","program.nlc")
