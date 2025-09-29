import argparse
from pathlib import Path
from english_programming.hlx.grammar import HLXParser
from english_programming.hlx.transpile_rtos import generate_rust_freertos
from english_programming.hlx.transpile_edge import generate_greengrass_manifest
from english_programming.hlx.transpile_edge import generate_azure_manifest
from english_programming.hlx.net import generate_wot_td
from english_programming.hlx.transpile_zephyr import generate_zephyr_c
from english_programming.hlx.verifier import verify_spec


def main():
    ap = argparse.ArgumentParser(description='HLX compiler')
    ap.add_argument('spec', help='HLX spec file')
    ap.add_argument('--out', default='out_hlx', help='Output directory')
    args = ap.parse_args()
    spec_text = Path(args.spec).read_text()
    spec = HLXParser().parse(spec_text)
    issues = verify_spec(spec)
    if issues:
        print("Verifier warnings:")
        for w in issues:
            print(" - ", w)
    out_dir = Path(args.out); out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / 'rtos.rs').write_text(generate_rust_freertos(spec))
    (out_dir / 'edge_manifest.json').write_text(generate_greengrass_manifest(spec))
    (out_dir / 'azure_deployment.json').write_text(generate_azure_manifest(spec))
    (out_dir / 'zephyr_main.c').write_text(generate_zephyr_c(spec))
    (out_dir / 'thing_description.json').write_text(generate_wot_td(spec))
    print(f"HLX build complete: {out_dir}")


if __name__ == '__main__':
    main()


