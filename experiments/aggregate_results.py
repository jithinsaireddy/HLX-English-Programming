import json, csv, glob

SCENARIOS = [
  'boiler', 'hvac', 'tank_flow', 'pipeline_leak', 'hospital_co2', 'freezer'
]

def main():
    rows = []
    for s in SCENARIOS:
        bench = f'traces/{s}_bench.json'
        tdv = f'traces/{s}_td_validate.json'
        try:
            b = json.load(open(bench))
        except Exception:
            b = {}
        try:
            v = json.load(open(tdv))
        except Exception:
            v = {}
        rows.append({
            'scenario': s,
            'p50_trigger_ms': b.get('p50_trigger_ms'),
            'p99_trigger_ms': b.get('p99_trigger_ms'),
            'cpu_pct': b.get('cpu_pct'),
            'mem_pct': b.get('mem_pct'),
            'repro_identical': b.get('repro_identical'),
            'td_valid': v.get('ok'),
        })
    with open('traces/summary.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)

if __name__ == '__main__':
    main()
