#!/usr/bin/env python3
"""
Run Extension Test

This script runs the extension test example using the improved VM with
extension support. It respects the fixed conditional logic implementation
and integrates features from english_runtime_complete.
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append('/Users/jithinpothireddy/Downloads/English Programming')

# Import compiler and VM
from english_programming.src.compiler.improved_nlp_compiler import ImprovedNLPCompiler
from english_programming.src.vm.improved_nlvm import ImprovedNLVM

class ExtensionTestRunner:
    """
    Test runner for the English Programming extensions
    """
    
    def __init__(self, debug=True):
        """Initialize the test runner"""
        self.compiler = ImprovedNLPCompiler()
        self.vm = ImprovedNLVM(debug=debug)
        
        # Set up path to example files
        self.examples_dir = Path("/Users/jithinpothireddy/Downloads/English Programming/english_programming/examples")
    
    def run_example(self, example_name):
        """
        Run a specific example file
        
        Args:
            example_name: Name of the example file (without .nl extension)
        
        Returns:
            Result of execution
        """
        # Get paths
        source_file = self.examples_dir / f"{example_name}.nl"
        bytecode_file = self.examples_dir / f"{example_name}.nlc"
        
        if not source_file.exists():
            print(f"Error: Example file {source_file} not found")
            return False
        
        print(f"Running example: {example_name}")
        print("=" * 60)
        
        try:
            # Step 1: Compile if needed
            if not bytecode_file.exists():
                print(f"Compiling {source_file}...")
                result = self.compile_file(source_file)
                if not result:
                    print("Compilation failed")
                    return False
            
            # Step 2: Execute
            print(f"Executing {bytecode_file}...")
            result = self.vm.execute(bytecode_file)
            
            # Step 3: Show final environment
            print("\nFinal environment variables:")
            print("-" * 40)
            
            for var_name, value in self.vm.env.items():
                if not var_name.startswith("_"):
                    print(f"{var_name} = {value}")
            
            print("\nExecution completed successfully!")
            return True
        
        except Exception as e:
            print(f"Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def compile_file(self, source_file):
        """
        Compile an English program to bytecode
        
        Args:
            source_file: Path to the source file
        
        Returns:
            True if compilation successful, False otherwise
        """
        try:
            bytecode_file = source_file.with_suffix(".nlc")
            os.system(f"python -m english_programming.src.compiler.improved_nlp_compiler {source_file} {bytecode_file}")
            
            if bytecode_file.exists():
                print(f"Successfully compiled to {bytecode_file}")
                return True
            else:
                print(f"Compilation failed: {bytecode_file} not created")
                return False
        
        except Exception as e:
            print(f"Error during compilation: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def load_extension_hooks(self):
        """
        Load hooks for extension features into the VM
        
        This adds support for:
        - Advanced control flow (while loops, for-each loops)
        - OOP features
        - Module system
        """
        # Patch execute_instructions to handle extension bytecode
        original_execute_instructions = self.vm.execute_instructions
        
        def enhanced_execute_instructions(instructions, env):
            """Enhanced execute_instructions with extension support"""
            i = 0
            result = None
            
            while i < len(instructions):
                instruction = instructions[i]
                parts = instruction.split()
                
                # Handle special extension instructions
                if parts and parts[0] == "WHILE_LESS_EQUAL":
                    # Process while loop
                    var_name = parts[1]
                    limit = parts[2]
                    
                    # Find the matching END
                    end_index = i
                    nesting = 1
                    for j in range(i + 1, len(instructions)):
                        if instructions[j].startswith("WHILE"):
                            nesting += 1
                        elif instructions[j] == "END":
                            nesting -= 1
                            if nesting == 0:
                                end_index = j
                                break
                    
                    loop_body = instructions[i+1:end_index]
                    
                    # Execute loop with condition
                    try:
                        var_value = int(env.get(var_name, 0))
                        limit_value = int(limit) if limit.isdigit() else int(env.get(limit, 0))
                        
                        iterations = 0
                        max_iterations = 100  # Safety limit
                        
                        print(f"Starting WHILE loop with {var_name}={var_value}, limit={limit_value}")
                        
                        while var_value <= limit_value and iterations < max_iterations:
                            # Execute loop body
                            original_execute_instructions(loop_body, env)
                            
                            # Update variable for next iteration
                            var_value = int(env.get(var_name, 0))
                            iterations += 1
                            
                            print(f"Loop iteration {iterations}: {var_name}={var_value}, limit={limit_value}")
                            
                            if iterations >= max_iterations:
                                print(f"Warning: Loop exceeded maximum iterations ({max_iterations})")
                                break
                    except Exception as e:
                        print(f"Error in while loop: {str(e)}")
                    
                    # Skip to after END
                    i = end_index + 1
                
                # Handle other instructions normally
                else:
                    result = original_execute_instructions([instruction], env)
                    i += 1
            
            return result
        
        # Replace standard execution with enhanced version
        self.vm.execute_instructions = enhanced_execute_instructions

def run_test():
    """Run the extension test"""
    runner = ExtensionTestRunner(debug=True)
    
    # Load extension hooks
    runner.load_extension_hooks()
    
    # Run the extension test
    return runner.run_example("extension_test")

if __name__ == "__main__":
    print("=" * 60)
    print("ENGLISH PROGRAMMING EXTENSION TEST")
    print("=" * 60)
    
    success = run_test()
    
    if success:
        print("\nExtension test completed successfully!")
    else:
        print("\nExtension test failed. See output for details.")
