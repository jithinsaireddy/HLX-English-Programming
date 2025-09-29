"""
Object-Oriented Programming Extension for English Programming
This module extends the English Programming language with:
- Classes and objects
- Inheritance
- Methods

These extensions integrate with the existing compiler and VM without modifying core files.
"""
import re
import sys
from typing import List, Dict, Any, Optional, Set

# Add the project root to path for imports
sys.path.append('/Users/jithinpothireddy/Downloads/English Programming')

# Import the base compiler and VM for extension
from english_programming.src.compiler.improved_nlp_compiler import ImprovedNLPCompiler
from english_programming.src.vm.improved_nlvm import ImprovedNLVM

class OOPExtension:
    """
    Extension providing object-oriented programming features for the English Programming language
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
        
        # Initialize class registry in VM if needed
        if not hasattr(self.vm, "class_registry"):
            self.vm.class_registry = {}
    
    def _register_compiler_extensions(self):
        """Register new pattern matchers in the compiler"""
        # Store original translate method to chain to it
        original_translate = self.compiler.translate_to_bytecode
        
        # Override the translate method to add our patterns
        def extended_translate(text):
            # Process with our extensions first
            bytecode = self._process_oop_statement(text)
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
            if self._is_oop_instruction(instruction):
                return self._execute_oop_instruction(instruction)
            
            # Fall back to original execution
            return original_execute(instruction)
        
        # Replace the method with our extended version
        self.vm.execute_instruction = extended_execute
    
    def _process_oop_statement(self, text: str) -> Optional[List[str]]:
        """
        Process text for OOP statements
        
        Args:
            text: English text to analyze
            
        Returns:
            List of bytecode instructions or None if no match
        """
        bytecode = []
        
        # Process class definitions
        if self._is_class_definition(text):
            bytecode = self._translate_class_definition(text)
        
        # Process method definitions
        elif self._is_method_definition(text):
            bytecode = self._translate_method_definition(text)
        
        # Process object creation
        elif self._is_object_creation(text):
            bytecode = self._translate_object_creation(text)
        
        # Process method calls
        elif self._is_method_call(text):
            bytecode = self._translate_method_call(text)
        
        # Process property access
        elif self._is_property_access(text):
            bytecode = self._translate_property_access(text)
        
        return bytecode if bytecode else None
    
    def _is_class_definition(self, text: str) -> bool:
        """Check if text defines a class"""
        patterns = [
            r'create\s+(?:a\s+)?class\s+(?:called\s+)?(\w+)(?:\s+that\s+(?:extends|inherits\s+from)\s+(\w+))?',
            r'define\s+(?:a\s+)?class\s+(?:called\s+)?(\w+)(?:\s+that\s+(?:extends|inherits\s+from)\s+(\w+))?',
            r'class\s+(\w+)(?:\s+(?:extends|inherits\s+from)\s+(\w+))?:',
        ]
        
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    def _is_method_definition(self, text: str) -> bool:
        """Check if text defines a method"""
        # Methods are defined within class blocks
        patterns = [
            r'define\s+(?:a\s+)?method\s+(?:called\s+)?(\w+)(?:\s+with\s+inputs\s+(.+))?:',
            r'add\s+(?:a\s+)?method\s+(?:called\s+)?(\w+)(?:\s+with\s+inputs\s+(.+))?:',
            r'method\s+(\w+)(?:\((.+)\))?:',
        ]
        
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    def _is_object_creation(self, text: str) -> bool:
        """Check if text creates an object"""
        patterns = [
            r'create\s+(?:a(?:n)?\s+)?(\w+)\s+object(?:\s+(?:called|named)\s+(\w+))?',
            r'instantiate\s+(?:a(?:n)?\s+)?(\w+)(?:\s+(?:called|named)\s+(\w+))?',
            r'new\s+(\w+)(?:\s+(?:called|named)\s+(\w+))?',
        ]
        
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    def _is_method_call(self, text: str) -> bool:
        """Check if text calls a method"""
        patterns = [
            r'call\s+(?:the\s+)?method\s+(\w+)\s+(?:on|of)\s+(?:the\s+)?object\s+(\w+)(?:\s+with\s+(?:inputs|parameters|arguments)\s+(.+))?',
            r'invoke\s+(\w+)\s+(?:on|of)\s+(\w+)(?:\s+with\s+(.+))?',
            r'(\w+)\.(\w+)\((.*)\)',
        ]
        
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    def _is_property_access(self, text: str) -> bool:
        """Check if text accesses an object property"""
        patterns = [
            r'(?:get|access|retrieve)\s+(?:the\s+)?(\w+)\s+(?:property|attribute)\s+(?:of|from)\s+(?:the\s+)?object\s+(\w+)',
            r'set\s+(?:the\s+)?(\w+)\s+(?:property|attribute)\s+(?:of|for)\s+(?:the\s+)?object\s+(\w+)\s+to\s+(.+)',
            r'(\w+)\.(\w+)',
        ]
        
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    def _translate_class_definition(self, text: str) -> List[str]:
        """Translate class definition to bytecode"""
        bytecode = []
        
        # Find class name and optional parent class
        class_name = ""
        parent_class = "Object"  # Default base class
        
        if ":" in text:
            # Class Name(Parent): syntax
            pattern = r'class\s+(\w+)(?:\s+(?:extends|inherits\s+from)\s+(\w+))?:'
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                class_name = match.group(1)
                if match.group(2):
                    parent_class = match.group(2)
        else:
            # More English-like syntax
            pattern = r'(?:create|define)\s+(?:a\s+)?class\s+(?:called\s+)?(\w+)(?:\s+that\s+(?:extends|inherits\s+from)\s+(\w+))?'
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                class_name = match.group(1)
                if match.group(2):
                    parent_class = match.group(2)
        
        if class_name:
            bytecode = [
                f"CLASS_START {class_name} {parent_class}",
                "BLOCK_START"
            ]
        
        return bytecode
    
    def _translate_method_definition(self, text: str) -> List[str]:
        """Translate method definition to bytecode"""
        method_name = ""
        parameters = []
        
        # Match different method definition patterns
        if ":" in text and "method" in text.lower():
            # Method-style syntax
            pattern = r'method\s+(\w+)(?:\((.+)\))?:'
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                method_name = match.group(1)
                if match.group(2):
                    parameters = [p.strip() for p in match.group(2).split(",")]
        else:
            # English-like syntax
            pattern = r'(?:define|add)\s+(?:a\s+)?method\s+(?:called\s+)?(\w+)(?:\s+with\s+inputs\s+(.+))?:'
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                method_name = match.group(1)
                if match.group(2):
                    # Extract parameters from "inputs a, b, and c" format
                    param_text = match.group(2)
                    # Split by commas or "and"
                    parameters = re.split(r',\s*|\s+and\s+', param_text)
                    parameters = [p.strip() for p in parameters]
        
        if method_name:
            params_str = " ".join(parameters)
            return [
                f"METHOD_START {method_name} {params_str}",
                "BLOCK_START"
            ]
        
        return []
    
    def _translate_object_creation(self, text: str) -> List[str]:
        """Translate object creation to bytecode"""
        class_name = ""
        obj_name = ""
        
        # Match various object creation patterns
        if text.lower().startswith(("create", "instantiate")):
            pattern = r'(?:create|instantiate)\s+(?:a(?:n)?\s+)?(\w+)(?:\s+(?:object))?(?:\s+(?:called|named)\s+(\w+))?'
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                class_name = match.group(1)
                obj_name = match.group(2) if match.group(2) else f"{class_name.lower()}_instance"
        elif text.lower().startswith("new"):
            pattern = r'new\s+(\w+)(?:\s+(?:called|named)\s+(\w+))?'
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                class_name = match.group(1)
                obj_name = match.group(2) if match.group(2) else f"{class_name.lower()}_instance"
        
        if class_name and obj_name:
            # Look for constructor arguments
            args = []
            arg_pattern = r'with\s+(?:inputs|parameters|arguments)\s+(.+)'
            arg_match = re.search(arg_pattern, text, re.IGNORECASE)
            if arg_match:
                arg_text = arg_match.group(1)
                args = re.split(r',\s*|\s+and\s+', arg_text)
                args = [a.strip() for a in args]
            
            args_str = " ".join(args) if args else ""
            return [f"CREATE_OBJECT {class_name} {obj_name} {args_str}"]
        
        return []
    
    def _translate_method_call(self, text: str) -> List[str]:
        """Translate method call to bytecode"""
        method_name = ""
        obj_name = ""
        arguments = []
        
        # Check for different method call patterns
        if "." in text and "(" in text and ")" in text:
            # object.method() syntax
            pattern = r'(\w+)\.(\w+)\((.*)\)'
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                obj_name = match.group(1)
                method_name = match.group(2)
                if match.group(3):
                    arg_text = match.group(3)
                    arguments = [a.strip() for a in arg_text.split(",")]
        else:
            # English-like syntax
            pattern = r'(?:call|invoke)\s+(?:the\s+)?(?:method\s+)?(\w+)\s+(?:on|of)\s+(?:the\s+)?(?:object\s+)?(\w+)'
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                method_name = match.group(1)
                obj_name = match.group(2)
                
                # Look for arguments
                arg_pattern = r'with\s+(?:inputs|parameters|arguments)\s+(.+)'
                arg_match = re.search(arg_pattern, text, re.IGNORECASE)
                if arg_match:
                    arg_text = arg_match.group(1)
                    arguments = re.split(r',\s*|\s+and\s+', arg_text)
                    arguments = [a.strip() for a in arguments]
        
        if method_name and obj_name:
            args_str = " ".join(arguments) if arguments else ""
            return [f"CALL_METHOD {obj_name} {method_name} {args_str}"]
        
        return []
    
    def _translate_property_access(self, text: str) -> List[str]:
        """Translate property access to bytecode"""
        property_name = ""
        obj_name = ""
        value = None
        
        # Check if it's a property get or set operation
        is_set_operation = text.lower().startswith("set")
        
        if "." in text and not ("(" in text and ")" in text):
            # object.property syntax
            pattern = r'(\w+)\.(\w+)'
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                obj_name = match.group(1)
                property_name = match.group(2)
                
                # Check if this is an assignment
                if "=" in text:
                    is_set_operation = True
                    value_pattern = r'=\s+(.+)'
                    value_match = re.search(value_pattern, text)
                    if value_match:
                        value = value_match.group(1).strip()
        else:
            # English-like syntax for get
            if not is_set_operation:
                pattern = r'(?:get|access|retrieve)\s+(?:the\s+)?(\w+)\s+(?:property|attribute)\s+(?:of|from)\s+(?:the\s+)?(?:object\s+)?(\w+)'
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    property_name = match.group(1)
                    obj_name = match.group(2)
            # English-like syntax for set
            else:
                pattern = r'set\s+(?:the\s+)?(\w+)\s+(?:property|attribute)\s+(?:of|for)\s+(?:the\s+)?(?:object\s+)?(\w+)\s+to\s+(.+)'
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    property_name = match.group(1)
                    obj_name = match.group(2)
                    value = match.group(3).strip()
        
        if property_name and obj_name:
            if is_set_operation and value is not None:
                return [f"SET_PROPERTY {obj_name} {property_name} {value}"]
            else:
                return [f"GET_PROPERTY {obj_name} {property_name}"]
        
        return []
    
    def _is_oop_instruction(self, instruction: str) -> bool:
        """Check if instruction is an OOP instruction"""
        oop_instructions = [
            "CLASS_START", "CLASS_END",
            "METHOD_START", "METHOD_END",
            "CREATE_OBJECT", "CALL_METHOD",
            "GET_PROPERTY", "SET_PROPERTY"
        ]
        
        for instr in oop_instructions:
            if instruction.startswith(instr):
                return True
        
        return False
    
    def _execute_oop_instruction(self, instruction: str) -> bool:
        """Execute OOP instruction"""
        # Handle class definition
        if instruction.startswith("CLASS_START"):
            return self._execute_class_start(instruction)
        elif instruction == "CLASS_END":
            return self._execute_class_end()
            
        # Handle method definition
        elif instruction.startswith("METHOD_START"):
            return self._execute_method_start(instruction)
        elif instruction == "METHOD_END":
            return self._execute_method_end()
            
        # Handle object creation
        elif instruction.startswith("CREATE_OBJECT"):
            return self._execute_create_object(instruction)
            
        # Handle method calls
        elif instruction.startswith("CALL_METHOD"):
            return self._execute_call_method(instruction)
            
        # Handle property access
        elif instruction.startswith("GET_PROPERTY"):
            return self._execute_get_property(instruction)
        elif instruction.startswith("SET_PROPERTY"):
            return self._execute_set_property(instruction)
            
        return False
    
    def _execute_class_start(self, instruction: str) -> bool:
        """Execute class start instruction"""
        # Implementation would begin a new class definition
        # Parse instruction: "CLASS_START class_name parent_class"
        parts = instruction.split(" ", 2)
        if len(parts) < 3:
            return False
            
        class_name = parts[1]
        parent_class = parts[2]
        
        # Initialize class structure with inheritance
        if not hasattr(self.vm, "class_registry"):
            self.vm.class_registry = {}
        
        # Create the class structure
        self.vm.class_registry[class_name] = {
            "parent": parent_class,
            "methods": {},
            "properties": {}
        }
        
        # Set current class context for method definitions
        self.vm.current_class = class_name
        
        return True
    
    def _execute_class_end(self) -> bool:
        """Execute class end instruction"""
        # Clear current class context
        if hasattr(self.vm, "current_class"):
            del self.vm.current_class
        
        return True
    
    def _execute_method_start(self, instruction: str) -> bool:
        """Execute method start instruction"""
        # Implementation would begin a new method definition
        # Parse instruction: "METHOD_START method_name param1 param2 ..."
        parts = instruction.split(" ")
        if len(parts) < 2:
            return False
            
        method_name = parts[1]
        parameters = parts[2:] if len(parts) > 2 else []
        
        # Store current method context
        if not hasattr(self.vm, "current_class") or self.vm.current_class not in self.vm.class_registry:
            print(f"Error: Method {method_name} defined outside of class context")
            return False
        
        # Save current instruction pointer as method start
        current_class = self.vm.class_registry[self.vm.current_class]
        current_class["methods"][method_name] = {
            "params": parameters,
            "start_ip": self.vm.instruction_pointer,
            "end_ip": None  # Will be set at METHOD_END
        }
        
        # Set current method context
        self.vm.current_method = method_name
        
        # Skip method body during class definition
        # We'll execute it later when method is called
        self._skip_to_matching_end("METHOD_END")
        
        return True
    
    def _execute_method_end(self) -> bool:
        """Execute method end instruction"""
        # Clear current method context
        if hasattr(self.vm, "current_method"):
            del self.vm.current_method
        
        return True
    
    def _execute_create_object(self, instruction: str) -> bool:
        """Execute object creation instruction"""
        # Parse instruction: "CREATE_OBJECT class_name obj_name [args...]"
        parts = instruction.split(" ")
        if len(parts) < 3:
            return False
            
        class_name = parts[1]
        obj_name = parts[2]
        args = parts[3:] if len(parts) > 3 else []
        
        # Check if class exists
        if not hasattr(self.vm, "class_registry") or class_name not in self.vm.class_registry:
            print(f"Error: Class {class_name} not found")
            return False
        
        # Create object instance
        obj_instance = {
            "class": class_name,
            "properties": {}  # Instance properties
        }
        
        # Store the object in VM environment
        self.vm.environment[obj_name] = obj_instance
        
        # Call constructor if it exists
        if "constructor" in self.vm.class_registry[class_name]["methods"]:
            self._call_method(obj_name, "constructor", args)
        
        return True
    
    def _execute_call_method(self, instruction: str) -> bool:
        """Execute method call instruction"""
        # Parse instruction: "CALL_METHOD obj_name method_name [args...]"
        parts = instruction.split(" ")
        if len(parts) < 3:
            return False
            
        obj_name = parts[1]
        method_name = parts[2]
        args = parts[3:] if len(parts) > 3 else []
        
        return self._call_method(obj_name, method_name, args)
    
    def _call_method(self, obj_name: str, method_name: str, args: List[str]) -> bool:
        """
        Call a method on an object
        
        Args:
            obj_name: Name of the object
            method_name: Name of the method
            args: Method arguments
            
        Returns:
            True if method called successfully, False otherwise
        """
        # Check if object exists
        if obj_name not in self.vm.environment:
            print(f"Error: Object {obj_name} not found")
            return False
        
        obj = self.vm.environment[obj_name]
        class_name = obj["class"]
        
        # Check if class exists
        if class_name not in self.vm.class_registry:
            print(f"Error: Class {class_name} not found")
            return False
        
        # Find method in class or parent classes
        method_info = self._find_method(class_name, method_name)
        if not method_info:
            print(f"Error: Method {method_name} not found in class {class_name}")
            return False
        
        # Save current environment and create method environment
        saved_env = self.vm.environment.copy()
        method_env = {}
        
        # Add "self" reference to method environment
        method_env["self"] = obj
        
        # Add parameters to method environment
        for i, param in enumerate(method_info["params"]):
            if i < len(args):
                method_env[param] = args[i]
            else:
                method_env[param] = None  # Default value
        
        # Save current instruction pointer
        saved_ip = self.vm.instruction_pointer
        
        # Set VM environment to method environment
        self.vm.environment = method_env
        
        # Set instruction pointer to method start
        self.vm.instruction_pointer = method_info["start_ip"]
        
        # Execute method (would need more complex implementation)
        # This is a simplified placeholder
        
        # Restore original environment and instruction pointer
        self.vm.environment = saved_env
        self.vm.instruction_pointer = saved_ip
        
        return True
    
    def _find_method(self, class_name: str, method_name: str) -> Optional[Dict[str, Any]]:
        """
        Find a method in a class or its parent classes
        
        Args:
            class_name: Class to search in
            method_name: Method to find
            
        Returns:
            Method info dict or None if not found
        """
        # Check current class
        if class_name in self.vm.class_registry:
            class_info = self.vm.class_registry[class_name]
            if method_name in class_info["methods"]:
                return class_info["methods"][method_name]
            
            # Check parent class recursively
            if class_info["parent"] != "Object":
                return self._find_method(class_info["parent"], method_name)
        
        return None
    
    def _execute_get_property(self, instruction: str) -> bool:
        """Execute property get instruction"""
        # Parse instruction: "GET_PROPERTY obj_name property_name"
        parts = instruction.split(" ")
        if len(parts) < 3:
            return False
            
        obj_name = parts[1]
        property_name = parts[2]
        
        # Check if object exists
        if obj_name not in self.vm.environment:
            print(f"Error: Object {obj_name} not found")
            return False
        
        obj = self.vm.environment[obj_name]
        
        # Get property value
        if property_name in obj["properties"]:
            # Store property value in result
            self.vm.result = obj["properties"][property_name]
        else:
            # Property not found
            self.vm.result = None
        
        return True
    
    def _execute_set_property(self, instruction: str) -> bool:
        """Execute property set instruction"""
        # Parse instruction: "SET_PROPERTY obj_name property_name value"
        parts = instruction.split(" ", 3)
        if len(parts) < 4:
            return False
            
        obj_name = parts[1]
        property_name = parts[2]
        value = parts[3]
        
        # Check if object exists
        if obj_name not in self.vm.environment:
            print(f"Error: Object {obj_name} not found")
            return False
        
        obj = self.vm.environment[obj_name]
        
        # Set property value
        # This would need to evaluate the value expression
        evaluated_value = value  # Simplified - would need actual evaluation
        obj["properties"][property_name] = evaluated_value
        
        return True
    
    def _skip_to_matching_end(self, end_marker: str):
        """
        Skip execution to the matching end marker
        
        Args:
            end_marker: The end marker to look for (e.g. "METHOD_END")
        """
        # Implementation would advance instruction pointer to matching end marker
        # This is a simplified placeholder
        pass


# Example usage in extensions loader:
# compiler = ImprovedNLPCompiler()
# vm = ImprovedNLVM()
# oop_extension = OOPExtension(compiler, vm)
