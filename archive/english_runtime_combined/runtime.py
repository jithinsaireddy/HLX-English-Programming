import re

class Interpreter:
    def __init__(self):
        self.env = {}
        self.functions = {}

    def run(self, lines):
        i = 0
        while i < len(lines):
            line = lines[i].strip().lower()  # Convert to lowercase for case-insensitive commands
            original_line = lines[i].strip()  # Keep original line for variable names
            try:
                if line.startswith("define a function called"):
                    name, params = self._parse_function_header(line)
                    i += 1
                    block = []
                    while i < len(lines) and lines[i].startswith("    "):
                        block.append(lines[i].strip())
                        i += 1
                    self.functions[name] = (params, block)
                    continue
                elif line.startswith("call"):
                    self._handle_function_call(line)
                elif "create a dictionary called" in line and "with" in line:
                    self._handle_dict_creation(line)
                elif "create a list called" in line and "with values" in line:
                    self._handle_list_creation(line)
                elif "create a variable" in line and "set it to" in line:
                    self._handle_variable(line)
                elif "get the length of list" in line:
                    self._handle_length(line)
                elif "get the maximum value in list" in line:
                    self._handle_maximum(line)
                elif "add" in line and "and" in line and "store the result in" in line:
                    self._handle_addition(line)
                elif line.startswith("print"):
                    self._handle_print(line)
                else:
                    print(f"Unrecognized instruction: '{line}'")
            except Exception as e:
                print(f"Error: {str(e)}")
            i += 1

    def _parse_function_header(self, line):
        match = re.search(r"define a function called (.+?) with inputs (.+):", line)
        if match:
            name = match.group(1).strip()
            params = [p.strip() for p in match.group(2).split("and")]
            return name, params
        raise ValueError("Invalid function definition")

    def _handle_function_call(self, line):
        match = re.search(r"call (.+?) with values (.+?) and store result in (.+)", line)
        if match:
            name = match.group(1).strip()
            args = [self._parse_value(x.strip()) for x in match.group(2).split("and")]
            result_var = match.group(3).strip()
            if name in self.functions:
                params, block = self.functions[name]
                if len(params) != len(args):
                    raise ValueError(f"Function '{name}' expects {len(params)} arguments")
                local_env = dict(zip(params, args))
                ret_val = self._execute_function(block, local_env)
                self.env[result_var] = ret_val
            else:
                raise NameError(f"Function '{name}' is not defined")

    def _execute_function(self, block, local_env):
        result = None
        for line in block:
            line_lower = line.lower()  # Work with lowercase for command matching
            
            if line_lower.startswith("return"):
                # Extract the variable name after the 'return' keyword
                expr = line_lower.replace("return", "").strip()
                # Get the variable value from the local environment or main env
                if expr in local_env:
                    result = local_env[expr]
                elif expr in self.env:
                    result = self.env[expr]
                else:
                    # If not a variable, try parsing it as a value
                    result = self._parse_value(expr)
                return result
            elif "add" in line_lower and "and" in line_lower and "store the result in" in line_lower:
                self._handle_addition(line, local_env)
        return result

    def _handle_variable(self, line):
        match = re.search(r"create a variable called (.+?) and set it to (.+)", line)
        if match:
            name = match.group(1).strip()
            value = self._parse_value(match.group(2).strip())
            self.env[name] = value

    def _handle_dict_creation(self, line):
        match = re.search(r"create a dictionary called (.+?) with (.+)", line)
        if match:
            name = match.group(1).strip()
            items = match.group(2).split(" and ")
            self.env[name] = {k.strip(): self._parse_value(v.strip())
                              for k, v in (item.split("as") for item in items)}

    def _handle_list_creation(self, line):
        match = re.search(r"create a list called (.+?) with values (.+)", line)
        if match:
            name = match.group(1).strip()
            self.env[name] = [self._parse_value(x.strip()) for x in match.group(2).split(",")]

    def _handle_length(self, line):
        match = re.search(r"get the length of list (.+?) and store it in (.+)", line)
        if match:
            name, var = match.group(1).strip(), match.group(2).strip()
            if not isinstance(self.env.get(name), list):
                raise ValueError(f"'{name}' is not a list")
            self.env[var] = len(self.env[name])

    def _handle_maximum(self, line):
        match = re.search(r"get the maximum value in list (.+?) and store it in (.+)", line)
        if match:
            name, var = match.group(1).strip(), match.group(2).strip()
            if not isinstance(self.env.get(name), list):
                raise ValueError(f"'{name}' is not a list")
            self.env[var] = max(self.env[name])

    def _handle_addition(self, line, env=None):
        line_lower = line.lower()  # Work with lowercase for command matching
        match = re.search(r"add (.+?) and (.+?) and store the result in (.+)", line_lower)
        if match:
            x = self._get_value(match.group(1).strip(), env)
            y = self._get_value(match.group(2).strip(), env)
            z = match.group(3).strip()
            (env or self.env)[z] = x + y

    def _handle_print(self, line):
        expr = line.replace("print", "").strip()
        if "." in expr:
            var, key = expr.split(".")
            val = self.env.get(var.strip(), {})
            print(val.get(key.strip(), f"{key.strip()} not found"))
        elif expr not in self.env:
            raise NameError(f"Variable '{expr}' is not defined")
        else:
            print(self.env[expr])

    def _parse_value(self, val):
        val = val.strip('"\'')
        if val.lower() == "true": return True
        if val.lower() == "false": return False
        try: return int(val)
        except ValueError:
            try: return float(val)
            except ValueError: return val

    def _get_value(self, token, env=None):
        env = env or self.env
        return env.get(token, self._parse_value(token))