#!/usr/bin/env python3
"""
Integrated English Programming Compiler
This is a specialized compiler that implements features from english_runtime_complete
while maintaining compatibility with the original english_programming architecture.
"""

import re
import sys
import os
from pathlib import Path

class IntegratedCompiler:
    """
    Specialized compiler implementing features from english_runtime_complete:
    - Functions with parameters and return values
    - List and dictionary operations
    - String concatenation
    - File I/O operations
    """
    
    def __init__(self):
        print("Initializing Integrated Compiler...")
        self.defined_variables = set()
        self.functions = {}
        
    def compile(self, input_file, output_file):
        """Compile the input file to bytecode"""
        print(f"Compiling {input_file} to {output_file}...")
        
        # Read the source file
        with open(input_file, 'r') as f:
            lines = [line.strip() for line in f if line.strip()]
            
        # First pass to gather variable names and functions
        self.preprocess(lines)
        
        # Generate bytecode
        bytecode = self.translate_to_bytecode(lines)
        
        # Write bytecode to output file
        with open(output_file, 'w') as f:
            for line in bytecode:
                f.write(line + '\n')
                
        print(f"Compilation complete. Generated {len(bytecode)} bytecode instructions.")
        return output_file
    
    def preprocess(self, lines):
        """Preprocess lines to gather variable names and function definitions"""
        print("Preprocessing source code...")
        for line in lines:
            # Skip comments
            if line.startswith('#'):
                continue
                
            # Variable creation
            var_match = re.match(r"create a variable called (\w+)", line.lower())
            if var_match:
                var_name = var_match.group(1)
                self.defined_variables.add(var_name)
                print(f"Found variable: {var_name}")
                
            # List creation
            list_match = re.match(r"create a list called (\w+)", line.lower())
            if list_match:
                list_name = list_match.group(1)
                self.defined_variables.add(list_name)
                print(f"Found list: {list_name}")
                
            # Dictionary creation
            dict_match = re.match(r"create a dictionary called (\w+)", line.lower())
            if dict_match:
                dict_name = dict_match.group(1)
                self.defined_variables.add(dict_name)
                print(f"Found dictionary: {dict_name}")
                
            # Function definition
            func_match = re.match(r"define a function called (\w+) with inputs (.+):", line.lower())
            if func_match:
                func_name = func_match.group(1)
                params = [p.strip() for p in func_match.group(2).split("and")]
                self.functions[func_name] = params
                print(f"Found function: {func_name} with params: {params}")
                
            # Look for store/set in variables
            store_match = re.search(r"store (?:in|into) (\w+)", line.lower())
            if store_match:
                result_var = store_match.group(1)
                self.defined_variables.add(result_var)
                print(f"Found result variable: {result_var}")
                
        print(f"Preprocessing complete. Found {len(self.defined_variables)} variables and {len(self.functions)} functions.")
    
    def translate_to_bytecode(self, lines):
        """Translate source code to bytecode"""
        bytecode = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # Skip comments
            if line.startswith('#'):
                i += 1
                continue
                
            # Variable creation and assignment
            var_match = re.match(r"create a variable called (\w+) and set it to (.+)", line.lower())
            if var_match:
                var_name = var_match.group(1)
                value = var_match.group(2)
                bytecode.append(f"SET {var_name} {value}")
                i += 1
                continue
                
            # List creation
            list_match = re.match(r"create a list called (\w+) with values (.+)", line.lower())
            if list_match:
                list_name = list_match.group(1)
                items = [item.strip() for item in list_match.group(2).split(",")]
                bytecode.append(f"LIST {list_name} {' '.join(items)}")
                i += 1
                continue
                
            # Dictionary creation
            dict_match = re.match(r"create a dictionary called (\w+) with (.+)", line.lower())
            if dict_match:
                dict_name = dict_match.group(1)
                parts = [p.strip() for p in dict_match.group(2).split("and")]
                kvs = []
                for part in parts:
                    if " as " in part:
                        k, v = part.split(" as ")
                        kvs.append(f"{k.strip()}:{v.strip()}")
                bytecode.append(f"DICT {dict_name} {','.join(kvs)}")
                i += 1
                continue
                
            # List length
            length_match = re.match(r"get the length of (?:list )?(\w+) and store (?:it )?in (\w+)", line.lower())
            if length_match:
                list_name = length_match.group(1)
                result = length_match.group(2)
                bytecode.append(f"BUILTIN LENGTH {list_name} {result}")
                i += 1
                continue
                
            # List sum
            sum_match = re.match(r"get the sum of (?:list )?(\w+) and store (?:it )?in (\w+)", line.lower())
            if sum_match:
                list_name = sum_match.group(1)
                result = sum_match.group(2)
                bytecode.append(f"BUILTIN SUM {list_name} {result}")
                i += 1
                continue
                
            # List indexing
            index_match = re.match(r"get (?:the )?item at index (\d+) from (?:list )?(\w+) and store (?:it )?in (\w+)", line.lower())
            if index_match:
                idx = index_match.group(1)
                list_name = index_match.group(2)
                result = index_match.group(3)
                bytecode.append(f"INDEX {list_name} {idx} {result}")
                i += 1
                continue
                
            # Dictionary access
            get_match = re.match(r"get (\w+) (\w+) and store (?:it )?in (\w+)", line.lower())
            if get_match:
                dict_name = get_match.group(1)
                key = get_match.group(2)
                result = get_match.group(3)
                bytecode.append(f"GET {dict_name} {key} {result}")
                i += 1
                continue
                
            # String concatenation
            concat_match = re.match(r"concatenate (\w+) and (\w+) and store (?:it )?in (\w+)", line.lower())
            if concat_match:
                str1 = concat_match.group(1)
                str2 = concat_match.group(2)
                result = concat_match.group(3)
                bytecode.append(f"CONCAT {str1} {str2} {result}")
                i += 1
                continue
                
            # Print
            print_match = re.match(r"print (\w+)", line.lower())
            if print_match:
                var_name = print_match.group(1)
                bytecode.append(f"PRINT {var_name}")
                i += 1
                continue
                
            # Function definition
            func_match = re.match(r"define a function called (\w+) with inputs (.+):", line.lower())
            if func_match:
                func_name = func_match.group(1)
                params = [p.strip() for p in func_match.group(2).split("and")]
                bytecode.append(f"FUNC_DEF {func_name} {' '.join(params)}")
                
                # Process function body until we hit an unindented line
                i += 1
                while i < len(lines):
                    body_line = lines[i]
                    if body_line.startswith("    "):  # Indented line - part of function body
                        # Strip indentation
                        stripped = body_line.lstrip()
                        # Process the body line into bytecode
                        body_bytecode = self.process_line(stripped)
                        if body_bytecode:
                            bytecode.append(body_bytecode)
                        i += 1
                    else:
                        # End of function body
                        break
                
                # Add END_FUNC marker
                bytecode.append("END_FUNC")
                continue
                
            # Function call
            call_match = re.match(r"call (\w+) with values (.+) and store result in (\w+)", line.lower())
            if call_match:
                func_name = call_match.group(1)
                args = [a.strip() for a in call_match.group(2).split("and")]
                result_var = call_match.group(3)
                bytecode.append(f"CALL {func_name} {' '.join(args)} {result_var}")
                i += 1
                continue
                
            # Return statement
            return_match = re.match(r"return (\w+)", line.lower())
            if return_match:
                var_name = return_match.group(1)
                bytecode.append(f"RETURN {var_name}")
                i += 1
                continue
                
            # Arithmetic operations
            add_match = re.match(r"add (\w+) and (\w+) and store (?:the )?(?:result|sum) in (\w+)", line.lower())
            if add_match:
                op1 = add_match.group(1)
                op2 = add_match.group(2)
                result = add_match.group(3)
                bytecode.append(f"ADD {op1} {op2} {result}")
                i += 1
                continue
                
            # If statements
            if_match = re.match(r"if (\w+) is (greater than|less than|equal to) (\w+):", line.lower())
            if if_match:
                var = if_match.group(1)
                op_text = if_match.group(2)
                val = if_match.group(3)
                
                # Map text operators to symbols
                op_map = {"greater than": ">", "less than": "<", "equal to": "=="}
                op = op_map[op_text]
                
                bytecode.append(f"IF {var} {op} {val}")
                
                # Process the if block
                i += 1
                while i < len(lines):
                    if_line = lines[i]
                    if if_line.startswith("    "):  # Indented line - part of if block
                        # Process the if block line
                        stripped = if_line.lstrip()
                        if stripped.lower() == "else:":
                            bytecode.append("ELSE")
                        else:
                            # Process statement within if block
                            if_bytecode = self.process_line(stripped)
                            if if_bytecode:
                                bytecode.append(if_bytecode)
                        i += 1
                    else:
                        # End of if block
                        break
                
                # Add END_IF marker
                bytecode.append("END_IF")
                continue
                
            # If no specific handler matched, try to process line more generically
            generic_bytecode = self.process_line(line)
            if generic_bytecode:
                bytecode.append(generic_bytecode)
            
            i += 1
            
        return bytecode
    
    def process_line(self, line):
        """Process a single line into bytecode (used for function bodies and generic processing)"""
        
        # Print statement
        print_match = re.match(r"print \"(.+)\"", line.lower())
        if print_match:
            message = print_match.group(1)
            return f"PRINTSTR {message}"
            
        print_match = re.match(r"print (\w+)", line.lower())
        if print_match:
            var_name = print_match.group(1)
            return f"PRINT {var_name}"
            
        # Add operation
        add_match = re.match(r"add (\w+) and (\w+) and store (?:the )?(?:result|sum) in (\w+)", line.lower())
        if add_match:
            op1 = add_match.group(1)
            op2 = add_match.group(2)
            result = add_match.group(3)
            return f"ADD {op1} {op2} {result}"
            
        # Return statement
        return_match = re.match(r"return (\w+)", line.lower())
        if return_match:
            var_name = return_match.group(1)
            return f"RETURN {var_name}"
            
        # If no match found, return None
        return None

# Run the compiler directly
if __name__ == "__main__":
    if len(sys.argv) >= 3:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
    else:
        input_file = "/Users/jithinpothireddy/Downloads/English Programming/simple_test.nl"
        output_file = "/Users/jithinpothireddy/Downloads/English Programming/simple_test.nlc"
        
    compiler = IntegratedCompiler()
    compiler.compile(input_file, output_file)
