import os
import sys
from pathlib import Path


def _ensure_src_on_path():
    current_file = Path(__file__).resolve()
    src_dir = current_file.parents[2]
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))


_ensure_src_on_path()

from compiler.improved_nlp_compiler import ImprovedNLPCompiler  # noqa: E402
from vm.improved_nlvm import ImprovedNLVM  # noqa: E402
from extensions.extension_loader import ExtensionLoader  # noqa: E402


def execute_instructions(vm: ImprovedNLVM, instructions):
    temp_file = Path(".cli_temp_bytecode.nlc")
    try:
        with open(temp_file, "w") as f:
            for instr in instructions:
                f.write(instr + "\n")
        vm.execute(str(temp_file))
    finally:
        if temp_file.exists():
            try:
                temp_file.unlink()
            except OSError:
                pass


def main():
    print("Welcome to the English Programming CLI. Type 'exit' to quit.")
    compiler = ImprovedNLPCompiler()
    vm = ImprovedNLVM(debug=False)
    try:
        extensions = ExtensionLoader(compiler, vm)
        extensions.load_all_extensions()
    except Exception:
        pass

    while True:
        try:
            line = input(">> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("")
            break

        if not line:
            continue
        if line.lower() in {"exit", "quit"}:
            break

        try:
            instructions = compiler.translate_to_bytecode([line])
            if instructions:
                execute_instructions(vm, instructions)
        except Exception as e:
            print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()