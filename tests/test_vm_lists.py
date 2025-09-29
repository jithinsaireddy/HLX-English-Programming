from pathlib import Path
from english_programming.src.compiler.improved_nlp_compiler import ImprovedNLPCompiler
from english_programming.src.vm.improved_nlvm import ImprovedNLVM


def run_lines(lines):
    comp = ImprovedNLPCompiler()
    vm = ImprovedNLVM()
    bc = Path(".tmp_vm.nlc")
    try:
        bytecode = comp.translate_to_bytecode(lines)
        with open(bc, "w") as f:
            for ln in bytecode:
                f.write(ln + "\n")
        vm.execute(str(bc))
    finally:
        try:
            bc.unlink()
        except Exception:
            pass
    return vm.env


def test_list_pop_and_length():
    lines = [
        "create a list called items with values 1, 2, 3",
        "length of items store in n",
        "pop from list items store in last",
    ]
    env = run_lines(lines)
    assert env.get("n") == 3
    assert env.get("last") == 3
    assert env.get("items") == [1, 2]




