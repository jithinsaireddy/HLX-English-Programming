import argparse, json, time, psutil, subprocess, tempfile, os
from pathlib import Path

def run_hlx(spec_path: str):
    t0 = time.time()
    p = subprocess.run([
        'python', '-m', 'english_programming.hlx.run_demo', spec_path, '--json'
    ], capture_output=True, text=True)
    t1 = time.time()
    if p.returncode != 0:
        return {'ok': False, 'error': p.stderr.strip()}
    try:
        trace = json.loads(p.stdout.strip())
    except Exception as e:
        return {'ok': False, 'error': f'bad json: {e}'}
    return {'ok': True, 'elapsed_ms': int((t1 - t0)*1000), 'trace': trace}

def measure(spec_path: str, repeats: int = 3):
    cpu = psutil.cpu_percent(interval=None)
    mem = psutil.virtual_memory().percent
    results = []
    for _ in range(repeats):
        res = run_hlx(spec_path)
        if not res['ok']:
            return res
        results.append(res['trace'])
    # p50/p99 of trigger times
    triggers = [r.get('trigger', {}).get('t_ms', None) for r in results if r.get('trigger')]
    triggers = [t for t in triggers if t is not None]
    triggers.sort()
    def percentile(vals, p):
        if not vals: return None
        k = int(round((p/100.0)*(len(vals)-1)))
        return vals[k]
    return {
        'ok': True,
        'cpu_pct': cpu,
        'mem_pct': mem,
        'p50_trigger_ms': percentile(triggers, 50),
        'p99_trigger_ms': percentile(triggers, 99),
        'repro_identical': len(set(json.dumps(r) for r in results)) == 1,
    }

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--spec', required=True)
    ap.add_argument('--repeats', type=int, default=3)
    args = ap.parse_args()
    out = measure(args.spec, args.repeats)
    print(json.dumps(out))
