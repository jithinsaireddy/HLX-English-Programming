from runtime import Interpreter

def test_combined_runtime():
    """Test script for the combined English Runtime implementation"""
    print("=== Testing Combined English Runtime ===\n")
    
    # Initialize the interpreter
    interpreter = Interpreter()
    
    # Define a comprehensive test program that uses features from both phases
    test_program = [
        # Basic variable creation and operations (Phase 6 features)
        "Create a variable called counter and set it to 10",
        "Create a variable called name and set it to Alice",
        "Add counter and 5 and store the result in sum",
        
        # List operations (Phase 6 features)
        "Create a list called numbers with values 5, 10, 15, 20",
        
        # Dictionary creation (Phase 5 features)
        "Create a dictionary called user with name as Bob and age as 25",
        
        # Function definition and calling (Phase 5 features)
        "Define a function called multiply with inputs a and b:",
        "    Add a and b and store the result in result",
        "    Return result",
        "Call multiply with values 7 and 8 and store result in product",
        
        # Printing values
        "Print counter",
        "Print name",
        "Print sum",
        "Print numbers",
        "Print user.name",
        "Print user.age",
        "Print product"
    ]
    
    # Execute the program
    print("Executing test program...\n")
    interpreter.run(test_program)
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_combined_runtime()
