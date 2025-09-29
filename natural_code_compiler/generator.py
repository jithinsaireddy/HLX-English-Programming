def generate_code(parsed_commands):
    code_lines = []
    for command in parsed_commands:
        if command[0] == "assign":
            code_lines.append(f"{command[1]} = {command[2]}")
        elif command[0] == "add":
            code_lines.append(f"{command[3]} = {command[1]} + {command[2]}")
        elif command[0] == "print":
            code_lines.append(f"print({command[1]})")
    return "\n".join(code_lines)