import os
from pathlib import Path

from english_programming.src.compiler.improved_nlp_compiler import ImprovedNLPCompiler
from english_programming.src.vm.improved_nlvm import ImprovedNLVM


def compile_and_run(lines):
    tmp_src = Path(".tmp_test.nl")
    tmp_bc = Path(".tmp_test.nlc")
    try:
        tmp_src.write_text("\n".join(lines))
        compiler = ImprovedNLPCompiler()
        compiler.compile(str(tmp_src), str(tmp_bc))
        vm = ImprovedNLVM(debug=False)
        vm.execute(str(tmp_bc))
        return vm.env
    finally:
        if tmp_src.exists():
            tmp_src.unlink()
        if tmp_bc.exists():
            tmp_bc.unlink()


def test_addition_and_print():
    env = compile_and_run([
        'create a variable called x and set it to 2',
        'create a variable called y and set it to 3',
        'add x and y and store the result in sum',
        'print sum',
    ])
    assert env.get('x') == 2
    assert env.get('y') == 3
    assert env.get('sum') == 5


def test_concat_and_if_else():
    env = compile_and_run([
        'create a variable called first_name and set it to "Alice"',
        'create a variable called last_name and set it to "Smith"',
        'concatenate first_name and last_name and store it in full_name',
        'create a variable called age and set it to 21',
        'if age is greater than 18:',
        '    set status to "Adult"',
        'else:',
        '    set status to "Minor"',
        'print status',
    ])
    assert env.get('full_name') == 'AliceSmith' or env.get('full_name') == 'alicesmith'
    assert env.get('status') == 'Adult'


def test_stdlib_string_ops():
    env = compile_and_run([
        'create a variable called name and set it to " alice "',
        'trim name and store it in cleaned',
        'make the cleaned uppercase and store it in uppered',
        'print uppered',
    ])
    assert env.get('cleaned') == ' alice '.strip()
    assert env.get('uppered') == 'ALICE'


def test_file_append_and_read(tmp_path):
    p = tmp_path / 'file.txt'
    env = compile_and_run([
        f'create a variable called fname and set it to "{p}"',
        'write "hello" to file fname',
        'append " world" to fname',
        'read file fname and store contents in content',
    ])
    assert env.get('content') == 'hello world'


def test_arithmetic_edges():
    env = compile_and_run([
        'create a variable called a and set it to 10',
        'create a variable called b and set it to 0',
        'divide a by b and store the result in q',
        'multiply a by 3 and store the result in m',
        'subtract 5 from m and store the result in d',
    ])
    assert env.get('m') == 30
    assert env.get('d') == 25
    # Div by zero returns None in current VM
    assert env.get('q') is None


def test_json_and_regex():
    env = compile_and_run([
        'create a variable called js and set it to "{\"name\":\"Alice\",\"age\":30}"',
        'parse json js and store result in obj',
        'get json obj key "name" and store result in nm',
        'stringify json obj and store result in out',
        'check if nm matches \\w+ and store result in is_word',
        'capture group 0 from nm with \\w+ and store result in cap',
    ])
    assert env.get('nm') == 'Alice'
    assert 'Alice' in env.get('out', '')
    assert env.get('is_word') is True
    assert env.get('cap') == 'Alice'


def test_now_and_headers():
    env = compile_and_run([
        'get current time and store it in now',
        'set http header X-Test to value',
    ])
    assert isinstance(env.get('now'), str)
