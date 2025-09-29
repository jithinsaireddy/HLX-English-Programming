# File Operations Example
# This demonstrates how the enhanced English Programming system can handle file operations

# Create a test file
Create a variable called filename and set it to "test_data.txt"
Create a variable called content and set it to "This is a test file created by the English Programming system."

# Writing to a file
Write content to filename
Print "File created successfully."

# Reading from a file
Read filename and store the result in file_data
Print "File contents:"
Print file_data

# Appending to a file
Create a variable called additional_content and set it to "\nThis is additional content appended to the file."
Append additional_content to filename
Print "File updated successfully."

# Reading the updated file
Read filename and store the result in updated_file_data
Print "Updated file contents:"
Print updated_file_data

# File existence check
If file exists filename:
    Print "The file exists."
Else:
    Print "The file does not exist."

# Delete the file for cleanup
Delete file filename
Print "File cleanup completed."
