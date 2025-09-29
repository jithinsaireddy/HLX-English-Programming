import re

def parse_value(v):
    v = v.strip('"')
    if re.match(r'^\d+$', v): return int(v)
    try: return float(v)
    except: return v

def execute_nlc(file_path):
    env = {}
    funcs = {}
    # load bytecode
    with open(file_path) as f: lines = [l.strip() for l in f if l.strip()]
    # helper to execute block
    def run_block(block_env, block):
        i = 0
        ret = None
        while i < len(block):
            parts = block[i].split()
            cmd = parts[0]
            if cmd == "SET":
                block_env[parts[1]] = parse_value(parts[2])
            elif cmd == "LIST":
                block_env[parts[1]] = [parse_value(x) for x in parts[2:]]
            elif cmd == "DICT":
                d = {}
                for kv in parts[2].split(","):
                    k,v = kv.split(":")
                    d[k] = parse_value(v)
                block_env[parts[1]] = d
            elif cmd == "ADD":
                block_env[parts[3]] = block_env.get(parts[1],0)+block_env.get(parts[2],0)
            elif cmd == "CONCAT":
                block_env[parts[3]] = str(block_env.get(parts[1],''))+str(block_env.get(parts[2],''))
            elif cmd == "BUILTIN":
                op = parts[1]
                if op == "LENGTH":
                    block_env[parts[3]] = len(block_env.get(parts[2],[]))
                elif op == "SUM":
                    block_env[parts[3]] = sum(block_env.get(parts[2],[]))
            elif cmd == "INDEX":
                arr = block_env.get(parts[1],[])
                idx = int(parts[2])
                block_env[parts[3]] = arr[idx]
            elif cmd == "GET":
                d = block_env.get(parts[1],{})
                block_env[parts[3]] = d.get(parts[2])
            elif cmd == "PRINT":
                print(block_env.get(parts[1], f"{parts[1]} not defined"))
            elif cmd == "READ":
                fname,var = parts[1],parts[2]
                with open(fname) as fr: block_env[var] = fr.read().splitlines()
            elif cmd == "WRITE":
                msg,fname = parts[1],parts[2]
                with open(fname,"w") as fw: fw.write(msg)
            elif cmd == "API":
                service,city,var=parts[1],parts[2],parts[3]
                block_env[var] = f"{city} has 22°C"
            elif cmd == "FUNC_DEF":
                name = parts[1]; params = parts[2:]
                # gather block
                bl = []
                j=i+1
                while j < len(block) and block[j] != "END_FUNC":
                    bl.append(block[j]); j+=1
                funcs[name] = (params, bl)
                i = j
            elif cmd == "CALL":
                name = parts[1]; args = parts[2:-1]; res = parts[-1]
                if name in funcs:
                    params, bl = funcs[name]
                    local_env = dict(zip(params, [parse_value(a) for a in args]))
                    r = run_block(local_env, bl)
                    env[res] = r
            elif cmd == "RETURN":
                ret = block_env.get(parts[1])
                return ret
            elif cmd == "IF":
                var,op,val = parts[1],parts[2],parts[3]
                cond = {"==":block_env.get(var)==parse_value(val),
                        ">":block_env.get(var)>parse_value(val),
                        "<":block_env.get(var)<parse_value(val)}[op]
                if not cond:
                    # skip to ELSE or END_IF
                    k=i+1
                    while k < len(block) and block[k] not in ("ELSE","END_IF"): k+=1
                    i = k + (1 if block[k]=="ELSE" else 0)
            elif cmd == "ELSE":
                # skip to END_IF
                k=i+1
                while k < len(block) and block[k] != "END_IF": k+=1
                i = k
            elif cmd == "END_IF":
                pass
            elif cmd == "REPEAT":
                count = int(parts[1])
                # gather block
                bl=[]
                j=i+1
                while j < len(block) and block[j] != "END_REPEAT":
                    bl.append(block[j]); j+=1
                for _ in range(count):
                    run_block(block_env, bl)
                i = j
            elif cmd == "END_REPEAT":
                pass
            i+=1
        return ret

    # load top-level block
    result = run_block(env, lines)
    return result

if __name__ == "__main__":
    execute_nlc("program.nlc")
