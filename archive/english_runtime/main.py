from runtime import Interpreter

if __name__ == "__main__":
    program = [
        "Create a variable called count and set it to 0",
        "Repeat 5 times:",
        "    Add 1 to count",
        "    Print count"
    ]
    
    interpreter = Interpreter()
    interpreter.run(program)