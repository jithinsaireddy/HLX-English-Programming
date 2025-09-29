"""
VM Bridge for English Programming Extensions

This module serves as a bridge between the extension system and the existing VM,
adapting the API to ensure compatibility between components.
"""

import sys
from pathlib import Path

# Add the project root to the path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent.parent))

# Import the VM
from english_programming.src.vm.improved_nlvm import ImprovedNLVM

class VMBridge:
    """
    Bridge adapter for the VM to support the extension system's expected interface.
    This class wraps the existing VM and provides the methods expected by the extension system.
    """
    
    def __init__(self, vm=None, debug=False):
        """
        Initialize the VM bridge
        
        Args:
            vm: Existing VM instance to wrap, or None to create new instance
            debug: Enable debug mode
        """
        self.vm = vm if vm is not None else ImprovedNLVM(debug=debug)
        self.environment = {}  # Main environment for variable storage
        self.instruction_pointer = 0
        self.debug = debug
        
    def execute_bytecode(self, instructions):
        """
        Execute a list of bytecode instructions
        This method is used by the extension system
        
        Args:
            instructions: List of instruction strings
        
        Returns:
            Result of execution
        """
        # Create a temporary file to pass to the VM
        temp_file = Path("temp_bytecode.nlc")
        
        try:
            # Write instructions to temp file
            with open(temp_file, 'w') as f:
                f.write('\n'.join(instructions))
            
            # Execute using VM's native method
            result = self.vm.execute(temp_file)
            
            # Copy the VM's environment to our environment
            self.environment = self.vm.env.copy()
            
            return result
            
        finally:
            # Clean up temp file
            if temp_file.exists():
                temp_file.unlink()
    
    def execute_instruction(self, instruction):
        """
        Execute a single bytecode instruction
        This method is used by the extension system
        
        Args:
            instruction: Instruction string
            
        Returns:
            True if execution successful, False otherwise
        """
        # For now, just execute it through the bytecode execution
        return self.execute_bytecode([instruction])
    
    # Provide any other bridge methods needed by extensions

# Monkey patch the original VM class to include the bridge methods
def patch_vm():
    """Patch the original VM class to include bridge methods"""
    
    # Add execute_bytecode method to ImprovedNLVM
    if not hasattr(ImprovedNLVM, 'execute_bytecode'):
        def execute_bytecode(self, instructions):
            """Execute a list of bytecode instructions"""
            # Create a temporary file
            temp_file = Path("temp_bytecode.nlc")
            
            try:
                # Write instructions to temp file
                with open(temp_file, 'w') as f:
                    f.write('\n'.join(instructions))
                
                # Execute using native method
                return self.execute(temp_file)
                
            finally:
                # Clean up temp file
                if temp_file.exists():
                    temp_file.unlink()
        
        # Add the method to the VM class
        ImprovedNLVM.execute_bytecode = execute_bytecode
        
        # Add environment property
        if not hasattr(ImprovedNLVM, 'environment'):
            ImprovedNLVM.environment = property(lambda self: self.env)
    
    # Add instruction_pointer attribute if needed
    if not hasattr(ImprovedNLVM, 'instruction_pointer'):
        ImprovedNLVM.instruction_pointer = 0

# Apply the patch
patch_vm()
