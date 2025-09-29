#!/usr/bin/env python3
"""
VM Extension Adapter for English Programming

This module provides a simplified adapter that translates extension bytecode
to VM-compatible instructions, focusing on the most essential extensions:
- While loops
- For-each loops with lists
- Basic conditional logic
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).absolute().parent.parent.parent.parent
sys.path.append(str(project_root))

# Import the VM
from english_programming.src.vm.improved_nlvm import ImprovedNLVM

class VMExtensionAdapter:
    """Simplified VM Extension Adapter for English Programming"""
    
    def __init__(self, vm=None, debug=False):
        """Initialize the VM Extension Adapter"""
        self.debug = debug
        
        # Create a VM if not provided
        self.vm = vm or ImprovedNLVM(debug=debug)
        
        # Store original methods
        self.original_execute = self.vm.execute
        
        # Replace VM's execute method
        self.vm.execute = self.enhanced_execute
    
    def enhanced_execute(self, bytecode_file):
        """Enhanced execute method with extension support"""
        if self.debug:
            print(f"VM Extension Adapter executing: {bytecode_file}")
        
        # Read bytecode file
        with open(bytecode_file, 'r') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
        
        # Process instructions to convert to VM-compatible format
        vm_instructions = self.preprocess_instructions(lines)
        
        # Write to temporary file
        temp_file = f"{bytecode_file}.temp"
        with open(temp_file, 'w') as f:
            for line in vm_instructions:
                f.write(line + '\n')
        
        # Execute with original VM
        result = self.original_execute(temp_file)
        
        # Clean up
        if os.path.exists(temp_file):
            os.remove(temp_file)
        
        return result
    
    def preprocess_instructions(self, instructions):
        """Preprocess instructions to make them VM-compatible"""
        processed = []
        i = 0
        
        while i < len(instructions):
            instruction = instructions[i]
            parts = instruction.split()
            
            if not parts:
                i += 1
                continue
            
            cmd = parts[0]
            
            # Handle custom print instruction
            if cmd == "PRINTSTR":
                message = " ".join(parts[1:]) if len(parts) > 1 else ""
                processed.append(f'PRINT "{message}"')
                i += 1
                continue
            
            # Handle while loops
            if cmd == "WHILE_START":
                loop_instructions, next_i = self._process_while_loop(instructions, i)
                processed.extend(loop_instructions)
                i = next_i
                continue
            
            # Handle for-each loops
            if cmd == "FOR_EACH":
                if len(parts) >= 3:
                    item_var = parts[1]
                    collection_var = parts[2]
                    loop_instructions, next_i = self._process_for_each_loop(
                        instructions, i, item_var, collection_var
                    )
                    processed.extend(loop_instructions)
                    i = next_i
                    continue
            
            # Skip end markers (they're handled in processing)
            if cmd in ["WHILE_END", "FOR_END"]:
                i += 1
                continue
            
            # Pass through normal instructions
            processed.append(instruction)
            i += 1
        
        return processed
    
    def _process_while_loop(self, instructions, start_index):
        """Process a while loop into VM-compatible instructions"""
        # Find the condition (normally next line after WHILE_START)
        condition_index = start_index + 1
        condition = ""
        
        # Skip comments and find the actual condition
        while condition_index < len(instructions):
            condition_line = instructions[condition_index]
            if condition_line.startswith("#"):
                condition_index += 1
                continue
                
            if condition_line.startswith("IF") or condition_line.startswith("CONDITION"):
                condition = condition_line
                break
            
            condition_index += 1
        
        # Normalize the condition
        if condition.startswith("CONDITION"):
            parts = condition.split()
            if len(parts) >= 2:
                condition = "IF " + " ".join(parts[1:])
        
        # Find WHILE_END
        end_index = start_index + 1
        nesting = 1
        
        while end_index < len(instructions):
            if instructions[end_index].startswith("WHILE_START"):
                nesting += 1
            elif instructions[end_index].startswith("WHILE_END"):
                nesting -= 1
                if nesting == 0:
                    break
            end_index += 1
        
        # Extract loop body (skip WHILE_START and condition)
        body_start = condition_index + 1
        body = instructions[body_start:end_index]
        
        # Create a unique label
        label = f"_while_{start_index}"
        
        # Generate VM-compatible loop
        vm_loop = [
            f"# While loop start",
            f"{label}:",
            condition   # IF condition
        ]
        
        # Process the body (recursive preprocessing)
        body_processed = self.preprocess_instructions(body)
        vm_loop.extend(body_processed)
        
        # Add loop jump and end
        vm_loop.extend([
            f"JUMP {label}",
            "END_IF",
            f"# While loop end"
        ])
        
        return vm_loop, end_index + 1
    
    def _process_for_each_loop(self, instructions, start_index, item_var, collection_var):
        """Process a for-each loop into VM-compatible instructions"""
        # Find FOR_END
        end_index = start_index + 1
        nesting = 1
        
        while end_index < len(instructions):
            if instructions[end_index].startswith("FOR_EACH"):
                nesting += 1
            elif instructions[end_index].startswith("FOR_END"):
                nesting -= 1
                if nesting == 0:
                    break
            end_index += 1
        
        # Extract loop body
        body = instructions[start_index + 1:end_index]
        
        # Generate unique variables
        index_var = f"_index_{start_index}"
        length_var = f"_length_{start_index}"
        
        # Generate VM-compatible loop
        vm_loop = [
            f"# For-each loop: {item_var} in {collection_var}",
            f"SET {index_var} 0",  # Initialize index
            f"BUILTIN LENGTH {collection_var} {length_var}",  # Get collection length
            f"_for_loop_{start_index}:",
            f"IF {index_var} < {length_var}"  # Loop condition
        ]
        
        # Get current item
        vm_loop.append(f"BUILTIN INDEX {collection_var} {index_var} {item_var}")
        
        # Process the body
        body_processed = self.preprocess_instructions(body)
        vm_loop.extend(body_processed)
        
        # Increment index and jump back
        vm_loop.extend([
            f"ADD {index_var} 1 {index_var}",
            f"JUMP _for_loop_{start_index}",
            "END_IF",
            f"# For-each loop end"
        ])
        
        return vm_loop, end_index + 1

# Standalone test function
def test_extension_adapter():
    """Test the VM extension adapter"""
    adapter = VMExtensionAdapter(debug=True)
    
    # Create a simple bytecode file with extensions
    test_file = "extension_test.nlc"
    bytecode = [
        "# Test program with extensions",
        "# Initialize variables",
        "SET counter 1",
        "SET sum 0",
        "PRINT \"Testing while loop:\"",
        
        # While loop using our extension syntax
        "WHILE_START",
        "CONDITION counter <= 5",
        "PRINT counter",
        "ADD counter sum sum",
        "ADD counter 1 counter",
        "WHILE_END",
        
        "PRINT \"Final sum:\"",
        "PRINT sum"
    ]
    
    with open(test_file, "w") as f:
        for line in bytecode:
            f.write(line + "\n")
    
    # Execute the test
    adapter.vm.execute(test_file)
    
    # Clean up
    if os.path.exists(test_file):
        os.remove(test_file)

if __name__ == "__main__":
    test_extension_adapter()
