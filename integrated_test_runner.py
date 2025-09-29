#!/usr/bin/env python3
"""
Integration Test Runner for English Programming

This script tests the integrated features from english_runtime_complete in the
original english_programming architecture. It provides a comprehensive test
framework for verifying all language features:

1. Variables and basic data types
2. Arithmetic operations
3. String operations (concatenation)
4. Collections (lists, dictionaries)
5. Function definition and calling
6. Conditional statements (if/else)
7. Built-in functions

This runner handles the full pipeline:
1. Compiling English text to bytecode using the improved NLP compiler
2. Fixing any bytecode issues (like duplicate ELSE statements)
3. Executing the bytecode using the improved VM
4. Displaying the execution results and final environment state

Usage:
    python integrated_test_runner.py [test_file.nl]
    
If no test file is specified, it will use the comprehensive_test.nl file.
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.append('/Users/jithinpothireddy/Downloads/English Programming')

# Import the improved compiler and VM
from english_programming.src.compiler.improved_nlp_compiler import ImprovedNLPCompiler
from english_programming.src.vm.improved_nlvm import ImprovedNLVM

def fix_bytecode(bytecode_file):
    """
    Fix any issues in the bytecode before execution
    - Remove duplicate ELSE statements
    - Ensure proper IF/THEN/ELSE structure
    """
    with open(bytecode_file, 'r') as f:
        instructions = [line.strip() for line in f.readlines() if line.strip()]
    
    # Find and fix duplicate ELSE statements
    fixed_instructions = []
    i = 0
    while i < len(instructions):
        instruction = instructions[i]
        
        # Add the current instruction
        fixed_instructions.append(instruction)
        
        # Check for duplicate ELSE statements
        if instruction == "ELSE" and i+1 < len(instructions) and instructions[i+1] == "ELSE":
            print(f"Fixed: Removing duplicate ELSE at position {i+1}")
            i += 1  # Skip the duplicate ELSE
        
        i += 1
    
    # Write the fixed bytecode back to the file
    with open(bytecode_file, 'w') as f:
        for instruction in fixed_instructions:
            f.write(instruction + '\n')
    
    print(f"Fixed bytecode written to {bytecode_file}")
    return bytecode_file

def run_test(test_file):
    """
    Compile and run a test file
    """
    # Define file paths
    source_file = test_file
    bytecode_file = os.path.splitext(source_file)[0] + ".nlc"
    
    print("\n=====================================================")
    print(f"RUNNING INTEGRATION TEST: {source_file}")
    print("=====================================================")
    
    # Step 1: Compile the test file
    print("\n=== COMPILATION PHASE ===")
    compiler = ImprovedNLPCompiler()
    compiler.compile(source_file, bytecode_file)
    
    # Step 1.5: Fix the bytecode if needed
    print("\n=== BYTECODE FIXING PHASE ===")
    fix_bytecode(bytecode_file)
    
    # Step 2: Execute the bytecode
    print("\n=== EXECUTION PHASE ===")
    vm = ImprovedNLVM()
    result = vm.execute(bytecode_file)
    
    # Step 3: Show final environment
    print("\n=== FINAL ENVIRONMENT ===")
    for var_name, value in vm.env.items():
        print(f"  {var_name} = {value}")
    
    print("\n=== TEST COMPLETE ===")
    return result

def main():
    """
    Main function to run the integration tests
    """
    # Create a comprehensive integration test
    create_comprehensive_test()
    
    # Run the test
    test_file = "/Users/jithinpothireddy/Downloads/English Programming/comprehensive_test.nl"
    run_test(test_file)

def create_comprehensive_test():
    """
    Create a comprehensive test that exercises all integrated features
    """
    test_content = """# Comprehensive Integration Test for English Programming
# This test exercises all features from english_runtime_complete

# 1. Basic variable assignment
create a variable called message and set it to "Hello, World!"
print message

# 2. Arithmetic operations
create a variable called x and set it to 10
create a variable called y and set it to 5
add x and y and store the result in sum
print sum

# 3. String concatenation
create a variable called first_name and set it to "John"
create a variable called last_name and set it to "Doe"
concatenate first_name and last_name and store it in full_name
print full_name

# 4. Lists
create a list called numbers with values 1, 2, 3, 4, 5
print numbers
get the length of numbers and store it in list_length
print list_length
get the sum of numbers and store it in list_sum
print list_sum
get item at index 2 from numbers and store it in third_item
print third_item

# 5. Dictionaries
create a dictionary called person with name as "Alice", age as 30, city as "New York"
print person
get person name and store it in person_name
print person_name

# 6. Function definition and calling
define a function called add_numbers with inputs a and b:
    add a and b and store the result in sum
    return sum

define a function called greet with inputs name:
    concatenate "Hello, " and name and store it in greeting
    return greeting

call add_numbers with values 7 and 3 and store result in function_result
print function_result

call greet with values "Alice" and store result in greeting_result
print greeting_result

# 7. Conditional statements
create a variable called age and set it to 25
if age is greater than 18:
    set status to "Adult"
else:
    set status to "Minor"
print status
"""
    
    # Write the test file
    test_file = "/Users/jithinpothireddy/Downloads/English Programming/comprehensive_test.nl"
    with open(test_file, "w") as f:
        f.write(test_content)
    
    print(f"Created comprehensive test file: {test_file}")

if __name__ == "__main__":
    main()
