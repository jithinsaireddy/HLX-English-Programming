"""
Enhanced NLP Functions for English Programming Language
This file contains improved NLP analysis and processing functions
that can be imported into the main NLPEnhancedCompiler
"""
import re
from typing import Dict, List, Optional, Any

def handle_print_statements(line: str) -> Optional[str]:
    """
    Handle print statements with better support for string literals
    and quoted text
    """
    # Direct print statements with quotes
    quoted_print_patterns = [
        r"(?:print|display|show|output) ['\"](.*?)['\"]",  # Print 'Hello World'
        r"['\"](.*?)['\"] (?:should be printed|should be displayed)"
    ]
    
    for pattern in quoted_print_patterns:
        match = re.search(pattern, line, re.IGNORECASE)
        if match:
            text = match.group(1)
            return f"PRINTSTR {text}"
    
    # Print variable statements
    var_print_patterns = [
        r"(?:print|display|show|output) (?:the |)([\w_]+)",
        r"(?:what is|tell me|show me) (?:the |)([\w_]+)"
    ]
    
    for pattern in var_print_patterns:
        match = re.search(pattern, line, re.IGNORECASE)
        if match:
            var_name = match.group(1).strip()
            # Clean up variable name
            var_name = var_name.rstrip('.,;?!')
            if var_name.lower() in ['it', 'this', 'that']:
                continue  # Skip pronouns
            return f"PRINT {var_name}"
    
    return None

def handle_conditional_statements(line: str) -> Optional[str]:
    """
    Handle conditional statements (if/else blocks) with better support for complex phrases
    """
    # First, check for ELSE and END statements since they're simpler
    # Else statements with variations
    else_patterns = [r"^\s*else:?\s*$", r"^\s*otherwise:?\s*$"]
    for pattern in else_patterns:
        if re.match(pattern, line, re.IGNORECASE):
            return "ELSE"
    
    # End if statements with variations
    end_patterns = [r"^\s*end\s*if\s*$", r"^\s*endif\s*$", r"^\s*end\s*$"]
    for pattern in end_patterns:
        if re.match(pattern, line, re.IGNORECASE):
            return "END"
    
    # Now handle the more complex IF statements
    # First, see if this is an if statement at all
    if_start = re.match(r"^\s*(?:if|when|whenever)\s+(.+)\s*:?\s*$", line, re.IGNORECASE)
    if not if_start:
        return None  # Not an if statement
    
    # Now we analyze the condition part
    condition_text = if_start.group(1).strip()
    
    # Check for the known comparison operators
    # Note the specific order - we need to check for multi-word operators first
    comparisons = [
        (r"is\s+greater\s+than\s+or\s+equal\s+to\s+([\w\d\.]+)", ">="),  # greater than or equal
        (r"is\s+less\s+than\s+or\s+equal\s+to\s+([\w\d\.]+)", "<="),     # less than or equal
        (r"is\s+not\s+equal\s+to\s+([\w\d\.]+)", "!="),                 # not equal
        (r"is\s+greater\s+than\s+([\w\d\.]+)", ">"),                     # greater than
        (r"is\s+less\s+than\s+([\w\d\.]+)", "<"),                        # less than
        (r"is\s+equal\s+to\s+([\w\d\.]+)", "=="),                        # equal to
        (r"equals\s+([\w\d\.]+)", "=="),                                  # equals
        (r"is\s+([\w\d\.]+)", "=="),                                      # is
        (r"==\s+([\w\d\.]+)", "=="),                                      # ==
        (r">\s+([\w\d\.]+)", ">"),                                        # >
        (r"<\s+([\w\d\.]+)", "<"),                                        # <
        (r">=\s+([\w\d\.]+)", ">="),                                      # >=
        (r"<=\s+([\w\d\.]+)", "<="),                                      # <=
        (r"!=\s+([\w\d\.]+)", "!=")                                       # !=
    ]
    
    # Extract the variable name from the beginning of the condition
    var_match = re.match(r"([\w_]+)\s+(.+)", condition_text)
    if not var_match:
        return None  # No variable found
    
    var_name = var_match.group(1).strip()
    condition_remainder = var_match.group(2).strip()
    
    # Try to match the remainder against our comparison operators
    for pattern, op_symbol in comparisons:
        match = re.match(pattern, condition_remainder, re.IGNORECASE)
        if match:
            value = match.group(1).strip()
            # Remove any trailing colons
            if value.endswith(':'):
                value = value[:-1].strip()
                
            print(f"Parsed conditional: IF {var_name} {op_symbol} {value}")
            return f"IF {var_name} {op_symbol} {value}"
    
    # If we couldn't find a specific operator, fall back to equality check
    # This handles shorthand like "if x: ..." meaning "if x is true"
    if condition_text.strip().endswith(':'):
        condition_text = condition_text[:-1].strip()
    
    var_only_match = re.match(r"^([\w_]+)$", condition_text)
    if var_only_match:
        var_name = var_only_match.group(1).strip()
        return f"IF {var_name} != 0"  # Assume checking if variable is non-zero/true
    
    return None

