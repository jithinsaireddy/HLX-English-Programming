def execute_nlc(file_path):
    env = {}
    with open(file_path, "r") as f:
        instructions = [line.strip() for line in f.readlines() if line.strip()]

    for instr in instructions:
        parts = instr.split()
        cmd = parts[0]

        if cmd == "SET":
            var, val = parts[1], parse_value(parts[2])
            env[var] = val
        elif cmd == "ADD":
            x, y, res = parts[1], parts[2], parts[3]
            env[res] = env.get(x, 0) + env.get(y, 0)
        elif cmd == "PRINT":
            var = parts[1]
            print(env.get(var, f"{var} not defined"))

def parse_value(val):
    try:
        return int(val)
    except:
        try:
            return float(val)
        except:
            return val

if __name__ == "__main__":
    execute_nlc("program.nlc")