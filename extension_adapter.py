#!/usr/bin/env python3
"""
Extension Adapter for English Programming

This adapter provides compatibility between extension bytecode and the fixed VM implementation,
maintaining the existing conditional logic improvements while adding support for:
- Advanced control flow (while loops, for-each loops)
- OOP features
- Module system

The adapter translates extension bytecode into compatible instructions for the VM.
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append('/Users/jithinpothireddy/Downloads/English Programming')

# Import VM components
from english_programming.src.vm.improved_nlvm import ImprovedNLVM

class ExtensionAdapter:
    """
    Adapter for English Programming Extensions
    
    This class provides translation between extension bytecode and the VM's
    supported instruction set, ensuring compatibility with the fixed VM.
    """
    
    def __init__(self, vm=None):
        """
        Initialize the adapter
        
        Args:
            vm: An instance of ImprovedNLVM, if None, creates a new one
        """
        self.vm = vm if vm else ImprovedNLVM(debug=True)
        
        # Register extension instructions
        self._register_extensions()
        
        # Map extension bytecode to compatible instructions
        self._define_instruction_mapping()
    
    def _register_extensions(self):
        """Register extension command handlers with the VM"""
        original_execute_instructions = self.vm.execute_instructions
        
        # Override the execute_instructions method
        def enhanced_execute_instructions(instructions, env):
            """Enhanced execute_instructions with extension support"""
            translated_instructions = []
            
            # Translate extension instructions
            i = 0
            while i < len(instructions):
                instruction = instructions[i]
                parts = instruction.split()
                
                # Handle extensions
                if parts and parts[0] in self.instruction_mapping:
                    # Get the translation function
                    translator = self.instruction_mapping[parts[0]]
                    
                    # Call the translator to get compatible instructions
                    compatible_instructions, skip = translator(instructions, i, env)
                    
                    # Add the compatible instructions
                    translated_instructions.extend(compatible_instructions)
                    
                    # Skip ahead if needed
                    i += skip
                else:
                    # Pass through unchanged
                    translated_instructions.append(instruction)
                    i += 1
            
            # Call the original method with translated instructions
            return original_execute_instructions(translated_instructions, env)
        
        # Replace the original method
        self.vm.execute_instructions = enhanced_execute_instructions
    
    def _define_instruction_mapping(self):
        """Define mapping from extension bytecode to compatible VM instructions"""
        self.instruction_mapping = {
            # Variable operations
            "STORE_VAR": self._translate_store_var,
            "GET_VAR": self._translate_get_var,
            
            # Control flow
            "WHILE_LESS_EQUAL": self._translate_while_less_equal,
            "WHILE_LESS": self._translate_while_less,
            "WHILE_GREATER_EQUAL": self._translate_while_greater_equal,
            "WHILE_GREATER": self._translate_while_greater,
            "WHILE_EQUAL": self._translate_while_equal,
            "WHILE_NOT_EQUAL": self._translate_while_not_equal,
            "FOR_EACH": self._translate_for_each,
            "FOR_RANGE": self._translate_for_range,
            
            # OOP operations
            "CREATE_CLASS": self._translate_create_class,
            "CREATE_OBJECT": self._translate_create_object,
            "CALL_METHOD": self._translate_call_method,
            
            # Module operations
            "IMPORT_MODULE": self._translate_import_module,
            "EXPORT_SYMBOL": self._translate_export_symbol
        }
    
    # Variable operation translators
    def _translate_store_var(self, instructions, index, env):
        """Translate STORE_VAR to compatible VM instructions"""
        # STORE_VAR name value
        parts = instructions[index].split()
        if len(parts) >= 3:
            var_name = parts[1]
            value = " ".join(parts[2:])  # Join in case value has spaces
            
            # Store directly in environment
            try:
                # Try to convert to numerical value if possible
                if value.isdigit():
                    env[var_name] = int(value)
                elif value.replace('.', '', 1).isdigit():
                    env[var_name] = float(value)
                else:
                    # Handle string values (with or without quotes)
                    if value.startswith('"') and value.endswith('"'):
                        env[var_name] = value[1:-1]  # Remove quotes
                    else:
                        # Could be a reference to another variable
                        if value in env:
                            env[var_name] = env[value]
                        else:
                            env[var_name] = value
            except Exception as e:
                print(f"Warning: Error storing variable {var_name}: {str(e)}")
                env[var_name] = value
        
        # Return empty list (already handled) and skip 1 instruction
        return [], 1
    
    def _translate_get_var(self, instructions, index, env):
        """Translate GET_VAR to compatible VM instructions"""
        # GET_VAR source_var target_var
        parts = instructions[index].split()
        if len(parts) >= 3:
            source_var = parts[1]
            target_var = parts[2]
            
            if source_var in env:
                env[target_var] = env[source_var]
        
        # Return empty list and skip 1 instruction
        return [], 1
    
    # Control flow translators
    def _translate_while_less_equal(self, instructions, index, env):
        """Translate WHILE_LESS_EQUAL to compatible VM instructions"""
        # Find the corresponding END instruction
        parts = instructions[index].split()
        if len(parts) >= 3:
            var_name = parts[1]
            limit = parts[2]
            
            # Find the matching END
            end_index = self._find_matching_end(instructions, index)
            if end_index > index:
                # Extract the loop body
                loop_body = instructions[index+1:end_index]
                
                # Execute loop while condition is true
                try:
                    # Max iterations safeguard
                    max_iterations = 1000
                    iteration_count = 0
                    
                    # Convert values - handle both direct literals and variable references
                    var_value = env.get(var_name, 0)
                    if isinstance(var_value, str) and var_value.isdigit():
                        var_value = int(var_value)
                    
                    if limit.isdigit():
                        limit_value = int(limit)
                    else:
                        limit_value = env.get(limit, 0)
                        if isinstance(limit_value, str) and limit_value.isdigit():
                            limit_value = int(limit_value)
                    
                    print(f"Debug - Starting while loop: {var_name}({var_value}) <= {limit}({limit_value})")
                    
                    while var_value <= limit_value and iteration_count < max_iterations:
                        # Execute loop body
                        print(f"Debug - Loop iteration {iteration_count+1}: {var_name} = {var_value}")
                        self.vm.execute_instructions(loop_body, env)
                        
                        # Update variable value for next iteration - must get fresh value from env
                        var_value = env.get(var_name, 0)
                        if isinstance(var_value, str) and var_value.isdigit():
                            var_value = int(var_value)
                        
                        # Safety counter
                        iteration_count += 1
                        
                        if iteration_count >= max_iterations:
                            print(f"Warning: Loop exceeded maximum iterations ({max_iterations}), breaking to prevent infinite loop")
                            break
                except Exception as e:
                    print(f"Warning: Error in while loop: {str(e)}")
            
            # Skip to after the END instruction
            return [], end_index - index + 1
        
        return [], 1
    
    def _translate_while_less(self, instructions, index, env):
        """Translate WHILE_LESS to compatible VM instructions"""
        # Similar to _translate_while_less_equal but with < instead of <=
        parts = instructions[index].split()
        if len(parts) >= 3:
            var_name = parts[1]
            limit = parts[2]
            
            end_index = self._find_matching_end(instructions, index)
            if end_index > index:
                loop_body = instructions[index+1:end_index]
                
                try:
                    var_value = env.get(var_name, 0)
                    limit_value = int(limit) if limit.isdigit() else env.get(limit, 0)
                    
                    while var_value < limit_value:
                        self.vm.execute_instructions(loop_body, env)
                        var_value = env.get(var_name, 0)
                except Exception as e:
                    print(f"Warning: Error in while loop: {str(e)}")
            
            return [], end_index - index + 1
        
        return [], 1
    
    def _translate_while_greater_equal(self, instructions, index, env):
        """Translate WHILE_GREATER_EQUAL to compatible VM instructions"""
        parts = instructions[index].split()
        if len(parts) >= 3:
            var_name = parts[1]
            limit = parts[2]
            
            end_index = self._find_matching_end(instructions, index)
            if end_index > index:
                loop_body = instructions[index+1:end_index]
                
                try:
                    var_value = env.get(var_name, 0)
                    limit_value = int(limit) if limit.isdigit() else env.get(limit, 0)
                    
                    while var_value >= limit_value:
                        self.vm.execute_instructions(loop_body, env)
                        var_value = env.get(var_name, 0)
                except Exception as e:
                    print(f"Warning: Error in while loop: {str(e)}")
            
            return [], end_index - index + 1
        
        return [], 1
    
    def _translate_while_greater(self, instructions, index, env):
        """Translate WHILE_GREATER to compatible VM instructions"""
        parts = instructions[index].split()
        if len(parts) >= 3:
            var_name = parts[1]
            limit = parts[2]
            
            end_index = self._find_matching_end(instructions, index)
            if end_index > index:
                loop_body = instructions[index+1:end_index]
                
                try:
                    var_value = env.get(var_name, 0)
                    limit_value = int(limit) if limit.isdigit() else env.get(limit, 0)
                    
                    while var_value > limit_value:
                        self.vm.execute_instructions(loop_body, env)
                        var_value = env.get(var_name, 0)
                except Exception as e:
                    print(f"Warning: Error in while loop: {str(e)}")
            
            return [], end_index - index + 1
        
        return [], 1
    
    def _translate_while_equal(self, instructions, index, env):
        """Translate WHILE_EQUAL to compatible VM instructions"""
        parts = instructions[index].split()
        if len(parts) >= 3:
            var_name = parts[1]
            value = parts[2]
            
            end_index = self._find_matching_end(instructions, index)
            if end_index > index:
                loop_body = instructions[index+1:end_index]
                
                try:
                    var_value = env.get(var_name)
                    compare_value = value if not value.isdigit() else int(value)
                    if value in env:
                        compare_value = env[value]
                    
                    while var_value == compare_value:
                        self.vm.execute_instructions(loop_body, env)
                        var_value = env.get(var_name)
                except Exception as e:
                    print(f"Warning: Error in while loop: {str(e)}")
            
            return [], end_index - index + 1
        
        return [], 1
    
    def _translate_while_not_equal(self, instructions, index, env):
        """Translate WHILE_NOT_EQUAL to compatible VM instructions"""
        parts = instructions[index].split()
        if len(parts) >= 3:
            var_name = parts[1]
            value = parts[2]
            
            end_index = self._find_matching_end(instructions, index)
            if end_index > index:
                loop_body = instructions[index+1:end_index]
                
                try:
                    var_value = env.get(var_name)
                    compare_value = value if not value.isdigit() else int(value)
                    if value in env:
                        compare_value = env[value]
                    
                    while var_value != compare_value:
                        self.vm.execute_instructions(loop_body, env)
                        var_value = env.get(var_name)
                except Exception as e:
                    print(f"Warning: Error in while loop: {str(e)}")
            
            return [], end_index - index + 1
        
        return [], 1
    
    def _translate_for_each(self, instructions, index, env):
        """Translate FOR_EACH to compatible VM instructions"""
        # FOR_EACH item_var collection_var
        parts = instructions[index].split()
        if len(parts) >= 3:
            item_var = parts[1]
            collection_var = parts[2]
            
            end_index = self._find_matching_end(instructions, index)
            if end_index > index:
                loop_body = instructions[index+1:end_index]
                
                try:
                    collection = env.get(collection_var, [])
                    
                    # Handle different collection types
                    if isinstance(collection, str):
                        # For string, iterate over characters
                        for item in collection:
                            env[item_var] = item
                            self.vm.execute_instructions(loop_body, env)
                    elif isinstance(collection, list) or isinstance(collection, tuple):
                        # For list/tuple, iterate over items
                        for item in collection:
                            env[item_var] = item
                            self.vm.execute_instructions(loop_body, env)
                    elif isinstance(collection, dict):
                        # For dict, iterate over keys
                        for key in collection:
                            env[item_var] = key
                            self.vm.execute_instructions(loop_body, env)
                    else:
                        print(f"Warning: Cannot iterate over {collection_var} (type: {type(collection)})")
                except Exception as e:
                    print(f"Warning: Error in for-each loop: {str(e)}")
            
            return [], end_index - index + 1
        
        return [], 1
    
    def _translate_for_range(self, instructions, index, env):
        """Translate FOR_RANGE to compatible VM instructions"""
        # FOR_RANGE counter_var start end [step]
        parts = instructions[index].split()
        if len(parts) >= 4:
            counter_var = parts[1]
            start = parts[2]
            end = parts[3]
            step = parts[4] if len(parts) >= 5 else "1"
            
            end_index = self._find_matching_end(instructions, index)
            if end_index > index:
                loop_body = instructions[index+1:end_index]
                
                try:
                    start_val = int(start) if start.isdigit() else env.get(start, 0)
                    end_val = int(end) if end.isdigit() else env.get(end, 0)
                    step_val = int(step) if step.isdigit() else env.get(step, 1)
                    
                    for i in range(start_val, end_val, step_val):
                        env[counter_var] = i
                        self.vm.execute_instructions(loop_body, env)
                except Exception as e:
                    print(f"Warning: Error in for-range loop: {str(e)}")
            
            return [], end_index - index + 1
        
        return [], 1
    
    # OOP translators
    def _translate_create_class(self, instructions, index, env):
        """Translate CREATE_CLASS to compatible VM instructions"""
        # CREATE_CLASS class_name [parent_class]
        parts = instructions[index].split()
        if len(parts) >= 2:
            class_name = parts[1]
            parent_class = parts[2] if len(parts) >= 3 else None
            
            # Find the class body (up to END)
            end_index = self._find_matching_end(instructions, index)
            if end_index > index:
                class_body = instructions[index+1:end_index]
                
                # Create class dictionary
                class_dict = {
                    "methods": {},
                    "parent": parent_class
                }
                
                # Process class body to find method definitions
                i = 0
                while i < len(class_body):
                    if class_body[i].startswith("METHOD"):
                        method_parts = class_body[i].split()
                        if len(method_parts) >= 2:
                            method_name = method_parts[1]
                            
                            # Find the method body
                            method_end = self._find_matching_end(class_body, i)
                            if method_end > i:
                                method_body = class_body[i+1:method_end]
                                
                                # Store method in class
                                class_dict["methods"][method_name] = method_body
                                
                                # Skip to after method end
                                i = method_end + 1
                                continue
                    
                    i += 1
                
                # Store class in environment
                env[class_name] = class_dict
            
            # Skip to after the class definition
            return [], end_index - index + 1
        
        return [], 1
    
    def _translate_create_object(self, instructions, index, env):
        """Translate CREATE_OBJECT to compatible VM instructions"""
        # CREATE_OBJECT class_name object_name [arg1 arg2 ...]
        parts = instructions[index].split()
        if len(parts) >= 3:
            class_name = parts[1]
            object_name = parts[2]
            args = parts[3:] if len(parts) > 3 else []
            
            # Check if class exists
            if class_name in env and isinstance(env[class_name], dict) and "methods" in env[class_name]:
                class_dict = env[class_name]
                
                # Create object dictionary
                object_dict = {
                    "class": class_name,
                    "properties": {}
                }
                
                # Call constructor if available
                if "constructor" in class_dict["methods"]:
                    # Create temp env with self and args
                    temp_env = env.copy()
                    temp_env["self"] = object_dict
                    
                    # Assign args to constructor parameters
                    for i, arg in enumerate(args):
                        temp_env[f"arg{i}"] = arg
                    
                    # Execute constructor
                    constructor_body = class_dict["methods"]["constructor"]
                    self.vm.execute_instructions(constructor_body, temp_env)
                    
                    # Update object with any properties set in constructor
                    object_dict = temp_env["self"]
                
                # Store object in environment
                env[object_name] = object_dict
        
        return [], 1
    
    def _translate_call_method(self, instructions, index, env):
        """Translate CALL_METHOD to compatible VM instructions"""
        # CALL_METHOD object_name method_name [result_var]
        parts = instructions[index].split()
        if len(parts) >= 3:
            object_name = parts[1]
            method_name = parts[2]
            result_var = parts[3] if len(parts) >= 4 else None
            
            # Check if object exists
            if object_name in env and isinstance(env[object_name], dict) and "class" in env[object_name]:
                object_dict = env[object_name]
                class_name = object_dict["class"]
                
                # Check if class exists
                if class_name in env and isinstance(env[class_name], dict) and "methods" in env[class_name]:
                    class_dict = env[class_name]
                    
                    # Check if method exists
                    if method_name in class_dict["methods"]:
                        # Create temp env with self
                        temp_env = env.copy()
                        temp_env["self"] = object_dict
                        
                        # Execute method
                        method_body = class_dict["methods"][method_name]
                        result = self.vm.execute_instructions(method_body, temp_env)
                        
                        # Update object with any property changes
                        env[object_name] = temp_env["self"]
                        
                        # Store result if requested
                        if result_var and result is not None:
                            env[result_var] = result
                    else:
                        print(f"Warning: Method {method_name} not found in class {class_name}")
                else:
                    print(f"Warning: Class {class_name} not found for object {object_name}")
            else:
                print(f"Warning: Object {object_name} not found")
        
        return [], 1
    
    # Module system translators
    def _translate_import_module(self, instructions, index, env):
        """Translate IMPORT_MODULE to compatible VM instructions"""
        # IMPORT_MODULE module_name [alias]
        parts = instructions[index].split()
        if len(parts) >= 2:
            module_name = parts[1]
            alias = parts[2] if len(parts) >= 3 else module_name
            
            # Find module file
            module_file = f"{module_name}.nlc"
            if os.path.exists(module_file):
                # Create a new VM to execute module
                module_vm = ImprovedNLVM(debug=False)
                
                # Execute module
                module_vm.execute(module_file)
                
                # Get exported symbols from module
                exported = {}
                for key, value in module_vm.env.items():
                    if key.startswith("_export_"):
                        export_name = key[8:]  # Remove _export_ prefix
                        exported[export_name] = value
                
                # Add module to environment
                env[alias] = exported
            else:
                print(f"Warning: Module {module_name} not found")
        
        return [], 1
    
    def _translate_export_symbol(self, instructions, index, env):
        """Translate EXPORT_SYMBOL to compatible VM instructions"""
        # EXPORT_SYMBOL symbol_name
        parts = instructions[index].split()
        if len(parts) >= 2:
            symbol_name = parts[1]
            
            # Check if symbol exists
            if symbol_name in env:
                # Add to exports
                env[f"_export_{symbol_name}"] = env[symbol_name]
            else:
                print(f"Warning: Symbol {symbol_name} not found for export")
        
        return [], 1
    
    # Helper methods
    def _find_matching_end(self, instructions, start_index):
        """Find the matching END instruction for a block"""
        nesting_level = 1
        i = start_index + 1
        
        while i < len(instructions):
            # Check for nested blocks
            if instructions[i].split()[0] in [
                "IF", "IF_GREATER", "IF_LESS", "IF_EQUAL", "IF_NOT_EQUAL",
                "WHILE_LESS_EQUAL", "WHILE_LESS", "WHILE_GREATER_EQUAL", "WHILE_GREATER",
                "WHILE_EQUAL", "WHILE_NOT_EQUAL", "FOR_EACH", "FOR_RANGE",
                "CREATE_CLASS", "METHOD"
            ]:
                nesting_level += 1
            
            # Check for end of block
            elif instructions[i].split()[0] == "END":
                nesting_level -= 1
                if nesting_level == 0:
                    return i
            
            i += 1
        
        # No matching END found
        return len(instructions)
    
    def write_bytecode_file(self, bytecode, filename):
        """Write bytecode to a file"""
        with open(filename, "w") as f:
            f.write("\n".join(bytecode))
        return filename
    
    def create_test_bytecode(self, test_type="basic", output_file=None):
        """Create bytecode for testing the extension adapter"""
        if output_file is None:
            output_file = f"extension_test_{test_type}.nlc"
        
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
            
            "while_loop": [
                "STORE_VAR counter 1",
                "STORE_VAR sum 0",
                "STORE_VAR increment 1",
                "PRINT \"Testing while loop:\"",
                "WHILE_LESS_EQUAL counter 5",
                "PRINT counter",
                "ADD counter sum sum",
                "ADD counter increment counter",
                "END",
                "PRINT \"Final sum is:\"",
                "PRINT sum"
            ],
            
            "for_loop": [
                "STORE_VAR fruits [\"apple\", \"banana\", \"cherry\"]",
                "PRINT \"Testing for-each loop:\"",
                "FOR_EACH fruit fruits",
                "PRINT fruit",
                "END",
                "PRINT \"Testing for-range loop:\"",
                "FOR_RANGE i 1 5",
                "PRINT i",
                "END"
            ],
            
            "oop": [
                "CREATE_CLASS Person",
                "METHOD constructor",
                "STORE_VAR self.name arg0",
                "STORE_VAR self.age arg1",
                "END",
                "METHOD greet",
                "PRINT \"Hello, my name is\"",
                "PRINT self.name",
                "PRINT \"and I am\"",
                "PRINT self.age",
                "PRINT \"years old.\"",
                "END",
                "END",
                "CREATE_OBJECT Person john \"John\" 30",
                "CALL_METHOD john greet"
            ]
        }
        
        # Write bytecode to file
        return self.write_bytecode_file(bytecodes[test_type], output_file)
    
    def run_test(self, test_type="basic"):
        """Run a test of the extension adapter"""
        print("=" * 60)
        print(f"EXTENSION ADAPTER TEST: {test_type.upper()}")
        print("=" * 60)
        
        try:
            # Create test bytecode
            bytecode_file = self.create_test_bytecode(test_type)
            
            print(f"Created bytecode file: {bytecode_file}")
            
            # Execute the bytecode
            result = self.vm.execute(bytecode_file)
            
            # Show final environment
            print("\nFinal environment variables:")
            print("-" * 40)
            for var_name, value in self.vm.env.items():
                if not var_name.startswith("_"):
                    print(f"{var_name} = {value}")
            
            # Clean up
            if os.path.exists(bytecode_file):
                os.remove(bytecode_file)
            
            print(f"\n{test_type.capitalize()} test completed successfully!")
            return True
        except Exception as e:
            print(f"Test failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

# Main entry point
if __name__ == "__main__":
    adapter = ExtensionAdapter()
    
    if len(sys.argv) > 1:
        test_type = sys.argv[1]
    else:
        test_type = "basic"
    
    adapter.run_test(test_type)
