from english_programming.bin.nlp_compiler_bin import compile_english_to_binary
from english_programming.bin.nlvm_bin import parse_module, run_module


def test_async_readfile(tmp_path):
    p = tmp_path / 'a.txt'
    p.write_text('hello')
    lines = [
        f"Set path to {str(p)}",
        "Async read file path await store in content",
    ]
    out = tmp_path / 'a.nlbc'
    compile_english_to_binary(lines, str(out))
    buf = out.read_bytes()
    _, _, _, consts, syms, code, funcs, classes = parse_module(buf)
    env = run_module(consts, syms, code, funcs, classes)
    assert env.get('content') == 'hello'


def test_async_httpget(tmp_path, monkeypatch):
    class DummyResp:
        def __init__(self, data): self._d = data
        def read(self): return self._d
        def __enter__(self): return self
        def __exit__(self, *a): return False

    def fake_urlopen(req):
        return DummyResp(b'OK')

    import urllib.request as _r
    monkeypatch.setattr(_r, 'urlopen', fake_urlopen)

    lines = [
        "Async http get 'http://example.com' await store in resp",
    ]
    out = tmp_path / 'h.nlbc'
    compile_english_to_binary(lines, str(out))
    buf = out.read_bytes()
    _, _, _, consts, syms, code, funcs, classes = parse_module(buf)
    env = run_module(consts, syms, code, funcs, classes)
    assert env.get('resp') == 'OK'


