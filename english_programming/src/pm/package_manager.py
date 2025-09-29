import os
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import urlopen, Request
import subprocess
import sys

from english_programming.src.compiler.improved_nlp_compiler import ImprovedNLPCompiler


class PackageManager:
    def __init__(self, base_dir: str | None = None):
        self.base_dir = Path(base_dir or os.getcwd())
        self.modules_dir = self.base_dir / "modules_cache"
        self.modules_dir.mkdir(exist_ok=True)

    def _safe_filename(self, url: str) -> Path:
        parsed = urlparse(url)
        safe = (parsed.netloc + parsed.path).replace('/', '_')
        if not safe.endswith('.nl'):
            safe += '.nl'
        return self.modules_dir / safe

    def fetch_module(self, url: str) -> Path | None:
        parsed = urlparse(url)
        if parsed.scheme not in {"https", "file"}:
            return None
        target = self._safe_filename(url)
        try:
            if parsed.scheme == 'file':
                source_path = Path(parsed.path)
                data = source_path.read_bytes()
            else:
                req = Request(url, headers={"User-Agent": "EnglishPM/1.0"})
                with urlopen(req, timeout=5) as resp:
                    data = resp.read()
            target.write_bytes(data)
            return target
        except Exception:
            return None

    def compile_module(self, source_path: Path) -> Path | None:
        try:
            out = source_path.with_suffix('.nlc')
            compiler = ImprovedNLPCompiler()
            compiler.compile(str(source_path), str(out))
            return out
        except Exception:
            return None


