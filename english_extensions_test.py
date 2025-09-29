#!/usr/bin/env python3
"""
Test script for English Programming language extensions
This script properly connects the extensions with the existing compiler and VM
"""

import os
import sys
from pathlib import Path

# Add the project root to the path
sys.path.append('/Users/jithinpothireddy/Downloads/English Programming')

# Import core components
from english_programming.src.compiler.improved_nlp_compiler import ImprovedNLPCompiler
from english_programming.src.vm.improved_nlvm import ImprovedNLVM

class ExtensionAdapter:
    """
    Adapter class to connect extensions with the existing compiler and VM
    """
    def __init__(self, compiler=None, vm=None):
        """Initialize with compiler and VM instances"""
        self.compiler = compiler if compiler else ImprovedNLPCompiler()
        self.vm = vm if vm else ImprovedNLVM(debug=True)
        
        # Add necessary methods to VM for extension compatibility
        self._patch_vm()
        
        # Load extensions
        self.extensions = {}
        
    def _patch_vm(self):
        """Add necessary methods to VM for extension compatibility"""
        # Map execute_instruction to execute_instructions if needed
        if not hasattr(self.vm, 'execute_instruction') and hasattr(self.vm, 'execute_instructions'):
            self.vm.execute_instruction = lambda instr: self.vm.execute_instructions([instr], self.vm.env)
        
        # Add execute_bytecode method
        if not hasattr(self.vm, 'execute_bytecode'):
            def execute_bytecode(bytecode):
                """Execute bytecode (file path or instructions list)"""
                if isinstance(bytecode, list):
                    # If given a list of instructions, write to temp file
                    temp_file = "temp_bytecode.nlc"
                    try:
                        with open(temp_file, 'w') as f:
                            f.write('\n'.join(bytecode))
                        return self.vm.execute(temp_file)
                    finally:
                        # Clean up
                        if os.path.exists(temp_file):
                            os.remove(temp_file)
                else:
                    # Assume it's a file path
                    return self.vm.execute(bytecode)
                    
            # Add method to VM
            self.vm.execute_bytecode = execute_bytecode
        
        # Add environment property
        if not hasattr(self.vm, 'environment'):
            # Get env attribute
            self.vm.environment = self.vm.env
        
        # Add instruction pointer
        if not hasattr(self.vm, 'instruction_pointer'):
            self.vm.instruction_pointer = 0
        
        # Add current_class and current_method attributes for OOP
        if not hasattr(self.vm, 'current_class'):
            self.vm.current_class = None
        
        if not hasattr(self.vm, 'current_method'):
            self.vm.current_method = None
    
    def load_extensions(self):
        """Load all extension modules"""
        print("Loading language extensions...")
        
        try:
            # Import extensions
            from english_programming.src.extensions.control_flow.advanced_loops import AdvancedControlFlowExtension
            from english_programming.src.extensions.module_system.module_loader import ModuleSystemExtension
            from english_programming.src.extensions.oop.class_system import OOPExtension
            
            # Initialize extensions
            print("Initializing Control Flow extension...")
            self.extensions['control_flow'] = AdvancedControlFlowExtension(self.compiler, self.vm)
            
            print("Initializing Module System extension...")
            self.extensions['module_system'] = ModuleSystemExtension(self.compiler, self.vm)
            
            print("Initializing OOP extension...")
            self.extensions['oop'] = OOPExtension(self.compiler, self.vm)
            
            print("All extensions loaded successfully!")
            return True
        except Exception as e:
            print(f"Error loading extensions: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_extensions(self, source_code=None):
        """
        Test the extensions with given source code or a default test
        
        Args:
            source_code: Optional source code to test (string)
        """
        if not source_code:
            # Default test code for extensions
            source_code = """
# Test file for English Programming extensions
create a variable called counter and set it to 1

# While loop test
while counter is less than 5:
    print counter
    add 1 to counter and store the result in counter

# For loop test
create a variable called numbers and set it to [1, 2, 3, 4, 5]
for each item in numbers:
    multiply item by 2 and store the result in doubled_item
    print doubled_item

# If-else-if test
create a variable called score and set it to 85
if score is greater than 90:
    print "Grade: A"
else if score is greater than 80:
    print "Grade: B"
else if score is greater than 70:
    print "Grade: C"
else:
    print "Grade: D"
"""
        
        # Write the source code to a test file
        test_file = Path("extension_test.nl")
        with open(test_file, 'w') as f:
            f.write(source_code)
        
        # Determine output bytecode file
        bytecode_file = test_file.with_suffix('.nlc')
        
        # Compile the test file
        print(f"\nCompiling test file: {test_file}")
        with open(test_file, 'r') as f:
            lines = f.readlines()
        
        bytecode = []
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if line and not line.startswith('#'):
                try:
                    # Compile the line with our extension-enhanced compiler
                    line_bytecode = self.compiler.translate_to_bytecode(line)
                    if line_bytecode:
                        bytecode.extend(line_bytecode)
                        if self.vm.debug:
                            print(f"Line {i}: '{line}' -> {line_bytecode}")
                except Exception as e:
                    print(f"Error compiling line {i}: '{line}'")
                    print(f"  {str(e)}")
        
        # Write bytecode to file
        with open(bytecode_file, 'w') as f:
            f.write('\n'.join(bytecode))
        
        print(f"Compiled to: {bytecode_file}")
        
        # Execute the bytecode
        try:
            print("\nExecuting with extensions...\n" + "="*50)
            result = self.vm.execute_bytecode(bytecode_file)
            print("="*50 + "\nExecution completed successfully!")
            
            # Show environment variables
            print("\nFinal environment:")
            for var_name, value in self.vm.environment.items():
                if not var_name.startswith('_'):
                    print(f"  {var_name} = {value}")
                    
            return result
        except Exception as e:
            print(f"Execution error: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
        finally:
            # Clean up
            if test_file.exists():
                test_file.unlink()
            if bytecode_file.exists():
                bytecode_file.unlink()

def main():
    """Main entry point"""
    print("Testing English Programming Extensions...")
    
    # Create adapter
    adapter = ExtensionAdapter()
    
    # Load extensions
    if adapter.load_extensions():
        # Test extensions
        adapter.test_extensions()

if __name__ == "__main__":
    main()
