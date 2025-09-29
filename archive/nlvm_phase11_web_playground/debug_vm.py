#!/usr/bin/env python3
"""
Debug script for the EnhancedNLVM to understand variable resolution issues
"""
import sys
import os

# Add the project root to the path
engprg_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if engprg_path not in sys.path:
    sys.path.insert(0, engprg_path)

# Import the VM
from english_programming.src.vm.enhanced_nlvm import EnhancedNLVM

class DebugNLVM(EnhancedNLVM):
    """Enhanced VM with additional debugging capabilities"""
    
    def __init__(self):
        super().__init__()
        self.debug_mode = True
        
    def debug_print(self, message):
        """Print a debug message"""
        if self.debug_mode:
            print(f"[DEBUG] {message}")
            
    def execute_instructions(self, instructions, local_env=None):
        """Override to add debug info for each instruction"""
        env = local_env or self.env
        i = 0
        
        while i < len(instructions):
            instr = instructions[i]
            parts = instr.split()
            
            self.debug_print(f"Executing: {instr}")
            self.debug_print(f"Current env: {env}")
            
            # Call the parent method to execute a single instruction
            # Instead of directly calling execute_instructions which would recurse,
            # we'll manually handle executing one instruction at a time
            
            # Increase i by default
            next_i = i + 1
            
            # Logic based on the original execute_instructions in EnhancedNLVM
            cmd = parts[0]
            
            # Process just this one instruction
            self._execute_single_instruction(instr, parts, env)
            
            # Update i to the next instruction
            i = next_i
            
            self.debug_print(f"After execution: {env}")
            self.debug_print("---")
        
        return env
    
    def _execute_single_instruction(self, instr, parts, env):
        """Execute a single bytecode instruction"""
        cmd = parts[0]
        
        # Based on EnhancedNLVM.execute_instructions logic
        # Here we'll just delegate back to the parent class for this instruction
        # The reason we're not calling execute_instructions directly is to avoid infinite recursion
        
        try:
            # We'll just delegate to the parent execute_instructions but only for one instruction
            super().execute_instructions([instr], env)
        except Exception as e:
            self.debug_print(f"Error executing {instr}: {e}")
        
        return True

def debug_execute(bytecode_file):
    """Execute bytecode with debugging"""
    print(f"Executing {bytecode_file} with debugging...")
    
    vm = DebugNLVM()
    
    # Read the bytecode file
    with open(bytecode_file, "r") as f:
        instructions = [line.strip() for line in f.readlines() if line.strip()]
    
    # Execute with debugging
    vm.execute_instructions(instructions)
    
    print("\nFinal state of variables:")
    for var_name, value in vm.env.items():
        print(f"  {var_name} = {value}")
    
    return None

if __name__ == "__main__":
    if len(sys.argv) > 1:
        bytecode_file = sys.argv[1]
        debug_execute(bytecode_file)
    else:
        print("Please provide a bytecode file to execute")
        sys.exit(1)
