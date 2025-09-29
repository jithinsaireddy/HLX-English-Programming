#!/usr/bin/env python3
"""
Run the integrated test with our enhanced VM
"""

import sys
import os
from pathlib import Path

# Add the necessary path for imports
sys.path.append('/Users/jithinpothireddy/Downloads/English Programming')
from english_programming.src.vm.improved_nlvm import ImprovedNLVM

def main():
    # Define files
    bytecode_file = "/Users/jithinpothireddy/Downloads/English Programming/simple_test.nlc"
    
    print("\n=== RUNNING INTEGRATED TEST ===")
    print(f"Bytecode file: {bytecode_file}")
    
    # Execute with our enhanced VM
    print("\n=== EXECUTION PROCESS ===")
    vm = ImprovedNLVM()
    result = vm.execute(bytecode_file)
    
    print("\n=== FINAL ENVIRONMENT ===")
    print("Variables in environment:")
    for var_name, value in vm.env.items():
        print(f"  {var_name} = {value}")
    
    print("\n=== TEST COMPLETE ===")

if __name__ == "__main__":
    main()