def handle_string_concatenation(line: str) -> Optional[str]:
    """
    Handle string concatenation operations with better pattern matching
    """
    # String concatenation patterns
    concat_patterns = [
        r"(?:concatenate|join|append|combine) (?:the |)?([\w_]+) (?:and|with|to) (?:the |)?([\w_]+)(?: (?:to|and) (?:make|create|set|store in|save as|put in) (?:the |)?([\w_]+))",
        r"(?:concatenate|join|append|combine) (?:the |)?([\w_]+) (?:and|with|to) (?:the |)?([\w_]+)(?: (?:as|in|into) (?:the |)?([\w_]+))"
    ]
    
    for pattern in concat_patterns:
        match = re.search(pattern, line, re.IGNORECASE)
        if match:
            left_operand = match.group(1).strip()
            right_operand = match.group(2).strip()
            
            # Get result variable if specified
            result_var = None
            if len(match.groups()) > 2 and match.group(3):
                result_var = match.group(3).strip()
            else:
                # Default result variable
                result_var = "result"
            
            return f"CONCAT {left_operand} {right_operand} {result_var}"
    
    return None

def handle_arithmetic_operations(line: str) -> Optional[str]:
    """
    Handle arithmetic operations with better pattern matching
    """
    # Addition patterns
    add_patterns = [
        r"(?:add|sum|plus) (?:the |)?([\w_\d]+) (?:and|with|to) (?:the |)?([\w_\d]+)(?: (?:to|and) (?:make|create|get|store in|save as|put in) (?:the |)?([\w_]+))",
        r"(?:add|sum|plus) (?:the |)?([\w_\d]+) (?:and|with|to) (?:the |)?([\w_\d]+)(?: (?:as|in|into) (?:the |)?([\w_]+))"
    ]
    
    for pattern in add_patterns:
        match = re.search(pattern, line, re.IGNORECASE)
        if match:
            left_operand = match.group(1).strip()
            right_operand = match.group(2).strip()
            
            # Get result variable if specified
            if len(match.groups()) > 2 and match.group(3):
                result_var = match.group(3).strip()
            else:
                # Default result variable
                result_var = "sum"
            
            return f"ADD {left_operand} {right_operand} {result_var}"
    
    # Subtraction patterns
    sub_patterns = [
        r"(?:subtract|minus|take away) (?:the |)?([\w_\d]+) (?:from) (?:the |)?([\w_\d]+)(?: (?:to|and) (?:get|find|calculate|make|create|store in|save as|put in) (?:the |)?([\w_]+))",
        r"(?:subtract|minus|take away) (?:the |)?([\w_\d]+) (?:from) (?:the |)?([\w_\d]+)(?: (?:as|in|into) (?:the |)?([\w_]+))"
    ]
    
    for pattern in sub_patterns:
        match = re.search(pattern, line, re.IGNORECASE)
        if match:
            subtrahend = match.group(1).strip()  # What's being subtracted
            minuend = match.group(2).strip()     # What we're subtracting from
            
            # Get result variable if specified
            if len(match.groups()) > 2 and match.group(3):
                result_var = match.group(3).strip()
            else:
                # Default result variable
                result_var = "difference"
            
            return f"SUB {minuend} {subtrahend} {result_var}"
    
    # Multiplication patterns
    mul_patterns = [
        r"(?:multiply|times) (?:the |)?([\w_\d]+) (?:by|with|and) (?:the |)?([\w_\d]+)(?: (?:to|and) (?:get|find|calculate|make|create|store in|save as|put in) (?:the |)?([\w_]+))",
        r"(?:multiply|times) (?:the |)?([\w_\d]+) (?:by|with|and) (?:the |)?([\w_\d]+)(?: (?:as|in|into) (?:the |)?([\w_]+))"
    ]
    
    for pattern in mul_patterns:
        match = re.search(pattern, line, re.IGNORECASE)
        if match:
            left_operand = match.group(1).strip()
            right_operand = match.group(2).strip()
            
            # Get result variable if specified
            if len(match.groups()) > 2 and match.group(3):
                result_var = match.group(3).strip()
            else:
                # Default result variable
                result_var = "product"
            
            return f"MUL {left_operand} {right_operand} {result_var}"
    
    # Division patterns
    div_patterns = [
        r"(?:divide) (?:the |)?([\w_\d]+) (?:by|with) (?:the |)?([\w_\d]+)(?: (?:to|and) (?:get|find|calculate|make|create|store in|save as|put in) (?:the |)?([\w_]+))",
        r"(?:divide) (?:the |)?([\w_\d]+) (?:by|with) (?:the |)?([\w_\d]+)(?: (?:as|in|into) (?:the |)?([\w_]+))"
    ]
    
    for pattern in div_patterns:
        match = re.search(pattern, line, re.IGNORECASE)
        if match:
            dividend = match.group(1).strip()   # What's being divided
            divisor = match.group(2).strip()    # What we're dividing by
            
            # Get result variable if specified
            if len(match.groups()) > 2 and match.group(3):
                result_var = match.group(3).strip()
            else:
                # Default result variable
                result_var = "quotient"
            
            return f"DIV {dividend} {divisor} {result_var}"
    
    return None

