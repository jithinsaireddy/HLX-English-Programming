import re
import requests

class Interpreter:
    def __init__(self):
        self.env = {}

    def run(self, lines):
        for line in lines:
            line = line.strip().lower()
            try:
                if line.startswith("create a variable called"):
                    name, val = self._parse_assignment(line)
                    self.env[name] = self._parse_value(val)
                elif line.startswith("add"):
                    x, y, res = self._parse_addition(line)
                    self.env[res] = self._get_value(x) + self._get_value(y)
                elif line.startswith("print"):
                    self._handle_print(line)
                elif line.startswith("read file"):
                    filename, var = self._parse_file_read(line)
                    with open(filename, "r") as f:
                        self.env[var] = f.read().splitlines()
                elif line.startswith("write"):
                    msg, filename = self._parse_file_write(line)
                    with open(filename, "w") as f:
                        f.write(msg)
                elif line.startswith("call openweather api"):
                    city, var = self._parse_api_call(line)
                    self.env[var] = self._call_openweather(city)
                else:
                    print(f"Unrecognized instruction: '{line}'")
            except Exception as e:
                print(f"Error: {str(e)}")

    def _parse_assignment(self, line):
        parts = re.search(r"create a variable called (.+?) and set it to (.+)", line)
        return parts.group(1).strip(), parts.group(2).strip()

    def _parse_addition(self, line):
        parts = re.search(r"add (.+?) and (.+?) and store the result in (.+)", line)
        return parts.group(1).strip(), parts.group(2).strip(), parts.group(3).strip()

    def _parse_file_read(self, line):
        parts = re.search(r"read file (.+?) and store lines in (.+)", line)
        return parts.group(1).strip(), parts.group(2).strip()

    def _parse_file_write(self, line):
        parts = re.search(r"write (.+?) to file (.+)", line)
        return parts.group(1).strip(), parts.group(2).strip()

    def _parse_api_call(self, line):
        parts = re.search(r"call openweather api with city as (.+?) and store temperature in (.+)", line)
        return parts.group(1).strip(), parts.group(2).strip()

    def _call_openweather(self, city):
        return f"{city.title()} has 22°C (demo value)"

    def _handle_print(self, line):
        expr = line.replace("print", "").strip()
        val = self.env.get(expr, f"{expr} not defined")
        print(val)

    def _parse_value(self, val):
        val = val.strip('"\'')
        if val.lower() == "true": return True
        if val.lower() == "false": return False
        try: return int(val)
        except ValueError:
            try: return float(val)
            except ValueError: return val

    def _get_value(self, token):
        return self.env.get(token, self._parse_value(token))