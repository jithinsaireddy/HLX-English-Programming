from dataclasses import dataclass
from typing import List, Optional, Union, Dict, Any


PrimitiveType = str  # e.g., "int", "float", "string", "bool", "list", "dict", "object"


@dataclass
class TypedValue:
    type_name: PrimitiveType
    value: Any


@dataclass
class TypedInstruction:
    opcode: str
    operands: List[Union[int, str, TypedValue]]
    result_type: Optional[PrimitiveType] = None


@dataclass
class TypedFunction:
    name: str
    parameters: List[PrimitiveType]
    body: List[TypedInstruction]
    return_type: Optional[PrimitiveType]


@dataclass
class TypedClass:
    name: str
    base: Optional[str]
    fields: Dict[str, PrimitiveType]
    methods: Dict[str, TypedFunction]


@dataclass
class TypedProgram:
    constants: List[TypedValue]
    symbols: List[str]
    main: List[TypedInstruction]
    functions: List[TypedFunction]
    classes: List[TypedClass]


def type_check_program(program: TypedProgram) -> bool:
    # Placeholder for future type checking; currently returns True without mutation
    return True