def enhanced_analyze_with_nlp(nlp, line: str, has_spacy: bool) -> Dict:
    """
    Enhanced NLP analysis function that better detects:
    - Arithmetic operations (add, subtract, multiply, divide)
    - String operations (concatenation)
    - Variables and operands
    - Result variable targets
    """
    if not has_spacy:
        return {}  # Fall back if spaCy isn't available
        
    doc = nlp(line)
    result = {
        'action': None,       # Main verb/action
        'subject': None,      # Subject of the sentence
        'object': None,       # Direct object
        'targets': [],        # Prepositional phrases with 'to', 'in', etc.
        'values': [],         # Numeric values
        'operation': None,    # Arithmetic/string operation
        'operands': [],       # Operands for operations
        'result_var': None,   # Where to store the result
        'variables': []       # All variables mentioned
    }
    
    # Extract basic sentence elements
    for token in doc:
        # Main verb identification
        if token.dep_ == "ROOT" and token.pos_ == "VERB":
            result['action'] = token.lemma_.lower()
        
        # Direct object identification
        if token.dep_ == "dobj":
            result['object'] = token.text
            # Add to variables list if looks like a variable name
            if token.text.lower() not in ["variable", "value", "it", "that", "this"]:
                result['variables'].append(token.text)
        
        # Subject identification
        if token.dep_ == "nsubj":
            result['subject'] = token.text
            # Add to variables list if looks like a variable name
            if token.text.lower() not in ["variable", "value", "it", "that", "this"]:
                result['variables'].append(token.text)
        
        # Extract numeric values
        if token.like_num or token.pos_ == "NUM":
            result['values'].append(token.text)
        
        # Identify potential variables (nouns that aren't common words)
        if token.pos_ in ["NOUN", "PROPN"] and token.text.lower() not in ["variable", "value", "result", "it", "that", "this"]:
            result['variables'].append(token.text)
        
        # Find prepositional targets (often where results go)
        if token.dep_ == "pobj" and token.head.dep_ == "prep":
            prep = token.head.text
            if prep in ["to", "into", "in", "as"]:
                result['targets'].append(token.text)
                # Often this is the result variable
                if token.text.lower() not in ["variable", "value", "result", "it", "that", "this"]:
                    result['result_var'] = token.text
    
    # Detect operations by keywords
    operation_map = {
        # Addition
        'add': 'add', 'plus': 'add', 'sum': 'add', 'increase': 'add', 'increment': 'add',
        # Subtraction
        'subtract': 'subtract', 'minus': 'subtract', 'decrease': 'subtract', 'decrement': 'subtract',
        'remove': 'subtract', 'take': 'subtract',
        # Multiplication
        'multiply': 'multiply', 'times': 'multiply', 'product': 'multiply',
        # Division
        'divide': 'divide', 'dividing': 'divide', 'quotient': 'divide', 'split': 'divide',
        # String operations
        'join': 'concat', 'combine': 'concat', 'concatenate': 'concat', 'merge': 'concat'
    }
    
    # Look for operation words
    for token in doc:
        if token.lemma_.lower() in operation_map:
            result['operation'] = operation_map[token.lemma_.lower()]
            
            # For arithmetic operations, look for operands nearby
            if result['operation'] in ['add', 'subtract', 'multiply', 'divide']:
                # Special case for divide/multiply - check typical patterns
                if result['operation'] == 'divide' and 'by' in line.lower():
                    # Look for "divide X by Y" pattern
                    div_pattern = re.search(r'divide\s+([\w_]+)\s+by\s+([\w_\d]+)', line, re.IGNORECASE)
                    if div_pattern and len(div_pattern.groups()) >= 2:
                        result['operands'] = [div_pattern.group(1), div_pattern.group(2)]
                elif result['operation'] == 'multiply' and 'by' in line.lower():
                    # Look for "multiply X by Y" pattern
                    mul_pattern = re.search(r'multiply\s+([\w_]+)\s+by\s+([\w_\d]+)', line, re.IGNORECASE)
                    if mul_pattern and len(mul_pattern.groups()) >= 2:
                        result['operands'] = [mul_pattern.group(1), mul_pattern.group(2)]
                else:
                    # Look for nouns or numbers as operands
                    for t in doc:
                        if ((t.pos_ in ["NOUN", "PROPN"] and t.text.lower() not in ["variable", "value"]) or 
                            t.like_num or t.pos_ == "NUM"):
                            if t.text not in result['operands'] and t.text != token.text:
                                result['operands'].append(t.text)
    
    # Check for string concatenation with + operator
    if "+" in line and not result['operation']:
        # Look for "X + Y" pattern
        concat_pattern = re.findall(r'([\w_]+|\\"[^\\"]*\\"|\\\'[^\\\']*\\\')\s*\+\s*([\w_]+|\\"[^\\"]*\\"|\\\'[^\\\']*\\\')', line)
        if concat_pattern:
            result['operation'] = 'concat'
            for left, right in concat_pattern:
                if left not in result['operands']:
                    result['operands'].append(left)
                if right not in result['operands']:
                    result['operands'].append(right)
    
    # Look for phrases like "store in X", "save in X", etc. to identify result variables
    if not result['result_var']:
        store_words = ["store", "save", "put", "place", "assign"]
        store_pattern = re.search(r'(?:' + '|'.join(store_words) + r')\s+(?:in|to|as)\s+([\w_]+)', line, re.IGNORECASE)
        if store_pattern:
            result['result_var'] = store_pattern.group(1)
    
    # Remove duplicates from variables and operands lists
    result['variables'] = list(dict.fromkeys(result['variables']))
    result['operands'] = list(dict.fromkeys(result['operands']))
    
    return result

