# Security Policy

## Supported Versions

We currently support security fixes on the `main` branch.

## Reporting a Vulnerability

- Please open a private security advisory on GitHub or email the maintainer.
- Include a proof of concept, impact assessment, and suggested remediation if possible.
- We aim to acknowledge reports within 5 business days.

## Scope and Assumptions

- Network access is disabled by default in NLVM unless `EP_ENABLE_NET=1` is set.
- Execution guards exist for operation count (`EP_MAX_OPS`) and wall‑clock (`EP_MAX_MS`).
- HLX edge modules may connect to MQTT/CoAP; deployments must authenticate endpoints.

## Disclosure

We prefer coordinated disclosure. We will attribute credit unless you request anonymity.

