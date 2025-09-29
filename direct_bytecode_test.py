#!/usr/bin/env python3
"""
Direct Bytecode Test for English Programming VM

This script bypasses the compiler issues by directly creating bytecode to test
the VM with a focus on the fixed conditional logic implementation.
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append('/Users/jithinpothireddy/Downloads/English Programming')

# Import the VM
from english_programming.src.vm.improved_nlvm import ImprovedNLVM

def create_direct_bytecode(test_type):
    """
    Create bytecode directly without using the compiler
    
    This ensures we can test the VM's execution capabilities independently
    """
    bytecodes = {
        "basic": [
            "STORE_VAR x 10",
            "STORE_VAR y 5",
            "ADD x y result",
            "PRINT \"Result is:\"",
            "PRINT result"
        ],
        
        "conditional": [
            "STORE_VAR age 20",
            "PRINT \"Testing conditionals with age = 20\"",
            "IF_GREATER age 18",
            "PRINT \"You are an adult\"",
            "ELSE",
            "PRINT \"You are a minor\"",
            "END",
            "IF_LESS age 18",
            "PRINT \"This should not print\"",
            "ELSE",
            "PRINT \"This should print\"",
            "END"
        ],
        
        "loop": [
            "STORE_VAR counter 1",
            "STORE_VAR sum 0",
            "PRINT \"Testing while loop:\"",
            "WHILE_LESS_EQUAL counter 5",
            "PRINT counter",
            "ADD counter sum new_sum",
            "STORE_VAR sum new_sum",
            "ADD counter 1 new_counter",
            "STORE_VAR counter new_counter",
            "END",
            "PRINT \"Final sum is:\"",
            "PRINT sum"
        ]
    }
    
    # Create bytecode file
    bytecode_file = f"test_{test_type}.nlc"
    with open(bytecode_file, "w") as f:
        f.write("\n".join(bytecodes[test_type]))
    
    print(f"Created direct bytecode file for {test_type} test: {bytecode_file}")
    print(f"Bytecode content:")
    for line in bytecodes[test_type]:
        print(f"  {line}")
    
    return bytecode_file

def run_test(test_type):
    """Run the VM with direct bytecode"""
    print("=" * 60)
    print(f"ENGLISH PROGRAMMING DIRECT BYTECODE TEST: {test_type.upper()}")
    print("=" * 60)
    
    try:
        # Create bytecode
        bytecode_file = create_direct_bytecode(test_type)
        
        # Initialize VM
        vm = ImprovedNLVM(debug=True)
        
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
        if Path(bytecode_file).exists():
            os.remove(bytecode_file)
        
        print(f"\n{test_type.capitalize()} test completed successfully!")
        return True
    
    except Exception as e:
        print(f"Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_type = sys.argv[1]
    else:
        test_type = "basic"
    
    if test_type not in ["basic", "conditional", "loop"]:
        print(f"Unknown test type: {test_type}")
        print("Available types: basic, conditional, loop")
        sys.exit(1)
    
    run_test(test_type)
