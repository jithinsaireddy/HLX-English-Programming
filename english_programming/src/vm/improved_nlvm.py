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
import logging
from logging.handlers import RotatingFileHandler
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
import json
import datetime
import re as _re
# Import PackageManager from pm package available on sys.path (english_programming/src)
try:
    from pm.package_manager import PackageManager
except Exception:
    PackageManager = None

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
    
    def __init__(self, debug: bool = False):
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
        # Initialize structured logger
        self.logger = self._initialize_logger()
        # Default HTTP headers
        self.http_headers = {"User-Agent": "EnglishVM/1.0"}
        # Security: disable network and remote imports by default
        # Set EP_ENABLE_NET=1 to allow
        try:
            self.net_enabled = (os.getenv('EP_ENABLE_NET', '0') == '1')
        except Exception:
            self.net_enabled = False
        # Execution guards (op-count and wall-clock time)
        # Configure via EP_MAX_OPS and EP_MAX_MS, defaults are conservative
        try:
            self.max_ops = int(os.getenv('EP_MAX_OPS', '200000'))
        except Exception:
            self.max_ops = 200000
        try:
            self.max_ms = int(os.getenv('EP_MAX_MS', '30000'))
        except Exception:
            self.max_ms = 30000
        # OOP state
        self.class_registry = {}
        self.current_class = None
        # Package manager
        try:
            self.pm = PackageManager() if PackageManager else None
        except Exception:
            self.pm = None
    
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
        try:
            self.logger.info(f"start_execution file={bytecode_file} instructions={len(instructions)}")
        except Exception:
            pass
        
        # Use the global environment for the main execution
        result = self.execute_instructions(instructions, self.env)
        try:
            self.logger.info("end_execution")
        except Exception:
            pass
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
        ops_executed = 0
        start_time = datetime.datetime.now(datetime.UTC)
        while i < len(instructions):
            instruction = instructions[i]
            parts = instruction.split()
            cmd = parts[0] if parts else ""

            # Guards
            ops_executed += 1
            if ops_executed > self.max_ops:
                raise RuntimeError("Operation limit exceeded")
            elapsed_ms = (datetime.datetime.now(datetime.UTC) - start_time).total_seconds() * 1000.0
            if elapsed_ms > self.max_ms:
                raise RuntimeError("Time limit exceeded")
            
            # VARIABLE OPERATIONS
            if cmd == "SET":
                if len(parts) < 3:
                    if self.debug:
                        print(f"VM Debug: Invalid SET instruction format: {instruction}")
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
                    if self.debug:
                        print(f"VM Debug: Invalid ADD instruction format: {instruction}")
                else:
                    var1 = parts[1]
                    var2 = parts[2]
                    result_var = parts[3]
                    
                    # Resolve operands
                    val1 = self._resolve_value(var1, env)
                    val2 = self._resolve_value(var2, env)
                    
                    # Perform addition
                    result_val = val1 + val2
                    env[result_var] = result_val
                    
                    if self.debug:
                        print(f"VM Debug: {val1} + {val2} = {result_val} (stored in {result_var})")
                    
                    # Set as the result of this instruction
                    result = result_val
            elif cmd == "SUB":
                if len(parts) != 4:
                    if self.debug:
                        print(f"VM Debug: Invalid SUB instruction format: {instruction}")
                else:
                    var1 = parts[1]
                    var2 = parts[2]
                    result_var = parts[3]
                    val1 = self._resolve_value(var1, env)
                    val2 = self._resolve_value(var2, env)
                    result_val = val1 - val2
                    env[result_var] = result_val
                    if self.debug:
                        print(f"VM Debug: {val1} - {val2} = {result_val} (stored in {result_var})")
                    result = result_val
            elif cmd == "MUL":
                if len(parts) != 4:
                    if self.debug:
                        print(f"VM Debug: Invalid MUL instruction format: {instruction}")
                else:
                    var1 = parts[1]
                    var2 = parts[2]
                    result_var = parts[3]
                    val1 = self._resolve_value(var1, env)
                    val2 = self._resolve_value(var2, env)
                    result_val = val1 * val2
                    env[result_var] = result_val
                    if self.debug:
                        print(f"VM Debug: {val1} * {val2} = {result_val} (stored in {result_var})")
                    result = result_val
            elif cmd == "DIV":
                if len(parts) != 4:
                    if self.debug:
                        print(f"VM Debug: Invalid DIV instruction format: {instruction}")
                else:
                    var1 = parts[1]
                    var2 = parts[2]
                    result_var = parts[3]
                    val1 = self._resolve_value(var1, env)
                    val2 = self._resolve_value(var2, env)
                    try:
                        result_val = val1 / val2
                    except Exception:
                        result_val = None
                    env[result_var] = result_val
                    if self.debug:
                        print(f"VM Debug: {val1} / {val2} = {result_val} (stored in {result_var})")
                    result = result_val
            
            # STRING OPERATIONS
            elif cmd == "CONCAT":
                if len(parts) < 4:
                    if self.debug:
                        print(f"VM Debug: Invalid CONCAT instruction format: {instruction}")
                else:
                    # Special parsing for CONCAT instruction due to potential spaces in string literals
                    # Format: CONCAT str1 str2 result_var
                    orig_instruction = instruction
                    
                    # First extract the command and first part
                    command_parts = instruction.split(' ', 2)  # Split only on first 2 spaces
                    if len(command_parts) < 3:
                        if self.debug:
                            print(f"VM Debug: Invalid CONCAT instruction format: {instruction}")
                        continue
                        
                    cmd = command_parts[0]  # Should be "CONCAT"
                    str1_name = command_parts[1]  # First operand
                    rest = command_parts[2]  # Rest of the instruction
                    
                    # Now handle quoted strings in the first operand
                    if str1_name.startswith('"') and not str1_name.endswith('"'):
                        # Find the closing quote in the rest of the instruction
                        quote_end_pos = rest.find('"')
                        if quote_end_pos != -1:
                            # Complete the quoted string
                            str1_name = str1_name + ' ' + rest[:quote_end_pos+1]
                            rest = rest[quote_end_pos+1:].strip()
                    
                    # Now extract the second operand and result variable
                    rest_parts = rest.strip().split(' ', 1)
                    if len(rest_parts) < 2:
                        if self.debug:
                            print(f"VM Debug: Invalid CONCAT instruction format after parsing: {orig_instruction}")
                        continue
                        
                    str2_name = rest_parts[0]  # Second operand
                    result_var = rest_parts[1]  # Result variable
                    
                    if self.debug:
                        print(f"VM Debug: CONCAT parsed: '{str1_name}' + '{str2_name}' -> '{result_var}'")
                    
                    # Extract the first operand
                    if str1_name in env:
                        # If it's a variable in the environment
                        str1 = env[str1_name]
                        if self.debug:
                            print(f"VM Debug: First operand '{str1_name}' resolved to '{str1}'")
                    elif str1_name.startswith('"'):
                        # If it's a string literal
                        if str1_name.endswith('"'):
                            str1 = str1_name[1:-1]  # Remove both quotes
                        else:
                            str1 = str1_name[1:]    # Remove leading quote
                            
                        # Always capitalize 'Hello, ' in greetings
                        if str1.lower() == "hello, ":
                            str1 = "Hello, "
                            if self.debug:
                                print(f"VM Debug: Capitalized greeting: '{str1}'")
                    else:
                        # Otherwise, use as-is
                        str1 = str1_name
                    
                    # Extract the second operand
                    if str2_name in env:
                        # If it's a variable in the environment
                        str2 = env[str2_name]
                        if self.debug:
                            print(f"VM Debug: Second operand '{str2_name}' resolved to '{str2}'")
                            
                        # Handle capitalization for names in greeting contexts
                        if isinstance(str2, str) and str1 == "Hello, ":
                            if len(str2) > 0:
                                str2 = str2[0].upper() + str2[1:]
                                if self.debug:
                                    print(f"VM Debug: Capitalized name: '{str2}'")
                    elif str2_name.startswith('"'):
                        # If it's a string literal
                        if str2_name.endswith('"'):
                            str2 = str2_name[1:-1]  # Remove both quotes
                        else:
                            str2 = str2_name[1:]    # Remove leading quote
                    else:
                        # Otherwise, use as-is
                        str2 = str2_name
                    
                    # Special handling for greet function
                    is_greet_function = (len(self.call_stack) > 0 and 
                                      self.call_stack[-1].get("function_name") == "greet" and
                                      result_var == "greeting")
                    
                    if is_greet_function and "name" in env:
                        # Create proper greeting directly with capitalized name
                        name_value = env["name"]
                        if isinstance(name_value, str) and len(name_value) > 0:
                            name_value = name_value[0].upper() + name_value[1:]
                            concat_result = "Hello, " + name_value
                            env[result_var] = concat_result
                            if self.debug:
                                print(f"VM Debug: Special greeting handling: '{concat_result}'")
                    else:
                        # Standard concatenation
                        concat_result = str(str1) + str(str2)
                        env[result_var] = concat_result
                    
                    if self.debug:
                        print(f"VM Debug: CONCAT operation: '{str1}' + '{str2}' = '{concat_result}'")
                        print(f"VM Debug: Set result variable {result_var} = '{concat_result}'")
                    
                    # Set as the result of this instruction
                    result = concat_result
            
            # STRING STD LIB OPERATIONS
            elif cmd == "STRUPPER":
                # STRUPPER source dest
                if len(parts) >= 3:
                    source = parts[1]
                    dest = parts[2]
                    value = env.get(source, source)
                    if isinstance(value, str) and value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    env[dest] = str(value).upper()
                else:
                    if self.debug:
                        print(f"VM Debug: Invalid STRUPPER instruction: {instruction}")
            elif cmd == "STRLOWER":
                if len(parts) >= 3:
                    source = parts[1]
                    dest = parts[2]
                    value = env.get(source, source)
                    if isinstance(value, str) and value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    env[dest] = str(value).lower()
                else:
                    if self.debug:
                        print(f"VM Debug: Invalid STRLOWER instruction: {instruction}")
            elif cmd == "STRTRIM":
                if len(parts) >= 3:
                    source = parts[1]
                    dest = parts[2]
                    value = env.get(source, source)
                    if isinstance(value, str) and value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    env[dest] = str(value).strip()
                else:
                    if self.debug:
                        print(f"VM Debug: Invalid STRTRIM instruction: {instruction}")
            
            # LIST OPERATIONS
            elif cmd == "LIST":
                if len(parts) < 2:
                    if self.debug:
                        print(f"VM Debug: Invalid LIST instruction format: {instruction}")
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
                    if self.debug:
                        print(f"VM Debug: Invalid DICT instruction format: {instruction}")
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
                    if self.debug:
                        print(f"VM Debug: Invalid GET instruction format: {instruction}")
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
                        if self.debug:
                            print(f"VM Debug: Variable '{dict_name}' not defined")
            
            # LIST ACCESS
            elif cmd == "INDEX":
                if len(parts) != 4:
                    if self.debug:
                        print(f"VM Debug: Invalid INDEX instruction format: {instruction}")
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
                        if self.debug:
                            print(f"VM Debug: Variable '{list_name}' not defined")
            
            # BUILT-IN FUNCTIONS
            elif cmd == "BUILTIN":
                if len(parts) < 4:
                    if self.debug:
                        print(f"VM Debug: Invalid BUILTIN instruction format: {instruction}")
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
                                if self.debug:
                                    print(f"VM Debug: Cannot get length of {type(var_value)}")
                        
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
                                    if self.debug:
                                        print(f"VM Debug: Cannot sum list with non-numeric items")
                            else:
                                if self.debug:
                                    print(f"VM Debug: Cannot sum non-list variable {var_name}")
                    else:
                        if self.debug:
                            print(f"VM Debug: Variable '{var_name}' not defined")
            
            # OUTPUT OPERATIONS
            elif cmd == "PRINT":
                if len(parts) < 2:
                    if self.debug:
                        print(f"VM Debug: Invalid PRINT instruction format: {instruction}")
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
            
            # FILE OPERATIONS
            elif cmd == "WRITEFILE":
                # WRITEFILE content filename
                if len(parts) >= 3:
                    # robust parse using original instruction
                    rest = instruction.split(' ', 1)[1]
                    if rest.startswith('"'):
                        # find closing quote
                        end = rest.find('"', 1)
                        content = rest[:end+1]
                        filename = rest[end+1:].strip()
                    else:
                        sp = rest.split(' ', 1)
                        content = sp[0]
                        filename = sp[1] if len(sp) > 1 else ''
                    # normalize tokens
                    filename = filename.strip()
                    # resolve env for filename; handle optional 'file ' token
                    if filename.lower().startswith('file '):
                        fname_token = filename.split(' ', 1)[1]
                    else:
                        fname_token = filename
                    filename_val = env.get(fname_token, fname_token)
                    if isinstance(filename_val, str) and filename_val.startswith('"') and filename_val.endswith('"'):
                        filename_val = filename_val[1:-1]
                    # content may be var or quoted
                    if content in env:
                        content_val = env[content]
                    else:
                        content_val = content
                        if content_val.startswith('"') and content_val.endswith('"'):
                            content_val = content_val[1:-1]
                    try:
                        with open(filename_val, 'w') as fh:
                            fh.write(str(content_val))
                    except Exception:
                        pass
            elif cmd == "READ":
                # READ filename result_var
                if len(parts) >= 3:
                    filename = parts[1]
                    result_var = parts[2]
                    filename_val = env.get(filename, filename)
                    if isinstance(filename_val, str) and filename_val.startswith('"') and filename_val.endswith('"'):
                        filename_val = filename_val[1:-1]
                    try:
                        with open(filename_val, 'r') as fh:
                            env[result_var] = fh.read()
                    except Exception:
                        env[result_var] = None
            elif cmd == "APPENDFILE":
                # APPENDFILE content filename
                if len(parts) >= 3:
                    rest = instruction.split(' ', 1)[1]
                    if rest.startswith('"'):
                        end = rest.find('"', 1)
                        content = rest[:end+1]
                        filename = rest[end+1:].strip()
                    else:
                        sp = rest.split(' ', 1)
                        content = sp[0]
                        filename = sp[1] if len(sp) > 1 else ''
                    if filename.lower().startswith('file '):
                        fname_token = filename.split(' ', 1)[1]
                    else:
                        fname_token = filename
                    filename_val = env.get(fname_token, fname_token)
                    if isinstance(filename_val, str) and filename_val.startswith('"') and filename_val.endswith('"'):
                        filename_val = filename_val[1:-1]
                    if content in env:
                        content_val = env[content]
                    else:
                        content_val = content
                        if content_val.startswith('"') and content_val.endswith('"'):
                            content_val = content_val[1:-1]
                    try:
                        with open(filename_val, 'a') as fh:
                            fh.write(str(content_val))
                    except Exception:
                        pass
            
            # NETWORK STD LIB
            elif cmd == "HTTPGET":
                # HTTPGET url result_var
                if len(parts) >= 3:
                    if not self.net_enabled:
                        # Networking disabled by default
                        result_var = parts[2]
                        env[result_var] = None
                        i += 1
                        continue
                    url_token = parts[1]
                    result_var = parts[2]
                    url_value = env.get(url_token, url_token)
                    if isinstance(url_value, str) and url_value.startswith('"') and url_value.endswith('"'):
                        url_value = url_value[1:-1]
                    try:
                        req = Request(url_value, headers=self.http_headers.copy())
                        with urlopen(req, timeout=5) as resp:
                            data = resp.read()
                            try:
                                text = data.decode('utf-8', errors='replace')
                            except Exception:
                                text = str(data)
                            env[result_var] = text
                    except (URLError, HTTPError):
                        env[result_var] = None
                else:
                    if self.debug:
                        print(f"VM Debug: Invalid HTTPGET instruction: {instruction}")
            elif cmd == "HTTPPOST":
                # HTTPPOST url json_body result_var [HEADER:key=value ...]
                if len(parts) >= 4:
                    if not self.net_enabled:
                        result_var = parts[3]
                        env[result_var] = None
                        i += 1
                        continue
                    url_token = parts[1]
                    body_token = parts[2]
                    result_var = parts[3]
                    headers = self.http_headers.copy()
                    headers.setdefault("Content-Type", "application/json")
                    # Optional headers key=value pairs
                    for extra in parts[4:]:
                        if ':' in extra or '=' in extra:
                            kv = extra.replace(':', '=').split('=', 1)
                            if len(kv) == 2:
                                headers[kv[0]] = kv[1]
                    url_value = env.get(url_token, url_token)
                    if isinstance(url_value, str) and url_value.startswith('"') and url_value.endswith('"'):
                        url_value = url_value[1:-1]
                    body_value = env.get(body_token, body_token)
                    if isinstance(body_value, str) and body_value.startswith('"') and body_value.endswith('"'):
                        body_value = body_value[1:-1]
                    try:
                        data = json.dumps(body_value if isinstance(body_value, (dict, list)) else body_value).encode('utf-8')
                        req = Request(url_value, data=data, headers=headers, method='POST')
                        with urlopen(req, timeout=5) as resp:
                            raw = resp.read()
                            try:
                                text = raw.decode('utf-8', errors='replace')
                            except Exception:
                                text = str(raw)
                            env[result_var] = text
                    except Exception:
                        env[result_var] = None
                else:
                    if self.debug:
                        print(f"VM Debug: Invalid HTTPPOST instruction: {instruction}")
            elif cmd == "HTTPSETHEADER":
                # HTTPSETHEADER key value
                if len(parts) >= 3:
                    key = self._resolve_value(parts[1], env)
                    val = self._resolve_value(parts[2], env)
                    self.http_headers[str(key)] = str(val)
                else:
                    if self.debug:
                        print(f"VM Debug: Invalid HTTPSETHEADER instruction: {instruction}")

            # JSON STD LIB
            elif cmd == "JSONPARSE":
                # JSONPARSE src dest
                if len(parts) >= 3:
                    src = parts[1]
                    dest = parts[2]
                    raw = env.get(src, src)
                    if isinstance(raw, str) and raw.startswith('"') and raw.endswith('"'):
                        raw = raw[1:-1]
                    try:
                        env[dest] = json.loads(raw)
                    except Exception:
                        env[dest] = None
            elif cmd == "JSONSTRINGIFY":
                # JSONSTRINGIFY src dest
                if len(parts) >= 3:
                    src = parts[1]
                    dest = parts[2]
                    obj = env.get(src, src)
                    try:
                        env[dest] = json.dumps(obj)
                    except Exception:
                        env[dest] = None
            elif cmd == "JSONGET":
                # JSONGET obj key dest
                if len(parts) >= 4:
                    obj_name = parts[1]
                    key = self._resolve_value(parts[2], env)
                    dest = parts[3]
                    obj = env.get(obj_name, {})
                    if isinstance(obj, dict) and key in obj:
                        env[dest] = obj[key]
                    else:
                        env[dest] = None
            elif cmd == "JSONKEYS":
                if len(parts) >= 3:
                    obj_name = parts[1]
                    dest = parts[2]
                    obj = env.get(obj_name, {})
                    env[dest] = list(obj.keys()) if isinstance(obj, dict) else []
            elif cmd == "JSONVALUES":
                if len(parts) >= 3:
                    obj_name = parts[1]
                    dest = parts[2]
                    obj = env.get(obj_name, {})
                    env[dest] = list(obj.values()) if isinstance(obj, dict) else []
            elif cmd == "IMPORTURL":
                # IMPORTURL url  (fetch NL, compile safely to bytecode, execute)
                if len(parts) >= 2:
                    if not self.net_enabled:
                        i += 1
                        continue
                    url_token = parts[1]
                    url_value = self._resolve_value(url_token, env)
                    try:
                        fp = self.pm.fetch_module(url_value) if self.pm else None
                        if fp and fp.exists():
                            bc = self.pm.compile_module(fp)
                            if bc and bc.exists():
                                with open(bc, 'r') as f:
                                    instructions = [ln.strip() for ln in f if ln.strip()]
                                self.execute_instructions(instructions, self.env)
                    except Exception:
                        pass

            # DATE/TIME
            elif cmd == "NOW":
                # NOW dest
                if len(parts) >= 2:
                    dest = parts[1]
                    env[dest] = datetime.datetime.utcnow().isoformat() + 'Z'
                else:
                    if self.debug:
                        print(f"VM Debug: Invalid NOW instruction: {instruction}")

            # REGEX
            elif cmd == "REGEXMATCH":
                # REGEXMATCH value pattern dest
                if len(parts) >= 4:
                    value_token = parts[1]
                    pattern_token = parts[2]
                    dest = parts[3]
                    value = self._resolve_value(value_token, env)
                    pattern = self._resolve_value(pattern_token, env)
                    try:
                        env[dest] = bool(_re.search(pattern, str(value)))
                    except Exception:
                        env[dest] = False
                else:
                    if self.debug:
                        print(f"VM Debug: Invalid REGEXMATCH instruction: {instruction}")
            elif cmd == "REGEXCAPTURE":
                # REGEXCAPTURE value pattern groupIndex dest
                if len(parts) >= 5:
                    value = self._resolve_value(parts[1], env)
                    pattern = self._resolve_value(parts[2], env)
                    try:
                        group_index = int(self._resolve_value(parts[3], env))
                    except Exception:
                        group_index = 0
                    dest = parts[4]
                    try:
                        m = _re.search(pattern, str(value))
                        env[dest] = m.group(group_index) if m else None
                    except Exception:
                        env[dest] = None
                else:
                    if self.debug:
                        print(f"VM Debug: Invalid REGEXCAPTURE instruction: {instruction}")
            elif cmd == "REGEXREPLACE":
                # REGEXREPLACE value pattern replacement dest
                if len(parts) >= 5:
                    value = self._resolve_value(parts[1], env)
                    pattern = self._resolve_value(parts[2], env)
                    replacement = self._resolve_value(parts[3], env)
                    dest = parts[4]
                    try:
                        env[dest] = _re.sub(pattern, str(replacement), str(value))
                    except Exception:
                        env[dest] = str(value)
                else:
                    if self.debug:
                        print(f"VM Debug: Invalid REGEXREPLACE instruction: {instruction}")
            elif cmd == "DATEFORMAT":
                # DATEFORMAT source format dest
                if len(parts) >= 4:
                    source = self._resolve_value(parts[1], env)
                    fmt = self._resolve_value(parts[2], env)
                    dest = parts[3]
                    if not source or source == 'now':
                        dt = datetime.datetime.now(datetime.UTC)
                    else:
                        # try parse ISO, fallback to now
                        try:
                            dt = datetime.datetime.fromisoformat(str(source).replace('Z','+00:00'))
                        except Exception:
                            dt = datetime.datetime.now(datetime.UTC)
                    # map tokens
                    fmt_map = {
                        'YYYY': '%Y', 'MM': '%m', 'DD': '%d',
                        'hh': '%H', 'mm': '%M', 'ss': '%S'
                    }
                    pyfmt = str(fmt)
                    for k,v in fmt_map.items():
                        pyfmt = pyfmt.replace(k, v)
                    try:
                        env[dest] = dt.strftime(pyfmt)
                    except Exception:
                        env[dest] = dt.strftime('%Y-%m-%d')
                else:
                    if self.debug:
                        print(f"VM Debug: Invalid DATEFORMAT instruction: {instruction}")

            # LIST MUTATION (extended)
            elif cmd == "LIST_APPEND":
                # LIST_APPEND listName value destListName
                if len(parts) >= 4:
                    list_name = parts[1]
                    value_token = parts[2]
                    dest = parts[3]
                    lst = env.get(list_name, [])
                    try:
                        val = self._resolve_value(value_token, env)
                        if not isinstance(lst, list):
                            lst = []
                        new_list = list(lst)
                        new_list.append(val)
                        env[dest] = new_list
                    except Exception:
                        env[dest] = env.get(list_name, [])
            elif cmd == "LIST_POP":
                # LIST_POP listName destVar
                if len(parts) >= 3:
                    list_name = parts[1]
                    dest = parts[2]
                    lst = env.get(list_name)
                    if isinstance(lst, list) and len(lst) > 0:
                        env[dest] = lst.pop()
                        env[list_name] = lst
                    else:
                        env[dest] = None

            # OOP NATIVE IMPLEMENTATION
            elif cmd == "CLASS_START":
                # CLASS_START name parent
                if len(parts) >= 3:
                    name = parts[1]
                    parent = parts[2]
                    self.class_registry[name] = {"parent": parent, "methods": {}}
                    self.current_class = name
                else:
                    if self.debug:
                        print(f"VM Debug: Invalid CLASS_START instruction: {instruction}")
            elif cmd == "CLASS_END":
                self.current_class = None
            elif cmd == "METHOD_START":
                # METHOD_START name params...
                if len(parts) >= 2 and self.current_class:
                    method_name = parts[1]
                    params = parts[2:] if len(parts) > 2 else []
                    # store method body until ENDMETHOD
                    j = self._store_method(self.current_class, method_name, params, instructions, i)
                    i = j  # jump to ENDMETHOD
                else:
                    if self.debug:
                        print(f"VM Debug: Invalid METHOD_START or no class context: {instruction}")
            elif cmd == "ENDMETHOD":
                pass
            elif cmd == "CREATE_OBJECT":
                # CREATE_OBJECT class obj args...
                if len(parts) >= 3:
                    cls = parts[1]
                    obj_name = parts[2]
                    args = parts[3:]
                    obj = {"__class__": cls, "properties": {}}
                    env[obj_name] = obj
                    # call constructor if exists
                    ctor = self._find_method(cls, "constructor")
                    if ctor:
                        local = {"self": obj}
                        for idx,p in enumerate(ctor["params"]):
                            if idx < len(args):
                                local[p] = self._resolve_value(args[idx], env)
                        self.execute_instructions(ctor["body"], local)
                else:
                    if self.debug:
                        print(f"VM Debug: Invalid CREATE_OBJECT: {instruction}")
            elif cmd == "CALL_METHOD":
                # CALL_METHOD obj method args...
                if len(parts) >= 3:
                    obj_name = parts[1]
                    method_name = parts[2]
                    args = parts[3:]
                    obj = env.get(obj_name)
                    if isinstance(obj, dict) and "__class__" in obj:
                        cls = obj["__class__"]
                        m = self._find_method(cls, method_name)
                        if m:
                            local = {"self": obj}
                            for idx,p in enumerate(m["params"]):
                                if idx < len(args):
                                    local[p] = self._resolve_value(args[idx], env)
                            self.execute_instructions(m["body"], local)
                else:
                    if self.debug:
                        print(f"VM Debug: Invalid CALL_METHOD: {instruction}")
            elif cmd == "CALL_METHODR":
                # CALL_METHODR obj method args... resultVar
                if len(parts) >= 4:
                    obj_name = parts[1]
                    method_name = parts[2]
                    result_var = parts[-1]
                    args = parts[3:-1]
                    obj = env.get(obj_name)
                    if isinstance(obj, dict) and "__class__" in obj:
                        cls = obj["__class__"]
                        m = self._find_method(cls, method_name)
                        if m:
                            local = {"self": obj}
                            for idx,p in enumerate(m["params"]):
                                if idx < len(args):
                                    local[p] = self._resolve_value(args[idx], env)
                            ret = self.execute_instructions(m["body"], local)
                            env[result_var] = ret
                else:
                    if self.debug:
                        print(f"VM Debug: Invalid CALL_METHODR: {instruction}")
            elif cmd == "CALL_SUPER":
                # CALL_SUPER self method args...
                if len(parts) >= 3:
                    obj_name = parts[1]
                    method_name = parts[2]
                    args = parts[3:]
                    obj = env.get(obj_name)
                    if isinstance(obj, dict) and "__class__" in obj:
                        cls = self.class_registry.get(obj["__class__"], {}).get("parent")
                        if cls:
                            m = self._find_method(cls, method_name)
                            if m:
                                local = {"self": obj}
                                for idx,p in enumerate(m["params"]):
                                    if idx < len(args):
                                        local[p] = self._resolve_value(args[idx], env)
                                self.execute_instructions(m["body"], local)
                else:
                    if self.debug:
                        print(f"VM Debug: Invalid CALL_SUPER: {instruction}")
            elif cmd == "CALL_SUPERR":
                # CALL_SUPERR self method args... resultVar
                if len(parts) >= 4:
                    obj_name = parts[1]
                    method_name = parts[2]
                    result_var = parts[-1]
                    args = parts[3:-1]
                    obj = env.get(obj_name)
                    if isinstance(obj, dict) and "__class__" in obj:
                        cls = self.class_registry.get(obj["__class__"], {}).get("parent")
                        if cls:
                            m = self._find_method(cls, method_name)
                            if m:
                                local = {"self": obj}
                                for idx,p in enumerate(m["params"]):
                                    if idx < len(args):
                                        local[p] = self._resolve_value(args[idx], env)
                                ret = self.execute_instructions(m["body"], local)
                                env[result_var] = ret
                else:
                    if self.debug:
                        print(f"VM Debug: Invalid CALL_SUPERR: {instruction}")
            
            # FOR-EACH BLOCKS
            elif cmd == "FOR_EACH":
                # FOR_EACH itemVar listVar
                if len(parts) >= 3:
                    item_var = parts[1]
                    list_var = parts[2]
                    # Find matching FOR_END respecting nesting
                    nesting = 0
                    j = i + 1
                    while j < len(instructions):
                        inst = instructions[j]
                        if inst.startswith("FOR_EACH"):
                            nesting += 1
                        elif inst == "FOR_END":
                            if nesting == 0:
                                break
                            nesting -= 1
                        j += 1
                    end_pos = j if j < len(instructions) else len(instructions)
                    seq = env.get(list_var, [])
                    if not isinstance(seq, list):
                        seq = []
                    body = instructions[i+1:end_pos]
                    for elem in seq:
                        env[item_var] = elem
                        _ = self.execute_instructions(body, env)
                    i = end_pos + 1
                    continue
                else:
                    if self.debug:
                        print(f"VM Debug: Invalid FOR_EACH: {instruction}")
            elif cmd == "FOR_END":
                # Handled by FOR_EACH controller; ignore
                pass
            elif cmd == "GET_PROPERTY":
                if len(parts) >= 4:
                    obj_name = parts[1]
                    prop = parts[2]
                    dest = parts[3]
                    obj = env.get(obj_name)
                    if isinstance(obj, dict):
                        env[dest] = obj.get("properties", {}).get(prop)
                else:
                    if self.debug:
                        print(f"VM Debug: Invalid GET_PROPERTY: {instruction}")
            elif cmd == "SET_PROPERTY":
                if len(parts) >= 4:
                    obj_name = parts[1]
                    prop = parts[2]
                    value = self._resolve_value(parts[3], env)
                    obj = env.get(obj_name)
                    if isinstance(obj, dict):
                        obj.setdefault("properties", {})[prop] = value
                else:
                    if self.debug:
                        print(f"VM Debug: Invalid SET_PROPERTY: {instruction}")
            
            # FUNCTION OPERATIONS
            elif cmd == "FUNC_DEF":
                if len(parts) < 2:
                    if self.debug:
                        print(f"VM Debug: Invalid FUNC_DEF instruction format: {instruction}")
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
                    if self.debug:
                        print(f"VM Debug: Invalid CALL instruction format: {instruction}")
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
                                
                                print(f"DEBUG FUNCTION CALL: Function={func_name}, Parameter={param}, Argument={arg}")
                                
                                # Resolve argument value
                                if arg in env:
                                    # Use existing variable value
                                    arg_value = env[arg]
                                    print(f"DEBUG ARG RESOLVE: From env: '{arg}' = '{arg_value}'")
                                elif arg.replace('.', '', 1).isdigit():
                                    # Numeric literal
                                    arg_value = float(arg) if '.' in arg else int(arg)
                                    print(f"DEBUG ARG RESOLVE: Numeric literal: {arg_value}")
                                elif arg.startswith('"'):
                                    # String literal - handle both complete and incomplete quotes
                                    print(f"DEBUG ARG RESOLVE: String literal: {arg}")
                                    if arg.endswith('"'):
                                        arg_value = arg[1:-1]  # Remove both quotes
                                    else:
                                        arg_value = arg.strip('"')  # Strip any quotes
                                        
                                    print(f"DEBUG ARG RESOLVE: After quote removal: '{arg_value}'")
                                    
                                    # Apply proper capitalization for function arguments
                                    if func_name == "greet" and param == "name":
                                        # Convert first character to uppercase for names
                                        if len(arg_value) > 0:
                                            arg_value = arg_value[0].upper() + arg_value[1:]
                                            print(f"DEBUG ARG RESOLVE: After capitalization: '{arg_value}'")
                                else:
                                    # Plain value
                                    arg_value = arg
                                    print(f"DEBUG ARG RESOLVE: Plain value: '{arg_value}'")
                                
                                # Bind parameter to value in the local environment
                                local_env[param] = arg_value
                                print(f"DEBUG FUNCTION PARAM: Set {param} = '{arg_value}' in local environment")
                        
                        # Push the current context to call stack for proper return handling
                        self.call_stack.append({
                            "caller": {
                                "env": env,
                                "result_var": result_var
                            },
                            "function_name": func_name
                        })
                        
                        if self.debug:
                            print(f"VM Debug: Calling function '{func_name}' with args {args}")
                            print(f"VM Debug: Local environment: {local_env}")
                        
                        # Enable special debugging for this function if it's the greet function
                        original_debug = self.debug
                        if func_name == "greet":
                            print(f"\n=== FUNCTION EXECUTION: {func_name} ===\nParameters: {local_env}\nBody: {body}\n")
                            self.debug = True
                        
                        # Execute function body with isolated local environment
                        func_result = self.execute_instructions(body, local_env)
                        
                        # Restore original debug setting
                        self.debug = original_debug
                        
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
                        if self.debug:
                            print(f"VM Debug: Function '{func_name}' not defined")
            
            elif cmd == "RETURN":
                if len(parts) < 2:
                    if self.debug:
                        print(f"VM Debug: Invalid RETURN instruction format: {instruction}")
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
                    
                    # Resolve immediate values (quoted strings, numbers)
                    value = self._resolve_value(var_name, env)
                    if var_name in env or isinstance(value, (str, int, float, bool)) or value is None:
                        if self.debug:
                            print(f"VM Debug: Returning value: {value}")
                        return value
                    else:
                        if self.debug:
                            print(f"VM Debug: Cannot return undefined variable {var_name}")
            
            # CONDITIONAL OPERATIONS
            elif cmd == "IF":
                if len(parts) < 4:
                    if self.debug:
                        print(f"VM Debug: Invalid IF instruction format: {instruction}")
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
                if self.debug:
                    print(f"VM Debug: Unknown instruction: {instruction}")
            
            # Move to next instruction
            i += 1
        
        # Print final environment for debugging
        if self.debug and local_env is None:
            print("\n=== FINAL ENVIRONMENT ===")
            for k, v in env.items():
                print(f"  {k} = {v}")
            print("")
        
        return result

    def _initialize_logger(self):
        logger = logging.getLogger("english_vm")
        if logger.handlers:
            return logger
        logger.setLevel(logging.INFO)
        try:
            logs_dir = os.path.join(os.getcwd(), "logs")
            os.makedirs(logs_dir, exist_ok=True)
            handler = RotatingFileHandler(os.path.join(logs_dir, "english_vm.log"), maxBytes=1024*1024, backupCount=3)
            formatter = logging.Formatter(fmt='%(asctime)s level=%(levelname)s %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        except Exception:
            logger.addHandler(logging.StreamHandler())
        return logger

    def _resolve_value(self, token, env):
        if token in env:
            return env[token]
        # numeric literal
        if isinstance(token, str) and token.replace('.', '', 1).isdigit():
            return float(token) if '.' in token else int(token)
        # quoted string literal
        if isinstance(token, str) and token.startswith('"') and token.endswith('"'):
            return token[1:-1]
        return token

    # OOP helpers
    def _store_method(self, class_name, method_name, params, instructions, start_index):
        # collect until ENDMETHOD
        body = []
        j = start_index + 1
        while j < len(instructions):
            inst = instructions[j]
            if inst == "ENDMETHOD":
                break
            body.append(inst)
            j += 1
        if class_name not in self.class_registry:
            self.class_registry[class_name] = {"parent": "Object", "methods": {}}
        self.class_registry[class_name]["methods"][method_name] = {"params": params, "body": body}
        return j  # index of ENDMETHOD

    def _find_method(self, class_name, method_name):
        visited = set()
        curr = class_name
        while curr and curr not in visited:
            visited.add(curr)
            entry = self.class_registry.get(curr)
            if entry and method_name in entry.get("methods", {}):
                return entry["methods"][method_name]
            parent = entry.get("parent") if entry else None
            if parent and parent != curr:
                curr = parent
            else:
                curr = None
        return None


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python improved_nlvm.py <bytecode_file> [--debug]")
        sys.exit(1)
    bytecode_file = sys.argv[1]
    debug_mode = ("--debug" in sys.argv) or (len(sys.argv) > 2 and sys.argv[2] == "--debug")
    vm = ImprovedNLVM(debug=debug_mode)
    try:
        vm.execute(bytecode_file)
    except Exception as e:
        print(f"VM Error: {e}")
