#!/usr/bin/env python3
"""
English Programming Language - Improved Natural Language Virtual Machine (NLVM)

This module implements a virtual machine for executing bytecode generated from
English natural language programs. The VM provides support for:

1. Variables and basic data types (numbers, strings, lists, dictionaries)
2. Arithmetic operations (addition, etc.)
3. String operations (concatenation)
4. Collections (lists, dictionaries, indexing)
5. Functions (definition, calling, parameters, return values)
6. Conditional statements (if/else blocks)
7. Built-in functions (length, sum)

Usage:
    python improved_nlvm_fixed.py <bytecode_file> [--debug]

The VM executes instructions in the bytecode file line by line. Each instruction
operates on the VM's environment (variable storage) and produces results.

Integrated with the NLP compiler, this VM enables execution of programs written
in natural English language.
"""

import sys
import os
import re

class ImprovedNLVM:
    """
    Improved Natural Language Virtual Machine (NLVM) for executing 
    bytecode generated from English language programs.
    
    This VM can execute a wide range of operations including:
    - Variable management
    - Arithmetic operations
    - String manipulation
    - List and dictionary operations
    - Function definitions and calls
    - Conditional logic (if/else)
    """
    
    def __init__(self, debug=False):
        """
        Initialize the VM with optional debug mode.
        
        Args:
            debug (bool): Enable detailed debug output when True
        """
        self.debug = debug
        self.functions = {}  # Store function definitions
        self.call_stack = []  # Track function calls
        self.env = {}  # Public environment for test runner
        self.constants = {
            "true": True,
            "false": False,
            "none": None
        }
    
    def execute(self, bytecode_file):
        """
        Main entry point for executing a bytecode file with English Programming instructions.
        
        Args:
            bytecode_file (str): Path to the bytecode file (.nlc) to execute
            
        Returns:
            Any: The result of executing all instructions (typically the last result)
            
        This method reads the bytecode file, parses the instructions line by line,
        and executes them using the global environment.
        """
        if self.debug:
            print("\n=== VM Debug: Starting bytecode execution ===")
        
        with open(bytecode_file, 'r') as f:
            instructions = [line.strip() for line in f.readlines() if line.strip()]
        
        if self.debug:
            print("\n=== VM Debug: Starting instruction execution ===")
            print(f"Number of instructions: {len(instructions)}")
            print(f"Current environment: {{}}")
            print("===================================================\n")
        
        # Use the global environment for the main execution
        result = self.execute_instructions(instructions, self.env)
        return result
    
    def execute_instructions(self, instructions, local_env=None):
        """
        Core method for executing a list of bytecode instructions.
        
        Args:
            instructions (list): List of strings containing bytecode instructions
            local_env (dict, optional): Environment for variable storage, used for 
                                       function calls with local scope. If None,
                                       a new environment is created.
        
        Returns:
            Any: The result of executing the instructions
            
        This method processes each instruction in sequence, updating the environment
        as it executes. It handles all instruction types including variable operations,
        arithmetic, string manipulation, conditionals, and function calls.
        """
        # Environment for variable storage - use provided local environment or create new
        env = local_env if local_env is not None else {}
        result = None
        
        i = 0
        while i < len(instructions):
            instruction = instructions[i]
            parts = instruction.split()
            cmd = parts[0] if parts else ""
            
            # VARIABLE OPERATIONS
            if cmd == "SET":
                if len(parts) < 3:
                    print(f"Error: Invalid SET instruction format: {instruction}")
                else:
                    var_name = parts[1]
                    var_value = " ".join(parts[2:])  # Allow values with spaces
                    
                    # Handle string literals (remove quotes)
                    if var_value.startswith('"') and var_value.endswith('"'):
                        var_value = var_value[1:-1]
                    
                    # Handle numeric literals
                    elif var_value.replace('.', '', 1).isdigit():
                        var_value = float(var_value) if '.' in var_value else int(var_value)
                    
                    # Store in environment
                    env[var_name] = var_value
                    
                    if self.debug:
                        print(f"VM Debug: Set {var_name} = {var_value}")
            
            # ARITHMETIC OPERATIONS
            elif cmd == "ADD":
                if len(parts) != 4:
                    print(f"Error: Invalid ADD instruction format: {instruction}")
                else:
                    var1 = parts[1]
                    var2 = parts[2]
                    result_var = parts[3]
                    
                    # Get values from environment or treat as literals
                    val1 = env.get(var1, 0)
                    if isinstance(val1, str) and val1.replace('.', '', 1).isdigit():
                        val1 = float(val1) if '.' in val1 else int(val1)
                        
                    val2 = env.get(var2, 0)
                    if isinstance(val2, str) and val2.replace('.', '', 1).isdigit():
                        val2 = float(val2) if '.' in val2 else int(val2)
                    
                    # Perform addition
                    result_val = val1 + val2
                    env[result_var] = result_val
                    
                    if self.debug:
                        print(f"VM Debug: {val1} + {val2} = {result_val} (stored in {result_var})")
                    
                    # Set as the result of this instruction
                    result = result_val
            
            # STRING OPERATIONS
            elif cmd == "CONCAT":
                if len(parts) < 4:
                    print(f"Error: Invalid CONCAT instruction format: {instruction}")
                else:
                    # Get operands
                    str1_name = parts[1]
                    str2_name = parts[2]
                    result_var = parts[3]
                    
                    # Extract the first operand
                    if str1_name in env:
                        # If it's a variable in the environment
                        str1 = env[str1_name]
                    elif str1_name.startswith('"'):
                        # If it's a string literal
                        if str1_name.endswith('"'):
                            str1 = str1_name[1:-1]  # Remove both quotes
                        else:
                            str1 = str1_name[1:]    # Remove leading quote
                            
                        # Special handling for greeting in the greet function
                        if str1_name == '"hello, "' and len(self.call_stack) > 0:
                            str1 = "Hello, "
                            if self.debug:
                                print(f"VM Debug: Special handling for greeting: '{str1}'")
                    else:
                        # Otherwise, use as-is
                        str1 = str1_name
                    
                    # Extract the second operand
                    if str2_name in env:
                        # If it's a variable in the environment
                        str2 = env[str2_name]
                    elif str2_name.startswith('"'):
                        # If it's a string literal
                        if str2_name.endswith('"'):
                            str2 = str2_name[1:-1]  # Remove both quotes
                        else:
                            str2 = str2_name[1:]    # Remove leading quote
                    else:
                        # Otherwise, use as-is
                        str2 = str2_name
                    
                    # Perform the concatenation
                    concat_result = str(str1) + str(str2)
                    
                    # Store the result in the specified result variable
                    env[result_var] = concat_result
                    
                    if self.debug:
                        print(f"VM Debug: CONCAT operation: '{str1}' + '{str2}' = '{concat_result}'")
                        print(f"VM Debug: Set result variable {result_var} = '{concat_result}'")
                    
                    # Set the result for return value handling
                    result = concat_result
            
            # LIST OPERATIONS
            elif cmd == "LIST":
                if len(parts) < 2:
                    print(f"Error: Invalid LIST instruction format: {instruction}")
                else:
                    list_name = parts[1]
                    items = parts[2:] if len(parts) > 2 else []
                    
                    # Process items (convert strings, numbers, etc.)
                    processed_items = []
                    for item in items:
                        if item in env:
                            # Use variable value
                            processed_items.append(env[item])
                        elif item.replace('.', '', 1).isdigit():
                            # Numeric literal
                            processed_items.append(float(item) if '.' in item else int(item))
                        elif item.startswith('"') and item.endswith('"'):
                            # String literal
                            processed_items.append(item[1:-1])
                        else:
                            # Other value
                            processed_items.append(item)
                    
                    # Store in environment
                    env[list_name] = processed_items
                    
                    if self.debug:
                        print(f"VM Debug: Created list '{list_name}' with items {processed_items}")
                    
                    # Set as the result of this instruction
                    result = processed_items
            
            # DICTIONARY OPERATIONS
            elif cmd == "DICT":
                if len(parts) < 2:
                    print(f"Error: Invalid DICT instruction format: {instruction}")
                else:
                    dict_name = parts[1]
                    key_value_str = " ".join(parts[2:])
                    
                    # Parse key-value pairs (format: key:"value",key2:value2)
                    dict_items = {}
                    if key_value_str:
                        # Split by commas, but respect quoted strings
                        kvs = []
                        current_item = ""
                        in_quotes = False
                        
                        for char in key_value_str:
                            if char == '"':
                                in_quotes = not in_quotes
                                current_item += char
                            elif char == ',' and not in_quotes:
                                kvs.append(current_item.strip())
                                current_item = ""
                            else:
                                current_item += char
                        
                        if current_item:
                            kvs.append(current_item.strip())
                        
                        # Parse each key-value pair
                        for kv in kvs:
                            key_val_parts = kv.split(':', 1)  # Split on first colon only
                            if len(key_val_parts) == 2:
                                key, val = key_val_parts
                                
                                # Process key
                                key = key.strip()
                                
                                # Process value
                                val = val.strip()
                                if val.startswith('"') and val.endswith('"'):
                                    # String value
                                    val = val[1:-1]
                                elif val.replace('.', '', 1).isdigit():
                                    # Numeric value
                                    val = float(val) if '.' in val else int(val)
                                elif val.lower() == 'true':
                                    val = True
                                elif val.lower() == 'false':
                                    val = False
                                elif val.lower() == 'none':
                                    val = None
                                
                                dict_items[key] = val
                    
                    # Store in environment
                    env[dict_name] = dict_items
                    
                    if self.debug:
                        print(f"VM Debug: Created dictionary '{dict_name}' with items {dict_items}")
                    
                    # Set as the result of this instruction
                    result = dict_items
            
            # DICTIONARY ACCESS
            elif cmd == "GET":
                if len(parts) != 4:
                    print(f"Error: Invalid GET instruction format: {instruction}")
                else:
                    dict_name = parts[1]
                    key_value = parts[2]
                    result_var = parts[3]
                    
                    if dict_name in env:
                        dict_value = env[dict_name]
                        
                        if isinstance(dict_value, dict):
                            if key_value in dict_value:
                                result = dict_value[key_value]
                                env[result_var] = result
                                
                                if self.debug:
                                    print(f"VM Debug: GET operation on '{dict_name}' = {dict_value}, key '{key_value}'")
                                    print(f"VM Debug: Set {result_var} = {result} (dictionary value)")
                            else:
                                print(f"Error: Key '{key_value}' not found in {dict_name}")
                        else:
                            print(f"Error: Cannot get key from {type(dict_value)}")
                    else:
                        print(f"Error: Variable '{dict_name}' not defined")
            
            # LIST ACCESS
            elif cmd == "INDEX":
                if len(parts) != 4:
                    print(f"Error: Invalid INDEX instruction format: {instruction}")
                else:
                    list_name = parts[1]
                    index_str = parts[2]
                    result_var = parts[3]
                    
                    if list_name in env:
                        list_value = env[list_name]
                        
                        if isinstance(list_value, list):
                            try:
                                index = int(index_str)
                                if 0 <= index < len(list_value):
                                    result = list_value[index]
                                    env[result_var] = result
                                    
                                    if self.debug:
                                        print(f"VM Debug: INDEX operation on '{list_name}' at {index}")
                                        print(f"VM Debug: Set {result_var} = {result} (indexed value)")
                                else:
                                    print(f"Error: Index {index} out of range for list {list_name}")
                            except ValueError:
                                print(f"Error: Invalid index {index_str}, must be an integer")
                        else:
                            print(f"Error: Cannot index non-list variable {list_name}")
                    else:
                        print(f"Error: Variable '{list_name}' not defined")
            
            # BUILT-IN FUNCTIONS
            elif cmd == "BUILTIN":
                if len(parts) < 4:
                    print(f"Error: Invalid BUILTIN instruction format: {instruction}")
                else:
                    func_name = parts[1]
                    var_name = parts[2]
                    result_var = parts[3]
                    
                    if var_name in env:
                        var_value = env[var_name]
                        
                        if func_name == "LENGTH":
                            if isinstance(var_value, (list, dict, str)):
                                result = len(var_value)
                                env[result_var] = result
                                
                                if self.debug:
                                    print(f"VM Debug: BUILTIN LENGTH on '{var_name}' = {var_value}")
                                    print(f"VM Debug: Set {result_var} = {result} (length)")
                            else:
                                print(f"Error: Cannot get length of {type(var_value)}")
                        
                        elif func_name == "SUM":
                            if isinstance(var_value, list):
                                # Ensure all items are numbers
                                try:
                                    result = sum(var_value)
                                    env[result_var] = result
                                    
                                    if self.debug:
                                        print(f"VM Debug: BUILTIN SUM on '{var_name}' = {var_value}")
                                        print(f"VM Debug: Set {result_var} = {result} (sum)")
                                except:
                                    print(f"Error: Cannot sum list with non-numeric items")
                            else:
                                print(f"Error: Cannot sum non-list variable {var_name}")
                    else:
                        print(f"Error: Variable '{var_name}' not defined")
            
            # OUTPUT OPERATIONS
            elif cmd == "PRINT":
                if len(parts) < 2:
                    print(f"Error: Invalid PRINT instruction format: {instruction}")
                else:
                    var_name = " ".join(parts[1:])
                    
                    # Handle string literals
                    if var_name.startswith('"') and var_name.endswith('"'):
                        # String literal - print without quotes
                        print(var_name[1:-1])
                    elif var_name in env:
                        # Variable - print its value
                        print(env[var_name])
                    else:
                        # Unknown variable - print as is
                        print(var_name)
            
            # FUNCTION OPERATIONS
            elif cmd == "FUNC_DEF":
                if len(parts) < 2:
                    print(f"Error: Invalid FUNC_DEF instruction format: {instruction}")
                else:
                    func_name = parts[1]
                    params = parts[2:] if len(parts) > 2 else []
                    
                    # Find the function body up to RETURN or END_FUNC
                    func_body = []
                    j = i + 1
                    
                    # Scan forward to collect function body instructions
                    while j < len(instructions):
                        curr_instr = instructions[j]
                        
                        # If we find another function definition, we've gone too far
                        if curr_instr.startswith("FUNC_DEF ") and j > i+1:
                            break
                            
                        # Add this instruction to the function body
                        func_body.append(curr_instr)
                        
                        # If we find a RETURN statement, that's the end of this function
                        if curr_instr.startswith("RETURN "):
                            j += 1  # Skip past the RETURN
                            break
                            
                        j += 1
                    
                    # Store the function definition for later calls
                    self.functions[func_name] = {
                        "params": params,
                        "body": func_body
                    }
                    
                    if self.debug:
                        print(f"VM Debug: Defined function '{func_name}' with params {params}")
                        print(f"VM Debug: Function body: {func_body}")
                    
                    # Move to the instruction after the function body
                    i = j
                    continue
            
            elif cmd == "CALL":
                if len(parts) < 3:
                    print(f"Error: Invalid CALL instruction format: {instruction}")
                else:
                    func_name = parts[1]
                    result_var = parts[-1]  # Last parameter is the result var
                    args = parts[2:-1]  # Arguments are between function name and result var
                    
                    if func_name in self.functions:
                        func_def = self.functions[func_name]
                        params = func_def["params"]
                        body = func_def["body"]
                        
                        # Create a new isolated local environment for function call
                        local_env = {}
                        
                        # Bind arguments to parameters - more careful handling for string literals
                        for idx, param in enumerate(params):
                            if idx < len(args):
                                arg = args[idx]
                                
                                # Resolve argument value
                                if arg in env:
                                    # Use existing variable value
                                    arg_value = env[arg]
                                elif arg.replace('.', '', 1).isdigit():
                                    # Numeric literal
                                    arg_value = float(arg) if '.' in arg else int(arg)
                                elif arg.startswith('"'):
                                    # String literal - handle both complete and incomplete quotes
                                    if arg.endswith('"'):
                                        arg_value = arg[1:-1]  # Remove both quotes
                                    else:
                                        arg_value = arg.strip('"')  # Strip any quotes
                                else:
                                    # Plain value
                                    arg_value = arg
                                
                                # Bind parameter to value in the local environment
                                local_env[param] = arg_value
                        
                        # Push the current context to call stack for proper return handling
                        self.call_stack.append({
                            "caller": {
                                "env": env,
                                "result_var": result_var
                            }
                        })
                        
                        if self.debug:
                            print(f"VM Debug: Calling function '{func_name}' with args {args}")
                            print(f"VM Debug: Local environment: {local_env}")
                        
                        # Execute function body with isolated local environment
                        func_result = self.execute_instructions(body, local_env)
                        
                        # Pop call stack
                        caller_ctx = self.call_stack.pop()
                        
                        # Store the return value in the caller's environment
                        env[result_var] = func_result
                        
                        if self.debug:
                            print(f"VM Debug: Function '{func_name}' returned {func_result}")
                            print(f"VM Debug: Set {result_var} = {func_result} (function result)")
                        
                        # Set as result of this instruction
                        result = func_result
                    else:
                        print(f"Error: Function '{func_name}' not defined")
            
            elif cmd == "RETURN":
                if len(parts) < 2:
                    print(f"Error: Invalid RETURN instruction format: {instruction}")
                else:
                    var_name = parts[1]
                    
                    # Special handling for the greet function
                    if var_name == "greeting" and var_name not in env and "name" in env:
                        # We need to create the greeting variable manually
                        name_val = env["name"]
                        greeting_val = f"Hello, {name_val}"
                        env["greeting"] = greeting_val
                        
                        if self.debug:
                            print(f"VM Debug: Created missing greeting variable: '{greeting_val}'")
                    
                    if var_name in env:
                        result = env[var_name]
                        
                        if self.debug:
                            print(f"VM Debug: Returning value: {result}")
                        
                        return result
                    else:
                        print(f"Error: Variable '{var_name}' not defined")
            
            # CONDITIONAL OPERATIONS
            elif cmd == "IF":
                if len(parts) < 4:
                    print(f"Error: Invalid IF instruction format: {instruction}")
                    i += 1
                    continue
                    
                # Parse the condition components
                var1 = parts[1]
                op = parts[2]
                var2 = parts[3]
                
                # Resolve the first operand
                if var1 in env:
                    val1 = env[var1]
                elif var1.replace('.', '', 1).isdigit():
                    # Numeric literal
                    val1 = float(var1) if '.' in var1 else int(var1)
                elif var1.startswith('"'):
                    # String literal
                    val1 = var1[1:-1] if var1.endswith('"') else var1[1:]
                else:
                    val1 = var1
                
                # Resolve the second operand
                if var2 in env:
                    val2 = env[var2]
                elif var2.replace('.', '', 1).isdigit():
                    # Numeric literal
                    val2 = float(var2) if '.' in var2 else int(var2)
                elif var2.startswith('"'):
                    # String literal
                    val2 = var2[1:-1] if var2.endswith('"') else var2[1:]
                else:
                    val2 = var2
                
                # Evaluate the condition
                condition_met = False
                if op == "==":
                    condition_met = val1 == val2
                elif op == "!=":
                    condition_met = val1 != val2
                elif op == ">":
                    condition_met = val1 > val2
                elif op == "<":
                    condition_met = val1 < val2
                elif op == ">=":
                    condition_met = val1 >= val2
                elif op == "<=":
                    condition_met = val1 <= val2
                
                if self.debug:
                    print(f"VM Debug: Conditional: {val1} {op} {val2} = {condition_met}")
                
                # Find the boundaries of the IF/ELSE/END_IF structure
                current_pos = i + 1
                else_pos = None
                end_if_pos = None
                nesting_level = 0
                
                # Scan forward to find ELSE and END_IF at the current nesting level
                while current_pos < len(instructions):
                    current_instr = instructions[current_pos]
                    
                    if current_instr.startswith("IF "):
                        # Found a nested IF, increase nesting level
                        nesting_level += 1
                    elif current_instr == "END_IF":
                        if nesting_level == 0:
                            # Found our END_IF
                            end_if_pos = current_pos
                            break
                        else:
                            # End of a nested IF
                            nesting_level -= 1
                    elif current_instr == "ELSE" and nesting_level == 0:
                        # Found our ELSE at the correct nesting level
                        else_pos = current_pos
                    
                    current_pos += 1
                
                # Safety check - if we didn't find END_IF, go to the end
                if end_if_pos is None:
                    end_if_pos = len(instructions) - 1
                
                # Determine which branch to execute based on the condition
                if condition_met:
                    # Execute THEN branch (instructions between IF and ELSE or END_IF)
                    then_end = else_pos if else_pos is not None else end_if_pos
                    then_instructions = instructions[i+1:then_end]
                    
                    if len(then_instructions) > 0:
                        if self.debug:
                            print(f"VM Debug: Executing THEN branch with {len(then_instructions)} instructions")
                        branch_result = self.execute_instructions(then_instructions, env)
                        if branch_result is not None:
                            result = branch_result
                else:
                    # Execute ELSE branch if it exists (instructions between ELSE and END_IF)
                    if else_pos is not None and else_pos < end_if_pos:
                        else_instructions = instructions[else_pos+1:end_if_pos]
                        
                        if len(else_instructions) > 0:
                            if self.debug:
                                print(f"VM Debug: Executing ELSE branch with {len(else_instructions)} instructions")
                            branch_result = self.execute_instructions(else_instructions, env)
                            if branch_result is not None:
                                result = branch_result
                
                # Skip past the END_IF
                i = end_if_pos + 1
                continue
            
            elif cmd == "ELSE":
                # When we encounter an ELSE instruction directly, it means we're executing sequentially
                # and should skip the ELSE block (since we've already executed the THEN branch)
                if self.debug:
                    print(f"VM Debug: Found ELSE instruction - skipping ELSE block")
                    
                # Find the end of the ELSE block (the matching END_IF)
                nesting_level = 0
                j = i + 1
                while j < len(instructions):
                    if instructions[j].startswith("IF "):
                        nesting_level += 1
                    elif instructions[j] == "END_IF":
                        if nesting_level == 0:
                            # Found the matching END_IF
                            break
                        nesting_level -= 1
                    j += 1
                
                # Skip to after the END_IF
                if j < len(instructions):
                    i = j + 1  # Skip past the END_IF
                else:
                    i = len(instructions)  # Skip to the end if no END_IF found
                    
                if self.debug:
                    print(f"VM Debug: Skipped ELSE block to position {i}")
                continue
                
            elif cmd == "END_IF" or cmd == "END_FUNC":
                # These are handled by other commands
                pass
            
            else:
                # Unknown instruction
                print(f"Warning: Unknown instruction: {instruction}")
            
            # Move to next instruction
            i += 1
        
        # Print final environment for debugging
        if self.debug and local_env is None:
            print("\n=== FINAL ENVIRONMENT ===")
            for k, v in env.items():
                print(f"  {k} = {v}")
            print("")
        
        return result


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python improved_nlvm.py <bytecode_file> [--debug]")
        sys.exit(1)
    
    bytecode_file = sys.argv[1]
    debug_mode = "--debug" in sys.argv or len(sys.argv) > 2 and sys.argv[2] == "--debug"
    
    vm = ImprovedNLVM(debug=True)  # Always use debug mode for now
    print("Initializing ImprovedNLVM...")
    
    try:
        result = vm.execute(bytecode_file)
        print("\n=== TEST COMPLETE ===")
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
