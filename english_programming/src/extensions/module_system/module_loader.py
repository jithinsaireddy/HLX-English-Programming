"""
Module System Extension for English Programming
This module extends the English Programming language with:
- File imports
- Code organization
- Module management

These extensions integrate with the existing compiler and VM without modifying core files.
"""
import os
import sys
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Set

# Add the project root to path for imports
sys.path.append('/Users/jithinpothireddy/Downloads/English Programming')

# Import the base compiler and VM for extension
from english_programming.src.compiler.improved_nlp_compiler import ImprovedNLPCompiler
from english_programming.src.vm.improved_nlvm import ImprovedNLVM

class ModuleSystemExtension:
    """
    Extension providing module system capabilities for the English Programming language
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
        
        # Map of module names to compiled bytecode
        self.loaded_modules = {}
        
        # Map of module names to exported symbols
        self.module_exports = {}
        
        # Track imported modules to prevent circular imports
        self.import_stack = []
        
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
            bytecode = self._process_module_statement(text)
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
            if self._is_module_instruction(instruction):
                return self._execute_module_instruction(instruction)
            
            # Fall back to original execution
            return original_execute(instruction)
        
        # Replace the method with our extended version
        self.vm.execute_instruction = extended_execute
    
    def _process_module_statement(self, text: str) -> Optional[List[str]]:
        """
        Process text for module system statements
        
        Args:
            text: English text to analyze
            
        Returns:
            List of bytecode instructions or None if no match
        """
        bytecode = []
        
        # Process import statements
        if self._is_import_statement(text):
            bytecode = self._translate_import_statement(text)
        
        # Process export statements
        elif self._is_export_statement(text):
            bytecode = self._translate_export_statement(text)
        
        # Process module declarations
        elif self._is_module_declaration(text):
            bytecode = self._translate_module_declaration(text)
        
        return bytecode if bytecode else None
    
    def _is_import_statement(self, text: str) -> bool:
        """Check if text describes an import statement"""
        patterns = [
            r'import\s+(.+)\s+from\s+(.+)',
            r'include\s+(.+)\s+from\s+(.+)',
            r'use\s+(.+)\s+from\s+(.+)',
            r'import\s+module\s+(.+)',
            r'load\s+module\s+(.+)',
        ]
        
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    def _is_export_statement(self, text: str) -> bool:
        """Check if text describes an export statement"""
        patterns = [
            r'export\s+(.+)',
            r'make\s+(.+)\s+available\s+to\s+other\s+modules',
            r'expose\s+(.+)\s+to\s+other\s+modules',
        ]
        
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    def _is_module_declaration(self, text: str) -> bool:
        """Check if text declares a module"""
        patterns = [
            r'module\s+(.+)',
            r'define\s+module\s+(.+)',
            r'create\s+module\s+(.+)',
        ]
        
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    def _translate_import_statement(self, text: str) -> List[str]:
        """Translate import statement to bytecode"""
        # Match different import patterns
        if "from" in text.lower():
            # Import specific symbols from module
            pattern = r'(?:import|include|use)\s+(.+)\s+from\s+(.+)'
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                symbols = match.group(1).strip()
                module_name = match.group(2).strip().strip('"\'')
                
                # Handle multiple symbols separated by commas or "and"
                symbols = re.split(r',\s*|\s+and\s+', symbols)
                symbols_str = ",".join(s.strip() for s in symbols)
                
                return [f"IMPORT_SYMBOLS {module_name} {symbols_str}"]
        else:
            # Import entire module
            pattern = r'(?:import|load)\s+module\s+(.+)'
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                module_name = match.group(1).strip().strip('"\'')
                return [f"IMPORT_MODULE {module_name}"]
        
        return []
    
    def _translate_export_statement(self, text: str) -> List[str]:
        """Translate export statement to bytecode"""
        # Pattern for direct exports
        export_pattern = r'export\s+(.+)'
        match = re.search(export_pattern, text, re.IGNORECASE)
        if match:
            symbols = match.group(1).strip()
            
            # Handle multiple symbols
            symbols = re.split(r',\s*|\s+and\s+', symbols)
            symbols_str = ",".join(s.strip() for s in symbols)
            
            return [f"EXPORT_SYMBOLS {symbols_str}"]
        
        # Alternative export syntax
        alt_pattern = r'(?:make|expose)\s+(.+)\s+available\s+to\s+other\s+modules'
        match = re.search(alt_pattern, text, re.IGNORECASE)
        if match:
            symbols = match.group(1).strip()
            
            # Handle multiple symbols
            symbols = re.split(r',\s*|\s+and\s+', symbols)
            symbols_str = ",".join(s.strip() for s in symbols)
            
            return [f"EXPORT_SYMBOLS {symbols_str}"]
        
        return []
    
    def _translate_module_declaration(self, text: str) -> List[str]:
        """Translate module declaration to bytecode"""
        pattern = r'(?:module|define\s+module|create\s+module)\s+(.+)'
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            module_name = match.group(1).strip().strip('"\'')
            return [f"MODULE_DECLARATION {module_name}"]
        
        return []
    
    def _is_module_instruction(self, instruction: str) -> bool:
        """Check if instruction is a module system instruction"""
        module_instructions = [
            "IMPORT_MODULE", "IMPORT_SYMBOLS",
            "EXPORT_SYMBOLS", "MODULE_DECLARATION"
        ]
        
        for instr in module_instructions:
            if instruction.startswith(instr):
                return True
        
        return False
    
    def _execute_module_instruction(self, instruction: str) -> bool:
        """Execute module system instruction"""
        # Handle import module
        if instruction.startswith("IMPORT_MODULE"):
            return self._execute_import_module(instruction)
            
        # Handle import symbols
        elif instruction.startswith("IMPORT_SYMBOLS"):
            return self._execute_import_symbols(instruction)
            
        # Handle export symbols
        elif instruction.startswith("EXPORT_SYMBOLS"):
            return self._execute_export_symbols(instruction)
            
        # Handle module declaration
        elif instruction.startswith("MODULE_DECLARATION"):
            return self._execute_module_declaration(instruction)
            
        return False
    
    def _execute_import_module(self, instruction: str) -> bool:
        """Execute import module instruction"""
        # Parse instruction: "IMPORT_MODULE module_name"
        parts = instruction.split(" ", 1)
        if len(parts) < 2:
            return False
            
        module_name = parts[1].strip()
        
        # Check for circular imports
        if module_name in self.import_stack:
            print(f"Error: Circular import detected: {' -> '.join(self.import_stack)} -> {module_name}")
            return False
        
        # Load the module if not already loaded
        if module_name not in self.loaded_modules:
            self._load_module(module_name)
        
        # Import all exported symbols from the module into current namespace
        if module_name in self.module_exports:
            for symbol in self.module_exports[module_name]:
                # Would copy symbol value to current VM environment
                # For example: self.vm.environment[symbol] = self.vm.module_environments[module_name][symbol]
                pass
        
        return True
    
    def _execute_import_symbols(self, instruction: str) -> bool:
        """Execute import symbols instruction"""
        # Parse instruction: "IMPORT_SYMBOLS module_name symbol1,symbol2,..."
        parts = instruction.split(" ", 2)
        if len(parts) < 3:
            return False
            
        module_name = parts[1].strip()
        symbols = parts[2].split(",")
        
        # Check for circular imports
        if module_name in self.import_stack:
            print(f"Error: Circular import detected: {' -> '.join(self.import_stack)} -> {module_name}")
            return False
        
        # Load the module if not already loaded
        if module_name not in self.loaded_modules:
            self._load_module(module_name)
        
        # Import only the specified symbols from the module
        if module_name in self.module_exports:
            for symbol in symbols:
                if symbol in self.module_exports[module_name]:
                    # Would copy specific symbol to current VM environment
                    # self.vm.environment[symbol] = self.vm.module_environments[module_name][symbol]
                    pass
                else:
                    print(f"Warning: Symbol '{symbol}' not exported by module '{module_name}'")
        
        return True
    
    def _execute_export_symbols(self, instruction: str) -> bool:
        """Execute export symbols instruction"""
        # Parse instruction: "EXPORT_SYMBOLS symbol1,symbol2,..."
        parts = instruction.split(" ", 1)
        if len(parts) < 2:
            return False
            
        symbols = parts[1].split(",")
        current_module = self.vm.current_module if hasattr(self.vm, "current_module") else "main"
        
        # Initialize exports for this module if needed
        if current_module not in self.module_exports:
            self.module_exports[current_module] = set()
        
        # Add symbols to the export list
        for symbol in symbols:
            symbol = symbol.strip()
            if symbol in self.vm.environment:
                self.module_exports[current_module].add(symbol)
            else:
                print(f"Warning: Cannot export undefined symbol '{symbol}'")
        
        return True
    
    def _execute_module_declaration(self, instruction: str) -> bool:
        """Execute module declaration instruction"""
        # Parse instruction: "MODULE_DECLARATION module_name"
        parts = instruction.split(" ", 1)
        if len(parts) < 2:
            return False
            
        module_name = parts[1].strip()
        
        # Set current module name
        self.vm.current_module = module_name
        
        # Initialize module environment if needed
        if not hasattr(self.vm, "module_environments"):
            self.vm.module_environments = {}
        
        if module_name not in self.vm.module_environments:
            # Create a new environment for this module
            self.vm.module_environments[module_name] = {}
        
        # Point VM environment to this module's environment
        # (Would save previous environment and restore when module execution completes)
        # self.vm.environment = self.vm.module_environments[module_name]
        
        return True
    
    def _load_module(self, module_name: str) -> bool:
        """
        Load a module from file
        
        Args:
            module_name: Name of the module to load
        
        Returns:
            True if module loaded successfully, False otherwise
        """
        # Add to import stack to detect circular imports
        self.import_stack.append(module_name)
        
        try:
            # Convert module name to file path (module_name → module_name.nl)
            module_path = self._resolve_module_path(module_name)
            
            if not module_path or not os.path.exists(module_path):
                print(f"Error: Module file not found: {module_name}")
                return False
            
            # Compile the module if needed
            bytecode_path = os.path.splitext(module_path)[0] + ".nlc"
            if not os.path.exists(bytecode_path) or os.path.getmtime(module_path) > os.path.getmtime(bytecode_path):
                self._compile_module(module_path, bytecode_path)
            
            # Load the compiled bytecode
            with open(bytecode_path, 'r') as f:
                bytecode = [line.strip() for line in f.readlines() if line.strip()]
            
            # Store the loaded module
            self.loaded_modules[module_name] = bytecode
            
            # Execute the module in its own environment to initialize exports
            self._execute_module(module_name)
            
            return True
            
        finally:
            # Remove from import stack when done
            self.import_stack.pop()
    
    def _resolve_module_path(self, module_name: str) -> Optional[str]:
        """
        Resolve a module name to its file path
        
        Args:
            module_name: Name of the module
            
        Returns:
            Path to the module file or None if not found
        """
        # Check in the current directory
        current_dir = os.path.dirname(self.vm.current_file) if hasattr(self.vm, "current_file") else os.getcwd()
        
        # Search paths in this order:
        # 1. Current directory
        # 2. Modules subdirectory
        # 3. Standard library directory
        search_paths = [
            current_dir,
            os.path.join(current_dir, "modules"),
            os.path.join(os.path.dirname(os.path.dirname(__file__)), "stdlib")
        ]
        
        for base_path in search_paths:
            # Try with .nl extension
            module_path = os.path.join(base_path, f"{module_name}.nl")
            if os.path.exists(module_path):
                return module_path
                
            # Try as directory with index.nl
            module_dir_path = os.path.join(base_path, module_name, "index.nl")
            if os.path.exists(module_dir_path):
                return module_dir_path
        
        return None
    
    def _compile_module(self, source_path: str, target_path: str) -> bool:
        """
        Compile a module
        
        Args:
            source_path: Path to the source file
            target_path: Path to the target bytecode file
            
        Returns:
            True if compilation successful, False otherwise
        """
        # Create a new compiler instance for compiling the module
        module_compiler = ImprovedNLPCompiler()
        
        try:
            # Read the source file
            with open(source_path, 'r') as f:
                source = f.read()
            
            # Compile it
            bytecode = []
            for line in source.splitlines():
                line = line.strip()
                if line:
                    line_bytecode = module_compiler.translate_to_bytecode(line)
                    if line_bytecode:
                        bytecode.extend(line_bytecode)
            
            # Write the bytecode to the target file
            with open(target_path, 'w') as f:
                f.write("\n".join(bytecode))
            
            return True
            
        except Exception as e:
            print(f"Error compiling module {source_path}: {str(e)}")
            return False
    
    def _execute_module(self, module_name: str) -> bool:
        """
        Execute a module to initialize its exports
        
        Args:
            module_name: Name of the module to execute
            
        Returns:
            True if execution successful, False otherwise
        """
        if module_name not in self.loaded_modules:
            return False
        
        # Create a temporary VM to execute the module
        module_vm = ImprovedNLVM(debug=self.vm.debug if hasattr(self.vm, "debug") else False)
        
        # Set the current module
        module_vm.current_module = module_name
        
        # Execute the module bytecode
        try:
            module_vm.execute_bytecode(self.loaded_modules[module_name])
            
            # Store the module's environment
            if not hasattr(self.vm, "module_environments"):
                self.vm.module_environments = {}
            
            self.vm.module_environments[module_name] = module_vm.environment
            
            return True
            
        except Exception as e:
            print(f"Error executing module {module_name}: {str(e)}")
            return False


# Example usage in extensions loader:
# compiler = ImprovedNLPCompiler()
# vm = ImprovedNLVM()
# module_system = ModuleSystemExtension(compiler, vm)
