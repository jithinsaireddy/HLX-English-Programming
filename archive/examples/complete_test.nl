
# Comprehensive English Programming Extensions Test

# Variable initialization
create a variable called counter and set it to 1
create a variable called sum and set it to 0

# While loop demonstration
print "Testing while loop:"
while counter is less than 6:
    print "Counter is"
    print counter
    add counter to sum and store the result in sum
    add 1 to counter and store the result in counter

print "Sum of numbers 1 to 5:"
print sum

# For loop demonstration
print "Testing for-each loop:"
create a variable called fruits and set it to ["apple", "banana", "cherry"]
for each fruit in fruits:
    print "Current fruit:"
    print fruit
    
# Numeric range loop
print "Testing numeric range loop:"
for i from 1 to 3:
    print "Value of i:"
    print i

# If/else-if demonstration
create a variable called score and set it to 85
print "Testing if/else-if with score = 85:"

if score is greater than 90:
    print "Grade: A"
else if score is greater than 80:
    print "Grade: B"
else if score is greater than 70:
    print "Grade: C"
else:
    print "Grade: D"

# Class definition
create class called Person:
    define method constructor with inputs name and age:
        set the name property of self to name
        set the age property of self to age
    
    define method greet:
        print "Hello, my name is"
        print self.name
        print "and I am"
        print self.age
        print "years old."

# Inheritance
create class called Student that extends Person:
    define method constructor with inputs name, age, and major:
        call constructor of Person with inputs name and age
        set the major property of self to major
        
    define method study:
        print "I am studying"
        print self.major

# Object creation and method call
print "Testing OOP features:"
create Person object called john with inputs "John Doe" and 30
call greet on john

create Student object called mary with inputs "Mary Smith", 20, and "Computer Science"
call greet on mary
call study on mary

# Testing complete
print "All tests completed successfully!"
