import os
import hashlib
import urllib.request


def _cache_dir() -> str:
    base = os.path.expanduser("~/.ep_cache")
    os.makedirs(base, exist_ok=True)
    return base


def _key(url: str) -> str:
    return hashlib.sha256(url.encode('utf-8')).hexdigest()


def is_allowed(url: str) -> bool:
    # Allow local files always; allow http(s) only if env var is set
    if url.startswith('http://') or url.startswith('https://'):
        # enforce lockfile presence when net access is enabled
        if os.environ.get('EP_ALLOW_NET', '0') != '1':
            return False
        lock = os.path.expanduser('~/.english_cache/registry.lock')
        return os.path.exists(lock)
    return True


def fetch(url: str) -> str:
    if not is_allowed(url):
        raise PermissionError("Network fetch not allowed. Set EP_ALLOW_NET=1 to enable.")
    # Local file
    if not (url.startswith('http://') or url.startswith('https://')):
        with open(url, 'r') as f:
            return f.read()
    # Cached fetch
    cd = _cache_dir()
    path = os.path.join(cd, _key(url) + '.txt')
    if os.path.exists(path):
        return open(path, 'r').read()
    with urllib.request.urlopen(url) as resp:
        data = resp.read().decode('utf-8')
    with open(path, 'w') as f:
        f.write(data)
    return data


