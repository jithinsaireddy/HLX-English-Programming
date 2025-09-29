import subprocess
import tempfile
import time
from pathlib import Path


def have(cmd: str) -> bool:
    try:
        subprocess.run([cmd, "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
        return True
    except Exception:
        return False


def bench_pypy_arith(n_iters: int) -> float | None:
    if not have("pypy3"):
        return None
    code = f"i=0\nimport time\nt0=time.perf_counter()\nfor _ in range({n_iters}):\n    i+=1\nprint(time.perf_counter()-t0)\n"
    out = subprocess.check_output(["pypy3", "-c", code])
    return float(out.strip())


def bench_node_arith(n_iters: int) -> float | None:
    if not have("node"):
        return None
    js = f"const t0=performance.now(); let i=0; for(let k=0;k<{n_iters};k++) i++; console.log((performance.now()-t0)/1000.0);"
    with tempfile.TemporaryDirectory() as td:
        f = Path(td)/"bench.js"
        f.write_text("const { performance } = require('perf_hooks');\n"+js)
        out = subprocess.check_output(["node", str(f)])
    return float(out.strip())


def bench_java_arith(n_iters: int) -> float | None:
    if not (have("javac") and have("java")):
        return None
    src = f"""
public class Bench {{
  public static void main(String[] args) {{
    long N = {n_iters}L;
    long i = 0;
    long t0 = System.nanoTime();
    for (long k=0;k<N;k++) i++;
    long took = System.nanoTime()-t0;
    System.out.println(took/1e9);
  }}
}}
"""
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        (td/"Bench.java").write_text(src)
        subprocess.check_call(["javac", str(td/"Bench.java")], cwd=str(td))
        out = subprocess.check_output(["java", "Bench"], cwd=str(td))
    return float(out.strip())


def main():
    N_ARITH = 400_000
    results = []
    pypy = bench_pypy_arith(N_ARITH)
    node = bench_node_arith(N_ARITH)
    java = bench_java_arith(N_ARITH)
    results.append(("pypy3", pypy))
    results.append(("node", node))
    results.append(("java", java))
    # write markdown
    out = Path(__file__).absolute().parents[2] / 'docs' / 'benchmarks_external.md'
    lines = ["# External Runtime Benchmarks (arith loop)\n", "", "| runtime | size | seconds |", "|---|---:|---:|"]
    for name, val in results:
        seconds = f"{val:.6f}" if isinstance(val, float) else "N/A"
        lines.append(f"| {name} | {N_ARITH} | {seconds} |")
    out.write_text('\n'.join(lines) + '\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()


