create a variable called counter and set it to 1

# While loop demonstration
while counter is less than 5:
    print counter
    add 1 to counter and store the result in counter

create a variable called numbers and set it to [1, 2, 3, 4, 5]

# For-each loop demonstration
for each item in numbers:
    multiply item by 2 and store the result in doubled_item
    print doubled_item

# Numeric range loop demonstration
for i from 1 to 5:
    print i

# Else-if demonstration
create a variable called score and set it to 85

if score is greater than 90:
    print "Grade: A"
else if score is greater than 80:
    print "Grade: B"
else if score is greater than 70:
    print "Grade: C"
else:
    print "Grade: D"

# Module system demonstration
# This would be in a separate file: math_utils.nl
# module math_utils
# 
# define function calculate_square with input x:
#     multiply x by x and store the result in result
#     return result
# 
# export calculate_square
#
# import calculate_square from math_utils
# call calculate_square with value 5 and store result in square_of_five
# print square_of_five

# OOP features demonstration
create class called Person:
    define method constructor with inputs name and age:
        set the name property of self to name
        set the age property of self to age
    
    define method greet:
        concatenate "Hello, my name is " and self.name and store the result in message
        print message
    
    define method have_birthday:
        add 1 to self.age and store the result in self.age
        print "Happy Birthday!"

create Person object called john with inputs "John Doe" and 30
call greet on john
call have_birthday on john
print john.age

# Inheritance demonstration
create class called Student that extends Person:
    define method constructor with inputs name, age, and major:
        call constructor of Person with inputs name and age
        set the major property of self to major
    
    define method study:
        concatenate "Studying " and self.major and store the result in message
        print message

create Student object called mary with inputs "Mary Smith", 22, and "Computer Science"
call greet on mary
call study on mary
