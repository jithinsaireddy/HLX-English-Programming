import re
import requests
import sys
import os

class EnhancedNLVM:
    """
    Enhanced Natural Language Virtual Machine
    Executes bytecode produced by the NL Compiler with support for:
    - Variables and basic operations
    - Control structures (if/while/for)
    - Functions
    - File I/O
    - API integration
    """
    def __init__(self):
        self.env = {}        # Global variable environment
        self.functions = {}  # Function definitions
        self.call_stack = [] # For tracking function calls

    def process_escape_sequences(self, s):
        """Process escape sequences in string literals"""
        if not s:
            return s
            
        # Convert string literal with Python escape sequences
        if s.startswith('"') and s.endswith('"') or s.startswith("'") and s.endswith("'"):
            try:
                # Use Python's literal_eval to properly handle escape sequences
                import ast
                # This properly handles quotes and escape sequences
                return ast.literal_eval(s)
            except Exception as e:
                # Fallback to manual replacement if literal_eval fails
                inner = s[1:-1]  # Remove surrounding quotes
                # Handle common escape sequences
                inner = inner.replace('\\n', '\n')
                inner = inner.replace('\\t', '\t')
                inner = inner.replace('\\r', '\r')
                return inner
                
        return s
        
    def mock_weather_api(self, city):
        """Mock weather API for demonstration purposes"""
        # This is a simple mock that returns fake weather data based on the city name
        city = city.lower()
        
        # Handle different city name formats
        city = city.replace('_', ' ')  # Replace underscores with spaces
        city = city.replace('-', ' ')  # Replace hyphens with spaces
        
        # Define some mock temperatures for common cities
        weather_data = {
            "san francisco": "72°F, Partly Cloudy",
            "sanfrancisco": "72°F, Partly Cloudy",
            "san_francisco": "72°F, Partly Cloudy",
            "new york": "68°F, Sunny",
            "newyork": "68°F, Sunny",
            "new_york": "68°F, Sunny",
            "london": "59°F, Rainy",
            "tokyo": "75°F, Clear",
            "paris": "62°F, Cloudy"
        }
        
        # Print debug info for API calls
        print(f"API Call: Getting weather for '{city}'")
        
        # Return the weather for the city if available, otherwise a default message
        return weather_data.get(city, f"65°F, Weather data not available for {city}")

    def execute(self, bytecode_file):
        """Execute bytecode from a file"""
        with open(bytecode_file, "r") as f:
            instructions = [line.strip() for line in f.readlines() if line.strip()]
        
        # Execute the program
        self.execute_instructions(instructions)
    
    def execute_instructions(self, instructions, local_env=None):
        """Execute a list of bytecode instructions"""
        env = local_env or self.env
        i = 0
        
        while i < len(instructions):
            instr = instructions[i]
            parts = instr.split()
            cmd = parts[0]

            # Basic operations
            if cmd == "SET":
                var = parts[1]
                # Extract the value part (could be multiple parts for a quoted string with spaces)
                val_part = " ".join(parts[2:])
                # Process and parse the value
                val = self.parse_value(val_part, env)
                
                # For proper string handling - if it's a quoted string, remove the quotes
                if isinstance(val, str):
                    if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                        # Remove the quotes but keep the inner content
                        val = val[1:-1]
                
                # Store in the environment
                env[var] = val
            
            elif cmd == "ADD":
                x, y, res = parts[1], parts[2], parts[3]
                val1 = self.get_value(x, env)
                val2 = self.get_value(y, env)
                
                # Convert strings to numbers if possible for arithmetic operations
                if isinstance(val1, str) and val1.lstrip('-').isdigit():
                    val1 = int(val1)
                elif isinstance(val1, str):
                    try:
                        val1 = float(val1)
                    except ValueError:
                        # Keep as string if not convertible
                        pass
                        
                if isinstance(val2, str) and val2.lstrip('-').isdigit():
                    val2 = int(val2)
                elif isinstance(val2, str):
                    try:
                        val2 = float(val2)
                    except ValueError:
                        # Keep as string if not convertible
                        pass
                
                # Perform the addition with proper type handling
                try:
                    # If both are numeric, do a mathematical addition
                    if (isinstance(val1, (int, float)) and isinstance(val2, (int, float))):
                        env[res] = val1 + val2  # Numeric addition
                    else:
                        # For mixed types or strings, try numeric addition first, then concat
                        try:
                            result = float(val1) + float(val2)
                            # If it's a whole number, convert to int
                            if result.is_integer():
                                env[res] = int(result)
                            else:
                                env[res] = result
                        except (ValueError, TypeError):
                            # If numeric conversion fails, do string concatenation
                            env[res] = str(val1) + str(val2)
                except Exception as e:
                    # Log the error and fall back to string concatenation
                    print(f"Warning: Error in ADD operation: {e}")
                    env[res] = str(val1) + str(val2)
            
            elif cmd == "PRINT":
                var = parts[1]
                value = env.get(var, f"{var} not defined")
                
                # Handle string literals better
                if isinstance(value, str):
                    # If it's a string that starts with a quote, it's likely a string literal
                    # that was processed properly. Print it without the surrounding quotes.
                    if value.startswith('"') and value.endswith('"'):
                        # Remove the surrounding quotes for display
                        print(value[1:-1])  # Print without the quotes
                    elif value.startswith('\'') and value.endswith('\''):
                        # Handle single quotes too
                        print(value[1:-1])  # Print without the quotes
                    else:
                        print(value)  # Print as is
                else:
                    print(value)  # Print as is for non-string values
                
            elif cmd == "PRINTSTR":
                # For direct string literals
                # Join all parts after the command to preserve spaces
                text = " ".join(parts[1:])
                # Process any escape sequences in the text
                processed_text = self.process_escape_sequences(text)
                print(processed_text)
            
            # Control flow
            elif cmd == "IF":
                condition = self.evaluate_condition(" ".join(parts[1:]), env)
                i += 1
                block_info = self.find_if_block_structure(instructions, i)
                
                if condition:
                    # Execute the IF block
                    self.execute_instructions(instructions[i:block_info['else_pos'] or block_info['elseif_pos'] or block_info['end_pos']], env)
                    i = block_info['end_pos']
                elif block_info['elseif_pos']:
                    # Skip to the ELSEIF
                    i = block_info['elseif_pos']
                    continue  # Continue to process the ELSEIF
                elif block_info['else_pos']:
                    # Execute the ELSE block
                    self.execute_instructions(instructions[block_info['else_pos']+1:block_info['end_pos']], env)
                    i = block_info['end_pos']
                else:
                    # No ELSE or ELSEIF, skip to the end
                    i = block_info['end_pos']
                continue
                
            elif cmd == "ELSEIF":
                condition = self.evaluate_condition(" ".join(parts[1:]), env)
                i += 1
                block_info = self.find_if_block_structure(instructions, i)
                
                if condition:
                    # Execute the ELSEIF block
                    self.execute_instructions(instructions[i:block_info['else_pos'] or block_info['elseif_pos'] or block_info['end_pos']], env)
                    i = block_info['end_pos']
                elif block_info['elseif_pos']:
                    # Skip to the next ELSEIF
                    i = block_info['elseif_pos']
                    continue  # Continue to process the ELSEIF
                elif block_info['else_pos']:
                    # Execute the ELSE block
                    self.execute_instructions(instructions[block_info['else_pos']+1:block_info['end_pos']], env)
                    i = block_info['end_pos']
                else:
                    # No more ELSE or ELSEIF, skip to the end
                    i = block_info['end_pos']
                continue
                
            elif cmd == "ELSE":
                # ELSE blocks are handled within the IF and ELSEIF processing
                i += 1
                block_end = self.find_matching_end(instructions, i)
                i = block_end
                continue
            
            elif cmd == "WHILE":
                condition_expr = " ".join(parts[1:])
                i += 1
                block_start = i
                block_end = self.find_matching_end(instructions, i)
                
                while self.evaluate_condition(condition_expr, env):
                    self.execute_instructions(instructions[block_start:block_end], env)
                
                i = block_end
                continue
                    
            # File operations
            elif cmd == "WRITEFILE":
                content_var = parts[1]
                file_var = parts[2]
                content = self.get_value(content_var, env)
                filename = self.get_value(file_var, env)
                
                # Process string literals and escape sequences
                content = self.process_escape_sequences(str(content))
                filename = self.process_escape_sequences(str(filename))
                
                try:
                    with open(filename, 'w') as f:
                        f.write(str(content))
                except Exception as e:
                    print(f"Error writing to file: {e}")
                    
            elif cmd == "READFILE":
                # Read from a file
                filename = parts[1]
                result_var = parts[2]
                
                # Get the filename value
                filename_val = env.get(filename, filename)
                
                # Process string literals correctly
                if isinstance(filename_val, str) and filename_val.startswith('"') and filename_val.endswith('"'):
                    filename_val = filename_val[1:-1]  # Remove surrounding quotes
                    
                try:
                    with open(filename_val, "r") as f:
                        # Store the content as raw text without any quote processing
                        content = f.read()
                        # Ensure there are no quotes surrounding the content
                        if content.startswith('"') and content.endswith('"'):
                            content = content[1:-1]
                        elif content.startswith('\'') and content.endswith('\''):
                            content = content[1:-1]
                        # Store it in the environment
                        env[result_var] = content
                except Exception as e:
                    print(f"Error reading file: {e}")
                    env[result_var] = f"Error: {str(e)}"
                    
            elif cmd == "APPENDFILE":
                content_var = parts[1]
                file_var = parts[2]
                
                # Get values from environment
                content_val = env.get(content_var, content_var)
                filename_val = env.get(file_var, file_var)
                
                # Process string literals correctly
                if isinstance(content_val, str) and content_val.startswith('"') and content_val.endswith('"'):
                    content_val = content_val[1:-1]  # Remove surrounding quotes
                
                if isinstance(filename_val, str) and filename_val.startswith('"') and filename_val.endswith('"'):
                    filename_val = filename_val[1:-1]  # Remove surrounding quotes
                
                try:
                    with open(filename_val, 'a') as f:
                        f.write(str(content_val))
                except Exception as e:
                    print(f"Error appending to file: {e}")
                    
            elif cmd == "DELETEFILE":
                file_var = parts[1]
                filename = self.get_value(file_var, env)
                
                # Process string literals and escape sequences
                filename = self.process_escape_sequences(str(filename))
                
                try:
                    import os
                    if os.path.exists(filename):
                        os.remove(filename)
                except Exception as e:
                    print(f"Error deleting file: {e}")
                    
            elif cmd == "FILEEXISTS":
                file_var = parts[1]
                filename = self.get_value(file_var, env)
                
                # Process string literals and escape sequences
                filename = self.process_escape_sequences(str(filename))
                
                try:
                    import os
                    condition = os.path.exists(filename)
                    i += 1
                    block_info = self.find_if_block_structure(instructions, i)
                    
                    if condition:
                        # Execute the IF block
                        self.execute_instructions(instructions[i:block_info['else_pos'] or block_info['elseif_pos'] or block_info['end_pos']], env)
                        i = block_info['end_pos']
                    elif block_info['else_pos']:
                        # Execute the ELSE block
                        self.execute_instructions(instructions[block_info['else_pos']+1:block_info['end_pos']], env)
                        i = block_info['end_pos']
                    else:
                        # No ELSE, skip to the end
                        i = block_info['end_pos']
                    continue
                except Exception as e:
                    print(f"Error checking file existence: {e}")
                    i = self.find_matching_end(instructions, i + 1)
                    continue
            
            # API operations
            elif cmd == "APICALL":
                api_type = parts[1]
                if api_type == "WEATHER":
                    city_var = parts[2]
                    result_var = parts[3]
                    city = self.get_value(city_var, env)
                    
                    # Process any string literals and remove quotes
                    if isinstance(city, str):
                        # Remove surrounding quotes if present
                        if (city.startswith('"') and city.endswith('"')) or \
                           (city.startswith('\'') and city.endswith('\'')):
                            city = city[1:-1]
                        # Process escape sequences
                        city = self.process_escape_sequences(city)
                    
                    try:
                        # In a real implementation, this would make an actual API call
                        # For demo purposes, we return mock data
                        weather_data = self.mock_weather_api(city)
                        env[result_var] = weather_data
                    except Exception as e:
                        print(f"Error making API call: {e}")
                        env[result_var] = "Error retrieving data"
            
            # Function operations
            elif cmd == "FUNC":
                func_name = parts[1]
                param_count = int(parts[2])
                params = parts[3:3+param_count]
                i += 1
                block_start = i
                block_end = self.find_matching_end(instructions, i)
                
                self.functions[func_name] = {
                    "params": params,
                    "body": instructions[block_start:block_end]
                }
                
                i = block_end
                continue
            
            elif cmd == "CALL":
                func_name = parts[1]
                arg_count = int(parts[2])
                args = [self.get_value(arg, env) for arg in parts[3:3+arg_count]]
                result_var = parts[3+arg_count] if 3+arg_count < len(parts) else None
                
                if func_name in self.functions:
                    func_def = self.functions[func_name]
                    func_env = dict(zip(func_def["params"], args))
                    
                    # Execute function
                    self.call_stack.append(func_name)
                    result = self.execute_function(func_def["body"], func_env)
                    self.call_stack.pop()
                    
                    # Store result if needed
                    if result_var and result is not None:
                        env[result_var] = result
                else:
                    # Handle special built-in functions
                    result = self.execute_builtin(func_name, args)
                    if result_var and result is not None:
                        env[result_var] = result
            
            # File operations
            elif cmd == "READFILE":
                filename, var = parts[1], parts[2]
                with open(self.get_value(filename, env), "r") as f:
                    env[var] = f.read().splitlines()
            
            elif cmd == "WRITEFILE":
                content = parts[1]
                filename = parts[2]
                
                # Get the content and filename values
                content_val = env.get(content, content)
                filename_val = env.get(filename, filename)
                
                # Process string literals correctly
                if isinstance(content_val, str) and content_val.startswith('"') and content_val.endswith('"'):
                    content_val = content_val[1:-1]  # Remove surrounding quotes
                
                if isinstance(filename_val, str) and filename_val.startswith('"') and filename_val.endswith('"'):
                    filename_val = filename_val[1:-1]  # Remove surrounding quotes
                
                # Write content to file
                with open(filename_val, "w") as f:
                    f.write(str(content_val))
            
            # API operations 
            elif cmd == "APICALL":
                api_type, arg, result_var = parts[1], parts[2], parts[3]
                if api_type == "WEATHER":
                    city = self.get_value(arg, env)
                    env[result_var] = self.call_weather_api(city)
            
            i += 1
            
        return env.get("result", None)  # Return the result variable if it exists
    
    def execute_function(self, instructions, local_env):
        """Execute a function and return its result"""
        for i, instr in enumerate(instructions):
            parts = instr.split()
            cmd = parts[0]
            
            if cmd == "RETURN":
                if len(parts) > 1:
                    return self.get_value(parts[1], local_env)
                return None
        
        # Execute the function body
        result = self.execute_instructions(instructions, local_env)
        return result
    
    def execute_builtin(self, func_name, args):
        """Execute a built-in function"""
        if func_name == "WEATHER":
            return self.call_weather_api(args[0])
        return None
    
    def call_weather_api(self, city):
        """Mock API call to weather service"""
        return f"{city.title()} has 22°C (demo value)"
    
    def evaluate_condition(self, condition, env):
        """Evaluate a condition expression"""
        parts = condition.split()
        if len(parts) < 3:
            return False
        
        left = self.get_value(parts[0], env)
        operator = parts[1]
        right = self.get_value(parts[2], env)
        
        # Type conversion for numeric comparisons
        # Convert strings to numbers if possible for comparison
        if isinstance(left, str) and left.lstrip('-').isdigit():
            left = int(left)
        elif isinstance(left, str):
            try:
                left = float(left)
            except ValueError:
                # Keep as string if not convertible
                pass
                
        if isinstance(right, str) and right.lstrip('-').isdigit():
            right = int(right)
        elif isinstance(right, str):
            try:
                right = float(right)
            except ValueError:
                # Keep as string if not convertible
                pass
        
        # If types are still different after conversion attempts
        if type(left) != type(right):
            # Convert both to strings for comparison if types are different
            left = str(left)
            right = str(right)
        
        if operator == "==":
            return left == right
        elif operator == "!=":
            return left != right
        elif operator == "<":
            return left < right
        elif operator == ">":
            return left > right
        elif operator == "<=":
            return left <= right
        elif operator == ">=":
            return left >= right
        
        return False
    
    def find_matching_end(self, instructions, start_idx):
        """Find the matching END instruction for blocks"""
        nesting = 1
        for i in range(start_idx, len(instructions)):
            parts = instructions[i].split()
            cmd = parts[0]
            
            if cmd in ["IF", "WHILE", "FUNC"]:
                nesting += 1
            elif cmd == "END":
                nesting -= 1
                if nesting == 0:
                    return i + 1
        
        return len(instructions)
    
    def find_if_block_structure(self, instructions, start_idx):
        """Find the structure of an if-elseif-else block
        
        Returns a dictionary with positions of:
        - elseif_pos: Position of the first ELSEIF (if any)
        - else_pos: Position of the ELSE (if any)
        - end_pos: Position after the final END
        """
        result = {
            'elseif_pos': None,
            'else_pos': None,
            'end_pos': None
        }
        
        nesting = 1
        i = start_idx
        
        while i < len(instructions):
            parts = instructions[i].split()
            cmd = parts[0]
            
            if cmd in ["IF", "WHILE", "FUNC"]:
                nesting += 1
            elif cmd == "ELSEIF" and nesting == 1:
                # Found an ELSEIF at the same level
                if result['elseif_pos'] is None:
                    result['elseif_pos'] = i
            elif cmd == "ELSE" and nesting == 1:
                # Found an ELSE at the same level
                result['else_pos'] = i
            elif cmd == "END":
                nesting -= 1
                if nesting == 0:
                    # Found the matching END
                    result['end_pos'] = i + 1
                    break
            
            i += 1
        
        if result['end_pos'] is None:
            result['end_pos'] = len(instructions)
            
        return result
    
    def get_value(self, token, env):
        """Get a value from the environment or parse it as a literal"""
        if token in env:
            return env[token]
        return self.parse_value(token, env)
    
    def parse_value(self, val, env=None):
        """Parse a literal value into the appropriate type"""
        # Handle empty or None value
        if not val:
            return ""
            
        # Remove quotes if it's a string but preserve the original string format
        # so we can handle it properly when displaying
        if val.startswith('"') and val.endswith('"'):
            # Keep the quotes in the string but mark it as a processed string literal
            # so we know to strip the quotes when displaying
            return val  # Preserve quotes for later processing
        if val.startswith("'") and val.endswith("'"):
            # Similarly preserve single quotes
            return val  # Preserve quotes for later processing
        
        # Handle boolean values
        if val.lower() == "true": 
            return True
        if val.lower() == "false": 
            return False
        
        # Try to convert to a number
        try:
            return int(val)
        except ValueError:
            try:
                return float(val)
            except ValueError:
                pass
        
        # If not a recognized literal and not in environment, return as is
        return val

if __name__ == "__main__":
    if len(sys.argv) > 1:
        vm = EnhancedNLVM()
        vm.execute(sys.argv[1])
    else:
        print("Usage: python enhanced_nlvm.py <bytecode_file>")
