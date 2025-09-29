from dataclasses import dataclass
from typing import List


@dataclass
class IRInstruction:
    op: str
    args: List[str]

    @staticmethod
    def from_bytecode(instruction: str) -> "IRInstruction":
        parts = instruction.split()
        op = parts[0] if parts else ""
        args = parts[1:] if len(parts) > 1 else []
        return IRInstruction(op=op, args=args)


@dataclass
class IRProgram:
    instructions: List[IRInstruction]



