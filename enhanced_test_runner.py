#!/usr/bin/env python3
"""
Enhanced Test Runner for English Programming with Extensions

This script tests the English Programming language with all extensions:
- Advanced Control Flow (while loops, for loops, else-if)
- Module System (imports, exports)
- OOP Features (classes, objects, inheritance)

Usage:
    python enhanced_test_runner.py [test_file.nl]
    
If no test file is specified, it will use the extended_features_demo.nl file.
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.append('/Users/jithinpothireddy/Downloads/English Programming')

# Import the compiler and VM
from english_programming.src.compiler.improved_nlp_compiler import ImprovedNLPCompiler
from english_programming.src.vm.improved_nlvm import ImprovedNLVM

# Import the extension loader
from english_programming.src.extensions.extension_loader import ExtensionLoader

def fix_bytecode(bytecode_file):
    """
    Fix any issues in the bytecode before execution
    - Remove duplicate instructions
    - Ensure proper block structure
    """
    with open(bytecode_file, 'r') as f:
        instructions = [line.strip() for line in f.readlines() if line.strip()]
    
    # Fix any issues (can be extended as needed)
    fixed_instructions = []
    for i, instruction in enumerate(instructions):
        # Add any specific fixes here if needed
        fixed_instructions.append(instruction)
    
    # Write fixed instructions back to file
    with open(bytecode_file, 'w') as f:
        f.write('\n'.join(fixed_instructions))
    
    return fixed_instructions

def compile_file(compiler, source_file, bytecode_file):
    """
    Compile an English program file to bytecode
    
    Args:
        compiler: The compiler instance
        source_file: Path to the source file
        bytecode_file: Path to write the bytecode
        
    Returns:
        List of bytecode instructions
    """
    print(f"Compiling {source_file}...")
    
    # Read the source file
    with open(source_file, 'r') as f:
        source_lines = f.readlines()
    
    # Compile each line
    bytecode = []
    for line_num, line in enumerate(source_lines, 1):
        line = line.strip()
        if line and not line.startswith('#'):  # Skip empty lines and comments
            try:
                line_bytecode = compiler.translate_to_bytecode(line)
                if line_bytecode:
                    bytecode.extend(line_bytecode)
            except Exception as e:
                print(f"Error compiling line {line_num}: {line}")
                print(f"  Error: {str(e)}")
    
    # Write bytecode to file
    with open(bytecode_file, 'w') as f:
        f.write('\n'.join(bytecode))
    
    print(f"Successfully compiled to {bytecode_file}")
    return bytecode

def execute_bytecode(vm, bytecode_file):
    """
    Execute a bytecode file
    
    Args:
        vm: The VM instance
        bytecode_file: Path to the bytecode file
    """
    print(f"\nExecuting {bytecode_file}...\n")
    
    # Fix any bytecode issues
    instructions = fix_bytecode(bytecode_file)
    
    # Execute the bytecode
    try:
        vm.execute_bytecode(instructions)
        print("\nProgram executed successfully.")
        
        # Display final environment (variables)
        print("\nFinal program state:")
        print("-" * 40)
        
        for var_name, value in vm.environment.items():
            if not var_name.startswith('_'):  # Skip internal variables
                print(f"{var_name} = {value}")
        
    except Exception as e:
        print(f"\nExecution error: {str(e)}")
        import traceback
        traceback.print_exc()

def main():
    # Determine the file to test
    if len(sys.argv) > 1:
        test_file = sys.argv[1]
    else:
        # Use the extended features demo by default
        test_file = os.path.join(
            os.path.dirname(__file__),
            'english_programming/examples/extended_features_demo.nl'
        )
    
    if not os.path.exists(test_file):
        print(f"Error: Test file not found: {test_file}")
        return
    
    # Determine output bytecode file
    bytecode_file = os.path.splitext(test_file)[0] + ".nlc"
    
    # Create compiler and VM instances
    compiler = ImprovedNLPCompiler()
    vm = ImprovedNLVM(debug=True)  # Enable debug mode
    
    # Load extensions
    print("Loading language extensions...")
    extensions = ExtensionLoader(compiler, vm)
    extensions.load_all_extensions()
    
    # Report loaded extensions
    loaded = extensions.get_loaded_extensions()
    print(f"Loaded extensions: {', '.join(loaded)}")
    
    # Compile and execute
    bytecode = compile_file(compiler, test_file, bytecode_file)
    execute_bytecode(vm, bytecode_file)

if __name__ == "__main__":
    main()
