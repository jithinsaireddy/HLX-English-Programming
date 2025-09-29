"""
English Programming Extensions Package
This package contains modular extensions to enhance the English Programming language:

1. Advanced Control Flow
   - While loops
   - For loops (enumeration and collection iteration)
   - Else-if constructs

2. Module System
   - File imports
   - Code organization
   - Export/import mechanisms

3. OOP Features
   - Classes and objects
   - Inheritance
   - Methods

Use the ExtensionLoader to easily integrate these extensions with the compiler and VM.
"""

# Make extension components importable
from english_programming.src.extensions.extension_loader import ExtensionLoader
from english_programming.src.extensions.control_flow.advanced_loops import AdvancedControlFlowExtension
from english_programming.src.extensions.module_system.module_loader import ModuleSystemExtension
from english_programming.src.extensions.oop.class_system import OOPExtension
