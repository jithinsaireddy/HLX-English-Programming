from runtime import Interpreter

if __name__ == "__main__":
    program = [
        "Create a list called numbers with values 1, 2, 3, 4, 5",
        "For each item in numbers:",
        "    Print item",
        "Create a variable called count and set it to 0",
        "While count is less than 5:",
        "    Add 1 to count",
        "    Print count"
    ]
    
    interpreter = Interpreter()
    interpreter.run(program)