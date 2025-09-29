from english_programming.bin.nlp_compiler_bin import compile_english_to_binary
from english_programming.bin.nlvm_bin import parse_module, run_module


def test_foreach_loop(tmp_path):
    lines = [
        "Create a list called numbers with values 1, 2, 3",
        "For each i in list numbers do Print i",
    ]
    out = tmp_path / 'for.nlbc'
    compile_english_to_binary(lines, str(out))
    consts, syms, code, funcs, classes = parse_module(out.read_bytes())[3:]
    env = run_module(consts, syms, code, funcs, classes)
    assert env.get('numbers') == [1,2,3]


def test_annotation_storage(tmp_path):
    # Manually emit annotation op: simulate annotations for function 'f'
    from english_programming.bin.nlbc_encoder import write_module_full
    consts = [(2, 'arg:int'), (2, 'ret:int')]
    syms = ['f']
    instrs = [('LOAD_CONST', 0), ('LOAD_CONST', 1), ('ANNOTATE_FUNC', 0, 2)]
    funcs = []
    classes = []
    out = tmp_path / 'ann.nlbc'
    write_module_full(str(out), consts, syms, instrs, funcs, classes)
    _, _, _, consts2, syms2, code2, funcs2, classes2 = parse_module(out.read_bytes())
    env = run_module(consts2, syms2, code2, funcs2, classes2)
    assert env.get('_annotations', {}).get('f') == ['arg:int', 'ret:int']


