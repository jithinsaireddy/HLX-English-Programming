# English Programming Language

An innovative programming language that allows you to write code in natural English.

## Overview

English Programming translates English natural language into executable code. This project consists of two main components:

1. **Compiler**: Converts English text into bytecode instructions
2. **Virtual Machine (VM)**: Executes the bytecode instructions

## Architecture

The system pipeline works as follows:

```
English Text → NLP Compiler → Bytecode → NLVM → Program Execution
```

### Key Components

- **Improved NLP Compiler**: Uses NLP (Natural Language Processing) with spaCy to understand and translate English sentences into bytecode instructions
- **Improved NLVM**: A virtual machine that executes the bytecode instructions

## Features

English Programming supports a wide range of programming features:

- **Variables**: Create and manipulate variables with different data types
- **Arithmetic**: Perform basic arithmetic operations (addition, etc.)
- **Strings**: Create and manipulate text with string concatenation
- **Data Structures**: Use lists and dictionaries
- **Functions**: Define functions with parameters and return values
- **Conditional Logic**: Use if/else statements for decision making
- **Built-in Functions**: Access built-in utilities like length and sum

## Usage

### Running a Program

```bash
# Compile an English program to bytecode
python english_programming/src/compiler/improved_nlp_compiler_fixed.py your_program.nl

# Execute the compiled bytecode
python english_programming/src/vm/improved_nlvm_fixed.py your_program.nlc
```

### Using the Integrated Test Runner

The integrated test runner handles both compilation and execution:

```bash
python integrated_test_runner.py your_program.nl
```

## Example Programs

### Basic Variables and Arithmetic

```
create a variable called x and set it to 10
create a variable called y and set it to 5
add x and y and store the result in sum
print sum
```

### Strings and Concatenation

```
create a variable called first_name and set it to "John"
create a variable called last_name and set it to "Doe"
concatenate first_name and last_name and store it in full_name
print full_name
```

### Functions

```
define a function called add_numbers with inputs a and b:
    add a and b and store the result in sum
    return sum

call add_numbers with values 7 and 3 and store result in function_result
print function_result
```

### Conditional Logic

```
create a variable called age and set it to 25
if age is greater than 18:
    set status to "Adult"
else:
    set status to "Minor"
print status
```

## Releases

See CHANGELOG.md and docs/ (when present) for release notes and examples.

## Extensions and Future Work

The English Programming language can be extended with:

1. **Loops**: For repetitive tasks
2. **More Data Structures**: Arrays, sets, etc.
3. **Error Handling**: Try/catch mechanisms
4. **Object-Oriented Features**: Classes and objects
5. **Module System**: Import code from other files

## Dependencies

- Python 3.6+
- spaCy (with en_core_web_sm model)

## Quick Start

- Create and activate a virtualenv:
```bash
python3 -m venv .venv && source .venv/bin/activate
```

- Install (with optional NLP extras):
```bash
pip install -e .[nlp]
```

- Run an English program:
```bash
english path/to/your_program.nl
```

- Launch CLI:
```bash
python english_programming/src/interfaces/cli/cli_app.py
```

- Launch Web UI:
```bash
python english_programming/src/interfaces/web/web_app.py
```

## Standard Library
- Strings: STRUPPER/STRLOWER/STRTRIM via natural phrases (e.g., "make the name uppercase and store it in upper_name").
- HTTP: "http get from URL and store result in page".
- Files: write/read/append using natural phrasing.

See `english_programming/examples/stdlib_demo.nl`.

## NLP Enhancements
## Tutorials (Start Here)

1) Hello, Variables and Math
```
create a variable called x and set it to 2
create a variable called y and set it to 3
add x and y and store the result in sum
print sum
```

2) Strings and HTTP
```
create a variable called name and set it to " world "
trim name and store it in cleaned
make the cleaned uppercase and store it in shout
print shout
http get from "https://example.com" and store result in page
get the length of page and store it in size
print size
```

3) JSON and Regex
```
create a variable called js and set it to "{\"name\":\"Alice\"}"
parse json js and store result in obj
get json obj key "name" and store result in nm
check if nm matches \\w+ and store result in ok
print ok
```

4) OOP
```
CLASS_START Person Object
METHOD_START constructor name
SET_PROPERTY self name name
ENDMETHOD
METHOD_START greet
GET_PROPERTY self name who
RETURN who
ENDMETHOD
CLASS_END
CREATE_OBJECT Person john "Alice"
CALL_METHODR john greet out
print out
```

See `english_programming/examples` for more.
If spaCy is installed (`pip install -e .[nlp]`), parsing becomes more forgiving and expressive. The CLI auto-detects spaCy and enables NLP by default; disable via `--no-nlp`.
# HLX-English-Programming
