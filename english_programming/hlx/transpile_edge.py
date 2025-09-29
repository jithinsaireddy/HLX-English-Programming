from english_programming.hlx.grammar import HLXSpec
import json


def generate_greengrass_manifest(spec: HLXSpec) -> str:
    thing = spec.thing
    manifest = {
        "RecipeFormatVersion": "2020-01-25",
        "ComponentName": f"{thing.name}_edge",
        "ComponentVersion": "1.0.0",
        "ComponentDescription": "HLX-generated edge component",
        "Manifests": [
            {
                "Platform": {"os": "linux"},
                "Artifacts": [
                    {"Uri": "s3://bucket/hlx-edge/edge_module.py"}
                ],
                "Lifecycle": {
                    "Install": {
                        "Script": "pip3 install english-programming[iot]"
                    },
                    "Run": {
                        "Script": f"python3 -m english_programming.hlx.edge_module --spec english_programming/examples/boiler_a.hlx --endpoint {thing.endpoint}"
                    }
                }
            }
        ]
    }
    return json.dumps(manifest, indent=2)


def generate_azure_manifest(spec: HLXSpec) -> str:
    thing = spec.thing
    # Minimal Azure IoT Edge deployment template with one module (illustrative)
    deployment = {
        "content": {
            "modulesContent": {
                "$edgeAgent": {
                    "properties.desired": {
                        "schemaVersion": "1.1",
                        "runtime": {
                            "type": "docker",
                            "settings": {"minDockerVersion": "v1.25"}
                        },
                        "modules": {
                            f"{thing.name}_edge": {
                                "version": "1.0",
                                "type": "docker",
                                "status": "running",
                                "restartPolicy": "always",
                                "settings": {
                                    "image": "ghcr.io/yourorg/hlx-edge:latest",
                                    "createOptions": "{}"
                                }
                            }
                        }
                    }
                },
                "$edgeHub": {
                    "properties.desired": {
                        "schemaVersion": "1.2",
                        "routes": {
                            "route1": "FROM /messages/* INTO $upstream"
                        },
                        "storeAndForwardConfiguration": {"timeToLiveSecs": 7200}
                    }
                }
            }
        }
    }
    return json.dumps(deployment, indent=2)


