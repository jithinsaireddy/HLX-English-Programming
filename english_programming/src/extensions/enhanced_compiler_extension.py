#!/usr/bin/env python3
"""
Enhanced Compiler Extension for English Programming

This module enhances the improved NLP compiler to better handle complete English
sentences and generate VM-compatible bytecode. It respects the existing fixed
conditional logic implementation while adding support for:

1. Advanced control flow (while loops, for-each loops)
2. Object-oriented programming
3. Module system
"""

import os
import sys
import re
from pathlib import Path

# Add project root to path
project_root = Path(__file__).absolute().parent.parent.parent.parent
sys.path.append(str(project_root))

# Import the compiler
from english_programming.src.compiler.improved_nlp_compiler import ImprovedNLPCompiler

class EnhancedCompilerExtension:
    """Enhanced compiler extension for English Programming"""
    
    def __init__(self, compiler=None, debug=False):
        """
        Initialize the enhanced compiler extension
        
        Args:
            compiler (ImprovedNLPCompiler, optional): Compiler to enhance
            debug (bool): Enable debug output
        """
        self.debug = debug
        
        # Create compiler if not provided
        self.compiler = compiler if compiler else ImprovedNLPCompiler()
        
        # Store original method
        self.original_translate = self.compiler.translate_to_bytecode
        
        # Replace the method
        self.compiler.translate_to_bytecode = self.enhanced_translate
        
        # Set up patterns for English language constructs
        self._initialize_patterns()
        
        if self.debug:
            print("Enhanced Compiler Extension initialized")
    
    def _initialize_patterns(self):
        """Initialize patterns for English language constructs"""
        # Control flow patterns
        self.while_patterns = [
            r'(?i)^\s*while\s+(.+?):',
            r'(?i)^\s*as\s+long\s+as\s+(.+?):',
            r'(?i)^\s*until\s+(.+?):',
            r'(?i)^\s*keep\s+(?:doing|executing)\s+(?:while|as long as)\s+(.+?):'
        ]
        
        self.for_each_patterns = [
            r'(?i)^\s*for\s+each\s+(\w+)\s+in\s+(\w+):',
            r'(?i)^\s*for\s+every\s+(\w+)\s+in\s+(\w+):',
            r'(?i)^\s*loop\s+through\s+(\w+)\s+(?:in|using)\s+(\w+):',
            r'(?i)^\s*iterate\s+(?:through|over)\s+(\w+)\s+(?:with|using)\s+(\w+):'
        ]
        
        # OOP patterns
        self.class_patterns = [
            r'(?i)^\s*create\s+(?:a|the)?\s*class\s+(?:called\s+)?(\w+)(?:\s+that\s+extends\s+(\w+))?:',
            r'(?i)^\s*define\s+(?:a|the)?\s*class\s+(?:called\s+)?(\w+)(?:\s+that\s+(?:inherits|extends)\s+(?:from\s+)?(\w+))?:'
        ]
        
        self.method_patterns = [
            r'(?i)^\s*define\s+(?:a|the)?\s*method\s+(?:called\s+)?(\w+)(?:\s+with\s+(?:inputs|parameters|arguments)\s+(.+))?:',
            r'(?i)^\s*create\s+(?:a|the)?\s*method\s+(?:called\s+)?(\w+)(?:\s+that\s+takes\s+(.+))?:'
        ]
        
        self.create_object_patterns = [
            r'(?i)^\s*create\s+(?:a|an)?\s*(\w+)\s+object\s+(?:called|named)\s+(\w+)(?:\s+with\s+(?:inputs|parameters|arguments)\s+(.+))?',
            r'(?i)^\s*instantiate\s+(?:a|an)?\s*(\w+)\s+(?:as|called|named)\s+(\w+)(?:\s+with\s+(?:inputs|parameters|arguments)\s+(.+))?'
        ]
        
        self.call_method_patterns = [
            r'(?i)^\s*call\s+(?:the)?\s*(\w+)\s+method\s+on\s+(\w+)(?:\s+with\s+(?:inputs|parameters|arguments)\s+(.+))?',
            r'(?i)^\s*invoke\s+(?:the)?\s*(\w+)\s+method\s+on\s+(\w+)(?:\s+with\s+(?:inputs|parameters|arguments)\s+(.+))?'
        ]
        
        # Module system patterns
        self.import_patterns = [
            r'(?i)^\s*import\s+(?:the)?\s*(\w+)\s+module(?:\s+as\s+(\w+))?',
            r'(?i)^\s*load\s+(?:the)?\s*(\w+)\s+module(?:\s+as\s+(\w+))?'
        ]
    
    def enhanced_translate(self, lines):
        """
        Enhanced translate method that handles complete English sentences
        
        Args:
            lines (list or str): Lines of English code
            
        Returns:
            list: VM-compatible bytecode
        """
        # Handle string input
        if isinstance(lines, str):
            lines = [lines]
        
        # Normalize input lines - ensure consistent indentation and strip comments
        normalized_lines = self._normalize_lines(lines)
        
        # Process line by line with block awareness
        bytecode = []
        i = 0
        
        while i < len(normalized_lines):
            line = normalized_lines[i]
            
            # Skip empty lines
            if not line:
                i += 1
                continue
            
            # Try to match and process extensions first
            processed, next_i = self._process_extensions(normalized_lines, i)
            if processed:
                bytecode.extend(processed)
                i = next_i
                continue
            
            # Fall back to original compiler
            if self.debug:
                print(f"Processing line: '{line}'")
                
            standard_bytecode = self.original_translate([line])
            if standard_bytecode:
                bytecode.extend(standard_bytecode)
                if self.debug:
                    for code in standard_bytecode:
                        print(f"  Generated bytecode: '{code}'")
            else:
                if self.debug and line:
                    print(f"Warning: Could not translate line: '{line}'")
            
            i += 1
        
        return bytecode
    
    def _normalize_lines(self, lines):
        """
        Normalize lines for processing
        
        Args:
            lines (list): Input lines
            
        Returns:
            list: Normalized lines
        """
        normalized = []
        for line in lines:
            # Remove trailing comments
            if '#' in line:
                comment_pos = line.find('#')
                # Check if # is inside a string
                quote_count = line[:comment_pos].count('"')
                if quote_count % 2 == 0:  # Even quotes means # is outside strings
                    line = line[:comment_pos].rstrip()
            
            # Skip empty lines
            if line.strip():
                normalized.append(line)
        
        return normalized
    
    def _process_extensions(self, lines, start_index):
        """
        Process extension language features
        
        Args:
            lines (list): All lines
            start_index (int): Current line index
            
        Returns:
            tuple: (bytecode, next_index)
        """
        line = lines[start_index]
        
        # Process while loops
        for pattern in self.while_patterns:
            match = re.match(pattern, line)
            if match:
                condition = match.group(1)
                bytecode, next_i = self._process_while_loop(lines, start_index, condition)
                return bytecode, next_i
        
        # Process for-each loops
        for pattern in self.for_each_patterns:
            match = re.match(pattern, line)
            if match:
                item_var = match.group(1)
                collection_var = match.group(2)
                bytecode, next_i = self._process_for_each_loop(lines, start_index, item_var, collection_var)
                return bytecode, next_i
        
        # Process class definitions
        for pattern in self.class_patterns:
            match = re.match(pattern, line)
            if match:
                class_name = match.group(1)
                parent_class = match.group(2)
                bytecode, next_i = self._process_class_definition(lines, start_index, class_name, parent_class)
                return bytecode, next_i
        
        # Process object creation
        for pattern in self.create_object_patterns:
            match = re.match(pattern, line)
            if match:
                class_name = match.group(1)
                object_name = match.group(2)
                params_str = match.group(3) if match.groups()[2] else ""
                bytecode = self._process_create_object(class_name, object_name, params_str)
                return bytecode, start_index + 1
        
        # Process method calls
        for pattern in self.call_method_patterns:
            match = re.match(pattern, line)
            if match:
                method_name = match.group(1)
                object_name = match.group(2)
                params_str = match.group(3) if match.groups()[2] else ""
                bytecode = self._process_method_call(object_name, method_name, params_str)
                return bytecode, start_index + 1
        
        # Process module imports
        for pattern in self.import_patterns:
            match = re.match(pattern, line)
            if match:
                module_name = match.group(1)
                alias = match.group(2) if match.groups()[1] else module_name
                bytecode = [f"IMPORT {module_name} {alias}"]
                return bytecode, start_index + 1
        
        # No extension matched
        return None, start_index
    
    def _extract_indented_block(self, lines, start_index):
        """
        Extract an indented block of code
        
        Args:
            lines (list): All lines
            start_index (int): Index of block header
            
        Returns:
            tuple: (block_lines, next_index)
        """
        if start_index + 1 >= len(lines):
            return [], start_index + 1
        
        # Get indentation level
        first_line = lines[start_index + 1]
        indent = len(first_line) - len(first_line.lstrip())
        block_lines = []
        i = start_index + 1
        
        while i < len(lines):
            line = lines[i]
            if not line:
                i += 1
                continue
            
            current_indent = len(line) - len(line.lstrip())
            
            # End of block
            if current_indent < indent and line.strip():
                break
            
            # Add to block
            if current_indent >= indent:
                block_lines.append(line)
            
            i += 1
        
        return block_lines, i
    
    def _process_while_loop(self, lines, start_index, condition):
        """
        Process a while loop
        
        Args:
            lines (list): All lines
            start_index (int): Index of while loop header
            condition (str): Loop condition
            
        Returns:
            tuple: (bytecode, next_index)
        """
        # Extract the loop body
        block_lines, next_index = self._extract_indented_block(lines, start_index)
        
        # Process the body
        body_bytecode = self.enhanced_translate(block_lines)
        
        # Convert English condition to bytecode syntax
        condition = self._convert_condition(condition)
        
        # Generate bytecode
        bytecode = [
            "# WHILE LOOP",
            f"IF {condition}"
        ]
        
        # Add loop body
        bytecode.extend(body_bytecode)
        
        # Add loop jump back and end
        bytecode.extend([
            "JUMP -" + str(len(body_bytecode) + 2),  # Jump back to IF instruction
            "END_IF"
        ])
        
        return bytecode, next_index
    
    def _process_for_each_loop(self, lines, start_index, item_var, collection_var):
        """
        Process a for-each loop
        
        Args:
            lines (list): All lines
            start_index (int): Index of for-each loop header
            item_var (str): Item variable name
            collection_var (str): Collection variable name
            
        Returns:
            tuple: (bytecode, next_index)
        """
        # Extract the loop body
        block_lines, next_index = self._extract_indented_block(lines, start_index)
        
        # Process the body
        body_bytecode = self.enhanced_translate(block_lines)
        
        # Generate setup bytecode
        bytecode = [
            f"# FOR-EACH LOOP: {item_var} in {collection_var}",
            f"BUILTIN LENGTH {collection_var} _length",
            f"SET _index 0",
            f"# FOR LOOP START"
        ]
        
        # Add loop condition
        bytecode.append(f"IF _index < _length")
        
        # Get current item
        bytecode.append(f"INDEX {collection_var} _index {item_var}")
        
        # Add loop body
        bytecode.extend(body_bytecode)
        
        # Add increment and loop back
        bytecode.extend([
            f"ADD _index 1 _index",
            f"JUMP -" + str(len(body_bytecode) + 4),  # Jump back to IF instruction
            "END_IF"
        ])
        
        return bytecode, next_index
    
    def _process_class_definition(self, lines, start_index, class_name, parent_class):
        """
        Process a class definition
        
        Args:
            lines (list): All lines
            start_index (int): Index of class definition
            class_name (str): Class name
            parent_class (str): Parent class name or None
            
        Returns:
            tuple: (bytecode, next_index)
        """
        # Extract class body
        block_lines, next_index = self._extract_indented_block(lines, start_index)
        
        # Set up class bytecode
        bytecode = [
            f"# CLASS: {class_name}",
            f"SET {class_name}_type \"class\""
        ]
        
        # Add parent class if specified
        if parent_class:
            bytecode.append(f"SET {class_name}_parent \"{parent_class}\"")
        
        # Process class body line by line
        i = 0
        while i < len(block_lines):
            line = block_lines[i]
            
            # Check for method definitions
            for pattern in self.method_patterns:
                match = re.match(pattern, line)
                if match:
                    method_name = match.group(1)
                    params_str = match.group(2) if match.groups()[1] else ""
                    method_bytecode, new_i = self._process_method_definition(
                        block_lines, i, class_name, method_name, params_str
                    )
                    bytecode.extend(method_bytecode)
                    i = new_i
                    break
            else:
                # Process regular class body line
                line_bytecode = self.original_translate([line])
                if line_bytecode:
                    bytecode.extend(line_bytecode)
                i += 1
        
        return bytecode, next_index
    
    def _process_method_definition(self, lines, start_index, class_name, method_name, params_str):
        """
        Process a method definition
        
        Args:
            lines (list): All lines
            start_index (int): Index of method definition
            class_name (str): Class name
            method_name (str): Method name
            params_str (str): Parameter string
            
        Returns:
            tuple: (bytecode, next_index)
        """
        # Parse parameters
        params = []
        if params_str:
            params = [p.strip() for p in re.split(r',|and', params_str)]
        
        # Extract method body
        block_lines, next_index = self._extract_indented_block(lines, start_index)
        
        # Process method body
        body_bytecode = self.enhanced_translate(block_lines)
        
        # Generate function definition bytecode
        func_name = f"{class_name}_{method_name}"
        params_list = " ".join(["self"] + params)
        
        bytecode = [
            f"# METHOD: {class_name}.{method_name}",
            f"FUNC_DEF {func_name} {params_list}"
        ]
        
        # Add method body
        bytecode.extend(body_bytecode)
        
        # End function
        bytecode.append("END_FUNC")
        
        return bytecode, next_index
    
    def _process_create_object(self, class_name, object_name, params_str):
        """
        Process object creation
        
        Args:
            class_name (str): Class name
            object_name (str): Object name
            params_str (str): Parameter string
            
        Returns:
            list: Bytecode
        """
        # Parse parameters
        params = []
        if params_str:
            params = [p.strip() for p in re.split(r',|and', params_str)]
        
        # Generate bytecode
        bytecode = [
            f"# CREATE OBJECT: {object_name} = new {class_name}",
            f"SET {object_name}_type \"object\"",
            f"SET {object_name}_class \"{class_name}\""
        ]
        
        # Call constructor if it exists
        constructor = f"{class_name}_constructor"
        args = " ".join([f'"{p}"' if not p.isdigit() and not p.startswith('"') else p for p in params])
        bytecode.append(f"CALL {constructor} {object_name} {args}")
        
        return bytecode
    
    def _process_method_call(self, object_name, method_name, params_str):
        """
        Process method call
        
        Args:
            object_name (str): Object name
            method_name (str): Method name
            params_str (str): Parameter string
            
        Returns:
            list: Bytecode
        """
        # Parse parameters
        params = []
        if params_str:
            params = [p.strip() for p in re.split(r',|and', params_str)]
        
        # Generate bytecode
        bytecode = [
            f"# CALL METHOD: {object_name}.{method_name}()",
            f"GET {object_name}_class _class",
            f"CONCAT _class \"_{method_name}\" _method"
        ]
        
        # Call the method
        args = " ".join([f'"{p}"' if not p.isdigit() and not p.startswith('"') else p for p in params])
        bytecode.append(f"CALL _method {object_name} {args}")
        
        return bytecode
    
    def _convert_condition(self, condition):
        """
        Convert English condition to bytecode syntax
        
        Args:
            condition (str): English condition
            
        Returns:
            str: Bytecode condition
        """
        # Common English phrases to bytecode operators
        replacements = [
            (r'is\s+less\s+than\s+or\s+equal\s+to', '<='),
            (r'is\s+less\s+than', '<'),
            (r'is\s+greater\s+than\s+or\s+equal\s+to', '>='),
            (r'is\s+greater\s+than', '>'),
            (r'is\s+equal\s+to', '=='),
            (r'equals', '=='),
            (r'is\s+not\s+equal\s+to', '!='),
            (r'is\s+not', '!='),
            (r'is', '==')
        ]
        
        result = condition.lower()
        for pattern, replacement in replacements:
            result = re.sub(pattern, replacement, result)
        
        # Ensure operands are separated from operators
        result = re.sub(r'([a-zA-Z0-9_])(==|!=|<=|>=|<|>)', r'\1 \2', result)
        result = re.sub(r'(==|!=|<=|>=|<|>)([a-zA-Z0-9_])', r'\1 \2', result)
        
        return result

# Standalone test
def test_enhanced_compiler():
    """Test the enhanced compiler extension"""
    compiler = ImprovedNLPCompiler()
    extension = EnhancedCompilerExtension(compiler, debug=True)
    
    # Create a test English program
    english = """
# Test the enhanced compiler extension
create a variable called counter and set it to 1
create a variable called sum and set it to 0

# Test a while loop
while counter is less than 6:
    print counter
    add counter to sum and store the result in sum
    add 1 to counter and store the result in counter

print "Sum is:"
print sum

# Test a class definition
create class Person:
    define method constructor with parameters name and age:
        set self.name to name
        set self.age to age
    
    define method greet:
        print "Hello, my name is"
        print self.name
        print "and I am"
        print self.age
        print "years old"

# Create an object and call a method
create a Person object called john with parameters "John" and 30
call the greet method on john
"""
    
    # Translate to bytecode
    bytecode = extension.enhanced_translate(english.strip().split('\n'))
    
    # Display result
    print("Generated bytecode:")
    for line in bytecode:
        print(f"  {line}")

if __name__ == "__main__":
    test_enhanced_compiler()
