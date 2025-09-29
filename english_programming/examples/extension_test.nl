# English Programming Extensions Test
# Tests our extensions with proper English syntax

# Basic variable setup
Create a variable called counter and set it to 1
Create a variable called sum and set it to 0
Create a variable called limit and set it to 5

# While loop test
Print "Testing while loop"
While counter is less than or equal to limit:
    Print counter
    Add counter to sum and store the result in sum
    Add 1 to counter and store the result in counter
    
Print "Sum of numbers 1 to 5:"
Print sum

# For-each loop test
Create a variable called fruits and set it to ["apple", "banana", "cherry"]
Print "Testing for-each loop"
For each fruit in fruits:
    Print "Current fruit:"
    Print fruit

# Conditional logic with else-if (using fixed implementation)
Create a variable called score and set it to 85
Print "Testing conditional logic with score = 85"

If score is greater than 90:
    Print "Grade: A"
Else if score is greater than 80:
    Print "Grade: B"
Else if score is greater than 70:
    Print "Grade: C"
Else:
    Print "Grade: D"

# Function test
Define a function called multiply with inputs x and y:
    Multiply x by y and store the result in product
    Return product

Call multiply with inputs 6 and 7 and store the result in calculation
Print "6 × 7 ="
Print calculation

# Class definition test
Create class Person:
    Define method constructor with inputs name and age:
        Set self.name to name
        Set self.age to age
    
    Define method greet:
        Print "Hello, my name is"
        Print self.name
        Print "and I am"
        Print self.age
        Print "years old"

# Object creation and method invocation
Create a Person object called john with inputs "John Doe" and 30
Call the greet method on john

Print "All extension tests completed!"
