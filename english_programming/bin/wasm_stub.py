"""
Minimal WASM backend stub.
Enable by setting EP_WASM_BACKEND=1 and call run_wasm(code) to simulate.
This is a placeholder; real backend would translate NLBC to WASM or embed a WASM VM.
"""

import os


def is_enabled() -> bool:
    return os.getenv('EP_WASM_BACKEND') == '1'


def run_wasm(consts, syms, code):
    if not is_enabled():
        raise RuntimeError("WASM backend disabled")
    # Placeholder: no-op execution returning empty env
    return {}


