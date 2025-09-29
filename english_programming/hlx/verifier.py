from typing import List
from english_programming.hlx.grammar import HLXSpec


VALID_COMPARATORS = {">", ">=", "<", "<=", "=="}


def verify_spec(spec: HLXSpec) -> List[str]:
    issues: List[str] = []
    # Thing endpoint
    if not (spec.thing.endpoint.startswith("mqtt://") or spec.thing.endpoint.startswith("coap://")):
        issues.append("Endpoint should start with mqtt:// or coap:// for IoT bindings")
    # Sensors map
    sensor_names = {s.name: s for s in spec.sensors}
    # Actuators map
    actuator_names = {a.name: a for a in spec.actuators}

    for p in spec.policies:
        # metric must exist as a sensor
        if p.metric not in sensor_names:
            issues.append(f"Policy references unknown sensor metric: {p.metric}")
        # comparator valid
        if p.comparator not in VALID_COMPARATORS:
            issues.append(f"Invalid comparator: {p.comparator}")
        # duration sanity
        if p.duration_ms <= 0:
            issues.append("Duration must be positive")
        # hysteresis/cooldown non-negative
        if p.hysteresis_pct < 0.0:
            issues.append("Hysteresis must be >= 0")
        if p.cooldown_ms < 0:
            issues.append("Cooldown must be >= 0")
        # actions known
        for act in p.actions:
            if act.startswith("open ") or act.startswith("close "):
                target = act.split(" ", 1)[1].strip()
                if target not in actuator_names:
                    issues.append(f"Action targets unknown actuator: {target}")
        # safety suggestions
        if p.cooldown_ms == 0 and p.hysteresis_pct == 0.0:
            issues.append("Policy has no hysteresis or cooldown; may flap in noisy conditions")
        # duty cycle heuristic (e.g., minimum 5s cooldown if triggering often)
        min_cool = max(0, int(p.duration_ms * 0.5))
        if p.cooldown_ms and p.cooldown_ms < min_cool:
            issues.append(f"Cooldown {p.cooldown_ms}ms may be too low; consider >= {min_cool}ms")
    return issues


