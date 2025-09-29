from runtime import Interpreter

if __name__ == "__main__":
    program = [
        "Create a list called numbers with values 5, 10, 15",
        "Get the length of list numbers and store it in count",
        "Print count",
        "Create a variable called a and set it to 20",
        "Create a variable called b and set it to 30",
        "Add a and b and store the result in sum",
        "Print sum",
        "Create a dictionary called user with name as Alice and age as 25",
        "Print user.name",
        "Define a function called greet with inputs first and second:",
        "    Add first and second and store the result in total",
        "    Return total",
        "Call greet with values 10 and 40 and store result in result",
        "Print result",
        "Print undefined_var"  # should trigger friendly error
    ]
    
    interpreter = Interpreter()
    interpreter.run(program)