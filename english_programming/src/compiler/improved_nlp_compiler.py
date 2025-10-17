"""
Improved NLP-Enhanced Compiler for English Programming
This version improves the original NLPEnhancedCompiler with:
- Better arithmetic operation detection and handling
- Enhanced string concatenation support
- Improved counter operations
- Better variable reference handling
- Function definition and calling with parameters and return values
- List and dictionary operations
- File I/O capabilities
"""
import re
import sys
import os
from typing import List, Dict, Tuple, Optional, Any

"""
Import from the `compiler` package which is expected to be on sys.path.
Both the web app and CLI add `english_programming/src` to sys.path,
so `compiler.*` imports are the most robust across environments.
"""
from compiler.enhanced_nl_compiler import EnhancedNLCompiler

# Import our enhanced NLP functions
from compiler.enhanced_nlp_functions import (
    enhanced_analyze_with_nlp,
    process_arithmetic_operation,
    process_string_concatenation,
    handle_counter_operations,
    handle_print_statements,
    handle_conditional_statements,
    handle_string_concatenation,
    handle_arithmetic_operations
)
from compiler.ir import IRInstruction, IRProgram

class ImprovedNLPCompiler(EnhancedNLCompiler):
    """
    Improved NLP-Enhanced Compiler with better support for:
    - Arithmetic operations (add, subtract, multiply, divide)
    - String operations (concatenation)
    - Counter operations
    - Variable references
    - Functions with parameters and return values
    - List and dictionary operations
    - File I/O operations
    """
    def __init__(self):
        """Initialize the compiler with enhanced NLP capabilities"""
        # Initialize the base compiler
        super().__init__()
        
        # Initialize spaCy for NLP capabilities (optional)
        self.has_spacy = False
        self.nlp = None
        try:
            # Import spaCy lazily so module import works without it
            import importlib
            spacy_module = importlib.import_module("spacy")
            print("Loading spaCy model... (This may take a moment)")
            self.nlp = spacy_module.load("en_core_web_sm")
            print("spaCy model loaded successfully!")
            self.has_spacy = True
        except Exception as e:
            print(f"Warning: spaCy unavailable. Using regex fallback only. Error: {e}")
        
        # Track defined variables and functions
        self.defined_variables = set()
        self.functions = {}
        
        # Enhanced patterns for more flexible natural language
        self.var_patterns = [
            # Standard set x to y (most common, check first)
            r"(?:set|make|let) ([\w_]+) (?:to|be|equal to|equals|=) (.+)",
            
            # Create a variable x with value 42
            r"(?:create|make|define|set up|establish) (?:a|the|an)? (?:variable|var) (?:called|named)? ([\w_]+) (?:with|to|as|with|equal to|equals|=|having|has|having a) (?:value|the value|a value)? ?(?:of|to|as)? (.+)",
            
            # Create a variable x and set it to 42 - this pattern needs special handling
            r"(?:create|make|define|set up|establish) (?:a|the|an)? (?:variable|var) (?:called|named)? ([\w_]+)(?: (?:and|then)? (?:set|make|let) (?:it|this) (?:to|equal to|equals|=) (.+))?",
            
            # Polite forms
            r"(?:please|kindly|could you)? (?:create|make|define|set) (?:a|the|an)? (?:variable|var)? ([\w_]+) (?:to|as|with|equal to|equals|=) (.+)"
        ]
        
        # Track specific patterns that need special handling
        self.create_var_pattern = r"create\s+a\s+variable\s+([\w_]+)\s+and\s+set\s+it\s+to\s+([\w\d]+)"
        
        # Questions about variables
        self.question_patterns = [
            r"(?:what is|what's) ([\w_]+)\??",
            r"(?:what is|what's) (?:the value of) ([\w_]+)\??",
            r"(?:tell me|show me) (?:about|the value of)? ([\w_]+)\??"
        ]
        
        # Print commands
        self.print_patterns = [
            r"(?:print|display|show|output) (?:the |)?([\w_]+)",
            r"(?:tell me|show me) (?:about |the |)?([\w_]+)"
        ]
    
    def analyze_with_nlp(self, line: str) -> Dict:
        """Use the enhanced NLP analysis function"""
        return enhanced_analyze_with_nlp(self.nlp, line, self.has_spacy)
    
    def process_string_literal(self, value):
        """Process string literals with better handling of expressions"""
        # If value is None or empty, return empty string
        if not value:
            return ""
        
        # First, check if it's a string literal (surrounded by quotes)
        if isinstance(value, str) and len(value) >= 2:
            # Check for double quotes
            if value.startswith('"') and value.endswith('"'):
                return value  # Keep as is for bytecode
                
            # Check for single quotes
            if value.startswith("'") and value.endswith("'"):
                # Convert single to double quotes for consistency
                return f'"{value[1:-1]}"'
        
        # If it's just a numeric string, convert to proper format for bytecode
        if isinstance(value, str) and value.replace('.', '', 1).isdigit():
            # If it contains a decimal point, it's a float
            if '.' in value:
                return float(value)
            else:
                return int(value)
        
        # For other values, treat as a string literal
        return f'"{value}"'
    
    def normalize_with_nlp(self, line: str) -> str:
        """
        Enhanced line normalization with better handling of:
        - Arithmetic operations
        - String operations
        - Counter operations
        - Print statements
        - Conditional statements
        - Functions (definition, call, return)
        - Data structures (lists, dictionaries)
        - Collection operations (length, sum, indexing)
        """
        if not line.strip():
            return None  # Skip empty lines
        
        # First check for variable creation pattern (high priority)
        create_var_match = re.match(r"create a variable called (\w+) and set it to (.+)", line, re.IGNORECASE)
        if create_var_match:
            var_name = create_var_match.group(1).strip()
            var_value = create_var_match.group(2).strip()
            bytecode = f"SET {var_name} {var_value}"
            print(f"  Compiler: Creating variable {var_name} = {var_value}")
            return bytecode
            
        # Then try counter operations (simple and common)
        counter_bytecode = handle_counter_operations(line)
        if counter_bytecode:
            return counter_bytecode
        
        # Handle print statements
        print_bytecode = handle_print_statements(line)
        if print_bytecode:
            return print_bytecode
        
        # Function definition
        func_match = re.match(r"define a function called (\w+) with inputs (.+):", line.lower())
        if func_match:
            name = func_match.group(1)
            params = [p.strip() for p in func_match.group(2).split("and")]
            return f"FUNC_DEF {name} {' '.join(params)}"
        
        # Function call
        call_match = re.match(r"call (\w+) with (?:values|inputs) (.+) and store (?:result|output) in (\w+)", line.lower())
        if call_match:
            func_name = call_match.group(1)
            args = [a.strip() for a in call_match.group(2).split("and")]
            result_var = call_match.group(3)
            return f"CALL {func_name} {' '.join(args)} {result_var}"
        
        # Return statement
        return_match = re.match(r"return (\w+)", line.lower())
        if return_match:
            return f"RETURN {return_match.group(1)}"
        
        # List creation - higher priority due to specificity
        list_match = re.match(r"create a list called (\w+) with values (.+)", line, re.IGNORECASE)
        if list_match:
            list_name = list_match.group(1)
            items = [item.strip() for item in list_match.group(2).split(",")]
            print(f"  Compiler: Creating LIST bytecode for {list_name} with items {items}")
            return f"LIST {list_name} {' '.join(items)}"
        
        # Dictionary creation
        dict_match = re.match(r"create a dictionary called (\w+) with (.+)", line, re.IGNORECASE)
        if dict_match:
            dict_name = dict_match.group(1)
            # Handle the case where entries are separated by commas and/or 'and'
            content = dict_match.group(2)
            # Replace 'and' with comma for consistent splitting
            content = re.sub(r'\s+and\s+', ', ', content)
            parts = [p.strip() for p in content.split(",")]
            
            kvs = []
            for part in parts:
                if " as " in part:
                    try:
                        # Split only on the first occurrence of 'as'
                        k_part, v_part = part.split(" as ", 1)
                        k = k_part.strip()
                        v = v_part.strip()
                        kvs.append(f"{k}:{v}")
                    except ValueError:
                        print(f"  Warning: Could not parse dictionary entry: {part}")
            
            if kvs:
                result = f"DICT {dict_name} {','.join(kvs)}"
                print(f"  Compiler: Creating DICT bytecode for {dict_name} with kvs {kvs}")
                return result
            else:
                print(f"  Warning: No valid key-value pairs found in dictionary creation")
                # Create empty dictionary as fallback
                return f"DICT {dict_name} empty:empty"

        
        # List/collection length
        length_match = re.match(r"get the length of (?:list )?(\w+) and store (?:it )?in (\w+)", line, re.IGNORECASE)
        if length_match:
            list_name = length_match.group(1)
            result = length_match.group(2)
            bytecode = f"BUILTIN LENGTH {list_name} {result}"
            print(f"  Compiler: Creating LENGTH bytecode for {list_name} stored in {result}")
            return bytecode

        # Support simplified phrase: "length of X store in Y" (zero-warning)
        length_short = re.match(r"length of\s+(\w+)\s+store in\s+(\w+)$", line.strip(), re.IGNORECASE)
        if length_short:
            list_name = length_short.group(1)
            result = length_short.group(2)
            bytecode = f"BUILTIN LENGTH {list_name} {result}"
            print(f"  Compiler: Creating LENGTH (short) for {list_name} -> {result}")
            return bytecode
        
        # List sum
        sum_match = re.match(r"get the sum of (?:list )?(\w+) and store (?:it )?in (\w+)", line, re.IGNORECASE)
        if sum_match:
            list_name = sum_match.group(1)
            result = sum_match.group(2)
            bytecode = f"BUILTIN SUM {list_name} {result}"
            print(f"  Compiler: Creating SUM bytecode for {list_name} stored in {result}")
            return bytecode
        
        # List indexing
        index_match = re.match(r"get (?:the )?item at index (\d+) from (?:list )?(\w+) and store (?:it )?in (\w+)", line, re.IGNORECASE)
        if index_match:
            idx = index_match.group(1)
            list_name = index_match.group(2)
            result = index_match.group(3)
            bytecode = f"INDEX {list_name} {idx} {result}"
            print(f"  Compiler: Creating INDEX bytecode for {list_name}[{idx}] stored in {result}")
            return bytecode

        # Pop from list X store in Y
        pop_match = re.match(r"pop from list\s+(\w+)\s+store in\s+(\w+)$", line, re.IGNORECASE)
        if pop_match:
            src = pop_match.group(1)
            dest = pop_match.group(2)
            print(f"  Compiler: Creating POP bytecode for list {src} -> {dest}")
            return f"LIST_POP {src} {dest}"
        
        # NOW special case should come before generic GET
        now_early = re.match(r"get (?:the )?current time (?:and )?store (?:it )?in (\w+)", line, re.IGNORECASE)
        if now_early:
            return f"NOW {now_early.group(1)}"
        # Dictionary access
        # NOTE: generic get fallback kept, but later we prioritize specific patterns like NOW/JSONGET
        get_match = re.match(r"get (\w+) (\w+) and store (?:it )?in (\w+)", line, re.IGNORECASE)
        if get_match:
            dict_name = get_match.group(1)
            key = get_match.group(2)
            result = get_match.group(3)
            bytecode = f"GET {dict_name} {key} {result}"
            print(f"  Compiler: Creating GET bytecode for {dict_name}[{key}] stored in {result}")
            return bytecode
        
        # String concatenation - better handling for literals
        concat_pattern = r'concatenate\s+("[^"]*"|[\w]+)\s+and\s+("[^"]*"|[\w]+)\s+and\s+store\s+(?:it\s+)?in(?:to)?\s+([\w]+)'
        concat_match = re.match(concat_pattern, line, re.IGNORECASE)
        if concat_match:
            str1 = concat_match.group(1).strip()
            str2 = concat_match.group(2).strip()
            result = concat_match.group(3).strip()
            
            print(f"  Compiler: Found string concatenation: '{str1}' + '{str2}' -> '{result}'")
            
            # Process string literals - keep quotes for bytecode
            # No need to modify - we'll pass the literals as-is to the bytecode
                
            bytecode = f"CONCAT {str1} {str2} {result}"
            print(f"  Compiler: Creating CONCAT bytecode for {str1} + {str2} stored in {result}")
            return bytecode
        
        # Try to match our enhanced variable patterns
        for pattern in self.var_patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                print(f"Pattern {self.var_patterns.index(pattern)} matched: {pattern}")
                # Most patterns have two groups: var_name and value
                if len(match.groups()) >= 2:
                    var_name = match.group(1).strip()
                    value = match.group(2).strip() if match.group(2) else ""
                    print(f"Captured var_name: '{var_name}', value: '{value}'")
                    
                    # Special handling for "create a variable" pattern
                    if var_name == "it" and "create a variable called" in line.lower():
                        # Extract the real variable name from the full line
                        real_var_match = re.search(r"create a variable called (\w+)", line.lower())
                        if real_var_match:
                            var_name = real_var_match.group(1).strip()
                            print(f"  Corrected variable name to: '{var_name}'")
                    
                    # Process the value to convert if needed (string, number, etc.)
                    processed_value = self.process_string_literal(value)
                    print(f"  Compiler: Creating SET bytecode: {var_name} = {processed_value}")
                    return f"SET {var_name} {processed_value}"
        
        # Try arithmetic operations (add, subtract, multiply, divide)
        add_match = re.match(r"(?:add|sum|calculate|compute) (\w+) and (\w+)(?: and store (?:the )?(?:result|outcome|sum|value) in (\w+))?(?:\.)?$", line.lower())
        if add_match:
            op1 = add_match.group(1).strip()
            op2 = add_match.group(2).strip()
            
            # Default result variable if none specified
            result_var = add_match.group(3).strip() if add_match.group(3) else "result"
            
            bytecode = f"ADD {op1} {op2} {result_var}"
            print(f"  Compiler: Creating ADD bytecode: {op1} + {op2} = {result_var}")
            return bytecode

        # Additional arithmetic phrases
        mul_simple = re.match(r"multiply (\w+) by (\w+) and store the result in (\w+)", line.lower())
        if mul_simple:
            return f"MUL {mul_simple.group(1)} {mul_simple.group(2)} {mul_simple.group(3)}"

        div_simple = re.match(r"divide (\w+) by (\w+) and store the result in (\w+)", line.lower())
        if div_simple:
            return f"DIV {div_simple.group(1)} {div_simple.group(2)} {div_simple.group(3)}"

        sub_simple = re.match(r"subtract (\w+) from (\w+) and store the result in (\w+)", line.lower())
        if sub_simple:
            return f"SUB {sub_simple.group(2)} {sub_simple.group(1)} {sub_simple.group(3)}"
            
        # Check for print/display patterns
        for pattern in self.print_patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                var_name = match.group(1).strip()
                # Remove any trailing punctuation
                var_name = var_name.rstrip('.,;?!')
                
                # If it starts with a quote, it's a string literal
                if var_name.startswith('"') or var_name.startswith("'"):
                    if var_name.endswith('"') or var_name.endswith("'"):
                        # Remove quotes for PRINTSTR
                        return f"PRINTSTR {var_name[1:-1]}"
                
                # Otherwise, it's a variable reference
                return f"PRINT {var_name}"
        
        # Handle file operations
        write_match = re.match(r"write \"(.+?)\" to file (.+)", line, re.IGNORECASE)
        if write_match:
            content = write_match.group(1)
            filename = write_match.group(2)
            return f"WRITEFILE \"{content}\" file {filename}"
        append_match = re.match(r"append \"(.+?)\" to (.+)", line.lower())
        if append_match:
            content = append_match.group(1)
            filename = append_match.group(2)
            return f"APPENDFILE \"{content}\" file {filename}"
        
        read_match = re.match(r"read file (.+) and store (?:lines|contents) in (\w+)", line, re.IGNORECASE)
        if read_match:
            filename = read_match.group(1)
            var_name = read_match.group(2)
            return f"READ {filename} {var_name}"

        # String stdlib operations
        up_match = re.match(r"make (?:the )?(\w+) uppercase and store (?:it )?in (\w+)", line, re.IGNORECASE)
        if up_match:
            src = up_match.group(1)
            dest = up_match.group(2)
            return f"STRUPPER {src} {dest}"

        low_match = re.match(r"make (?:the )?(\w+) lowercase and store (?:it )?in (\w+)", line, re.IGNORECASE)
        if low_match:
            src = low_match.group(1)
            dest = low_match.group(2)
            return f"STRLOWER {src} {dest}"

        trim_match = re.match(r"trim (?:the )?(\w+) and store (?:it )?in (\w+)", line, re.IGNORECASE)
        if trim_match:
            src = trim_match.group(1)
            dest = trim_match.group(2)
            return f"STRTRIM {src} {dest}"

        # HTTP GET
        http_match = re.match(r"http get (?:from )?(\S+) and store (?:it|response|result) in (\w+)", line, re.IGNORECASE)
        if http_match:
            url = http_match.group(1)
            dest = http_match.group(2)
            return f"HTTPGET {url} {dest}"

        # HTTP POST with JSON
        post_match = re.match(r"http post to (\S+) with (?:json )?(\w+) and store (?:it|response|result) in (\w+)(?: (?:headers|with headers) (.+))?", line, re.IGNORECASE)
        if post_match:
            url = post_match.group(1)
            body = post_match.group(2)
            dest = post_match.group(3)
            headers = post_match.group(4)
            header_tokens = []
            if headers:
                for h in re.split(r"\s+", headers.strip()):
                    if '=' in h or ':' in h:
                        header_tokens.append(h)
            return " ".join(["HTTPPOST", url, body, dest] + header_tokens)

        # JSON parse/stringify
        jp = re.match(r"parse json (\w+) and store (?:it|result) in (\w+)", line, re.IGNORECASE)
        if jp:
            return f"JSONPARSE {jp.group(1)} {jp.group(2)}"

        js = re.match(r"stringify json (\w+) and store (?:it|result) in (\w+)", line, re.IGNORECASE)
        if js:
            return f"JSONSTRINGIFY {js.group(1)} {js.group(2)}"

        # Now/datetime
        now_match = re.match(r"get (?:the )?current time (?:and )?store (?:it )?in (\w+)", line, re.IGNORECASE)
        if now_match:
            return f"NOW {now_match.group(1)}"

        # Regex match
        rx = re.match(r"check if (\w+) matches (\S+) and store (?:it|result) in (\w+)", line, re.IGNORECASE)
        if rx:
            return f"REGEXMATCH {rx.group(1)} {rx.group(2)} {rx.group(3)}"

        # Regex capture groups
        rxc = re.match(r"capture group (\d+) from (\w+) with (\S+) and store (?:it|result) in (\w+)", line, re.IGNORECASE)
        if rxc:
            return f"REGEXCAPTURE {rxc.group(2)} {rxc.group(3)} {rxc.group(1)} {rxc.group(4)}"

        # HTTP headers mutation
        seth = re.match(r"set http header (\S+) to (\S+)", line, re.IGNORECASE)
        if seth:
            return f"HTTPSETHEADER {seth.group(1)} {seth.group(2)}"

        # JSON helpers
        jg = re.match(r"get json (\w+) key (\S+) and store (?:it|result) in (\w+)", line, re.IGNORECASE)
        if jg:
            return f"JSONGET {jg.group(1)} {jg.group(2)} {jg.group(3)}"
        jk = re.match(r"get json keys from (\w+) and store (?:them|it) in (\w+)", line, re.IGNORECASE)
        if jk:
            return f"JSONKEYS {jk.group(1)} {jk.group(2)}"
        jv = re.match(r"get json values from (\w+) and store (?:them|it) in (\w+)", line, re.IGNORECASE)
        if jv:
            return f"JSONVALUES {jv.group(1)} {jv.group(2)}"

        # Regex replace
        rrr = re.match(r"replace (\S+) in (\w+) with (\S+) and store (?:it|result) in (\w+)", line, re.IGNORECASE)
        if rrr:
            return f"REGEXREPLACE {rrr.group(2)} {rrr.group(1)} {rrr.group(3)} {rrr.group(4)}"

        # Date formatting
        df = re.match(r"format (\w+|now) as (\S+) and store (?:it|result) in (\w+)", line, re.IGNORECASE)
        if df:
            return f"DATEFORMAT {df.group(1)} {df.group(2)} {df.group(3)}"

        # Import by URL
        imp = re.match(r"import module from (\S+)", line, re.IGNORECASE)
        if imp:
            return f"IMPORTURL {imp.group(1)}"
        
        # If basic patterns didn't match and we have spaCy, use enhanced NLP analysis
        if self.has_spacy:
            nlp_result = self.analyze_with_nlp(line)
            if nlp_result:
                # Check for arithmetic operations
                if nlp_result['operation'] in ['add', 'subtract', 'multiply', 'divide'] and len(nlp_result['operands']) >= 2:
                    bytecode = process_arithmetic_operation(
                        nlp_result['operation'], 
                        nlp_result['operands'], 
                        nlp_result['result_var']
                    )
                    if bytecode:
                        return bytecode
                
                # Check for string concatenation
                if nlp_result['operation'] == 'concat' and len(nlp_result['operands']) >= 2:
                    bytecode = process_string_concatenation(
                        nlp_result['operands'],
                        nlp_result['result_var'],
                        self.defined_variables
                    )
                    if bytecode:
                        return bytecode
                
                # Handle other actions based on the verb
                action = nlp_result['action']
                if action:
                    # Variable creation/assignment
                    if action in ["create", "set", "make", "define", "let"]:
                        if nlp_result['object'] and (nlp_result['values'] or nlp_result['variables']):
                            var_name = nlp_result['object']
                            # Use first value or variable as the value
                            if nlp_result['values']:
                                val = nlp_result['values'][0]
                            else:
                                val = nlp_result['variables'][0]
                            
                            self.defined_variables.add(var_name)
                            return f"SET {var_name} {val}"
                    
                    # Print/display commands
                    elif action in ["print", "show", "display", "output", "tell"]:
                        if nlp_result['object']:
                            obj = nlp_result['object']
                            return f"PRINT {obj}"
        
        # If we couldn't understand the line, return None
        return None
    
    def preprocess_lines(self, lines: List[str]) -> None:
        """Preprocess lines to gather variable names for better reference tracking"""
        # First pass - just identify variables and their types
        self.defined_variables = set()
        # Also track function definitions and their parameters
        self.functions = {}
        
        for line in lines:
            # Skip empty lines and comments
            if not line.strip() or line.strip().startswith("#"):
                continue
            
            # Variable assignment
            for pattern in self.var_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    var_name = match.group(1).strip()
                    self.defined_variables.add(var_name)
            
            # Special handling for "create a variable X and set it to Y"
            match = re.search(self.create_var_pattern, line, re.IGNORECASE)
            if match:
                var_name = match.group(1).strip()
                value = match.group(2).strip()
                self.defined_variables.add(var_name)
                print(f"  Compiler: Found variable declaration: {var_name} = {value}")
                
            # Function definitions
            func_match = re.match(r"define a function called (\w+) with inputs (.+):", line.lower())
            if func_match:
                func_name = func_match.group(1)
                params = [p.strip() for p in func_match.group(2).split("and")]
                self.functions[func_name] = params
                
            # List creation
            list_match = re.match(r"create a list called (\w+)", line.lower())
            if list_match:
                list_name = list_match.group(1)
                self.defined_variables.add(list_name)
                
            # Dictionary creation
            dict_match = re.match(r"create a dictionary called (\w+)", line.lower())
            if dict_match:
                dict_name = dict_match.group(1)
                self.defined_variables.add(dict_name)
            
            # Check for implicit variable assignments
            # e.g., "Store the result in X"
            for suffix in ["in", "as", "to", "into"]:
                if f" {suffix} " in line.lower():
                    parts = line.lower().split(f" {suffix} ")
                    if len(parts) > 1:
                        result_var = parts[1].strip()
                        # Clean any trailing punctuation
                        result_var = result_var.rstrip(',.;:?!')
                        self.defined_variables.add(result_var)
    
    def translate_to_bytecode(self, lines: List[str]) -> List[str]:
        """Override to use our enhanced normalization"""
        bytecode = []
        
        # Initial preprocessing - scan through the lines to gather variables
        # This helps us handle forward references
        self.preprocess_lines(lines)
        
        print("\n=== Compiler Debug: Variables detected in preprocessing ===")
        print("Defined variables:", self.defined_variables)
        print("Functions:", self.functions)
        print("===================================================\n")
        
        # Process one line at a time
        i = 0
        while i < len(lines):
            line = lines[i]
            print(f"\nProcessing line: '{line}'")
            
            # Handle block structure markers
            if line == "BEGIN":
                bytecode.append("BEGIN")
                i += 1
                continue
            elif line == "END":
                bytecode.append("END")
                i += 1
                continue
            
            # Try to understand the line with our enhanced NLP
            nlp_bytecode = self.normalize_with_nlp(line)
            if nlp_bytecode:
                if nlp_bytecode != "COMMENT":  # Skip comments
                    bytecode.append(nlp_bytecode)
                    print(f"  Generated bytecode: '{nlp_bytecode}'")
                else:
                    print(f"  Skipping comment")
                i += 1
                continue
                
            # Handle function definitions with indented blocks
            if line.startswith("define a function"):
                func_match = re.match(r"define a function called (\w+) with inputs (.+):", line.lower())
                if func_match:
                    func_name = func_match.group(1)
                    params = [p.strip() for p in func_match.group(2).split("and")]
                    bytecode.append(f"FUNC_DEF {func_name} {' '.join(params)}")
                    print(f"  Generated bytecode: 'FUNC_DEF {func_name} {' '.join(params)}'")
                    
                    # Process function body until end of indentation
                    i += 1
                    while i < len(lines) and (lines[i].startswith("    ") or not lines[i].strip()):
                        if not lines[i].strip():  # Skip blank lines
                            i += 1
                            continue
                            
                        # Remove indentation and process as normal line
                        body_line = lines[i].strip()
                        body_bytecode = self.normalize_with_nlp(body_line)
                        if body_bytecode:
                            bytecode.append(body_bytecode)
                            print(f"  Generated bytecode (function body): '{body_bytecode}'")
                        else:
                            print(f"  Warning: Could not understand function body line: '{body_line}'")
                        i += 1
                    
                    # Add END_FUNC marker
                    bytecode.append("END_FUNC")
                    print(f"  Generated bytecode: 'END_FUNC'")
                    continue
            
            # If statements with indented blocks
            if line.startswith("if "):
                if_match = re.match(r"if (\w+) is (greater than|less than|equal to) (\w+):", line.lower())
                if if_match:
                    var = if_match.group(1)
                    op_text = if_match.group(2)
                    val = if_match.group(3)
                    
                    # Map text operators to symbols
                    op_map = {"greater than": ">", "less than": "<", "equal to": "=="}
                    op = op_map[op_text]
                    
                    # Emit the IF instruction
                    bytecode.append(f"IF {var} {op} {val}")
                    print(f"  Generated bytecode: 'IF {var} {op} {val}'")
                    
                    # Process if block
                    i += 1
                    in_else_block = False
                    then_block = []
                    else_block = []
                    
                    # Process the then/else blocks
                    while i < len(lines):
                        if not lines[i].strip():  # Skip blank lines
                            i += 1
                            continue
                            
                        if lines[i].strip().lower() == "else:":
                            in_else_block = True
                            i += 1
                            continue
                            
                        if not lines[i].startswith("    "):  # End of block
                            break
                            
                        # Process indented line
                        block_line = lines[i].strip()
                        block_bytecode = self.normalize_with_nlp(block_line)
                        if block_bytecode:
                            if in_else_block:
                                else_block.append(block_bytecode)
                            else:
                                then_block.append(block_bytecode)
                            print(f"  Generated bytecode ({('else' if in_else_block else 'if')} block): '{block_bytecode}'")
                        else:
                            print(f"  Warning: Could not understand {('else' if in_else_block else 'if')} block line: '{block_line}'")
                        i += 1
                    
                    # Create a proper IF/THEN/ELSE structure
                    # First, add the IF instruction (already done above)
                    # Next, add then block instructions
                    bytecode.extend(then_block)
                    
                    # If there's an else block, add a single ELSE marker followed by else instructions
                    if else_block:
                        # Make sure we only add one ELSE marker
                        bytecode.append("ELSE")
                        print(f"  Generated bytecode: 'ELSE'")
                        bytecode.extend(else_block)
                    
                    # Always add END_IF marker at the end
                    bytecode.append("END_IF")
                    print(f"  Generated bytecode: 'END_IF'")
                    continue
            
            # For blocks and other complex structures, fall back to parent implementation
            if line.endswith(":"):
                # Let the parent class handle blocks with BEGIN/END
                old_len = len(bytecode)
                block_bytecode = super().translate_to_bytecode([line])
                bytecode.extend(block_bytecode)
                i += 1
                continue
            
            # If nothing worked, let the parent class try
            old_len = len(bytecode)
            single_line_bytecode = super().translate_to_bytecode([line])
            
            # Skip comments
            if line.startswith("#"):
                i += 1
                continue
            
            # Add any bytecode the parent generated
            if single_line_bytecode and len(single_line_bytecode) > 0:
                bytecode.extend(single_line_bytecode)
            elif not line.strip():  # Skip empty lines silently
                pass
            else:
                # Neither our enhanced NLP nor the parent could understand this line
                # Silence warnings by default for phrases handled in the binary compiler.
                import os as _os
                if _os.getenv('EP_NLP_WARN', '0') == '1':
                    print(f"Warning: Could not understand line: '{line}'")
            
            i += 1
        
        return bytecode
    
    def compile(self, input_file: str, output_file: str) -> str:
        """Compile a source file using the improved NLP capabilities"""
        print(f"\nCompiling {input_file} with NLP enhancements...")
        
        # Read the input file
        with open(input_file, "r") as f:
            lines = [line.strip() for line in f.readlines()]
        
        # Generate bytecode using our improved translator
        bytecode = self.translate_to_bytecode(lines)
        # Build a typed IR (basic pass wrapping bytecode)
        ir = IRProgram(instructions=[IRInstruction.from_bytecode(b) for b in bytecode])
        try:
            # Apply simple optimizations
            from compiler.optimizer import optimize_ir
            ir = optimize_ir(ir)
            bytecode = [f"{ins.op} {' '.join(ins.args)}".strip() for ins in ir.instructions]
        except Exception:
            pass
        
        # Write the bytecode to file
        with open(output_file, "w") as f:
            for code in bytecode:
                f.write(code + "\n")
        
        print(f"\nBytecode output:")
        for code in bytecode:
            print(code)
        
        print(f"\nCompiled {input_file} to {output_file}")
        return output_file

# Create a standalone runner
if __name__ == "__main__":
    if len(sys.argv) > 2:
        compiler = ImprovedNLPCompiler()
        compiler.compile(sys.argv[1], sys.argv[2])
    else:
        # Default behavior: compile program.nl to program.nlc
        input_file = "program.nl"
        output_file = "program.nlc"
        if len(sys.argv) > 1:
            input_file = sys.argv[1]
            output_file = os.path.splitext(input_file)[0] + ".nlc"
        
        compiler = ImprovedNLPCompiler()
        compiler.compile(input_file, output_file)
