from runtime import Interpreter

if __name__ == "__main__":
    interpreter = Interpreter()

    program = [
        "Create a variable called x and set it to 5",
        "Create a variable called y and set it to 15",
        "Add x and y and store the result in total",
        "Print total",
        "Read file sample.txt and store lines in mylist",
        "Print mylist",
        "Write Hello World to file output.txt",
        "Call OpenWeather API with city as London and store temperature in temp",
        "Print temp"
    ]

    interpreter.run(program)