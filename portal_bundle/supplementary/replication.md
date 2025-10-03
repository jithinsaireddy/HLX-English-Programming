# Replication Guide

## Environment
- Python 3.9+
- `pip install -r requirements.txt`
- `make nlp-model`

## HLX Scenarios
Run and capture traces:
```bash
python -m english_programming.hlx.run_demo english_programming/examples/boiler_a.hlx --json > traces/boiler.json
python -m english_programming.hlx.run_demo english_programming/examples/hvac.hlx --json > traces/hvac.json
python -m english_programming.hlx.run_demo english_programming/examples/tank_flow.hlx --json > traces/tank_flow.json
python -m english_programming.hlx.run_demo english_programming/examples/pipeline_leak.hlx --json > traces/pipeline_leak.json
python -m english_programming.hlx.run_demo english_programming/examples/hospital_co2.hlx --json > traces/hospital_co2.json
python -m english_programming.hlx.run_demo english_programming/examples/freezer.hlx --json > traces/freezer.json
```

## Benchmarks
```bash
python experiments/bench_hlx.py --spec english_programming/examples/boiler_a.hlx
```

## WoT TD Validation
```bash
python experiments/validate_wot_td.py hlx_out/thing_description.json
```
