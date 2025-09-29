import re

def compile_nl_to_nlc(input_file, output_file):
    with open(input_file, "r") as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]

    bytecode = []
    for line in lines:
        line = line.lower()
        if line.startswith("create a variable called"):
            m = re.search(r"create a variable called (.+?) and set it to (.+)", line)
            if m:
                bytecode.append(f"SET {m.group(1).strip()} {m.group(2).strip()}")
        elif line.startswith("add"):
            m = re.search(r"add (.+?) and (.+?) and store the result in (.+)", line)
            if m:
                bytecode.append(f"ADD {m.group(1).strip()} {m.group(2).strip()} {m.group(3).strip()}")
        elif line.startswith("print"):
            var = line.replace("print", "").strip()
            bytecode.append(f"PRINT {var}")

    with open(output_file, "w") as f:
        for code in bytecode:
            f.write(code + "\n")

if __name__ == "__main__":
    compile_nl_to_nlc("program.nl", "program.nlc")