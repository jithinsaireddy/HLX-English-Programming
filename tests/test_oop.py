from english_programming.src.vm.improved_nlvm import ImprovedNLVM


def run(bytecodes):
    vm = ImprovedNLVM(debug=False)
    # write temp file
    import tempfile
    import os
    fd, path = tempfile.mkstemp(suffix='.nlc')
    try:
        with os.fdopen(fd, 'w') as f:
            for b in bytecodes:
                f.write(b + '\n')
        vm.execute(path)
        return vm.env
    finally:
        os.remove(path)


def test_oop_minimal():
    code = [
        'CLASS_START Person Object',
        'METHOD_START constructor name',
        'SET_PROPERTY self name name',
        'ENDMETHOD',
        'METHOD_START greet',
        'GET_PROPERTY self name who',
        'ENDMETHOD',
        'CLASS_END',
        'CREATE_OBJECT Person john "Alice"',
        'CALL_METHOD john greet',
    ]
    env = run(code)
    assert isinstance(env.get('john'), dict)


def test_oop_method_return_and_super():
    code = [
        'CLASS_START Animal Object',
        'METHOD_START speak',
        'RETURN "sound"',
        'ENDMETHOD',
        'CLASS_END',
        'CLASS_START Dog Animal',
        'METHOD_START constructor name',
        'SET_PROPERTY self name name',
        'ENDMETHOD',
        'METHOD_START speak',
        'CALL_SUPERR self speak result',
        'RETURN result',
        'ENDMETHOD',
        'CLASS_END',
        'CREATE_OBJECT Dog d "Rex"',
        'CALL_METHODR d speak out',
    ]
    env = run(code)
    assert env.get('out') == 'sound'

