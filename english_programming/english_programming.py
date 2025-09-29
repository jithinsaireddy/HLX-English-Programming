#!/usr/bin/env python3
"""
English Programming - Unified System Launcher
The world's first Human Language Virtual Machine

This launcher provides a unified interface to:
- Compile English language programs to bytecode
- Execute bytecode with the enhanced NLVM
- Run the CLI or web interfaces
- Access examples and documentation
"""

import os
import sys
import subprocess
import shutil
import time
from pathlib import Path

# Determine the base directory
BASE_DIR = Path(__file__).resolve().parent
SRC_DIR = BASE_DIR / "src"
EXAMPLES_DIR = BASE_DIR / "examples"

# Component paths (use improved implementations)
COMPILER_PATH = SRC_DIR / "compiler" / "improved_nlp_compiler.py"
VM_PATH = SRC_DIR / "vm" / "improved_nlvm.py"
CLI_PATH = SRC_DIR / "interfaces" / "cli" / "cli_app.py"
WEB_PATH = SRC_DIR / "interfaces" / "web" / "web_app.py"

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Print the application header"""
    clear_screen()
    print("=====================================================")
    print("                ENGLISH PROGRAMMING                  ")
    print("        The Human Language Virtual Machine           ")
    print("=====================================================")
    print("Programming in natural language - no syntax required")
    print("\n")

def compile_and_run(source_file):
    """Compile and run an English program"""
    # Ensure source file exists
    if not os.path.exists(source_file):
        print(f"Error: Source file '{source_file}' not found.")
        return
    
    # Determine output bytecode file
    bytecode_file = os.path.splitext(source_file)[0] + ".nlc"
    
    # Compile the program
    print(f"Compiling {source_file}...")
    result = subprocess.run(
        [sys.executable, str(COMPILER_PATH), source_file, bytecode_file],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print("Compilation failed:")
        print(result.stderr)
        return
    
    print(f"Successfully compiled to {bytecode_file}")
    
    # Run the compiled program
    print("\nExecuting program...\n")
    result = subprocess.run(
        [sys.executable, str(VM_PATH), bytecode_file],
        capture_output=False,
        text=True
    )
    
    if result.returncode != 0:
        print("\nExecution failed.")
    else:
        print("\nProgram executed successfully.")

def list_examples():
    """List available example programs"""
    print("Available Example Programs:")
    print("---------------------------")
    
    examples = list(EXAMPLES_DIR.glob("*.nl"))
    if not examples:
        print("No examples found.")
        return None
    
    for i, example in enumerate(examples, 1):
        print(f"{i}. {example.name}")
    
    print("\nEnter the number of the example to run, or 0 to return to menu:")
    choice = input("> ")
    
    try:
        choice = int(choice)
        if choice == 0:
            return None
        if 1 <= choice <= len(examples):
            return examples[choice-1]
        else:
            print("Invalid choice.")
            return None
    except ValueError:
        print("Invalid input. Please enter a number.")
        return None

def show_main_menu():
    """Display the main menu and handle user selections"""
    while True:
        print_header()
        print("Main Menu:")
        print("1. Run English program (compile and execute)")
        print("2. Run example program")
        print("3. Launch CLI interface")
        print("4. Launch web interface")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ")
        
        if choice == "1":
            print("\nEnter the path to your English program (.nl file):")
            source_file = input("> ")
            compile_and_run(source_file)
            input("\nPress Enter to return to the menu...")
        
        elif choice == "2":
            example = list_examples()
            if example:
                compile_and_run(example)
            input("\nPress Enter to return to the menu...")
        
        elif choice == "3":
            clear_screen()
            print("Launching command line interface...\n")
            subprocess.run([sys.executable, str(CLI_PATH)])
            input("\nPress Enter to return to the menu...")
        
        elif choice == "4":
            clear_screen()
            print("Launching web interface...\n")
            print("Open your browser and navigate to: http://localhost:5000\n")
            print("Press Ctrl+C to stop the server when finished.")
            os.chdir(WEB_PATH.parent)
            subprocess.run([sys.executable, str(WEB_PATH)])
            input("\nPress Enter to return to the menu...")
        
        elif choice == "5":
            clear_screen()
            print("Thank you for using English Programming!")
            sys.exit(0)
        
        else:
            print("\nInvalid choice. Please try again.")
            time.sleep(1)

if __name__ == "__main__":
    # If command line arguments are provided, compile and run directly
    if len(sys.argv) > 1:
        compile_and_run(sys.argv[1])
    else:
        # Otherwise show the interactive menu
        show_main_menu()
