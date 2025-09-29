from runtime import Interpreter

if __name__ == "__main__":
    program = [
        "Create a variable called x and set it to 5",
        "Ask the user to enter a number and store it in y",
        "If y is greater than x:",
        "    Print y",
        "Else:",
        "    Print x",
        "Define a function called greet:",
        "    Print Hello",
        "Call greet"
    ]
    
    interpreter = Interpreter()
    interpreter.run(program)