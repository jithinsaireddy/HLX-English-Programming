"""
Advanced Control Flow Extensions for English Programming
This module extends the English Programming language with:
- While loops
- For loops
- Else-if constructs

These extensions integrate with the existing compiler and VM without modifying core files.
"""
import re
import sys
from typing import List, Dict, Tuple, Any, Optional

# Add the project root to path for imports
sys.path.append('/Users/jithinpothireddy/Downloads/English Programming')

# Import the base compiler and VM for extension
from english_programming.src.compiler.improved_nlp_compiler import ImprovedNLPCompiler
from english_programming.src.vm.improved_nlvm import ImprovedNLVM

class AdvancedControlFlowExtension:
    """
    Extension providing advanced control flow constructs for the English Programming language
    """
    def __init__(self, compiler: ImprovedNLPCompiler, vm: ImprovedNLVM):
        """
        Initialize the extension with references to compiler and VM
        
        Args:
            compiler: The NLP compiler instance to extend
            vm: The VM instance to extend
        """
        self.compiler = compiler
        self.vm = vm
        
        # Register new pattern matchers and instruction handlers
        self._register_compiler_extensions()
        self._register_vm_extensions()
    
    def _register_compiler_extensions(self):
        """Register new pattern matchers in the compiler"""
        # Store original translate method to chain to it
        original_translate = self.compiler.translate_to_bytecode
        
        # Override the translate method to add our patterns
        def extended_translate(text):
            # Process with our extensions first
            bytecode = self._process_advanced_control_flow(text)
            if bytecode:
                return bytecode
                
            # Fall back to original method if our extensions don't match
            return original_translate(text)
        
        # Replace the method with our extended version
        self.compiler.translate_to_bytecode = extended_translate
    
    def _register_vm_extensions(self):
        """Register new instruction handlers in the VM"""
        # Add new instruction handlers to the VM
        original_execute = self.vm.execute_instruction
        
        def extended_execute(instruction):
            # Check if this is one of our extended instructions
            if self._is_advanced_control_flow_instruction(instruction):
                return self._execute_advanced_control_flow(instruction)
            
            # Fall back to original execution
            return original_execute(instruction)
        
        # Replace the method with our extended version
        self.vm.execute_instruction = extended_execute
    
    def _process_advanced_control_flow(self, text: str) -> Optional[List[str]]:
        """
        Process text for advanced control flow constructs
        
        Args:
            text: English text to analyze
            
        Returns:
            List of bytecode instructions or None if no match
        """
        bytecode = []
        
        # Process while loops
        if self._is_while_loop(text):
            bytecode = self._translate_while_loop(text)
        
        # Process for loops
        elif self._is_for_loop(text):
            bytecode = self._translate_for_loop(text)
        
        # Process else-if constructs
        elif self._is_else_if(text):
            bytecode = self._translate_else_if(text)
        
        return bytecode if bytecode else None
    
    def _is_while_loop(self, text: str) -> bool:
        """Check if text describes a while loop"""
        patterns = [
            r'while\s+(.+)\s*:',
            r'repeat\s+while\s+(.+)\s*:',
            r'as\s+long\s+as\s+(.+)\s*:',
            r'continue\s+until\s+(.+)\s*:',
        ]
        
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    def _is_for_loop(self, text: str) -> bool:
        """Check if text describes a for loop"""
        patterns = [
            r'for\s+each\s+(.+)\s+in\s+(.+)\s*:',
            r'loop\s+through\s+(.+)\s*:',
            r'iterate\s+over\s+(.+)\s*:',
            r'for\s+(.+)\s+from\s+(.+)\s+to\s+(.+)\s*:',
        ]
        
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    def _is_else_if(self, text: str) -> bool:
        """Check if text describes an else-if construct"""
        patterns = [
            r'else\s+if\s+(.+)\s*:',
            r'otherwise\s+if\s+(.+)\s*:',
            r'elif\s+(.+)\s*:',
        ]
        
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    def _translate_while_loop(self, text: str) -> List[str]:
        """Translate while loop text to bytecode"""
        # Extract condition
        if "while" in text.lower():
            pattern = r'while\s+(.+)\s*:'
        elif "as long as" in text.lower():
            pattern = r'as\s+long\s+as\s+(.+)\s*:'
        elif "repeat while" in text.lower():
            pattern = r'repeat\s+while\s+(.+)\s*:'
        elif "continue until" in text.lower():
            pattern = r'continue\s+until\s+(.+)\s*:'
            # Negate condition for "until"
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                condition = match.group(1)
                return [
                    f"WHILE_START NOT {condition}",
                    "BLOCK_START"
                ]
        
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            condition = match.group(1)
            return [
                f"WHILE_START {condition}",
                "BLOCK_START"
            ]
        
        return []
    
    def _translate_for_loop(self, text: str) -> List[str]:
        """Translate for loop text to bytecode"""
        bytecode = []
        
        # For each loop (iteration over collection)
        if "for each" in text.lower() or "iterate over" in text.lower() or "loop through" in text.lower():
            pattern = r'(?:for\s+each|iterate\s+over|loop\s+through)\s+(.+)\s+in\s+(.+)\s*:'
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                var_name = match.group(1).strip()
                collection = match.group(2).strip()
                bytecode = [
                    f"FOR_EACH_START {var_name} {collection}",
                    "BLOCK_START"
                ]
        
        # Numeric for loop (from x to y)
        elif "from" in text.lower() and "to" in text.lower():
            pattern = r'for\s+(.+)\s+from\s+(.+)\s+to\s+(.+)\s*:'
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                var_name = match.group(1).strip()
                start_val = match.group(2).strip()
                end_val = match.group(3).strip()
                bytecode = [
                    f"FOR_RANGE_START {var_name} {start_val} {end_val}",
                    "BLOCK_START"
                ]
        
        return bytecode
    
    def _translate_else_if(self, text: str) -> List[str]:
        """Translate else-if constructs to bytecode"""
        patterns = [
            r'else\s+if\s+(.+)\s*:',
            r'otherwise\s+if\s+(.+)\s*:',
            r'elif\s+(.+)\s*:',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                condition = match.group(1).strip()
                return [
                    "ELSE_END",
                    f"ELSE_IF {condition}",
                    "BLOCK_START"
                ]
        
        return []
    
    def _is_advanced_control_flow_instruction(self, instruction: str) -> bool:
        """Check if instruction is an advanced control flow instruction"""
        adv_instructions = [
            "WHILE_START", "WHILE_END",
            "FOR_EACH_START", "FOR_EACH_END",
            "FOR_RANGE_START", "FOR_RANGE_END",
            "ELSE_IF"
        ]
        
        for instr in adv_instructions:
            if instruction.startswith(instr):
                return True
        
        return False
    
    def _execute_advanced_control_flow(self, instruction: str) -> bool:
        """Execute advanced control flow instruction"""
        # Handle while loops
        if instruction.startswith("WHILE_START"):
            return self._execute_while_start(instruction)
        elif instruction == "WHILE_END":
            return self._execute_while_end()
            
        # Handle for-each loops
        elif instruction.startswith("FOR_EACH_START"):
            return self._execute_for_each_start(instruction)
        elif instruction == "FOR_EACH_END":
            return self._execute_for_each_end()
            
        # Handle numeric for loops
        elif instruction.startswith("FOR_RANGE_START"):
            return self._execute_for_range_start(instruction)
        elif instruction == "FOR_RANGE_END":
            return self._execute_for_range_end()
            
        # Handle else-if
        elif instruction.startswith("ELSE_IF"):
            return self._execute_else_if(instruction)
            
        return False
    
    def _execute_while_start(self, instruction: str) -> bool:
        """Execute while loop start"""
        # Implementation will reference VM variables and internal state
        # For now, placeholder implementation
        condition = instruction.replace("WHILE_START", "").strip()
        
        # Store loop information in VM's state
        if not hasattr(self.vm, "_while_loops"):
            self.vm._while_loops = []
            
        # Store current instruction pointer and condition for loop
        self.vm._while_loops.append({
            "condition": condition,
            "start_ip": self.vm.instruction_pointer,
        })
        
        # Evaluate condition to decide if we enter loop
        # (implementation would access VM's evaluate_condition method)
        return True
    
    def _execute_while_end(self) -> bool:
        """Execute while loop end"""
        # Implementation will jump back to loop start if condition is true
        # For now, placeholder implementation
        if hasattr(self.vm, "_while_loops") and self.vm._while_loops:
            loop_info = self.vm._while_loops[-1]
            
            # Evaluate condition again
            # If condition is still true, jump back to start
            # Otherwise, remove loop info and continue
            self.vm._while_loops.pop()
            
        return True
    
    def _execute_for_each_start(self, instruction: str) -> bool:
        """Execute for-each loop start"""
        # Parse instruction: "FOR_EACH_START var_name collection"
        parts = instruction.split(" ", 2)
        if len(parts) < 3:
            return False
            
        var_name = parts[1]
        collection_name = parts[2]
        
        # Setup for-each loop state in VM
        if not hasattr(self.vm, "_for_loops"):
            self.vm._for_loops = []
            
        # Implementation would get collection from VM's environment
        # and prepare iteration
        
        # Store loop state
        self.vm._for_loops.append({
            "type": "foreach",
            "var_name": var_name,
            "collection_name": collection_name,
            "start_ip": self.vm.instruction_pointer,
            "index": 0
        })
        
        return True
    
    def _execute_for_each_end(self) -> bool:
        """Execute for-each loop end"""
        # Implementation will advance to next item or exit loop
        # For now, placeholder implementation
        if hasattr(self.vm, "_for_loops") and self.vm._for_loops:
            loop_info = self.vm._for_loops[-1]
            
            # If more items in collection, update var_name and jump back
            # Otherwise, remove loop info and continue
            self.vm._for_loops.pop()
            
        return True
    
    def _execute_for_range_start(self, instruction: str) -> bool:
        """Execute numeric for loop start"""
        # Parse instruction: "FOR_RANGE_START var_name start_val end_val"
        parts = instruction.split(" ", 3)
        if len(parts) < 4:
            return False
            
        var_name = parts[1]
        start_val = parts[2]
        end_val = parts[3]
        
        # Setup for-range loop state in VM
        if not hasattr(self.vm, "_for_loops"):
            self.vm._for_loops = []
            
        # Implementation would evaluate start_val and end_val
        # and initialize counter variable
        
        # Store loop state
        self.vm._for_loops.append({
            "type": "range",
            "var_name": var_name,
            "start_val": start_val,
            "end_val": end_val,
            "start_ip": self.vm.instruction_pointer,
            "current": int(start_val)  # Simplified
        })
        
        return True
    
    def _execute_for_range_end(self) -> bool:
        """Execute numeric for loop end"""
        # Implementation will increment counter and check if done
        # For now, placeholder implementation
        if hasattr(self.vm, "_for_loops") and self.vm._for_loops:
            loop_info = self.vm._for_loops[-1]
            
            # If counter < end_val, increment counter and jump back
            # Otherwise, remove loop info and continue
            self.vm._for_loops.pop()
            
        return True
    
    def _execute_else_if(self, instruction: str) -> bool:
        """Execute else-if construct"""
        # Parse instruction: "ELSE_IF condition"
        condition = instruction.replace("ELSE_IF", "").strip()
        
        # Implementation would evaluate condition 
        # and determine if this branch should execute
        # (Would leverage VM's existing condition evaluation)
        
        return True


# Example usage in extensions loader:
# compiler = ImprovedNLPCompiler()
# vm = ImprovedNLVM()
# control_flow_extension = AdvancedControlFlowExtension(compiler, vm)
