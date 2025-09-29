"""
Extension Loader for English Programming
This module provides a unified interface to load and activate language extensions.

It manages the integration of modular extensions with the core compiler and VM:
- Advanced Control Flow (while loops, for/each loops, else-if)
- Module System (imports, code organization)
- OOP Features (classes, objects, inheritance, methods)

These extensions are designed to work without modifying the original codebase.
"""

import sys
import os
from typing import List, Dict, Any, Optional

# Add the project root to path for imports
sys.path.append('/Users/jithinpothireddy/Downloads/English Programming')

# Import core components
from english_programming.src.compiler.improved_nlp_compiler import ImprovedNLPCompiler
from english_programming.src.vm.improved_nlvm import ImprovedNLVM

# Import extensions
from english_programming.src.extensions.control_flow.advanced_loops import AdvancedControlFlowExtension
from english_programming.src.extensions.module_system.module_loader import ModuleSystemExtension
from english_programming.src.extensions.oop.class_system import OOPExtension

class ExtensionLoader:
    """
    Extension loader that manages the loading and activation of language extensions
    for the English Programming language.
    """
    
    def __init__(self, compiler: ImprovedNLPCompiler, vm: ImprovedNLVM):
        """
        Initialize the extension loader
        
        Args:
            compiler: The compiler instance to extend
            vm: The VM instance to extend
        """
        self.compiler = compiler
        self.vm = vm
        self.loaded_extensions = {}
    
    def load_all_extensions(self):
        """Load all available extensions"""
        # Load control flow extensions
        self.load_extension("control_flow", AdvancedControlFlowExtension)
        
        # Load module system
        self.load_extension("module_system", ModuleSystemExtension)
        
        # Load OOP features
        self.load_extension("oop", OOPExtension)
    
    def load_extension(self, name: str, extension_class):
        """
        Load a specific extension
        
        Args:
            name: Name of the extension
            extension_class: Extension class to instantiate
        """
        if name in self.loaded_extensions:
            print(f"Extension '{name}' already loaded")
            return
        
        try:
            # Create extension instance
            extension = extension_class(self.compiler, self.vm)
            
            # Store extension reference
            self.loaded_extensions[name] = extension
            
            print(f"Successfully loaded extension: {name}")
            return extension
        except Exception as e:
            print(f"Error loading extension '{name}': {str(e)}")
            return None
    
    def unload_extension(self, name: str):
        """
        Unload a specific extension
        
        Args:
            name: Name of the extension to unload
        """
        if name not in self.loaded_extensions:
            print(f"Extension '{name}' not loaded")
            return False
        
        # Remove extension reference
        del self.loaded_extensions[name]
        print(f"Successfully unloaded extension: {name}")
        return True
    
    def get_extension(self, name: str):
        """
        Get a reference to a loaded extension
        
        Args:
            name: Name of the extension
        
        Returns:
            The extension instance or None if not loaded
        """
        return self.loaded_extensions.get(name)
    
    def get_loaded_extensions(self) -> List[str]:
        """
        Get list of loaded extensions
        
        Returns:
            List of extension names
        """
        return list(self.loaded_extensions.keys())


# Example usage:
# compiler = ImprovedNLPCompiler()
# vm = ImprovedNLVM()
# extensions = ExtensionLoader(compiler, vm)
# extensions.load_all_extensions()
