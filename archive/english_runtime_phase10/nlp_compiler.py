import spacy
import re

def normalize_line(line):
    line = line.lower()
    if "create a variable" in line or "set" in line:
        match = re.search(r"(?:create a variable|set) (.+?) (?:to|as) (.+)", line)
        if match:
            return f"SET {match.group(1).strip()} {match.group(2).strip()}"
    elif "add" in line:
        match = re.search(r"add (.+?) and (.+?)(?:,| and)? store (?:the )?(?:result|outcome) in (.+)", line)
        if match:
            return f"ADD {match.group(1).strip()} {match.group(2).strip()} {match.group(3).strip()}"
    elif "print" in line or "show" in line or "display" in line:
        match = re.search(r"(?:print|show|display) (.+?)[\?\.]?", line)
        if match:
            return f"PRINT {match.group(1).strip()}"
    return None

def compile_nlp_to_nlc(input_file, output_file):
    nlp = spacy.load("en_core_web_sm")
    with open(input_file, "r") as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]

    bytecode = []
    for line in lines:
        doc = nlp(line)
        norm = normalize_line(line)
        if norm:
            bytecode.append(norm)

    with open(output_file, "w") as f:
        for code in bytecode:
            f.write(code + "\n")

if __name__ == "__main__":
    compile_nlp_to_nlc("program_nlp.nl", "program_nlp.nlc")