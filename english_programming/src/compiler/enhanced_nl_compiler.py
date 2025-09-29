import re
import sys
import os

class EnhancedNLCompiler:
    """
    Enhanced Natural Language Compiler
    Compiles natural language code to bytecode that can be executed by the Enhanced NLVM.
    Supports:
    - Variables and basic operations
    - Control structures (if/while/for)
    - Functions
    - File I/O
    - API integration
    """
    def __init__(self):
        self.indent_level = 0
        self.indent_stack = []  # Track indent levels for nested blocks
        
    def process_string_literal(self, string_literal):
        """Process string literals and handle escape sequences"""
        # Return as is if not surrounded by quotes
        if not ((string_literal.startswith('"') and string_literal.endswith('"')) or 
                (string_literal.startswith('\'') and string_literal.endswith('\''))):  
            return string_literal
        
        # Remove the surrounding quotes
        inner = string_literal[1:-1]
        
        # Process special escape sequences
        inner = inner.replace('\\n', '\n')  # Replace \n with actual newline
        inner = inner.replace('\\t', '\t')  # Replace \t with actual tab
        inner = inner.replace('\\"', '\"')  # Replace \" with "
        inner = inner.replace('\\\'', '\'')  # Replace \' with '
        
        # Return the processed string with quotes
        return f'"{inner}"'

    def compile(self, input_file, output_file):
        """Compile a natural language source file to bytecode"""
        print(f"\nCompiling {input_file}...")
        with open(input_file, "r") as f:
            lines = [line.rstrip() for line in f.readlines()]
            
        # Print original lines for debugging
        print("\nOriginal lines:")
        for line in lines:
            if "get weather" in line.lower():
                print(f"[API FOUND] {line}")
            else:
                print(f"{line}")

        # First pass: handle indentation to identify blocks
        processed_lines = self.process_indentation(lines)
        
        # Print processed lines for debugging
        print("\nProcessed lines:")
        for line in processed_lines:
            if "get weather" in line:
                print(f"[API FOUND] {line}")
            else:
                print(f"{line}")
        
        # Second pass: translate to bytecode
        bytecode = self.translate_to_bytecode(processed_lines)
        
        # Print resulting bytecode for debugging
        print("\nBytecode output:")
        for code in bytecode:
            if "APICALL" in code:
                print(f"[API CALL] {code}")
            else:
                print(code)
        
        # Write bytecode to output file
        with open(output_file, "w") as f:
            for code in bytecode:
                f.write(code + "\n")
        
        print(f"\nCompiled {input_file} to {output_file}")
        return output_file

    def process_indentation(self, lines):
        """Process indentation to identify blocks and add BEGIN/END markers"""
        processed = []
        current_indent = 0
        self.indent_stack = []
        
        for line in lines:
            if not line.strip():  # Skip empty lines
                continue
                
            # Calculate the indentation level
            indent = len(line) - len(line.lstrip())
            stripped_line = line.strip().lower()
            
            if indent > current_indent:
                # Indentation increased, beginning of a new block
                self.indent_stack.append(indent)
                current_indent = indent
            elif indent < current_indent:
                # Indentation decreased, end of one or more blocks
                while self.indent_stack and indent < current_indent:
                    self.indent_stack.pop()
                    current_indent = self.indent_stack[-1] if self.indent_stack else 0
                    processed.append("END")
            
            # Add the normalized line
            processed.append(stripped_line)
            
            # Check if the line is a block starter
            if (stripped_line.startswith("if ") or 
                stripped_line.startswith("while ") or 
                stripped_line.startswith("define a function")):
                # No need to add BEGIN, as the IF/WHILE/FUNC instruction marks the start
                pass
        
        # Close any remaining open blocks
        while self.indent_stack:
            self.indent_stack.pop()
            processed.append("END")
            
        return processed

    def translate_to_bytecode(self, lines):
        """Translate processed lines to bytecode instructions"""
        bytecode = []
        
        # Debug counter for API calls
        api_calls_found = 0
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # Skip empty lines
            if not line.strip():
                i += 1
                continue
                
            # Debug output for API calls
            if "get weather" in line:
                print(f"Processing API line: {line}")
                # Explicit handling for API calls
                if line.startswith("get weather for"):
                    m = re.search(r"get weather for (.+?) and store the result in (.+)", line)
                    if m:
                        city_var = m.group(1).strip()
                        result_var = m.group(2).strip()
                        bytecode.append(f"APICALL WEATHER {city_var} {result_var}")
                        api_calls_found += 1
                        print(f"Added API call: APICALL WEATHER {city_var} {result_var}")
                        i += 1
                        continue
                
            # Handle specific instruction types
            if line == "END":
                bytecode.append("END")
            
            elif line.startswith("create a variable called"):
                m = re.search(r"create a variable called (.+?) and set it to (.+)", line)
                if m:
                    var_name = m.group(1).strip()
                    value = m.group(2).strip()
                    
                    # Process string literals correctly
                    if (value.startswith('"') and value.endswith('"')) or (value.startswith('\'') and value.endswith('\'')):
                        # Handle escape sequences
                        value = self.process_string_literal(value)
                    
                    bytecode.append(f"SET {var_name} {value}")
                    
            elif line.startswith("set"):
                # Handle 'Set variable to value' syntax
                m = re.search(r"set (.+?) to (.+)", line)
                if m:
                    var_name = m.group(1).strip()
                    value = m.group(2).strip()
                    bytecode.append(f"SET {var_name} {value}")
            
            elif line.startswith("add"):
                # Handle "Add X and Y and store the result in Z" format
                m = re.search(r"add (.+?) and (.+?) and store the result in (.+)", line)
                if m:
                    x = m.group(1).strip()
                    y = m.group(2).strip()
                    result = m.group(3).strip()
                    bytecode.append(f"ADD {x} {y} {result}")
                else:
                    # Handle "Add X to Y" format
                    m = re.search(r"add (.+?) to (.+)", line)
                    if m:
                        value = m.group(1).strip()
                        var = m.group(2).strip()
                        bytecode.append(f"ADD {value} {var} {var}")
            
            elif line.startswith("print"):
                content = line.replace("print", "").strip()
                
                # Check if it's a quoted string
                if (content.startswith('"') and content.endswith('"')) or (content.startswith('\'') and content.endswith('\'')):
                    # It's a quoted string literal
                    string_content = content[1:-1]  # Remove the quotes
                    bytecode.append(f"PRINTSTR {string_content}")
                # Check if this looks like an unquoted string literal (legacy format)
                elif content[0].isupper() and ' ' not in content and not any(content.startswith(prefix) for prefix in ["var", "list", "dict", "count", "sum", "result", "temp"]):
                    # Likely a string literal not a variable reference
                    bytecode.append(f"PRINTSTR {content}")
                else:
                    # Likely a variable reference
                    bytecode.append(f"PRINT {content}")
            
            elif line.startswith("if"):
                m = re.search(r"if (.+?):", line)
                if m:
                    condition = self.translate_condition(m.group(1).strip())
                    bytecode.append(f"IF {condition}")
                    
            elif line.startswith("else if"):
                m = re.search(r"else if (.+?):", line)
                if m:
                    condition = self.translate_condition(m.group(1).strip())
                    bytecode.append(f"ELSEIF {condition}")
                    
            elif line.startswith("else"):
                bytecode.append("ELSE")
            
            elif line.startswith("while"):
                m = re.search(r"while (.+?):", line)
                if m:
                    condition = self.translate_condition(m.group(1).strip())
                    bytecode.append(f"WHILE {condition}")
                    
            # File operations
            elif line.startswith("write"):
                m = re.search(r"write (.+?) to (.+)", line)
                if m:
                    content_var = m.group(1).strip()
                    file_var = m.group(2).strip()
                    bytecode.append(f"WRITEFILE {content_var} {file_var}")
                    
            elif line.startswith("read"):
                m = re.search(r"read (.+?) and store the result in (.+)", line)
                if m:
                    file_var = m.group(1).strip()
                    result_var = m.group(2).strip()
                    bytecode.append(f"READFILE {file_var} {result_var}")
                    
            elif line.startswith("append"):
                m = re.search(r"append (.+?) to (.+)", line)
                if m:
                    content_var = m.group(1).strip()
                    file_var = m.group(2).strip()
                    bytecode.append(f"APPENDFILE {content_var} {file_var}")
                    
            elif line.startswith("delete file"):
                m = re.search(r"delete file (.+)", line)
                if m:
                    file_var = m.group(1).strip()
                    bytecode.append(f"DELETEFILE {file_var}")
                    
            elif line.startswith("if file exists"):
                m = re.search(r"if file exists (.+?):", line)
                if m:
                    file_var = m.group(1).strip()
                    bytecode.append(f"FILEEXISTS {file_var}")
            
            elif line.startswith("define a function called"):
                m = re.search(r"define a function called (.+?) with inputs (.+?):", line)
                if m:
                    func_name = m.group(1).strip()
                    params = [p.strip() for p in m.group(2).split("and")]
                    bytecode.append(f"FUNC {func_name} {len(params)} {' '.join(params)}")
            
            elif line.startswith("call"):
                m = re.search(r"call (.+?) with values (.+?) and store result in (.+)", line)
                if m:
                    func_name = m.group(1).strip()
                    args = [arg.strip() for arg in m.group(2).split("and")]
                    result_var = m.group(3).strip()
                    bytecode.append(f"CALL {func_name} {len(args)} {' '.join(args)} {result_var}")
            
            elif line.startswith("return"):
                val = line.replace("return", "").strip()
                if val:
                    bytecode.append(f"RETURN {val}")
                else:
                    bytecode.append("RETURN")
            
            elif line.startswith("read file"):
                m = re.search(r"read file (.+?) and store lines in (.+)", line)
                if m:
                    filename = m.group(1).strip()
                    var_name = m.group(2).strip()
                    bytecode.append(f"READFILE {filename} {var_name}")
            
            elif line.startswith("write"):
                m = re.search(r"write (.+?) to file (.+)", line)
                if m:
                    content = m.group(1).strip()
                    filename = m.group(2).strip()
                    bytecode.append(f"WRITEFILE {content} {filename}")
            
            elif line.startswith("call openweather api"):
                m = re.search(r"call openweather api with city as (.+?) and store temperature in (.+)", line)
                if m:
                    city = m.group(1).strip()
                    result_var = m.group(2).strip()
                    bytecode.append(f"APICALL WEATHER {city} {result_var}")
            i += 1
            continue
            
        # Handle specific instruction types
        if line == "END":
            bytecode.append("END")
        
        elif line.startswith("create a variable called"):
            m = re.search(r"create a variable called (.+?) and set it to (.+)", line)
            if m:
                var_name = m.group(1).strip()
                value = m.group(2).strip()
                
                # Process string literals correctly
                if (value.startswith('"') and value.endswith('"')) or (value.startswith('\'') and value.endswith('\'')):
                    # Handle escape sequences
                    value = self.process_string_literal(value)
                
                bytecode.append(f"SET {var_name} {value}")
                
        elif line.startswith("set"):
            # Handle 'Set variable to value' syntax
            m = re.search(r"set (.+?) to (.+)", line)
            if m:
                var_name = m.group(1).strip()
                value = m.group(2).strip()
                bytecode.append(f"SET {var_name} {value}")
        
        elif line.startswith("add"):
            # Handle "Add X and Y and store the result in Z" format
            m = re.search(r"add (.+?) and (.+?) and store the result in (.+)", line)
            if m:
                x = m.group(1).strip()
                y = m.group(2).strip()
                result = m.group(3).strip()
                bytecode.append(f"ADD {x} {y} {result}")
            else:
                # Handle "Add X to Y" format
                m = re.search(r"add (.+?) to (.+)", line)
                if m:
                    value = m.group(1).strip()
                    var = m.group(2).strip()
                    bytecode.append(f"ADD {value} {var} {var}")
        
        elif line.startswith("print"):
            content = line.replace("print", "").strip()
            
            # Check if it's a quoted string
            if (content.startswith('"') and content.endswith('"')) or (content.startswith('\'') and content.endswith('\'')):
                # It's a quoted string literal
                string_content = content[1:-1]  # Remove the quotes
                bytecode.append(f"PRINTSTR {string_content}")
            # Check if this looks like an unquoted string literal (legacy format)
            elif content[0].isupper() and ' ' not in content and not any(content.startswith(prefix) for prefix in ["var", "list", "dict", "count", "sum", "result", "temp"]):
                # Likely a string literal not a variable reference
                bytecode.append(f"PRINTSTR {content}")
            else:
                # Likely a variable reference
                bytecode.append(f"PRINT {content}")
        
        elif line.startswith("if"):
            m = re.search(r"if (.+?):", line)
            if m:
                condition = self.translate_condition(m.group(1).strip())
                bytecode.append(f"IF {condition}")
                
        elif line.startswith("else if"):
            m = re.search(r"else if (.+?):", line)
            if m:
                condition = self.translate_condition(m.group(1).strip())
                bytecode.append(f"ELSEIF {condition}")
                
        elif line.startswith("else"):
            bytecode.append("ELSE")
        
        elif line.startswith("while"):
            m = re.search(r"while (.+?):", line)
            if m:
                condition = self.translate_condition(m.group(1).strip())
                bytecode.append(f"WHILE {condition}")
                
        # File operations
        elif line.startswith("write"):
            m = re.search(r"write (.+?) to (.+)", line)
            if m:
                content_var = m.group(1).strip()
                file_var = m.group(2).strip()
                bytecode.append(f"WRITEFILE {content_var} {file_var}")
                
        elif line.startswith("read"):
            m = re.search(r"read (.+?) and store the result in (.+)", line)
            if m:
                file_var = m.group(1).strip()
                result_var = m.group(2).strip()
                bytecode.append(f"READFILE {file_var} {result_var}")
                
        elif line.startswith("append"):
            m = re.search(r"append (.+?) to (.+)", line)
            if m:
                content_var = m.group(1).strip()
                file_var = m.group(2).strip()
                bytecode.append(f"APPENDFILE {content_var} {file_var}")
                
        elif line.startswith("delete file"):
            m = re.search(r"delete file (.+)", line)
            if m:
                file_var = m.group(1).strip()
                bytecode.append(f"DELETEFILE {file_var}")
                
        elif line.startswith("if file exists"):
            m = re.search(r"if file exists (.+?):", line)
            if m:
                file_var = m.group(1).strip()
                bytecode.append(f"FILEEXISTS {file_var}")
        
        elif line.startswith("define a function called"):
            m = re.search(r"define a function called (.+?) with inputs (.+?):", line)
            if m:
                func_name = m.group(1).strip()
                params = [p.strip() for p in m.group(2).split("and")]
                bytecode.append(f"FUNC {func_name} {len(params)} {' '.join(params)}")
                
        # API Integration
        elif line.startswith("get weather for"):
            m = re.search(r"get weather for (.+?) and store the result in (.+)", line)
            if m:
                city_var = m.group(1).strip()
                result_var = m.group(2).strip()
                # Make sure we have API call in the bytecode
                bytecode.append(f"APICALL WEATHER {city_var} {result_var}")
        
        elif line.startswith("call"):
            m = re.search(r"call (.+?) with values (.+?) and store result in (.+)", line)
            if m:
                func_name = m.group(1).strip()
                args = [arg.strip() for arg in m.group(2).split("and")]
                result_var = m.group(3).strip()
                bytecode.append(f"CALL {func_name} {len(args)} {' '.join(args)} {result_var}")
        
        elif line.startswith("return"):
            val = line.replace("return", "").strip()
            if val:
                bytecode.append(f"RETURN {val}")
            else:
                bytecode.append("RETURN")
                
        return bytecode
        
    def translate_condition(self, condition):
        """Translate natural language conditions to bytecode format"""
        # Direct mapping of simple conditions - order matters here!
        # Handle compound conditions first
        condition = condition.replace(" is less than or equal to ", " <= ")
        condition = condition.replace(" is greater than or equal to ", " >= ")
        
        # Then handle simple conditions
        condition = condition.replace(" is equal to ", " == ")
        condition = condition.replace(" equals ", " == ")
        condition = condition.replace(" is not equal to ", " != ")
        condition = condition.replace(" is greater than ", " > ")
        condition = condition.replace(" is less than ", " < ")
        
        # Special case for exact phrase
        condition = condition.replace(" < or equal to ", " <= ")
        condition = condition.replace(" > or equal to ", " >= ")
        
        # Logical operators
        condition = condition.replace(" and ", " and ")
        condition = condition.replace(" or ", " or ")
        condition = condition.replace(" not ", " not ")
        
        return condition

if __name__ == "__main__":
    if len(sys.argv) > 2:
        compiler = EnhancedNLCompiler()
        compiler.compile(sys.argv[1], sys.argv[2])
    else:
        # Default behavior: compile program.nl to program.nlc
        input_file = "program.nl"
        output_file = "program.nlc"
        if len(sys.argv) > 1:
            input_file = sys.argv[1]
        
        compiler = EnhancedNLCompiler()
        compiler.compile(input_file, output_file)
