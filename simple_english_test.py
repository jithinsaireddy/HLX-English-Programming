#!/usr/bin/env python3
"""
Simple English Programming Test

This script focuses on testing basic features with minimal dependencies to isolate
where issues might be occurring. It respects the fixed conditional logic implementation
that was previously established.
"""

import os
import sys
from pathlib import Path

# Add the project root to the path
project_root = '/Users/jithinpothireddy/Downloads/English Programming'
sys.path.append(project_root)

# Import core components
from english_programming.src.compiler.improved_nlp_compiler import ImprovedNLPCompiler
from english_programming.src.vm.improved_nlvm import ImprovedNLVM

def create_sample_program(program_type="basic"):
    """Create sample programs for testing specific features"""
    programs = {
        "basic": """
# Basic operations test
create a variable called x and set it to 10
create a variable called y and set it to 5
add x and y and store the result in sum
print "Sum is:"
print sum
""",
        "conditional": """
# Conditional test - testing fixed conditional logic
create a variable called age and set it to 20
print "Testing conditionals with age = 20"

if age is greater than 18:
    print "You are an adult"
else:
    print "You are a minor"
    
# Test another condition that should not execute
if age is less than 18:
    print "This should not print"
else:
    print "This should print"
""",
        "loop": """
# Loop test
create a variable called counter and set it to 1
create a variable called sum and set it to 0

print "Testing simple loop with counter from 1 to 5"
while counter is less than or equal to 5:
    print counter
    add counter to sum and store the result in sum
    add 1 to counter and store the result in counter

print "Final sum is:"
print sum
"""
    }
    
    program_file = f"test_{program_type}.nl"
    with open(program_file, "w") as f:
        f.write(programs[program_type])
    
    print(f"Created {program_type} test program: {program_file}")
    return program_file

def compile_program(compiler, source_file):
    """Compile whole English sentences to bytecode"""
    print(f"Compiling {source_file}...")
    bytecode_file = Path(source_file).with_suffix(".nlc")
    
    with open(source_file, "r") as f:
        content = f.read()
    
    # Process complete lines rather than character by character
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
                    print(f"  -> Bytecode: {line_bytecode}")
            except Exception as e:
                print(f"Error compiling line {line_num}: {line}")
                print(f"  Error: {str(e)}")
    
    with open(bytecode_file, "w") as f:
        f.write("\n".join(bytecode))
    
    print(f"Compiled to: {bytecode_file}")
    return bytecode_file

def run_program(vm, bytecode_file):
    """Execute a compiled program with the VM"""
    print(f"\nExecuting program: {bytecode_file}")
    print("=" * 60)
    
    try:
        result = vm.execute(bytecode_file)
        
        print("=" * 60)
        print("Program executed successfully!")
        
        # Show final environment
        print("\nFinal environment variables:")
        print("-" * 40)
        for var_name, value in vm.env.items():
            if not var_name.startswith("_"):
                print(f"{var_name} = {value}")
        
        return result
    except Exception as e:
        print(f"Error executing program: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def run_test(program_type="basic"):
    """Run a test with specified program type"""
    print("=" * 60)
    print(f"ENGLISH PROGRAMMING TEST: {program_type.upper()}")
    print("=" * 60)
    
    try:
        # Create compiler and VM
        compiler = ImprovedNLPCompiler()
        vm = ImprovedNLVM(debug=True)
        
        # Create test program
        program_file = create_sample_program(program_type)
        
        # Compile the program
        bytecode_file = compile_program(compiler, program_file)
        
        # Run the program
        run_program(vm, bytecode_file)
        
        # Clean up
        if Path(program_file).exists():
            os.remove(program_file)
        if Path(bytecode_file).exists():
            os.remove(bytecode_file)
        
        print(f"\n{program_type.capitalize()} test completed successfully!")
        return True
    except Exception as e:
        print(f"Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Parse command line arguments
    if len(sys.argv) > 1:
        program_type = sys.argv[1]
    else:
        program_type = "basic"
    
    run_test(program_type)
