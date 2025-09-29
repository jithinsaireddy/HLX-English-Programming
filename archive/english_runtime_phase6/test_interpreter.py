from runtime import Interpreter

def test_english_runtime():
    print("==== Testing English Runtime Phase 6 ====")
    
    # Initialize the interpreter
    interpreter = Interpreter()
    
    # Define test commands
    test_commands = [
        "Create a variable called counter and set it to 10",
        "Create a variable called name and set it to Alice",
        "Create a list called numbers with values 5, 10, 15, 20",
        "Add counter and 5 and store the result in sum",
        "Print counter",
        "Print name",
        "Print numbers",
        "Print sum"
    ]
    
    # Execute each command and show the results
    print("\n\n=== Test Results ===")
    for i, cmd in enumerate(test_commands):
        print(f"\nCommand {i+1}: {cmd}")
        try:
            # First run the command
            interpreter.run([cmd])
            
            # If it's a print command, the output is already shown
            # Otherwise show the current state of related variables
            if not cmd.lower().startswith("print"):
                parts = cmd.lower().split()
                if "called" in parts:
                    var_name = parts[parts.index("called") + 1]
                    if var_name in interpreter.env:
                        print(f"Variable '{var_name}' = {interpreter.env[var_name]}")
                if "result in" in cmd.lower():
                    result_var = parts[parts.index("in") + 1]
                    if result_var in interpreter.env:
                        print(f"Result '{result_var}' = {interpreter.env[result_var]}")
        except Exception as e:
            print(f"Error: {str(e)}")
    
    # Test error handling
    print("\n=== Error Handling Test ===")
    try:
        interpreter.run(["Print undefined_variable"])
    except Exception as e:
        print(f"Error handling working as expected: {str(e)}")

if __name__ == "__main__":
    test_english_runtime()
