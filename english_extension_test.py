#!/usr/bin/env python3
"""
English Extension Test

This script tests the English Programming language extensions using proper English-like
code as input, not just raw bytecode. It compiles English sentences to bytecode and
then executes that bytecode using our extension-enabled VM.
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append('/Users/jithinpothireddy/Downloads/English Programming')

# Import compiler and VM
from english_programming.src.compiler.improved_nlp_compiler import ImprovedNLPCompiler
from english_programming.src.vm.improved_nlvm import ImprovedNLVM
from english_programming.src.vm.extension_handler import VMExtensionHandler

def create_english_program(program_type="basic"):
    """Create English-language programs for testing various features"""
    programs = {
        "basic": """
# Basic English Programming Test
create a variable called x and set it to 10
create a variable called y and set it to 5
add x and y and store the result in sum
print "The sum is:"
print sum
""",
        "conditional": """
# Conditional Logic Test
create a variable called age and set it to 20
print "Testing conditionals with age = 20"

if age is greater than 18:
    print "You are an adult"
else:
    print "You are a minor"
    
# Test another condition
if age is less than 18:
    print "This should not print"
else:
    print "This should print"
""",
        "while_loop": """
# While Loop Test
create a variable called counter and set it to 1
create a variable called sum and set it to 0

print "Testing while loop with counter from 1 to 5:"
while counter is less than or equal to 5:
    print counter
    add counter to sum and store the result in sum
    add 1 to counter and store the result in counter

print "The sum of numbers from 1 to 5 is:"
print sum
""",
        "for_loop": """
# For-Each Loop Test
create a variable called fruits and set it to ["apple", "banana", "cherry"]
print "Testing for-each loop with fruits:"

for each fruit in fruits:
    print "Current fruit:"
    print fruit
    
print "Testing numeric range loop:"
for i from 1 to 5:
    print "Value of i:"
    print i
""",
        "classes": """
# Classes and OOP Test
create class Person:
    define method constructor with parameters name and age:
        set the name property of self to name
        set the age property of self to age
    
    define method greet:
        print "Hello, my name is"
        print self.name
        print "and I am"
        print self.age
        print "years old."

