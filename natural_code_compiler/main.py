from tokenizer import tokenize
from parser import parse
from generator import generate_code

def run_natural_language_code(nl_input):
    tokens = tokenize(nl_input)
    parsed = parse(tokens)
    python_code = generate_code(parsed)
    print("Generated Python Code:")
    print(python_code)
    exec(python_code)

if __name__ == "__main__":
    sample_input = [
        "Create a variable called x and set it to 10",
        "Create a variable called y and set it to 5",
        "Add x and y and store the result in z",
        "Print z"
    ]
    run_natural_language_code(sample_input)