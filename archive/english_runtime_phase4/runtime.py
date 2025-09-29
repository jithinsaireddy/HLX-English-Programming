class Interpreter:
    def __init__(self):
        self.env = {}
        self.functions = {}

    def run(self, lines, local_env=None):
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line.startswith("Create a variable called"):
                self._handle_assignment(line, local_env)
            elif line.startswith("Add"):
                self._handle_addition(line, local_env)
            elif line.startswith("Print"):
                self._handle_print(line, local_env)
            elif line.startswith("Ask the user"):
                self._handle_input(line, local_env)
            elif line.startswith("If"):
                condition = self._evaluate_condition(line, local_env)
                i += 1
                block = []
                while i < len(lines) and lines[i].startswith("    "):
                    block.append(lines[i].strip())
                    i += 1
                if condition:
                    self.run(block, local_env)
                elif i < len(lines) and lines[i].strip().startswith("Else:"):
                    i += 1
                    else_block = []
                    while i < len(lines) and lines[i].startswith("    "):
                        else_block.append(lines[i].strip())
                        i += 1
                    self.run(else_block, local_env)
                continue
            elif line.startswith("Define a function called"):
                func_name = line.split("called")[1].split(":")[0].strip()
                i += 1
                block = []
                while i < len(lines) and lines[i].startswith("    "):
                    block.append(lines[i].strip())
                    i += 1
                self.functions[func_name] = block
                continue
            elif line.startswith("Call"):
                func_name = line.split("Call")[1].strip()
                if func_name in self.functions:
                    self.run(self.functions[func_name], {})
            elif line.startswith("Create a list called"):
                self._handle_list_creation(line, local_env)
            elif line.startswith("For each item in"):
                list_name = line.split("in")[1].replace(":", "").strip()
                i += 1
                block = []
                while i < len(lines) and lines[i].startswith("    "):
                    block.append(lines[i].replace("item", "loop_item").strip())
                    i += 1
                iterable = (local_env or self.env).get(list_name, [])
                for val in iterable:
                    loop_env = dict(local_env or self.env)
                    loop_env["loop_item"] = val
                    self.run(block, loop_env)
                continue
            elif line.startswith("While"):
                condition_line = line
                i += 1
                block = []
                while i < len(lines) and lines[i].startswith("    "):
                    block.append(lines[i].strip())
                    i += 1
                while self._evaluate_condition(condition_line, local_env):
                    self.run(block, local_env)
                continue
            i += 1

    def _handle_assignment(self, line, env=None):
        parts = line.split()
        var_name = parts[4]
        value = int(parts[-1])
        (env or self.env)[var_name] = value

    def _handle_addition(self, line, env=None):
        parts = line.split()
        value = int(parts[1])
        var_name = parts[-1]
        (env or self.env)[var_name] += value

    def _handle_print(self, line, env=None):
        parts = line.split()
        var_name = parts[1]
        print((env or self.env).get(var_name, var_name))

    def _handle_input(self, line, env=None):
        parts = line.split()
        var_name = parts[-1]
        user_input = input("Enter value: ")
        try:
            val = int(user_input)
        except:
            val = user_input
        (env or self.env)[var_name] = val

    def _handle_list_creation(self, line, env=None):
        parts = line.split("with values")
        list_name = parts[0].split("called")[1].strip()
        values = [int(x.strip()) for x in parts[1].split(",")]
        (env or self.env)[list_name] = values

    def _evaluate_condition(self, line, env=None):
        tokens = line.replace(":", "").split()
        left = tokens[1]
        operator = tokens[2]
        right = tokens[3]
        env = env or self.env
        left_val = env.get(left, left)
        right_val = env.get(right, right)
        try:
            left_val = int(left_val)
            right_val = int(right_val)
        except:
            pass
        if operator == "is":
            return left_val == right_val
        elif operator == "greater":
            return left_val > right_val
        elif operator == "less":
            return left_val < right_val
        elif operator == "equal":
            return left_val == right_val
        elif operator == "not":
            return left_val != right_val
        return False