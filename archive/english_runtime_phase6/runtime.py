import re

class Interpreter:
    def __init__(self):
        self.env = {}
        self.functions = {}

    def run(self, lines):
        for line in lines:
            line = line.strip().lower()
            if not line:
                continue
            try:
                if line.startswith("create a variable called"):
                    name, value = self._parse_assignment(line)
                    self.env[name] = self._parse_value(value)
                elif line.startswith("create a list called"):
                    name, values = self._parse_list(line)
                    self.env[name] = [self._parse_value(v) for v in values]
                elif line.startswith("print"):
                    var = line.replace("print", "").strip()
                    if "." in var:
                        obj, key = var.split(".")
                        print(self.env.get(obj, {}).get(key, f"{key} not found"))
                    else:
                        print(self.env.get(var, f"{var} not defined"))
                elif line.startswith("add"):
                    x, y, res = self._parse_addition(line)
                    self.env[res] = self._get_value(x) + self._get_value(y)
                else:
                    print(f"Unrecognized instruction: '{line}'")
            except Exception as e:
                print(f"Error: {str(e)}")

    def _parse_assignment(self, line):
        parts = re.search(r"create a variable called (.+?) and set it to (.+)", line)
        return parts.group(1).strip(), parts.group(2).strip()

    def _parse_list(self, line):
        parts = re.search(r"create a list called (.+?) with values (.+)", line)
        name = parts.group(1).strip()
        values = [x.strip() for x in parts.group(2).split(",")]
        return name, values

    def _parse_addition(self, line):
        parts = re.search(r"add (.+?) and (.+?) and store the result in (.+)", line)
        return parts.group(1).strip(), parts.group(2).strip(), parts.group(3).strip()

    def _get_value(self, token):
        return self.env.get(token, self._parse_value(token))

    def _parse_value(self, val):
        val = val.strip('"\'')
        if val.lower() == "true": return True
        if val.lower() == "false": return False
        try: return int(val)
        except ValueError:
            try: return float(val)
            except ValueError: return val