def process_arithmetic_operation(operation: str, operands: List[str], result_var: Optional[str]) -> Optional[str]:
    """
    Generate appropriate bytecode for arithmetic operations
    with much better operand handling
    """
    if not operation or len(operands) < 2:
        return None
        
    # Map operations to bytecode operations
    op_map = {
        'add': 'ADD',
        'subtract': 'SUB',
        'multiply': 'MUL',
        'divide': 'DIV',
        'concat': 'CONCAT'
    }
    
    if operation not in op_map:
        return None
        
    # Get bytecode operation
    bytecode_op = op_map[operation]
    
    # If no result variable specified, use appropriate default based on operation
    if not result_var:
        if operation == 'add':
            result_var = 'sum'
        elif operation == 'subtract':
            result_var = 'difference'
        elif operation == 'multiply':
            result_var = 'product'
        elif operation == 'divide':
            result_var = 'quotient'
        elif operation == 'concat':
            result_var = 'result'
        else:
            result_var = operands[0]  # Default to first operand
    
    # Return the bytecode operation
    return f"{bytecode_op} {operands[0]} {operands[1]} {result_var}"

def process_string_concatenation(operands: List[str], result_var: Optional[str], defined_variables: set) -> Optional[str]:
    """
    Generate appropriate bytecode for string concatenation
    with better handling of variables and string literals
    """
    if len(operands) < 2:
        return None
    
    # Process operands to handle string literals vs variables
    processed_operands = []
    for op in operands[:2]:  # Just use first two operands for now
        # Clean the operand of any quotes
        clean_op = op.strip('\'"')
        
        # If it's a string literal (quoted), process it
        if (op.startswith('"') and op.endswith('"')) or (op.startswith("'") and op.endswith("'")):
            processed_operands.append(op)
        # If it's a known variable, use as is
        elif op in defined_variables:
            processed_operands.append(op)
        # Otherwise treat as string literal
        else:
            processed_operands.append(f'"{op}"')
    
    # If no result variable, use a sensible default
    if not result_var:
        result_var = 'message' if 'message' in defined_variables else 'result'
    
    # Return the CONCAT operation
    return f"CONCAT {processed_operands[0]} {processed_operands[1]} {result_var}"

