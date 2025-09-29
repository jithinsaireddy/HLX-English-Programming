from english_programming.bin.nlp_compiler_bin import compile_english_to_binary
from english_programming.bin.nlvm_bin import parse_module, run_module


def test_schedule_and_run_tasks(tmp_path):
    lines = [
        "Set url to 'http://example.com'",
        "Async http get url await store in r1",
        # schedule two reads (they return futures) and run them
        "Async http get url await store in r2",
    ]
    out = tmp_path / 'sched.nlbc'
    compile_english_to_binary(lines, str(out))
    buf = out.read_bytes()
    _, _, _, consts, syms, code, funcs, classes = parse_module(buf)
    env = run_module(consts, syms, code, funcs, classes)
    assert env.get('r1') is not None
    assert env.get('r2') is not None