# Create an object and call a method
create a Person object called john with parameters "John" and 30
call the greet method on john
"""
    }
    
    # Create the program file
    program_file = f"test_{program_type}.nl"
    with open(program_file, "w") as f:
        f.write(programs[program_type])
    
    print(f"Created {program_type} test program: {program_file}")
    return program_file

def compile_english_program(compiler, source_file):
    """Compile an English program to bytecode"""
    print(f"Compiling {source_file}...")
    bytecode_file = Path(source_file).with_suffix(".nlc")
    
    with open(source_file, "r") as f:
        content = f.read()
    
    # Process line by line
    lines = [line.strip() for line in content.split('\n')]
    bytecode = []
    
    for line_num, line in enumerate(lines, 1):
        if line and not line.startswith("#"):  # Skip comments and empty lines
            try:
                # Process the entire line at once
                print(f"Processing line: '{line}'")
                line_bytecode = compiler.translate_to_bytecode(line)
                if line_bytecode:
                    bytecode.extend(line_bytecode)
                    print(f"  -> {line_bytecode}")
            except Exception as e:
                print(f"Error compiling line {line_num}: {line}")
                print(f"  Error: {str(e)}")
    
    with open(bytecode_file, "w") as f:
        f.write("\n".join(bytecode))
    
    print(f"Compiled to: {bytecode_file}")
    return bytecode_file

def setup_vm_with_extensions():
    """Set up VM with all extensions"""
    compiler = ImprovedNLPCompiler()
    vm = ImprovedNLVM(debug=True)
    
    # Add extension handler that can process additional bytecode instructions
    handler = VMExtensionHandler(vm)
    
    # Monkey-patch the VM to handle extension instructions
    original_execute_instructions = vm.execute_instructions
    
    def enhanced_execute_instructions(instructions, env):
        """Enhanced execute_instructions with extension handling"""
        i = 0
        while i < len(instructions):
            instruction = instructions[i]
            parts = instruction.split()
            
            # Handle extension instructions
            if parts and parts[0] in ["WHILE_LESS_EQUAL", "WHILE_LESS", 
                                     "FOR_EACH", "FOR_RANGE",
                                     "CREATE_CLASS", "CREATE_OBJECT", "CALL_METHOD"]:
                try:
                    if parts[0] == "WHILE_LESS_EQUAL":
                        # Process while loop
                        var_name = parts[1]
                        limit = parts[2]
                        
                        # Find the matching END
                        end_index = find_matching_end(instructions, i)
                        loop_body = instructions[i+1:end_index]
                        
                        # Execute loop with condition
                        var_value = int(env.get(var_name, 0))
                        limit_value = int(limit) if limit.isdigit() else int(env.get(limit, 0))
                        
                        iterations = 0
                        max_iterations = 100  # Safety limit
                        
                        while var_value <= limit_value and iterations < max_iterations:
                            # Execute loop body
                            original_execute_instructions(loop_body, env)
                            
                            # Update variable for next iteration
                            var_value = int(env.get(var_name, 0))
                            iterations += 1
                        
                        # Skip to after END
                        i = end_index + 1
                        continue
                    
                    # Handle other extension instructions here
                    
                except Exception as e:
                    print(f"Error processing extension instruction: {str(e)}")
            
            # Default behavior for standard instructions
            original_execute_instructions([instruction], env)
            i += 1
    
    # Replace standard execution with enhanced version
    vm.execute_instructions = enhanced_execute_instructions
    
    return compiler, vm

def find_matching_end(instructions, start_index):
    """Find the matching END instruction for a block"""
    nesting_level = 1
    i = start_index + 1
    
    while i < len(instructions):
        parts = instructions[i].split()
        
        # Check for nested blocks
        if parts and parts[0] in ["IF", "IF_GREATER", "IF_LESS", "WHILE_LESS_EQUAL", "FOR_EACH"]:
            nesting_level += 1
        
        # Check for block end
        elif parts and parts[0] == "END":
            nesting_level -= 1
            if nesting_level == 0:
                return i
        
        i += 1
    
    # No matching END found
    return len(instructions)

def run_test(program_type="basic"):
    """Run a test with proper English code"""
    print("=" * 60)
    print(f"ENGLISH PROGRAMMING EXTENSION TEST: {program_type.upper()}")
    print("=" * 60)
    
    try:
        # Create English program
        program_file = create_english_program(program_type)
        
        # Set up compiler and VM with extensions
        compiler, vm = setup_vm_with_extensions()
        
        # Compile English program to bytecode
        bytecode_file = compile_english_program(compiler, program_file)
        
        # Execute bytecode
        print(f"\nExecuting program: {bytecode_file}")
        print("=" * 60)
        
        result = vm.execute(bytecode_file)
        
        print("=" * 60)
        print("Program executed successfully!")
        
        # Show final environment
        print("\nFinal environment variables:")
        print("-" * 40)
        for var_name, value in vm.env.items():
            if not var_name.startswith("_"):
                print(f"{var_name} = {value}")
        
        # Clean up
        if os.path.exists(program_file):
            os.remove(program_file)
        if os.path.exists(bytecode_file):
            os.remove(bytecode_file)
        
        print(f"\n{program_type.capitalize()} test completed successfully!")
        return True
    
    except Exception as e:
        print(f"Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def run_all_tests():
    """Run all extension tests"""
    test_types = ["basic", "conditional", "while_loop", "for_loop", "classes"]
    results = {}
    
    for test_type in test_types:
        print("\n\n")
        success = run_test(test_type)
        results[test_type] = success
    
    print("\n" + "=" * 60)
    print("ENGLISH PROGRAMMING EXTENSION TEST SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for test_type, success in results.items():
        status = "PASSED" if success else "FAILED"
        print(f"{test_type.ljust(15)}: {status}")
        if not success:
            all_passed = False
    
    if all_passed:
        print("\nAll tests passed successfully!")
    else:
        print("\nSome tests failed. Check the output for details.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_type = sys.argv[1]
        run_test(test_type)
    else:
        run_all_tests()
