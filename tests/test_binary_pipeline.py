from english_programming.bin.nlvm_bin import parse_module, run_module
from english_programming.bin.nlp_compiler_bin import compile_english_to_binary


def test_binary_end_to_end(tmp_path):
    lines = [
        "Define function makefive(a, b)",
        "Set a to 5",
        "Set b to 7",
        "End function",
        "Set x to 2",
        "Add x and 3 and store the result in y",
        "Print y",
        "Create a list called numbers with values 1, 2, 3",
        "Get item at index 1 from list numbers and store in second",
    ]
    out_file = tmp_path / "program.nlbc"
    compile_english_to_binary(lines, str(out_file))
    buf = out_file.read_bytes()
    ver_major, ver_minor, flags, consts, syms, code, funcs, classes = parse_module(buf)
    assert ver_major == 1
    env = run_module(consts, syms, code, funcs)
    assert env.get('y') == 5
    assert env.get('second') == 2


def test_binary_call_and_control_flow(tmp_path):
    lines = [
        "Define function add2(a, b)",
        "Add a and b and store the result in sum",
        "Print sum",
        "End function",
        "Set a to 10",
        "Set b to 20",
        # CALL not yet lowered from English; simulate by function in main through VM registry in run_module
        # We'll just ensure function compiled and registry can be used.
        "If a is less than 15 then print a",
        "While a is less than 12 do print a",
    ]
    out_file = tmp_path / "program2.nlbc"
    compile_english_to_binary(lines, str(out_file))
    buf = out_file.read_bytes()
    ver_major, ver_minor, flags, consts, syms, code, funcs, classes = parse_module(buf)
    env = run_module(consts, syms, code, funcs)
    # function exists
    func_names = [syms[n] for (n, _, _) in funcs]
    assert 'add2' in func_names

    # Now include a direct CALL lowering
    lines2 = [
        "Define function add2(a, b)",
        "Add a and b and store the result in sum",
        "Return sum",
        "End function",
        "Set p to 7",
        "Set q to 8",
        "Call function add2 with p, q and store in r",
    ]
    out2 = tmp_path / "program3.nlbc"
    compile_english_to_binary(lines2, str(out2))
    buf2 = out2.read_bytes()
    _, _, _, consts2, syms2, code2, funcs2, classes2 = parse_module(buf2)
    env2 = run_module(consts2, syms2, code2, funcs2, classes2)
    assert env2.get('r') == 15


def test_binary_arith_and_crud(tmp_path):
    f = tmp_path / 'f.txt'
    lines = [
        "Set a to 9",
        "Set b to 3",
        "Subtract a and 2 and store the result in s1",
        "Multiply b and 7 and store the result in s2",
        "Divide s2 by b and store the result in q",
        "Concatenate 'hi' and ' there' and store in g",
        "Length of g store in glen",
        f"Set path to {str(f)}",
        "Write file path with content 'hello'",
        "Append to file path content ' world'",
        "Read file path store in content",
        f"Import from url '{str(f)}' store in imported",
    ]
    out = tmp_path / 'arith.nlbc'
    compile_english_to_binary(lines, str(out))
    buf = out.read_bytes()
    _, _, _, consts, syms, code, funcs, classes = parse_module(buf)
    env = run_module(consts, syms, code, funcs, classes)


def test_binary_oop_and_exceptions(tmp_path):
    lines = [
        "Define class Person with fields: name",
        "Method greet(other)",
        "Concatenate 'Hello ' and other and store in msg",
        "Return msg",
        "End method",
        "End class",
        "Set who to 'world'",
        # Try/Catch pattern (synthetic): push msg, SETUP_CATCH, CALL, END_TRY
    ]
    out = tmp_path / 'oop.nlbc'
    compile_english_to_binary(lines, str(out))
    buf = out.read_bytes()
    _, _, _, consts, syms, code, funcs, classes = parse_module(buf)
    # ensure class exists
    class_names = [syms[c[0]] for c in classes]
    assert 'Person' in class_names

