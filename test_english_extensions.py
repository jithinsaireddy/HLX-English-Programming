#!/usr/bin/env python3
"""
Comprehensive Test Script for English Programming Extensions

This script tests all the enhanced features added to the English Programming language:
- Advanced control flow (while loops, for loops, else-if)
- OOP features (classes, objects, methods, inheritance)
- Module system

The test creates a complete English program using all these features and
executes it using the extended VM.
"""

import os
import sys
from pathlib import Path

# Add the project root to the path
sys.path.append('/Users/jithinpothireddy/Downloads/English Programming')

# Import the core components
from english_programming.src.compiler.improved_nlp_compiler import ImprovedNLPCompiler
from english_programming.src.vm.improved_nlvm import ImprovedNLVM
from english_programming.src.vm.extension_handler import VMExtensionHandler

# Import the extension system
from english_programming.src.extensions.control_flow.advanced_loops import AdvancedControlFlowExtension
from english_programming.src.extensions.module_system.module_loader import ModuleSystemExtension
from english_programming.src.extensions.oop.class_system import OOPExtension

def create_test_program():
    """Create a comprehensive test program in English"""
    program = """
# Comprehensive English Programming Extensions Test

# Variable initialization
create a variable called counter and set it to 1
create a variable called sum and set it to 0

# While loop demonstration
print "Testing while loop:"
while counter is less than 6:
    print "Counter is"
    print counter
    add counter to sum and store the result in sum
    add 1 to counter and store the result in counter

print "Sum of numbers 1 to 5:"
print sum

# For loop demonstration
print "Testing for-each loop:"
create a variable called fruits and set it to ["apple", "banana", "cherry"]
for each fruit in fruits:
    print "Current fruit:"
    print fruit
    
# Numeric range loop
print "Testing numeric range loop:"
for i from 1 to 3:
    print "Value of i:"
    print i

# If/else-if demonstration
create a variable called score and set it to 85
print "Testing if/else-if with score = 85:"

if score is greater than 90:
    print "Grade: A"
else if score is greater than 80:
    print "Grade: B"
else if score is greater than 70:
    print "Grade: C"
else:
    print "Grade: D"

# Class definition
create class called Person:
    define method constructor with inputs name and age:
        set the name property of self to name
        set the age property of self to age
    
    define method greet:
        print "Hello, my name is"
        print self.name
        print "and I am"
        print self.age
        print "years old."

# Inheritance
create class called Student that extends Person:
    define method constructor with inputs name, age, and major:
        call constructor of Person with inputs name and age
        set the major property of self to major
        
    define method study:
        print "I am studying"
        print self.major

# Object creation and method call
print "Testing OOP features:"
create Person object called john with inputs "John Doe" and 30
call greet on john

create Student object called mary with inputs "Mary Smith", 20, and "Computer Science"
call greet on mary
call study on mary

# Testing complete
print "All tests completed successfully!"
"""
    
    # Write program to file
    test_file = Path("complete_test.nl")
    with open(test_file, "w") as f:
        f.write(program)
    
    return test_file

def setup_extended_vm():
    """Set up the VM with extensions"""
    # Create compiler and VM
    compiler = ImprovedNLPCompiler()
    vm = ImprovedNLVM(debug=True)
    
    # Set up extension handler
    handler = VMExtensionHandler(vm)
    
    # Load all extensions
    control_flow = AdvancedControlFlowExtension(compiler, vm)
    module_system = ModuleSystemExtension(compiler, vm)
    oop = OOPExtension(compiler, vm)
    
    return compiler, vm, handler

def compile_english_program(compiler, source_file):
    """Compile an English program to bytecode"""
    print(f"Compiling {source_file}...")
    bytecode_file = source_file.with_suffix(".nlc")
    
    with open(source_file, "r") as f:
        lines = f.readlines()
    
    bytecode = []
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        if line and not line.startswith("#"):
            try:
                line_bytecode = compiler.translate_to_bytecode(line)
                if line_bytecode:
                    bytecode.extend(line_bytecode)
                    print(f"Line {line_num}: {line} -> {line_bytecode}")
            except Exception as e:
                print(f"Error compiling line {line_num}: {line}")
                print(f"  Error: {str(e)}")
    
    with open(bytecode_file, "w") as f:
        f.write("\n".join(bytecode))
    
    print(f"Compiled to: {bytecode_file}")
    return bytecode_file

def run_test():
    """Run the complete test"""
    print("=" * 60)
    print("ENGLISH PROGRAMMING EXTENSIONS TEST")
    print("=" * 60)
    
    try:
        # Create test program
        test_file = create_test_program()
        
        # Set up extended VM
        compiler, vm, handler = setup_extended_vm()
        
        # Compile the program
        bytecode_file = compile_english_program(compiler, test_file)
        
        # Execute the program
        print("\nExecuting program...")
        print("=" * 60)
        
        result = vm.execute(bytecode_file)
        
        print("=" * 60)
        print("Program executed successfully!")
        
        # Display final environment
        print("\nFinal environment variables:")
        print("-" * 40)
        
        for var_name, value in vm.env.items():
            if not var_name.startswith("_"):
                print(f"{var_name} = {value}")
        
        # Clean up
        print("\nCleaning up...")
        if test_file.exists():
            test_file.unlink()
        if bytecode_file.exists():
            bytecode_file.unlink()
        
        print("Test completed successfully!")
        return True
    
    except Exception as e:
        print(f"Error during test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    run_test()
