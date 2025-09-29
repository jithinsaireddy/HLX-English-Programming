from __future__ import annotations
from typing import Dict
from english_programming.src.compiler.ir import IRProgram, IRInstruction


def _is_number(token: str) -> bool:
    return token.replace('.', '', 1).isdigit()


def optimize_ir(ir: IRProgram) -> IRProgram:
    consts: Dict[str, float | int | str] = {}
    optimized: list[IRInstruction] = []

    # Constant folding for arithmetic
    for instr in ir.instructions:
        op = instr.op
        args = instr.args
        if op == 'SET' and len(args) >= 2:
            var, val = args[0], ' '.join(args[1:])
            if _is_number(val):
                consts[var] = float(val) if '.' in val else int(val)
            elif val.startswith('"') and val.endswith('"'):
                consts[var] = val[1:-1]
            optimized.append(instr)
            continue

        if op in {'ADD', 'SUB', 'MUL', 'DIV'} and len(args) == 3:
            a, b, r = args
            va = consts.get(a, a)
            vb = consts.get(b, b)
            if isinstance(va, (int, float)) and isinstance(vb, (int, float)):
                try:
                    if op == 'ADD': res = va + vb
                    elif op == 'SUB': res = va - vb
                    elif op == 'MUL': res = va * vb
                    else: res = va / vb
                    # Replace with SET r result
                    val_str = str(res)
                    optimized.append(IRInstruction(op='SET', args=[r, val_str]))
                    consts[r] = res
                    continue
                except Exception:
                    pass
        optimized.append(instr)

    # Be conservative: skip dead code elimination to preserve variables for debugging/inspection
    return IRProgram(instructions=optimized)


