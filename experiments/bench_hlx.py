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
    cpu_samples = []
    mem_samples = []
    results = []
    for _ in range(repeats):
        # sample short CPU interval around each run for a non-zero estimate
        psutil.cpu_percent(interval=None)
        res = run_hlx(spec_path)
        if not res['ok']:
            return res
        results.append(res['trace'])
        cpu_samples.append(psutil.cpu_percent(interval=0.2))
        mem_samples.append(psutil.virtual_memory().percent)
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
        'cpu_pct': round(sum(cpu_samples)/len(cpu_samples), 1) if cpu_samples else None,
        'mem_pct': round(sum(mem_samples)/len(mem_samples), 1) if mem_samples else None,
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
