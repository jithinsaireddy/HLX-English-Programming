#!/usr/bin/env python3
"""
Enhanced Test Script for the English Programming Project
Tests the extended capabilities of the ImprovedNLPCompiler
"""
import sys
import os

# Add the project root to the path
engprg_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if engprg_path not in sys.path:
    sys.path.insert(0, engprg_path)

# Try to import our improved compiler first
try:
    from english_programming.src.compiler.improved_nlp_compiler import ImprovedNLPCompiler as Compiler
    print("Using ImprovedNLPCompiler with enhanced capabilities")
except ImportError:
    from english_programming.src.compiler.nlp_enhanced_compiler import NLPEnhancedCompiler as Compiler
    print("Using original NLPEnhancedCompiler (fallback)")

# Import the improved VM
try:
    from english_programming.src.vm.improved_nlvm import ImprovedNLVM as VM
    print("Using ImprovedNLVM for better operation handling")
except ImportError:
    from english_programming.src.vm.enhanced_nlvm import EnhancedNLVM as VM
    print("Using original EnhancedNLVM (fallback)")

# Define a comprehensive test program with various natural language patterns
test_program = """
# Test enhanced NLP capabilities

# Variable assignment
Create a variable total with value 100
Set result to 25
Print result

# String operations
Set name to "John Doe"
Set greeting to "Hello, "
Concatenate greeting and name to make full_greeting
Print full_greeting

# String literals in print statements
Print 'This is a direct string literal'

# Another way to print string literals
'This should also work as a print statement' should be printed

# Counter operations - different styles
Create a counter with initial value 1
Print counter
Increment counter by 2
Print counter
Add 3 to counter
Print counter
Increment the counter
Print counter

# Arithmetic operations
Set number1 to 10
Set number2 to 5
Add number1 and number2 to create sum_result
Print sum_result

Multiply number1 by number2 to get product_result
Print product_result

Subtract number2 from number1 to find difference
Print difference

Divide number1 by number2 to calculate quotient
Print quotient

# Conditional logic
Set age to 21
If age is greater than 18:
    Print 'You are an adult'
Else:
    Print 'You are a minor'
End if

# More complex variable assignment
Set final_message to "The total is: " + total
Print final_message
"""

def run_enhanced_tests():
    """Run tests on the enhanced NLP capabilities"""
    print("=== Testing Enhanced NLP Capabilities ===")
    print("\nInput Program:")
    print(test_program)
    
    # Write the test program to a temporary file
    with open("temp_enhanced_test.nl", "w") as f:
        f.write(test_program)
    
    # Compile and run the program
    compiler = Compiler()
    bytecode_file = compiler.compile("temp_enhanced_test.nl", "temp_enhanced_test.nlc")
    
    print("\nRunning the program:")
    vm = VM()
    output = vm.execute(bytecode_file)
    
    print("\nExecution Output:")
    print(output)
    
    print("\n=== Enhanced Test Complete ===")
    
    # Keep temporary files for debugging
    print("\nTemporary files retained for debugging:")
    print("  Source file: temp_enhanced_test.nl")
    print("  Bytecode file: temp_enhanced_test.nlc")

if __name__ == "__main__":
    run_enhanced_tests()
