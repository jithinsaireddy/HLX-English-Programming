from runtime import Interpreter
import os

def main():
    print("====================================================")
    print("Welcome to the English Runtime CLI - Combined Edition")
    print("====================================================")
    print("Type 'exit' to quit, 'help' for commands, 'env' to see variables")
    print("Type 'clear' to clear the screen, 'save' or 'load' for program files")
    
    interpreter = Interpreter()
    session = []
    file_path = None
    
    while True:
        line = input(">> ").strip()
        command = line.lower()
        
        # Handle special commands
        if command == "exit":
            print("Goodbye!")
            break
        elif command == "clear":
            os.system('cls' if os.name == 'nt' else 'clear')
            continue
        elif command == "env":
            _display_environment(interpreter)
            continue
        elif command == "help":
            _display_help()
            continue
        elif command.startswith("save "):
            file_path = command.split(" ", 1)[1].strip()
            _save_program(file_path, session)
            continue
        elif command.startswith("load "):
            file_path = command.split(" ", 1)[1].strip()
            session = _load_program(file_path)
            if session:
                print(f"Program loaded from {file_path}. Run 'run' to execute it.")
            continue
        elif command == "run":
            print(f"Executing program ({len(session)} lines)...")
            try:
                interpreter.run(session)
                print("Program executed successfully.")
            except Exception as e:
                print(f"Error: {str(e)}")
            continue
        elif command == "list":
            _list_program(session)
            continue
        
        # Regular English command processing
        if line:
            session.append(line)
            # For individual lines, execute immediately
            try:
                interpreter.run([line])
            except Exception as e:
                print(f"Error: {str(e)}")
                
                
def _display_environment(interpreter):
    """Display all variables in the environment"""
    if not interpreter.env:
        print("Environment is empty.")
        return
        
    print("\n=== Current Environment Variables ===\n")
    for var, value in interpreter.env.items():
        print(f"{var} = {value}")
    print()
    
def _display_help():
    """Display help information"""
    print("\n=== English Runtime CLI Help ===\n")
    print("Special Commands:")
    print("  exit         - Exit the program")
    print("  clear        - Clear the screen")
    print("  env          - Display all variables")
    print("  list         - Show the current program")
    print("  save <file>  - Save the current program to a file")
    print("  load <file>  - Load a program from a file")
    print("  run          - Run the entire program")
    print("  help         - Show this help information")
    
    print("\nLanguage Examples:")
    print("  Create a variable called count and set it to 5")
    print("  Add count and 3 and store the result in sum")
    print("  Define a function called double with inputs x:")
    print("    Add x and x and store the result in result")
    print("    Return result")
    print("  Call double with values 10 and store result in doubled")
    print("  Print doubled")
    print()
    
def _save_program(file_path, session):
    """Save the current program to a file"""
    try:
        with open(file_path, 'w') as f:
            f.write('\n'.join(session))
        print(f"Program saved to {file_path}")
    except Exception as e:
        print(f"Error saving program: {str(e)}")

def _load_program(file_path):
    """Load a program from a file"""
    try:
        with open(file_path, 'r') as f:
            lines = [line.rstrip() for line in f if line.strip()]
        print(f"Loaded {len(lines)} lines from {file_path}")
        return lines
    except Exception as e:
        print(f"Error loading program: {str(e)}")
        return []

def _list_program(session):
    """List the current program"""
    if not session:
        print("No program in session.")
        return
        
    print("\n=== Current Program ===\n")
    for i, line in enumerate(session):
        print(f"{i+1:3d}: {line}")
    print()

if __name__ == "__main__":
    main()