def execute_nlc(file_path):
    env = {}
    with open(file_path, "r") as f:
        instructions = [line.strip() for line in f.readlines() if line.strip()]

    for instr in instructions:
        parts = instr.split()
        cmd = parts[0]
        if cmd == "SET":
            env[parts[1]] = parse_value(parts[2])
        elif cmd == "ADD":
            env[parts[3]] = env.get(parts[1], 0) + env.get(parts[2], 0)
        elif cmd == "PRINT":
            print(env.get(parts[1], f"{parts[1]} not defined"))

def parse_value(val):
    try: return int(val)
    except: return val

if __name__ == "__main__":
    execute_nlc("program_nlp.nlc")