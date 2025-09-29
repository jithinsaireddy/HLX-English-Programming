from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class IRThing:
    name: str
    endpoint: str


@dataclass
class IRSensor:
    name: str
    unit: str
    period_ms: int


@dataclass
class IRAction:
    kind: str
    args: Dict[str, Any]


@dataclass
class IRPolicy:
    metric: str
    comparator: str
    threshold: float
    duration_ms: int
    actions: List[IRAction] = field(default_factory=list)


@dataclass
class IRModule:
    thing: IRThing
    sensors: List[IRSensor]
    policies: List[IRPolicy]


