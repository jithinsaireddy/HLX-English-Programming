import re
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Thing:
    name: str
    endpoint: str


@dataclass
class Sensor:
    name: str
    unit: str
    period_ms: int


@dataclass
class Actuator:
    name: str
    actions: List[str]


@dataclass
class Policy:
    metric: str
    comparator: str
    threshold: float
    duration_ms: int
    hysteresis_pct: float = 0.0
    cooldown_ms: int = 0
    actions: List[str] = field(default_factory=list)


@dataclass
class HLXSpec:
    thing: Thing
    sensors: List[Sensor] = field(default_factory=list)
    actuators: List[Actuator] = field(default_factory=list)
    policies: List[Policy] = field(default_factory=list)


class HLXParser:
    def parse(self, text: str) -> HLXSpec:
        lines = [ln.strip() for ln in text.splitlines() if ln.strip() and not ln.strip().startswith('#')]
        # Canonicalize common synonyms/units to keep regex stable
        def canon(s: str) -> str:
            s2 = s
            # comparators
            s2 = re.sub(r"\bgreater than or equal to\b", ">=", s2, flags=re.I)
            s2 = re.sub(r"\bmore than or equal to\b", ">=", s2, flags=re.I)
            s2 = re.sub(r"\bat least\b", ">=", s2, flags=re.I)
            s2 = re.sub(r"\bno less than\b", ">=", s2, flags=re.I)
            s2 = re.sub(r"\bless than or equal to\b", "<=", s2, flags=re.I)
            s2 = re.sub(r"\bat most\b", "<=", s2, flags=re.I)
            s2 = re.sub(r"\bno more than\b", "<=", s2, flags=re.I)
            s2 = re.sub(r"\bgreater than\b", ">", s2, flags=re.I)
            s2 = re.sub(r"\bmore than\b", ">", s2, flags=re.I)
            s2 = re.sub(r"\babove\b", ">", s2, flags=re.I)
            s2 = re.sub(r"\bbelow\b", "<", s2, flags=re.I)
            s2 = re.sub(r"\bless than\b", "<", s2, flags=re.I)
            s2 = re.sub(r"\bequal to\b", "==", s2, flags=re.I)
            # units
            s2 = re.sub(r"\bmilliseconds?\b", "ms", s2, flags=re.I)
            s2 = re.sub(r"\bseconds?\b|\bsec\b", "s", s2, flags=re.I)
            return s2
        lines = [canon(ln) for ln in lines]
        # Optional spaCy normalization for HLX terms (graceful fallback)
        try:
            import spacy
            try:
                nlp = spacy.load('en_core_web_sm')
            except Exception:
                nlp = spacy.blank('en')
            normed = []
            for ln in lines:
                doc = nlp(ln)
                lemma_line = ' '.join(t.lemma_.lower() or t.text.lower() for t in doc)
                normed.append(lemma_line)
            # Keep quoted strings intact by mixing original tokens when needed
            lines = [normed[i] if '"' not in lines[i] else lines[i] for i in range(len(lines))]
        except Exception:
            pass
        # Additional action synonym expansion (spaCy or regex-based), e.g., 'turn on' -> 'on', 'shut off' -> 'off'
        def expand_actions(s: str) -> str:
            s2 = re.sub(r"\bturn\s+on\b", "on", s, flags=re.I)
            s2 = re.sub(r"\bturn\s+off\b|\bshut\s+off\b|\bswitch\s+off\b", "off", s2, flags=re.I)
            s2 = re.sub(r"\bopen\s+valve\b", "open", s2, flags=re.I)
            s2 = re.sub(r"\bclose\s+valve\b", "close", s2, flags=re.I)
            s2 = re.sub(r"\bemit\s+event\b|\bpublish\s+event\b", "publish event", s2, flags=re.I)
            s2 = re.sub(r"\blog\s+\b", "store", s2, flags=re.I)
            return s2
        lines = [expand_actions(ln) for ln in lines]
        thing: Optional[Thing] = None
        sensors: List[Sensor] = []
        actuators: List[Actuator] = []
        policies: List[Policy] = []
        i = 0
        while i < len(lines):
            ln = lines[i]
            m = re.match(r'^Device\s+"([^"]+)"\s+at\s+(.+)$', ln, re.I)
            if m:
                thing = Thing(name=m.group(1), endpoint=m.group(2))
                i += 1
                continue
            m = re.match(r'^Sensor\s+"([^"]+)"\s+unit\s+(\w+)\s+period\s+(\d+)\s*(ms|s)?$', ln, re.I)
            if m:
                s_name = m.group(1)
                s_unit = m.group(2)
                p_val = int(m.group(3))
                p_unit = (m.group(4) or 'ms').lower()
                p_ms = p_val * (1000 if p_unit == 's' else 1)
                sensors.append(Sensor(name=s_name, unit=s_unit, period_ms=p_ms))
                i += 1
                continue
            m = re.match(r'^Actuator\s+"([^"]+)"\s+actions\s+(.+)$', ln, re.I)
            if m:
                acts = [a.strip() for a in m.group(2).split(',')]
                actuators.append(Actuator(name=m.group(1), actions=acts))
                i += 1
                continue
            # Policy start
            m = re.match(r'^If\s+(.+?)\s*([<>]=?|==)\s*([\w\.\-\+]+)\s*(\w+)?\s*for\s*(\d+)\s*(ms|s)?\s*(?:with\s*hysteresis\s*(\d+)\s*%\s*and\s*cooldown\s*(\d+)\s*ms\s*)?then$', ln, re.I)
            if m:
                metric = m.group(1).strip()
                comp = m.group(2)
                thr_token = m.group(3)
                unit = (m.group(4) or '').lower()
                dur_val = int(m.group(5))
                dur_unit = (m.group(6) or 'ms').lower()
                dur = dur_val * (1000 if dur_unit == 's' else 1)
                hysteresis_pct = float(m.group(7) or 0)
                cooldown_ms = int(m.group(8) or 0)
                # consume action lines until blank or next block
                acts: List[str] = []
                i += 1
                while i < len(lines) and not re.match(r'^(Device|Sensor|Actuator|If)\b', lines[i], re.I):
                    acts.append(lines[i])
                    i += 1
                # threshold may be numeric or symbolic; keep numeric where possible
                try:
                    thr_val = float(thr_token)
                    thr_store = thr_val
                except Exception:
                    thr_store = thr_token
                policies.append(Policy(metric=metric, comparator=comp, threshold=thr_store, duration_ms=dur, hysteresis_pct=hysteresis_pct, cooldown_ms=cooldown_ms, actions=acts))
                continue
            i += 1
        if thing is None:
            raise ValueError('Thing not defined')
        return HLXSpec(thing=thing, sensors=sensors, actuators=actuators, policies=policies)


