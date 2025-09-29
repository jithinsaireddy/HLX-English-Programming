"""
VM Extension Handler for English Programming

This module adds support for advanced instructions:
- While loops
- For loops
- Else-if constructs
- OOP features

It extends the existing VM to handle new bytecode instructions added by the extensions.
"""

import os
import sys
import re

class VMExtensionHandler:
    """
    Extension handler that integrates with the English Programming VM
    to support advanced language features.
    """
    
    def __init__(self, vm):
        """Initialize with a reference to the VM instance"""
        self.vm = vm
        
        # Store original methods for chaining
        self.original_execute = vm.execute
        self.original_execute_instructions = vm.execute_instructions if hasattr(vm, 'execute_instructions') else None
        
        # Patch the VM
        self.patch_vm()
        
        # Initialize extension state
        self.vm.loop_stack = []  # For tracking loops
        self.vm.class_registry = {}  # For OOP
        self.vm.current_class = None
        self.vm.block_stack = []  # For nested blocks
        self.vm.instruction_pointer = 0  # Current instruction index
        
        # For for-loops
        self.vm.for_loops = {}
        
    def patch_vm(self):
        """Patch the VM to handle extension instructions"""
        # Replace the VM's execute method with our enhanced version
        self.vm.execute = self.enhanced_execute
        
        # Add extension attributes if they don't exist
        if not hasattr(self.vm, 'environment'):
            self.vm.environment = self.vm.env
            
        # Add method to evaluate conditions if it doesn't exist
        if not hasattr(self.vm, 'evaluate_condition'):
            self.vm.evaluate_condition = self.evaluate_condition
        
    def enhanced_execute(self, bytecode_file):
        """Enhanced version of VM execute that handles extensions"""
        # Read the bytecode file
        with open(bytecode_file, 'r') as f:
            instructions = [line.strip() for line in f.readlines() if line.strip()]
        
        # Execute with extensions
        return self.execute_instructions_with_extensions(instructions)
    
    def execute_instructions_with_extensions(self, instructions, env=None):
        """Execute instructions with support for extensions"""
        if env is None:
            env = self.vm.env
            
        i = 0
        result = None
        
        # Execute each instruction
        while i < len(instructions):
            instruction = instructions[i]
            
            # Set current instruction pointer
            self.vm.instruction_pointer = i
            
            # Check if it's a custom instruction
            if self.is_extension_instruction(instruction):
                # Handle with our extension logic
                next_i = self.execute_extension_instruction(instructions, i, env)
                i = next_i
            else:
                # Use original VM behavior for standard instructions
                if self.original_execute_instructions:
                    # If VM has execute_instructions method, use it for a single instruction
                    result = self.original_execute_instructions([instruction], env)
                else:
                    # Otherwise just log the instruction (VM would normally handle it)
                    self.vm.debug_print(f"Executing standard instruction: {instruction}")
                i += 1
                
        return result
    
    def is_extension_instruction(self, instruction):
        """Check if instruction is from our extensions"""
        extension_prefixes = [
            "WHILE_", "FOR_", "ELSE_IF", 
            "CLASS_", "METHOD_", "CREATE_OBJECT", 
            "CALL_METHOD", "GET_PROPERTY", "SET_PROPERTY",
            "IMPORT_", "EXPORT_", "MODULE_"
        ]
        
        for prefix in extension_prefixes:
            if instruction.startswith(prefix):
                return True
                
        return False
    
    def execute_extension_instruction(self, instructions, index, env):
        """Execute an extension instruction and return the next instruction index"""
        instruction = instructions[index]
        
        # Handle different extension instructions
        if instruction.startswith("WHILE_"):
            return self.handle_while_instruction(instructions, index, env)
        elif instruction.startswith("FOR_"):
            return self.handle_for_instruction(instructions, index, env)
        elif instruction.startswith("ELSE_IF"):
            return self.handle_else_if_instruction(instructions, index, env)
        elif instruction.startswith(("CLASS_", "METHOD_", "CREATE_OBJECT", "CALL_METHOD", "GET_PROPERTY", "SET_PROPERTY")):
            return self.handle_oop_instruction(instructions, index, env)
        elif instruction.startswith(("IMPORT_", "EXPORT_", "MODULE_")):
            return self.handle_module_instruction(instructions, index, env)
        
        # If not handled, move to next instruction
        print(f"Warning: Unhandled extension instruction: {instruction}")
        return index + 1
    
    def handle_while_instruction(self, instructions, index, env):
        """Handle while loop instructions"""
        instruction = instructions[index]
        
        if instruction.startswith("WHILE_START"):
            # Extract condition from WHILE_START instruction
            condition = instruction[len("WHILE_START "):].strip()
            
            # Evaluate condition
            condition_result = self.vm.evaluate_condition(condition, env)
            
            if condition_result:
                # Enter the loop - store loop info
                self.vm.loop_stack.append({
                    "type": "while",
                    "start_index": index,
                    "condition": condition
                })
                # Move to next instruction (inside loop)
                return index + 1
            else:
                # Skip the loop - find matching end
                return self.find_block_end(instructions, index)
                
        elif instruction == "WHILE_END":
            # End of while loop - check condition again
            if self.vm.loop_stack and self.vm.loop_stack[-1]["type"] == "while":
                loop_info = self.vm.loop_stack[-1]
                
                # Evaluate condition again
                condition_result = self.vm.evaluate_condition(loop_info["condition"], env)
                
                if condition_result:
                    # Jump back to start of loop
                    return loop_info["start_index"]
                else:
                    # Exit the loop
                    self.vm.loop_stack.pop()
            
            # Move to next instruction after loop
            return index + 1
        
        # Unrecognized while instruction, move to next
        return index + 1
    
    def handle_for_instruction(self, instructions, index, env):
        """Handle for loop instructions"""
        instruction = instructions[index]
        
        if instruction.startswith("FOR_EACH_START"):
            # Parse "FOR_EACH_START var collection"
            parts = instruction.split(" ", 2)
            if len(parts) < 3:
                print(f"Error: Invalid FOR_EACH_START instruction: {instruction}")
                return index + 1
                
            var_name = parts[1]
            collection_name = parts[2]
            
            # Get the collection from environment
            if collection_name not in env:
                print(f"Error: Collection '{collection_name}' not found")
                # Skip the loop
                return self.find_block_end(instructions, index)
                
            collection = env[collection_name]
            
            # Make sure it's iterable
            if not isinstance(collection, (list, tuple, dict, str)):
                print(f"Error: '{collection_name}' is not iterable")
                return self.find_block_end(instructions, index)
                
            # Start the loop with first item
            if not hasattr(self.vm, 'for_loops'):
                self.vm.for_loops = {}
                
            # Create a unique loop ID
            loop_id = f"for_{index}"
            
            # Initialize loop state
            self.vm.for_loops[loop_id] = {
                "var": var_name,
                "collection": collection,
                "index": 0,
                "start": index
            }
            
            # Assign the first item to the variable
            if len(collection) > 0:
                env[var_name] = collection[0]
                # Store loop info
                self.vm.loop_stack.append({
                    "type": "for",
                    "id": loop_id
                })
                # Continue to loop body
                return index + 1
            else:
                # Empty collection - skip the loop
                return self.find_block_end(instructions, index)
                
        elif instruction.startswith("FOR_RANGE_START"):
            # Parse "FOR_RANGE_START var start end"
            parts = instruction.split(" ", 3)
            if len(parts) < 4:
                print(f"Error: Invalid FOR_RANGE_START instruction: {instruction}")
                return index + 1
                
            var_name = parts[1]
            start_val = self.evaluate_value(parts[2], env)
            end_val = self.evaluate_value(parts[3], env)
            
            # Make sure values are numeric
            try:
                start = int(start_val)
                end = int(end_val)
            except (ValueError, TypeError):
                print(f"Error: Range values must be integers: {start_val}, {end_val}")
                return self.find_block_end(instructions, index)
            
            # Create a range collection
            collection = list(range(start, end + 1))  # inclusive range
            
            # Create a unique loop ID
            loop_id = f"for_{index}"
            
            # Initialize loop state
            self.vm.for_loops[loop_id] = {
                "var": var_name,
                "collection": collection,
                "index": 0,
                "start": index
            }
            
            # Assign the first item to the variable
            if len(collection) > 0:
                env[var_name] = collection[0]
                # Store loop info
                self.vm.loop_stack.append({
                    "type": "for",
                    "id": loop_id
                })
                # Continue to loop body
                return index + 1
            else:
                # Empty range - skip the loop
                return self.find_block_end(instructions, index)
                
        elif instruction == "FOR_EACH_END" or instruction == "FOR_RANGE_END":
            # End of for loop - move to next item
            if self.vm.loop_stack and self.vm.loop_stack[-1]["type"] == "for":
                loop_info = self.vm.loop_stack[-1]
                loop_id = loop_info["id"]
                
                if loop_id in self.vm.for_loops:
                    for_info = self.vm.for_loops[loop_id]
                    
                    # Increment index
                    for_info["index"] += 1
                    
                    # Check if we have more items
                    if for_info["index"] < len(for_info["collection"]):
                        # Assign next item to variable
                        env[for_info["var"]] = for_info["collection"][for_info["index"]]
                        # Jump back to start of loop body
                        return for_info["start"] + 1
                    else:
                        # End of collection - exit loop
                        self.vm.loop_stack.pop()
                        del self.vm.for_loops[loop_id]
        
            # Move to next instruction after loop
            return index + 1
        
        # Unrecognized for instruction, move to next
        return index + 1
    
    def handle_else_if_instruction(self, instructions, index, env):
        """Handle else-if instructions"""
        instruction = instructions[index]
        
        if instruction.startswith("ELSE_IF"):
            # Extract condition from ELSE_IF instruction
            condition = instruction[len("ELSE_IF "):].strip()
            
            # Evaluate condition
            condition_result = self.vm.evaluate_condition(condition, env)
            
            if condition_result:
                # Condition is true - enter this branch
                return index + 1
            else:
                # Condition is false - skip to next ELSE_IF, ELSE, or END_IF
                return self.find_next_branch(instructions, index)
        
        # Should never get here
        return index + 1
    
    def handle_oop_instruction(self, instructions, index, env):
        """Handle OOP-related instructions"""
        instruction = instructions[index]
        
        if instruction.startswith("CLASS_START"):
            # Parse "CLASS_START class_name parent_class"
            parts = instruction.split(" ", 2)
            if len(parts) < 3:
                print(f"Error: Invalid CLASS_START instruction: {instruction}")
                return index + 1
                
            class_name = parts[1]
            parent_class = parts[2]
            
            # Initialize class in registry
            self.vm.class_registry[class_name] = {
                "parent": parent_class,
                "methods": {},
                "properties": {}
            }
            
            # Set current class context
            self.vm.current_class = class_name
            
            # Continue to class body
            return index + 1
            
        elif instruction == "CLASS_END":
            # End of class definition
            self.vm.current_class = None
            return index + 1
            
        elif instruction.startswith("METHOD_START"):
            # Parse "METHOD_START method_name param1 param2 ..."
            parts = instruction.split(" ")
            if len(parts) < 2:
                print(f"Error: Invalid METHOD_START instruction: {instruction}")
                return index + 1
                
            method_name = parts[1]
            parameters = parts[2:] if len(parts) > 2 else []
            
            # Store method in current class
            if not self.vm.current_class:
                print(f"Error: Method {method_name} defined outside of class context")
                return index + 1
                
            # Find method end to get the code block
            method_end_index = self.find_method_end(instructions, index)
            method_body = instructions[index+1:method_end_index]
            
            # Store method info
            self.vm.class_registry[self.vm.current_class]["methods"][method_name] = {
                "params": parameters,
                "body": method_body,
                "start": index,
                "end": method_end_index
            }
            
            # Skip to after method end
            return method_end_index + 1
            
        elif instruction == "METHOD_END":
            # End of method definition
            return index + 1
            
        elif instruction.startswith("CREATE_OBJECT"):
            # Parse "CREATE_OBJECT class_name obj_name arg1 arg2 ..."
            parts = instruction.split(" ")
            if len(parts) < 3:
                print(f"Error: Invalid CREATE_OBJECT instruction: {instruction}")
                return index + 1
                
            class_name = parts[1]
            obj_name = parts[2]
            args = parts[3:] if len(parts) > 3 else []
            
            # Check if class exists
            if class_name not in self.vm.class_registry:
                print(f"Error: Class {class_name} not found")
                return index + 1
                
            # Create object instance
            obj = {
                "class": class_name,
                "properties": {}
            }
            
            # Store in environment
            env[obj_name] = obj
            
            # Call constructor if it exists
            if "constructor" in self.vm.class_registry[class_name]["methods"]:
                self.call_method(obj_name, "constructor", args, env)
            
            return index + 1
            
        elif instruction.startswith("CALL_METHOD"):
            # Parse "CALL_METHOD obj_name method_name arg1 arg2 ..."
            parts = instruction.split(" ")
            if len(parts) < 3:
                print(f"Error: Invalid CALL_METHOD instruction: {instruction}")
                return index + 1
                
            obj_name = parts[1]
            method_name = parts[2]
            args = parts[3:] if len(parts) > 3 else []
            
            # Call the method
            self.call_method(obj_name, method_name, args, env)
            
            return index + 1
            
        elif instruction.startswith("GET_PROPERTY"):
            # Parse "GET_PROPERTY obj_name property_name"
            parts = instruction.split(" ")
            if len(parts) < 3:
                print(f"Error: Invalid GET_PROPERTY instruction: {instruction}")
                return index + 1
                
            obj_name = parts[1]
            property_name = parts[2]
            
            # Get object
            if obj_name not in env:
                print(f"Error: Object {obj_name} not found")
                return index + 1
                
            obj = env[obj_name]
            
            # Get property
            if "properties" in obj and property_name in obj["properties"]:
                # Store result in VM's result variable
                self.vm.result = obj["properties"][property_name]
            else:
                print(f"Warning: Property {property_name} not found in object {obj_name}")
                self.vm.result = None
            
            return index + 1
            
        elif instruction.startswith("SET_PROPERTY"):
            # Parse "SET_PROPERTY obj_name property_name value"
            parts = instruction.split(" ", 3)
            if len(parts) < 4:
                print(f"Error: Invalid SET_PROPERTY instruction: {instruction}")
                return index + 1
                
            obj_name = parts[1]
            property_name = parts[2]
            value_expr = parts[3]
            
            # Get object
            if obj_name not in env:
                print(f"Error: Object {obj_name} not found")
                return index + 1
                
            obj = env[obj_name]
            
            # Evaluate value
            value = self.evaluate_value(value_expr, env)
            
            # Set property
            if "properties" not in obj:
                obj["properties"] = {}
                
            obj["properties"][property_name] = value
            
            return index + 1
        
        # Unrecognized OOP instruction, move to next
        return index + 1
    
    def handle_module_instruction(self, instructions, index, env):
        """Handle module system instructions"""
        instruction = instructions[index]
        
        # Basic module system implementation
        if instruction.startswith("IMPORT_MODULE"):
            # Parse "IMPORT_MODULE module_name"
            parts = instruction.split(" ", 1)
            if len(parts) < 2:
                print(f"Error: Invalid IMPORT_MODULE instruction: {instruction}")
                return index + 1
                
            module_name = parts[1]
            print(f"Importing module: {module_name}")
            
            # Basic module importing logic (placeholder)
            # In a complete implementation, this would load the module's code
            
            return index + 1
            
        elif instruction.startswith("IMPORT_SYMBOLS"):
            # Parse "IMPORT_SYMBOLS module_name symbol1,symbol2,..."
            parts = instruction.split(" ", 2)
            if len(parts) < 3:
                print(f"Error: Invalid IMPORT_SYMBOLS instruction: {instruction}")
                return index + 1
                
            module_name = parts[1]
            symbols = parts[2].split(",")
            
            print(f"Importing symbols {symbols} from module: {module_name}")
            
            # Basic symbol importing logic (placeholder)
            
            return index + 1
            
        elif instruction.startswith("EXPORT_SYMBOLS"):
            # Parse "EXPORT_SYMBOLS symbol1,symbol2,..."
            parts = instruction.split(" ", 1)
            if len(parts) < 2:
                print(f"Error: Invalid EXPORT_SYMBOLS instruction: {instruction}")
                return index + 1
                
            symbols = parts[1].split(",")
            
            print(f"Exporting symbols: {symbols}")
            
            # Basic symbol exporting logic (placeholder)
            
            return index + 1
            
        elif instruction.startswith("MODULE_DECLARATION"):
            # Parse "MODULE_DECLARATION module_name"
            parts = instruction.split(" ", 1)
            if len(parts) < 2:
                print(f"Error: Invalid MODULE_DECLARATION instruction: {instruction}")
                return index + 1
                
            module_name = parts[1]
            
            print(f"Declaring module: {module_name}")
            
            # Basic module declaration logic (placeholder)
            
            return index + 1
        
        # Unrecognized module instruction, move to next
        return index + 1
    
    def find_block_end(self, instructions, start_index):
        """Find the end of a block starting at start_index"""
        block_depth = 0
        i = start_index + 1
        
        while i < len(instructions):
            if instructions[i] == "BLOCK_START":
                block_depth += 1
            elif instructions[i] == "BLOCK_END":
                if block_depth == 0:
                    # Found the end of this block
                    return i + 1
                block_depth -= 1
            i += 1
        
        # If we don't find the end, return the end of instructions
        return len(instructions)
    
    def find_next_branch(self, instructions, start_index):
        """Find the next branch (ELSE_IF, ELSE) or the end of the if statement"""
        block_depth = 0
        i = start_index + 1
        
        while i < len(instructions):
            if instructions[i] == "BLOCK_START":
                block_depth += 1
            elif instructions[i] == "BLOCK_END":
                if block_depth == 0:
                    # End of this branch
                    if i+1 < len(instructions) and (
                        instructions[i+1].startswith("ELSE_IF") or 
                        instructions[i+1] == "ELSE"):
                        # Found another branch
                        return i + 1
                    # End of if statement
                    return i + 1
                block_depth -= 1
            i += 1
        
        # If we don't find a next branch, return the end of instructions
        return len(instructions)
    
    def find_method_end(self, instructions, start_index):
        """Find the end of a method definition"""
        block_depth = 0
        i = start_index + 1
        
        while i < len(instructions):
            if instructions[i] == "BLOCK_START":
                block_depth += 1
            elif instructions[i] == "BLOCK_END":
                if block_depth == 0:
                    # End of method
                    return i
                block_depth -= 1
            elif instructions[i] == "METHOD_END":
                # Explicit method end marker
                return i
            i += 1
        
        # If we don't find the end, return the end of instructions
        return len(instructions)
    
    def call_method(self, obj_name, method_name, args, env):
        """Call a method on an object"""
        # Get object
        if obj_name not in env:
            print(f"Error: Object {obj_name} not found")
            return
        
        obj = env[obj_name]
        
        # Get object's class
        if "class" not in obj:
            print(f"Error: Invalid object {obj_name}")
            return
        
        class_name = obj["class"]
        
        # Get class from registry
        if class_name not in self.vm.class_registry:
            print(f"Error: Class {class_name} not found")
            return
        
        # Find method (traverse inheritance hierarchy)
        method_info = self.find_method(class_name, method_name)
        if not method_info:
            print(f"Error: Method {method_name} not found in class {class_name}")
            return
        
        # Create method environment
        method_env = {}
        
        # Add 'self' reference
        method_env["self"] = obj
        
        # Add parameters
        for i, param in enumerate(method_info["params"]):
            if i < len(args):
                # Convert string arguments to values if needed
                method_env[param] = self.evaluate_value(args[i], env)
            else:
                # Default value for missing args
                method_env[param] = None
        
        # Save VM state
        saved_env = env.copy()
        
        # Execute method body
        if "body" in method_info:
            # Execute method body in method environment
            for instr in method_info["body"]:
                if instr.startswith("RETURN"):
                    # Handle return instruction
                    if len(instr) > 7:  # "RETURN " + value
                        return_value = self.evaluate_value(instr[7:], method_env)
                        self.vm.result = return_value
                    break
                else:
                    # Execute other instructions in method body
                    # (In a full implementation, we'd recursively execute)
                    print(f"Executing method instruction: {instr}")
        
        # Restore VM state
        env.update(saved_env)
    
    def find_method(self, class_name, method_name):
        """Find a method in a class or its parent classes"""
        # Check if method exists in this class
        if class_name in self.vm.class_registry:
            class_info = self.vm.class_registry[class_name]
            if "methods" in class_info and method_name in class_info["methods"]:
                return class_info["methods"][method_name]
            
            # Check parent class if this class inherits
            if "parent" in class_info and class_info["parent"] != "Object":
                return self.find_method(class_info["parent"], method_name)
        
        # Method not found
        return None
    
    def evaluate_condition(self, condition, env):
        """Evaluate a condition expression and return a boolean result"""
        # Very basic condition evaluation - in a real implementation this would be more sophisticated
        
        # Handle comparison operators
        if " is greater than " in condition:
            left, right = condition.split(" is greater than ", 1)
            left_val = self.get_var_value(left.strip(), env)
            right_val = self.evaluate_value(right.strip(), env)
            return float(left_val) > float(right_val)
            
        elif " is less than " in condition:
            left, right = condition.split(" is less than ", 1)
            left_val = self.get_var_value(left.strip(), env)
            right_val = self.evaluate_value(right.strip(), env)
            return float(left_val) < float(right_val)
            
        elif " is equal to " in condition:
            left, right = condition.split(" is equal to ", 1)
            left_val = self.get_var_value(left.strip(), env)
            right_val = self.evaluate_value(right.strip(), env)
            return left_val == right_val
            
        # Handle boolean operators
        elif " and " in condition:
            left, right = condition.split(" and ", 1)
            return self.evaluate_condition(left, env) and self.evaluate_condition(right, env)
            
        elif " or " in condition:
            left, right = condition.split(" or ", 1)
            return self.evaluate_condition(left, env) and self.evaluate_condition(right, env)
            
        elif condition.startswith("not "):
            return not self.evaluate_condition(condition[4:], env)
            
        # Handle direct boolean values
        elif condition.lower() == "true":
            return True
            
        elif condition.lower() == "false":
            return False
        
        # Default to falsy
        return False
    
    def evaluate_value(self, value_expr, env):
        """Evaluate a value expression, which could be a variable, literal, or simple expression"""
        # Trim whitespace
        value_expr = value_expr.strip()
        
        # Handle string literals
        if (value_expr.startswith('"') and value_expr.endswith('"')) or (value_expr.startswith("'") and value_expr.endswith("'")):
            return value_expr[1:-1]
        
        # Handle numeric literals
        try:
            return int(value_expr)
        except ValueError:
            try:
                return float(value_expr)
            except ValueError:
                pass
        
        # Handle lists
        if value_expr.startswith('[') and value_expr.endswith(']'):
            items_str = value_expr[1:-1].strip()
            if not items_str:
                return []
            # Parse items (very basic implementation)
            items = []
            for item_str in items_str.split(','):
                items.append(self.evaluate_value(item_str.strip(), env))
            return items
        
        # Handle variables
        return self.get_var_value(value_expr, env)
    
    def get_var_value(self, var_name, env):
        """Get a variable's value from the environment"""
        if var_name in env:
            return env[var_name]
        
        # For properties (obj.prop)
        if '.' in var_name:
            obj_name, prop_name = var_name.split('.', 1)
            if obj_name in env and isinstance(env[obj_name], dict) and "properties" in env[obj_name]:
                if prop_name in env[obj_name]["properties"]:
                    return env[obj_name]["properties"][prop_name]
        
        # Not found
        return None
