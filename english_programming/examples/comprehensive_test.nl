Create a variable called test_name and set it to Comprehensive English Programming Test
Print test_name

Create a variable called counter and set it to 0
Create a variable called max_count and set it to 5

Define a function called process_data with inputs data and filter_value:
    Create a variable called result and set it to 0
    
    If data is greater than filter_value:
        Add data and filter_value and store the result in result
    Else:
        Add data and -1 and store the result in result
    
    Return result

Define a function called log_result with inputs message and value:
    Print message
    Print value
    Write value to file test_log.txt
    Return value

While counter is less than max_count:
    Add counter and 1 and store the result in counter
    
    Call process_data with values counter and 3 and store result in processed
    Call log_result with values Processed Value and processed and store result in logged
    
    If processed is greater than 5:
        Print Found large value
        Call OpenWeather API with city as London and store temperature in weather
        Print weather

Print Test completed
