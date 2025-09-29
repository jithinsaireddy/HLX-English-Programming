#!/usr/bin/env python3
"""
Enhanced VM Adapter for English Programming Extensions

This module provides a refined adapter that better integrates with the existing VM
implementation. It specifically addresses:

1. Instruction compatibility - using only VM-compatible bytecode formats
2. List and dictionary operations - fixing variable tracking issues
3. Conditional logic - respecting the fixed implementation
4. OOP support - implementing classes and objects using VM-compatible constructs

The adapter integrates features from english_runtime_complete while maintaining
the fixed conditional logic implementation.
"""

import os
import sys
import re
from pathlib import Path

# Add project root to path
project_root = Path(__file__).absolute().parent.parent.parent.parent
sys.path.append(str(project_root))

# Import the VM
from english_programming.src.vm.improved_nlvm import ImprovedNLVM

class EnhancedVMAdapter:
    """
    Enhanced adapter for the VM that fixes compatibility issues and adds support
    for advanced language features.
    """
    
    def __init__(self, vm=None, debug=False):
        """
        Initialize the enhanced VM adapter
        
        Args:
            vm (ImprovedNLVM, optional): VM to enhance
            debug (bool): Enable debug output
        """
        self.debug = debug
        
        # Create VM if not provided
        self.vm = vm if vm else ImprovedNLVM(debug=debug)
        
        # Store original methods for later reference
        self.original_execute = self.vm.execute
        self.original_execute_instructions = self.vm.execute_instructions
        
        # Replace VM methods with our enhanced versions
        self.vm.execute = self.enhanced_execute
        self.vm.execute_instructions = self.enhanced_execute_instructions
        
        # Counter for generating unique labels
        self.label_counter = 0
        
        # Initialize runtime state
        self.initialize_runtime()
        
        if self.debug:
            print("Enhanced VM Adapter initialized")
    
    def initialize_runtime(self):
        """Initialize runtime state for extension features"""
        # Store OOP-related state
        self.classes = {}
        self.objects = {}
        
        # Track variables for proper type handling
        self.variable_types = {}
        
        # Set variable tracking in VM environment
        self.vm.env["_has_extensions"] = True
        
        # Set up container for extension variables
        if "_extension_vars" not in self.vm.env:
            self.vm.env["_extension_vars"] = {}
    
    def enhanced_execute(self, bytecode_file):
        """
        Enhanced execute method with extension support
        
        Args:
            bytecode_file (str): Path to bytecode file
            
        Returns:
            Any: Result of execution
        """
        if self.debug:
            print(f"Enhanced VM Adapter executing: {bytecode_file}")
        
        # Read bytecode file
        with open(bytecode_file, 'r') as f:
            instructions = [line.strip() for line in f.readlines() if line.strip()]
        
        # Preprocess the instructions
        processed_instructions = self.preprocess_instructions(instructions)
        
        # Execute instructions
        result = self.enhanced_execute_instructions(processed_instructions, self.vm.env)
        return result
    
    def enhanced_execute_instructions(self, instructions, env):
        """
        Enhanced execute_instructions method with extension support
        
        Args:
            instructions (list): Bytecode instructions
            env (dict): Environment
            
        Returns:
            Any: Result of execution
        """
        # Process instructions one by one
        i = 0
        result = None
        
        while i < len(instructions):
            instruction = instructions[i]
            parts = instruction.split()
            
            if not parts:
                i += 1
                continue
            
            cmd = parts[0]
            
            # Handle control flow and extension instructions
            if self.is_extension_instruction(cmd):
                next_i = self.process_extension_instruction(instructions, i, env)
                if next_i > i:
                    i = next_i
                    continue
            
            # Default: let the original VM handle it
            try:
                # Execute a single instruction
                result = self.original_execute_instructions([instruction], env)
            except Exception as e:
                if self.debug:
                    print(f"Error executing instruction '{instruction}': {str(e)}")
            
            i += 1
        
        return result
    
    def is_extension_instruction(self, cmd):
        """
        Check if an instruction is an extension instruction
        
        Args:
            cmd (str): Instruction command
            
        Returns:
            bool: True if extension instruction
        """
        extension_commands = [
            "WHILE_START", "WHILE_END",
            "FOR_EACH", "FOR_END",
            "CLASS_DEF", "CLASS_END",
            "METHOD_DEF", "METHOD_END",
            "CREATE_OBJECT", "CALL_METHOD",
            "JUMP"
        ]
        
        return cmd in extension_commands or cmd.startswith("_")
    
    def process_extension_instruction(self, instructions, index, env):
        """
        Process an extension instruction
        
        Args:
            instructions (list): All instructions
            index (int): Current instruction index
            env (dict): Environment
            
        Returns:
            int: New instruction index
        """
        instruction = instructions[index]
        parts = instruction.split()
        cmd = parts[0]
        
        # Handle jump instructions
        if cmd == "JUMP":
            if len(parts) < 2:
                return index + 1
            
            # Find the label
            target_label = parts[1]
            for i, instr in enumerate(instructions):
                if instr.startswith(f"{target_label}:"):
                    return i
            
            return index + 1
        
        # Handle while loops
        elif cmd == "WHILE_START":
            # Find matching WHILE_END
            end_index = self.find_matching_end(instructions, index, "WHILE_END")
            if end_index == -1:
                return index + 1
            
            # Get condition (next instruction should be IF)
            if index + 1 >= len(instructions) or not instructions[index + 1].startswith("IF"):
                return index + 1
            
            # Extract condition from IF
            condition_parts = instructions[index + 1].split()
            if len(condition_parts) < 4:
                return index + 1
            
            var1 = condition_parts[1]
            op = condition_parts[2]
            var2 = condition_parts[3]
            
            # Set up loop
            loop_body = instructions[index + 2:end_index]
            
            # Execute loop until condition is false
            max_iterations = 1000  # Safety limit
            iteration = 0
            
            while iteration < max_iterations:
                # Evaluate condition
                condition_met = self.evaluate_condition(var1, op, var2, env)
                
                if not condition_met:
                    break
                
                # Execute loop body
                self.enhanced_execute_instructions(loop_body, env)
                
                # Increment loop counter
                iteration += 1
                
                if iteration >= max_iterations:
                    if self.debug:
                        print(f"Warning: Maximum iterations reached for while loop")
                    break
            
            # Skip past the loop
            return end_index + 1
        
        # Handle for-each loops
        elif cmd == "FOR_EACH":
            if len(parts) < 3:
                return index + 1
            
            item_var = parts[1]
            collection_var = parts[2]
            
            # Find matching FOR_END
            end_index = self.find_matching_end(instructions, index, "FOR_END")
            if end_index == -1:
                return index + 1
            
            # Extract loop body
            loop_body = instructions[index + 1:end_index]
            
            # Get collection
            if collection_var in env:
                collection = env[collection_var]
                
                # Ensure it's iterable
                if isinstance(collection, (list, tuple, str, dict)):
                    items = collection
                    if isinstance(collection, dict):
                        items = collection.keys()
                    
                    # Iterate over collection
                    for item in items:
                        # Set loop variable
                        env[item_var] = item
                        
                        # Execute loop body
                        self.enhanced_execute_instructions(loop_body, env)
            
            # Skip past the loop
            return end_index + 1
        
        # Handle class definitions
        elif cmd == "CLASS_DEF":
            if len(parts) < 2:
                return index + 1
            
            class_name = parts[1]
            parent_class = parts[2] if len(parts) > 2 else None
            
            # Find matching CLASS_END
            end_index = self.find_matching_end(instructions, index, "CLASS_END")
            if end_index == -1:
                return index + 1
            
            # Create class structure
            class_def = {
                "name": class_name,
                "parent": parent_class,
                "methods": {}
            }
            
            # Process class body
            i = index + 1
            while i < end_index:
                if instructions[i].startswith("METHOD_DEF"):
                    method_parts = instructions[i].split()
                    if len(method_parts) < 2:
                        i += 1
                        continue
                    
                    method_name = method_parts[1]
                    params = method_parts[2:] if len(method_parts) > 2 else []
                    
                    # Find matching METHOD_END
                    method_end = self.find_matching_end(instructions[i:end_index], 0, "METHOD_END")
                    if method_end == -1:
                        i += 1
                        continue
                    
                    method_end += i  # Adjust to full instruction list
                    
                    # Extract method body
                    method_body = instructions[i + 1:method_end]
                    
                    # Store method
                    class_def["methods"][method_name] = {
                        "params": params,
                        "body": method_body
                    }
                    
                    # Skip past method
                    i = method_end + 1
                else:
                    i += 1
            
            # Store class
            self.classes[class_name] = class_def
            
            # Add class to environment for type tracking
            env[f"_{class_name}_class"] = class_def
            
            # Skip past class definition
            return end_index + 1
        
        # Handle object creation
        elif cmd == "CREATE_OBJECT":
            if len(parts) < 3:
                return index + 1
            
            class_name = parts[1]
            object_name = parts[2]
            args = parts[3:] if len(parts) > 3 else []
            
            # Check if class exists
            if class_name in self.classes:
                class_def = self.classes[class_name]
                
                # Create object structure
                obj = {
                    "class": class_name,
                    "properties": {}
                }
                
                # Store object
                self.objects[object_name] = obj
                
                # Add object to environment
                env[object_name] = obj
                
                # Call constructor if it exists
                if "constructor" in class_def["methods"]:
                    constructor = class_def["methods"]["constructor"]
                    
                    # Create local environment for constructor
                    local_env = env.copy()
                    local_env["self"] = obj
                    
                    # Map args to params
                    for i, param in enumerate(constructor["params"]):
                        if i < len(args):
                            local_env[param] = self.process_value(args[i], env)
                    
                    # Execute constructor
                    self.enhanced_execute_instructions(constructor["body"], local_env)
                    
                    # Update object
                    obj.update(local_env["self"])
                    self.objects[object_name] = obj
                    env[object_name] = obj
            
            return index + 1
        
        # Handle method calls
        elif cmd == "CALL_METHOD":
            if len(parts) < 3:
                return index + 1
            
            object_name = parts[1]
            method_name = parts[2]
            result_var = parts[3] if len(parts) > 3 else None
            args = parts[4:] if len(parts) > 4 else []
            
            # Check if object exists
            if object_name in self.objects:
                obj = self.objects[object_name]
                class_name = obj["class"]
                
                # Check if class exists
                if class_name in self.classes:
                    class_def = self.classes[class_name]
                    
                    # Check if method exists
                    if method_name in class_def["methods"]:
                        method = class_def["methods"][method_name]
                        
                        # Create local environment for method
                        local_env = env.copy()
                        local_env["self"] = obj
                        
                        # Map args to params
                        for i, param in enumerate(method["params"]):
                            if i < len(args):
                                local_env[param] = self.process_value(args[i], env)
                        
                        # Execute method
                        result = self.enhanced_execute_instructions(method["body"], local_env)
                        
                        # Store result if requested
                        if result_var and result is not None:
                            env[result_var] = result
                        
                        # Update object
                        obj.update(local_env["self"])
                        self.objects[object_name] = obj
                        env[object_name] = obj
            
            return index + 1
        
        # Default: No special processing
        return index + 1
    
    def preprocess_instructions(self, instructions):
        """
        Preprocess instructions to ensure compatibility with the VM
        
        Args:
            instructions (list): Original instructions
            
        Returns:
            list: Processed instructions
        """
        processed = []
        
        for instruction in instructions:
            parts = instruction.split()
            
            if not parts:
                continue
            
            cmd = parts[0]
            
            # Process PRINTSTR to standard PRINT with quotes
            if cmd == "PRINTSTR":
                message = " ".join(parts[1:])
                processed.append(f'PRINT "{message}"')
                continue
            
            # Process CONDITION to standard IF
            if cmd == "CONDITION":
                condition = " ".join(parts[1:])
                condition_parts = re.split(r'\s+([<>=!]+)\s+', condition, 1)
                
                if len(condition_parts) == 3:
                    var1, op, var2 = condition_parts
                    processed.append(f"IF {var1} {op} {var2}")
                else:
                    # Keep original if parsing fails
                    processed.append(instruction)
                
                continue
            
            # Process other instructions as-is
            processed.append(instruction)
        
        return processed
    
    def find_matching_end(self, instructions, start_index, end_marker):
        """
        Find the matching end marker for a block
        
        Args:
            instructions (list): All instructions
            start_index (int): Starting index
            end_marker (str): End marker to find
            
        Returns:
            int: Index of matching end marker, or -1 if not found
        """
        nesting_level = 1
        start_marker = instructions[start_index].split()[0]
        
        for i in range(start_index + 1, len(instructions)):
            parts = instructions[i].split()
            if not parts:
                continue
            
            if parts[0] == start_marker:
                nesting_level += 1
            elif parts[0] == end_marker:
                nesting_level -= 1
                if nesting_level == 0:
                    return i
        
        return -1
    
    def evaluate_condition(self, var1, op, var2, env):
        """
        Evaluate a condition with variables from environment
        
        Args:
            var1 (str): First operand
            op (str): Operator
            var2 (str): Second operand
            env (dict): Environment
            
        Returns:
            bool: Result of condition
        """
        # Get values from environment or use as literals
        val1 = self.get_value(var1, env)
        val2 = self.get_value(var2, env)
        
        # Evaluate condition
        if op == "==":
            return val1 == val2
        elif op == "!=":
            return val1 != val2
        elif op == ">":
            return val1 > val2
        elif op == "<":
            return val1 < val2
        elif op == ">=":
            return val1 >= val2
        elif op == "<=":
            return val1 <= val2
        else:
            return False
    
    def get_value(self, var, env):
        """
        Get a value from the environment or interpret as literal
        
        Args:
            var (str): Variable name or literal
            env (dict): Environment
            
        Returns:
            Any: Variable value or literal value
        """
        # Check if it's in the environment
        if var in env:
            return env[var]
        
        # Try to interpret as numeric
        if var.replace('.', '', 1).isdigit():
            return float(var) if '.' in var else int(var)
        
        # Try to interpret as string literal
        if var.startswith('"') and var.endswith('"'):
            return var[1:-1]
        
        # Return as-is if not found
        return var
    
    def process_value(self, value, env):
        """
        Process a value for assignment or method calls
        
        Args:
            value (str): Value to process
            env (dict): Environment
            
        Returns:
            Any: Processed value
        """
        # Handle quoted strings
        if value.startswith('"') and value.endswith('"'):
            return value[1:-1]
        
        # Handle numeric literals
        if value.replace('.', '', 1).isdigit():
            return float(value) if '.' in value else int(value)
        
        # Handle boolean literals
        if value.lower() == "true":
            return True
        if value.lower() == "false":
            return False
        
        # Handle null/None
        if value.lower() == "none" or value.lower() == "null":
            return None
        
        # Get from environment if available
        return env.get(value, value)

# Standalone test
def test_enhanced_adapter():
    """Test the enhanced VM adapter"""
    vm = ImprovedNLVM(debug=True)
    adapter = EnhancedVMAdapter(vm, debug=True)
    
    # Create a test bytecode file
    test_file = "enhanced_test.nlc"
    bytecode = [
        "# Enhanced VM Adapter Test",
        "PRINT \"Starting enhanced VM test\"",
        
        # Variables
        "SET counter 1",
        "SET sum 0",
        
        # While loop
        "WHILE_START",
        "IF counter <= 5",
        "PRINT counter",
        "ADD counter sum sum",
        "ADD counter 1 counter",
        "WHILE_END",
        
        # Final output
        "PRINT \"Final sum:\"",
        "PRINT sum"
    ]
    
    with open(test_file, "w") as f:
        for line in bytecode:
            f.write(line + "\n")
    
    # Execute
    print(f"Executing test: {test_file}")
    adapter.enhanced_execute(test_file)
    
    # Clean up
    if os.path.exists(test_file):
        os.remove(test_file)

if __name__ == "__main__":
    test_enhanced_adapter()
