from runtime import Interpreter

def main():
    print("Welcome to the English Runtime CLI. Type 'exit' to quit.")
    interpreter = Interpreter()
    session = []
    while True:
        line = input(">> ").strip()
        if line.lower() == "exit":
            break
        if line:
            session.append(line)
            try:
                interpreter.run([line])
            except Exception as e:
                print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()