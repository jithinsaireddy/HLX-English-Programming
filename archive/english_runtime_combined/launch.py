#!/usr/bin/env python3
"""
English Runtime Combined Edition - Launcher
This script provides an easy way to launch either the CLI or web interface.
"""

import os
import sys
import subprocess

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    clear_screen()
    print("==========================================================")
    print("       ENGLISH RUNTIME PROGRAMMING LANGUAGE")
    print("              Combined Edition")
    print("==========================================================")
    print("Programming in plain English - Feature-complete implementation")
    print()

def main():
    print_header()
    print("Please select an interface to launch:\n")
    print("1. Command Line Interface")
    print("2. Web Interface")
    print("3. Run Sample Program")
    print("4. Exit")
    
    choice = input("\nEnter your choice (1-4): ")
    
    if choice == '1':
        clear_screen()
        print("Launching command line interface...")
        subprocess.call([sys.executable, "cli_app.py"])
    elif choice == '2':
        clear_screen()
        print("Launching web interface...")
        print("Open your browser and navigate to: http://localhost:5000\n")
        print("Press Ctrl+C to stop the server when finished.")
        os.chdir('web')
        subprocess.call([sys.executable, "web_app.py"])
    elif choice == '3':
        clear_screen()
        print("Running sample program...\n")
        from runtime import Interpreter
        interpreter = Interpreter()
        
        with open("sample_program.txt", "r") as f:
            sample_program = [line.rstrip() for line in f if line.strip()]
        
        print("=== Sample Program ===\n")
        for i, line in enumerate(sample_program):
            print(f"{i+1:2d}: {line}")
        
        print("\n=== Program Output ===\n")
        interpreter.run(sample_program)
        
        input("\nPress Enter to return to menu...")
        main()
    elif choice == '4':
        clear_screen()
        print("Thank you for using English Runtime!")
        sys.exit(0)
    else:
        print("\nInvalid choice. Please try again.")
        input("Press Enter to continue...")
        main()

if __name__ == "__main__":
    main()
