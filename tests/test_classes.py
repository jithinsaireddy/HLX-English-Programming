import os, tempfile
from english_programming.bin.nlp_compiler_bin import compile_english_to_binary
from english_programming.bin.nlvm_bin import parse_module, run_module


def run_epl(lines):
    with tempfile.NamedTemporaryFile(suffix='.nlbc', delete=False) as tf:
        out = tf.name
    try:
        compile_english_to_binary(lines, out)
        data = open(out, 'rb').read()
        ver_major, ver_minor, flags, consts, syms, code, funcs, classes = parse_module(data)
        env = run_module(consts, syms, code, funcs, classes)
        return env
    finally:
        try:
            os.remove(out)
        except Exception:
            pass


def test_class_basic_field_and_method():
    env = run_epl([
        'Define class Counter with fields: value',
        'Method inc(n)',
        '  set self.value to n',
        '  return self.value',
        'End method',
        'End class',
        'new Counter store in c',
        'call method c.inc(5) store in ret',
        'get c.value store in v'
    ])
    assert env.get('v') == 5
    assert env.get('ret') == 5


def test_inheritance_and_override():
    env = run_epl([
        'Define class Animal with fields: name',
        'Method speak()',
        "  return '...'",
        'End method',
        'End class',
        'Define class Dog extends Animal',
        'Method speak()',
        "  return 'woof'",
        'End method',
        'End class',
        'new Dog store in d',
        "set d.name to 'Rex'",
        'call method d.speak() store in s'
    ])
    assert env.get('s') == 'woof'
    assert env.get('d', None) is None  # object lives only in VM env frames; public vars captured separately


def test_constructor_with_args():
    env = run_epl([
        'Define class Acc with fields: value',
        'Method __init__(v)',
        '  set self.value to v',
        'End method',
        'End class',
        'new Acc with args 42 store in a',
        'get a.value store in out'
    ])
    assert env.get('out') == 42


def test_polymorphism_dispatch():
    env = run_epl([
        'Define class Animal',
        'Method speak()',
        "  return '...'",
        'End method',
        'End class',
        'Define class Cat extends Animal',
        'Method speak()',
        "  return 'meow'",
        'End method',
        'End class',
        'new Animal store in a',
        'new Cat store in c',
        'call method a.speak() store in sa',
        'call method c.speak() store in sc'
    ])
    assert env.get('sa') == '...'
    assert env.get('sc') == 'meow'
