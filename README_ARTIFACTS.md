# Artifact and Replication Guide

This package contains all artifacts referenced in the paper.

## Contents
- `artifacts/` — HLX outputs per scenario (rtos.rs, zephyr_main.c, manifests, thing_description.json)
- `traces/` — JSON traces, TD validation results, benchmark summaries, and `summary.csv`
- `docs/replication.md` — step-by-step commands to reproduce results
- `paper/` — LaTeX sources and figures

## Quick Start
1. Create venv and install deps
   ```bash
   python3 -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   make nlp-model
   ```
2. Generate artifacts (example)
   ```bash
   python -m english_programming.hlx.cli english_programming/examples/boiler_a.hlx --out artifacts/boiler
   ```
3. Run demo and capture JSON trace
   ```bash
   python -m english_programming.hlx.run_demo english_programming/examples/boiler_a.hlx --json > traces/boiler.json
   ```
4. Validate Thing Description
   ```bash
   python experiments/validate_wot_td.py artifacts/boiler/thing_description.json > traces/boiler_td_validate.json
   ```
5. Benchmark
   ```bash
   python experiments/bench_hlx.py --spec english_programming/examples/boiler_a.hlx > traces/boiler_bench.json
   python experiments/aggregate_results.py && cat traces/summary.csv
   ```

## Notes
- All numbers in `traces/summary.csv` derive from natural-trigger simulations.
- WoT TDs are generated per scenario and validated with a minimal schema.
- For RTOS builds, wire `rtos.rs` or `zephyr_main.c` into your board/target.
