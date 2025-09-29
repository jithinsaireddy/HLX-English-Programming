#!/usr/bin/env python3
"""
Test script for English Programming language extensions
This script tests the new language features added by the extensions
"""

import os
import sys
from pathlib import Path

# Add the project root to the path
sys.path.append('/Users/jithinpothireddy/Downloads/English Programming')

# Import core components
from english_programming.src.compiler.improved_nlp_compiler import ImprovedNLPCompiler
from english_programming.src.vm.improved_nlvm import ImprovedNLVM

def patch_vm(vm):
    """Add necessary methods to the VM for extension support"""
    # Add execute_bytecode method
    if not hasattr(vm, 'execute_bytecode'):
        def execute_bytecode(instructions):
            if isinstance(instructions, list):
                temp_file = "temp_bytecode.nlc"
                try:
                    with open(temp_file, 'w') as f:
                        f.write('\n'.join(instructions))
                    return vm.execute(temp_file)
                finally:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
            else:
                return vm.execute(instructions)
        
        vm.execute_bytecode = execute_bytecode
    
    # Add environment property
    if not hasattr(vm, 'environment'):
        vm.environment = vm.env
    
    # Add instruction pointer
    if not hasattr(vm, 'instruction_pointer'):
        vm.instruction_pointer = 0

def test_extensions():
    """Test the advanced language features"""
    print("Testing English Programming language extensions...")
    
    # Create compiler and VM
    compiler = ImprovedNLPCompiler()
    vm = ImprovedNLVM(debug=True)
    
    # Patch VM to support extensions
    patch_vm(vm)
    
    # Load extensions
    from english_programming.src.extensions.control_flow.advanced_loops import AdvancedControlFlowExtension
    from english_programming.src.extensions.module_system.module_loader import ModuleSystemExtension
    from english_programming.src.extensions.oop.class_system import OOPExtension
    
    # Initialize extensions
    print("Loading extensions...")
    control_flow = AdvancedControlFlowExtension(compiler, vm)
    module_system = ModuleSystemExtension(compiler, vm)
    oop = OOPExtension(compiler, vm)
    
    # Create simple test file with control flow features
    test_file = Path("test_extensions.nl")
    with open(test_file, 'w') as f:
        f.write("""# Test file for English Programming extensions
create a variable called counter and set it to 1

# While loop test
while counter is less than 5:
    print counter
    add 1 to counter and store the result in counter

# For loop test
create a variable called numbers and set it to [1, 2, 3, 4, 5]
for each item in numbers:
    multiply item by 2 and store the result in doubled_item
    print doubled_item

# Class definition test
create class called Person:
    define method constructor with inputs name and age:
        set the name property of self to name
        set the age property of self to age
    
    define method greet:
        print "Hello, my name is " 
        print self.name

# Create object and call method
create Person object called john with inputs "John Doe" and 30
call greet on john
""")
    
    # Compile the test file
    print(f"Compiling test file: {test_file}")
    bytecode_file = test_file.with_suffix('.nlc')
    
    with open(test_file, 'r') as f:
        lines = f.readlines()
    
    bytecode = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):
            try:
                line_bytecode = compiler.translate_to_bytecode(line)
                if line_bytecode:
                    bytecode.extend(line_bytecode)
            except Exception as e:
                print(f"Error compiling line: {line}")
                print(f"  {str(e)}")
    
    # Write bytecode to file
    with open(bytecode_file, 'w') as f:
        f.write('\n'.join(bytecode))
    
    print(f"Compiled to: {bytecode_file}")
    
    # Execute the bytecode
    try:
        print("Executing with extensions...")
        vm.execute_bytecode(bytecode_file)
        print("Execution completed successfully")
    except Exception as e:
        print(f"Execution error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # Clean up
    if test_file.exists():
        test_file.unlink()
    if bytecode_file.exists():
        bytecode_file.unlink()

if __name__ == "__main__":
    test_extensions()