def handle_counter_operations(line: str) -> Optional[str]:
    """
    Handle counter creation and increment/decrement operations
    with better pattern matching
    """
    # Counter creation - more flexible patterns
    counter_patterns = [
        r"(?:create|make) (?:a|the|an)? counter (?:with|having) (?:initial|starting)? value (?:of)? ([\d]+)",
        r"(?:create|make|set) (?:a|the|an)? counter (?:to|equal to|with value) ([\d]+)"
    ]
    
    for pattern in counter_patterns:
        counter_match = re.search(pattern, line, re.IGNORECASE)
        if counter_match:
            value = counter_match.group(1).strip()
            return f"SET counter {value}"
    
    # Counter increment - more flexible patterns
    increment_patterns = [
        r"(?:increment|increase) (?:the |)?([\w_]+)(?: by| with) ([\d]+)",
        r"(?:add) ([\d]+) (?:to) (?:the |)?([\w_]+)",  # "Add 3 to counter"
        r"(?:increase|increment) (?:the |)?([\w_]+)",     # "Increment the counter"
    ]
    
    for i, pattern in enumerate(increment_patterns):
        increment_match = re.search(pattern, line, re.IGNORECASE)
        if increment_match:
            if i == 0:  # First pattern: "increment counter by 2"
                var_name = increment_match.group(1).strip()
                value = increment_match.group(2).strip()
            elif i == 1:  # Second pattern: "add 3 to counter"
                var_name = increment_match.group(2).strip()
                value = increment_match.group(1).strip()
            else:  # Default increment by 1: "increment counter"
                var_name = increment_match.group(1).strip()
                value = "1"
                
            return f"ADD {var_name} {value} {var_name}"
    
    # Counter decrement - more flexible patterns
    decrement_patterns = [
        r"(?:decrement|decrease) (?:the|)? ([\w_]+) (?:by|with)? ([\d]+)",
        r"(?:subtract) ([\d]+) (?:from) (?:the|)? ([\w_]+)"
    ]
    
    for i, pattern in enumerate(decrement_patterns):
        decrement_match = re.search(pattern, line, re.IGNORECASE)
        if decrement_match:
            if i == 0:  # First pattern: "decrement counter by 2"
                var_name = decrement_match.group(1).strip()
                value = decrement_match.group(2).strip()
            else:  # Second pattern: "subtract 3 from counter"
                var_name = decrement_match.group(2).strip()
                value = decrement_match.group(1).strip()
                
            return f"SUB {var_name} {value} {var_name}"
    
    return None
