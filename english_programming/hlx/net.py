from english_programming.hlx.grammar import HLXSpec
import json


def generate_wot_td(spec: HLXSpec) -> str:
    thing = spec.thing
    td = {
        "@context": ["https://www.w3.org/2019/wot/td/v1"],
        "title": thing.name,
        "security": ["basic_sc"],
        "securityDefinitions": {
            "basic_sc": {
                "scheme": "basic"
            }
        },
        "properties": {s.name: {"type": "number", "unit": s.unit} for s in spec.sensors},
        "actions": {a.name: {} for a in spec.actuators},
        "base": thing.endpoint,
        "forms": [
            {
                "href": thing.endpoint,
                "op": ["readproperty", "invokeaction"],
                "contentType": "application/json",
                "mqv:method": "mqtt",
                "mqv:topics": {
                    "read": f"{thing.name}/sensor/+",
                    "action": f"{thing.name}/actuator/+"
                }
            }
        ]
    }
    return json.dumps(td, indent=2)


