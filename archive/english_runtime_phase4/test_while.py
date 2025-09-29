from runtime import Interpreter

# Create a test program specifically for the while loop
test_program = [
    "Create a variable called count and set it to 0",
    "While count is less than 5:",
    "    Add 1 to count",
    "    Print count"
]

# Initialize and run the interpreter
interpreter = Interpreter()
print("Starting test program execution...")
interpreter.run(test_program)
print("Test program execution completed.")
