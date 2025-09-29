#!/usr/bin/env python3
"""
English Programming VM Adapter

This adapter connects the extensions with the existing VM implementation,
respecting the fixed conditional logic and making sure we maintain the block
structure handling that was already fixed in the original codebase.
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.append('/Users/jithinpothireddy/Downloads/English Programming')

# Import the core components
from english_programming.src.compiler.improved_nlp_compiler import ImprovedNLPCompiler
from english_programming.src.vm.improved_nlvm import ImprovedNLVM

class EnglishProgrammingAdapter:
    """
    Adapter class for English Programming that connects extensions to the existing VM
    while preserving the fixed conditional logic execution.
    """
    
    def __init__(self):
        """Initialize the adapter"""
        self.compiler = ImprovedNLPCompiler()
        self.vm = ImprovedNLVM(debug=True)
        
        # Add compatibility attributes to VM
        self._patch_vm()
        
        # Store if any extensions are loaded
        self.extensions_loaded = False
    
    def _patch_vm(self):
        """Add compatibility attributes to VM"""
        # Add execute_instruction method (singular) that calls execute_instructions (plural)
        if not hasattr(self.vm, 'execute_instruction'):
            self.vm.execute_instruction = lambda instr: self.vm.execute_instructions([instr], self.vm.env)
        
        # Add environment property that maps to env
        if not hasattr(self.vm, 'environment'):
            self.vm.environment = self.vm.env
        
        # Add instruction pointer for tracking position
        if not hasattr(self.vm, 'instruction_pointer'):
            self.vm.instruction_pointer = 0
    
    def load_extensions(self):
        """Load extensions for control flow, module system, and OOP"""
        try:
            # Import extensions
            from english_programming.src.extensions.control_flow.advanced_loops import AdvancedControlFlowExtension
            from english_programming.src.extensions.module_system.module_loader import ModuleSystemExtension
            from english_programming.src.extensions.oop.class_system import OOPExtension
            
            # Initialize control flow extension
            print("Loading control flow extension...")
            self.control_flow = AdvancedControlFlowExtension(self.compiler, self.vm)
            
            # Initialize module system extension
            print("Loading module system extension...")
            self.module_system = ModuleSystemExtension(self.compiler, self.vm)
            
            # Initialize OOP extension
            print("Loading OOP extension...")
            self.oop = OOPExtension(self.compiler, self.vm)
            
            self.extensions_loaded = True
            print("All extensions loaded successfully!")
            
            return True
        except Exception as e:
            print(f"Error loading extensions: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def compile_program(self, source_file):
        """
        Compile an English program to bytecode
        
        Args:
            source_file: Path to the source file
            
        Returns:
            Path to the compiled bytecode file
        """
        print(f"Compiling {source_file}...")
        bytecode_file = Path(source_file).with_suffix(".nlc")
        
        # Read the source file
        with open(source_file, "r") as f:
            lines = f.readlines()
        
        # Process each line
        bytecode = []
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if line and not line.startswith("#"):  # Skip comments and empty lines
                try:
                    # Compile the line to bytecode
                    line_bytecode = self.compiler.translate_to_bytecode(line)
                    if line_bytecode:
                        bytecode.extend(line_bytecode)
                        print(f"Line {line_num}: {line} -> {', '.join(line_bytecode)}")
                except Exception as e:
                    print(f"Error compiling line {line_num}: {line}")
                    print(f"  Error: {str(e)}")
        
        # Write bytecode to file
        with open(bytecode_file, "w") as f:
            f.write("\n".join(bytecode))
        
        print(f"Compiled to: {bytecode_file}")
        return bytecode_file
    
    def run_program(self, bytecode_file):
        """
        Run a compiled English program
        
        Args:
            bytecode_file: Path to the bytecode file
            
        Returns:
            Result of program execution
        """
        print(f"\nExecuting program: {bytecode_file}")
        print("=" * 60)
        
        try:
            # Execute the program using the VM
            result = self.vm.execute(bytecode_file)
            
            print("=" * 60)
            print("Program executed successfully!")
            
            # Display the final environment
            print("\nFinal environment variables:")
            print("-" * 40)
            
            for var_name, value in self.vm.env.items():
                if not var_name.startswith("_"):  # Skip internal variables
                    print(f"{var_name} = {value}")
            
            return result
        except Exception as e:
            print(f"Error executing program: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def create_test_program(self, output_file=None):
        """
        Create a test program that demonstrates all language features
        
        Args:
            output_file: Optional path to write the program
            
        Returns:
            Path to the test program file
        """
        # Create a comprehensive test program
        program = """
# English Programming - Comprehensive Feature Test

# Basic variable operations
create a variable called counter and set it to 1
create a variable called total and set it to 0

# While loop demonstration
print "Testing while loop:"
while counter is less than 6:
    print counter
    add counter to total and store the result in total
    add 1 to counter and store the result in counter

print "Sum of numbers from 1 to 5:"
print total

# For-each loop with a list
print "Testing for-each loop:"
create a variable called fruits and set it to ["apple", "banana", "cherry"]
for each fruit in fruits:
    print fruit

# Conditional logic with else-if
print "Testing if-else-if:"
create a variable called score and set it to 85

if score is greater than 90:
    print "Grade: A"
else if score is greater than 80:
    print "Grade: B"
else if score is greater than 70:
    print "Grade: C"
else:
    print "Grade: D"

# Function definition and calling
define a function called multiply with inputs x and y:
    multiply x by y and store the result in product
    return product

call multiply with values 5 and 6 and store result in multiplication_result
print "5 × 6 ="
print multiplication_result

# Dictionary operations
create a variable called person and set it to {"name": "John", "age": 30}
print "Person name:"
print person["name"]

# String operations
create a variable called greeting and set it to "Hello, "
create a variable called name and set it to "World"
concatenate greeting and name and store it in message
print message

print "All features tested successfully!"
"""
        
        # Determine output file path
        if output_file is None:
            output_file = "english_feature_test.nl"
        
        # Write program to file
        with open(output_file, "w") as f:
            f.write(program)
        
        print(f"Created test program: {output_file}")
        return output_file
    
    def run_english_test(self, program_file=None):
        """
        Run a complete test of the English Programming language with extensions
        
        Args:
            program_file: Optional path to an existing program file
            
        Returns:
            True if test successful, False otherwise
        """
        try:
            # Create or use program file
            if program_file is None:
                program_file = self.create_test_program()
            
            # Compile the program
            bytecode_file = self.compile_program(program_file)
            
            # Run the program
            self.run_program(bytecode_file)
            
            return True
        except Exception as e:
            print(f"Test failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

# Main entry point
if __name__ == "__main__":
    print("=" * 60)
    print("English Programming Language - Extended Features Test")
    print("=" * 60)
    
    # Create adapter
    adapter = EnglishProgrammingAdapter()
    
    # Load extensions if specified
    if "--with-extensions" in sys.argv:
        adapter.load_extensions()
    
    # Run test with specified file or default
    program_file = None
    for arg in sys.argv[1:]:
        if not arg.startswith("--") and os.path.exists(arg):
            program_file = arg
            break
    
    adapter.run_english_test(program_file)
