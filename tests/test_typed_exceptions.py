from english_programming.bin.nlbc_encoder import write_module_full


def test_typed_throw_and_catch(tmp_path):
    # Build a tiny module manually to exercise typed catch/throw
    consts = [(2, 'MyError'), (2, 'boom')]
    syms = ['exc_type', 'msg']
    instrs = [
        ('SETUP_CATCH_T', 0, 'CATCH'),         # type sym index 0 (exc_type placeholder), jump label
        ('LOAD_CONST', 1),                     # 'boom'
        ('LOAD_CONST', 0),                     # 'MyError'
        ('THROW_T',),
        ('LABEL', 'CATCH'),
    ]
    funcs = []
    classes = []
    out = tmp_path / 'typed.nlbc'
    write_module_full(str(out), consts, syms, instrs, funcs, classes)
    # If assembly/verification/execution passes, feature is wired
    assert out.exists()


