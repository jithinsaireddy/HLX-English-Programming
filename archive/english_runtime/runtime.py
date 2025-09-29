class Interpreter:
    def __init__(self):
        self.env = {}
    
    def run(self, lines):
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line.startswith("Create a variable called"):
                self._handle_assignment(line)
            elif line.startswith("Add"):
                self._handle_addition(line)
            elif line.startswith("Print"):
                self._handle_print(line)
            elif line.startswith("Repeat"):
                count = int(line.split()[1])
                i += 1
                block = []
                while i < len(lines) and lines[i].startswith("    "):
                    block.append(lines[i].strip())
                    i += 1
                for _ in range(count):
                    self.run(block)
                continue  # skip i increment
            i += 1

    def _handle_assignment(self, line):
        parts = line.split()
        var_name = parts[4]
        value = int(parts[-1])
        self.env[var_name] = value

    def _handle_addition(self, line):
        parts = line.split()
        value = int(parts[1])
        var_name = parts[-1]
        self.env[var_name] += value

    def _handle_print(self, line):
        parts = line.split()
        var_name = parts[-1]
        print(self.env.get(var_name, "Undefined"))