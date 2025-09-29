"""Minimal package manager stub with manifest parsing and cache directory.
Manifest format (english.toml):
  [package]
  name = "myapp"
  version = "0.1.0"
  
  [dependencies]
  std = "*"
  http = "*"
"""
import os
from pathlib import Path
from typing import Dict


def get_cache_dir() -> Path:
    root = Path.home() / ".english_cache"
    root.mkdir(parents=True, exist_ok=True)
    return root


def read_manifest(path: str) -> dict:
    # Very small TOML-less parser for a tiny subset
    res = {'package': {}, 'dependencies': {}}
    section = None
    for line in Path(path).read_text().splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if line.startswith('[') and line.endswith(']'):
            section = line.strip('[]')
            continue
        if '=' in line and section:
            k, v = [x.strip() for x in line.split('=', 1)]
            v = v.strip('"')
            if section == 'package':
                res['package'][k] = v
            elif section == 'dependencies':
                res['dependencies'][k] = v
    return res


def _parse_semver(v: str):
    parts = v.strip().split('.')
    try:
        return tuple(int(p) for p in parts)
    except Exception:
        return (0,)


def resolve_dependencies(manifest: dict, registry: dict) -> dict:
    """Return resolved name->version using a simple semver pick from registry.
    Registry is a dict name -> list of versions like ['1.0.0','1.2.3'].
    """
    deps = manifest.get('dependencies', {})
    resolved = {}
    for name, constraint in deps.items():
        if name not in registry:
            continue
        # pick highest version for now (ignore constraint)
        versions = sorted(registry[name], key=_parse_semver)
        if versions:
            resolved[name] = versions[-1]
    return resolved


def _capabilities_from_manifest(manifest: dict) -> Dict[str, bool]:
    caps = manifest.get('capabilities', {}) or {}
    # Normalize to booleans
    out = {
        'net': bool(caps.get('net', False)),
        'fs_read': bool(caps.get('fs_read', True)),
        'fs_write': bool(caps.get('fs_write', False)),
    }
    return out


def install_dependencies(manifest: dict):
    # Placeholder: in the future, resolve URLs or registries
    cache = get_cache_dir()
    # For now, just ensure cache exists
    # Create a lockfile snapshot (very minimal)
    pkg = manifest.get('package', {}).get('name', 'app')
    lock = cache / f"{pkg}.lock"
    deps = manifest.get('dependencies', {})
    lock.write_text('\n'.join(f"{k}={v}" for k,v in deps.items()))
    # Write a registry gate lock to permit network fetches if capability allows
    caps = _capabilities_from_manifest(manifest)
    if caps.get('net'):
        (cache / 'registry.lock').write_text('allow')
    else:
        try:
            (cache / 'registry.lock').unlink()
        except Exception:
            pass
    return cache


