import re

def parse_value(v):
    v=v.strip('\"')
    if v.isdigit(): return int(v)
    try: return float(v)
    except: return v

def execute_nlc(file_path):
    env = {}
    with open(file_path) as f:
        lines = [l.strip() for l in f if l.strip()]
    i=0
    while i < len(lines):
        parts = lines[i].split()
        cmd = parts[0]
        if cmd=="SET":
            env[parts[1]] = parse_value(parts[2])
        elif cmd=="LIST":
            env[parts[1]] = [parse_value(x) for x in parts[2:]]
        elif cmd=="DICT":
            d={}
            for kv in parts[2].split(","):
                k,v=kv.split(":")
                d[k]=parse_value(v)
            env[parts[1]] = d
        elif cmd=="ADD":
            env[parts[3]] = env.get(parts[1],0)+env.get(parts[2],0)
        elif cmd=="PRINT":
            print(env.get(parts[1], f"{parts[1]} not defined"))
        elif cmd=="READ":
            fname, var = parts[1], parts[2]
            with open(fname) as fr:
                env[var] = fr.read().splitlines()
        elif cmd=="WRITE":
            msg, fname = parts[1], parts[2]
            with open(fname,"w") as fw:
                fw.write(msg)
        elif cmd=="API":
            api, city, var = parts[1], parts[2], parts[3]
            env[var]=f"{city.title()} has 22C"
        elif cmd=="REPEAT":
            count=int(parts[1])
            block = []
            i+=1
            while i<len(lines) and lines[i]!="$END":
                block.append(lines[i])
                i+=1
            for _ in range(count):
                for b in block:
                    parts2=b.split()
                    if parts2[0]=="PRINT":
                        print(env.get(parts2[1], ...))
        elif cmd=="IF":
            var, op, val = parts[1], parts[2], parts[3]
            cond = {"==":env.get(var)==parse_value(val),
                    ">":env.get(var)>parse_value(val),
                    "<":env.get(var)<parse_value(val)}.get(op,False)
            if not cond:
                # skip to ELSE or $END
                depth=0
                i+=1
                while i<len(lines):
                    if lines[i]=="ELSE":
                        break
                    i+=1
        elif cmd=="ELSE":
            pass
        i+=1

if __name__=="__main__":
    execute_nlc("program.nlc")
