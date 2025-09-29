#!/usr/bin/env python3
"""
English Programming System - Main Runner
Integrates enhanced compiler and VM with spaCy NLP capabilities
"""
import os
import sys
import argparse
import importlib.util
from pathlib import Path

# Ensure src directory is in the Python path
current_dir = Path(__file__).parent.absolute()
src_dir = current_dir / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

# Require spaCy with English model
try:
    import spacy  # noqa: F401
    _NLP = None
    try:
        _NLP = spacy.load('en_core_web_sm')
    except Exception:
        # Try to download automatically once
        import subprocess
        subprocess.run([sys.executable, '-m', 'spacy', 'download', 'en_core_web_sm'], check=True)
        import spacy as _sp2
        _NLP = _sp2.load('en_core_web_sm')
    has_spacy = True
except Exception as e:
    print("Error: spaCy with model 'en_core_web_sm' is required.")
    print("Install with: pip install spacy && python -m spacy download en_core_web_sm")
    print(f"Details: {e}")
    sys.exit(2)

# Import compiler and VM components
from compiler.improved_nlp_compiler import ImprovedNLPCompiler
from vm.improved_nlvm import ImprovedNLVM

# Import NLP compiler if spaCy is available
if has_spacy:
    try:
        # Try both import paths to handle different environments
        try:
            from english_programming.src.compiler.nlp_enhanced_compiler import NLPEnhancedCompiler
        except ImportError:
            # Fallback for when running from within the package
            from src.compiler.nlp_enhanced_compiler import NLPEnhancedCompiler
        nlp_enabled = True
    except ImportError as e:
        nlp_enabled = False
        print(f"Warning: NLP-enhanced compiler not found. Using standard compiler. Error: {e}")
else:
    nlp_enabled = False

def main():
    """Main entry point for the English Programming System"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='English Programming System')
    parser.add_argument('file', help='Natural language program file to run (.nl extension)')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--compile-only', action='store_true', help='Only compile, do not execute')
    parser.add_argument('--output', '-o', help='Specify output file for compiled bytecode')
    # NLP is mandatory; keep flag for compatibility but ignore
    parser.add_argument('--no-nlp', action='store_true', help='(Deprecated) NLP is mandatory and always enabled')
    parser.add_argument('--text', action='store_true', help='Use legacy text IR instead of NLBC binary')
    parser.add_argument('--disassemble', action='store_true', help='Disassemble an NLBC file and exit')
    args = parser.parse_args()
    
    # Ensure file exists and has .nl extension
    if not os.path.exists(args.file):
        print(f"Error: File {args.file} not found")
        return 1
        
    if not args.file.endswith('.nl'):
        print(f"Warning: Input file should have .nl extension")
    
    # Determine output file path
    if args.output:
        output_file = args.output
    else:
        output_file = os.path.splitext(args.file)[0] + '.nlc'
    
    print(f"===== English Programming System =====")
    
    # Initialize appropriate compiler based on availability and user preference
    print("NLP: ON (spaCy mandatory; using en_core_web_sm)")
    compiler = ImprovedNLPCompiler()
    
    # Initialize VM
    vm = ImprovedNLVM()
    
    # Disassemble mode
    if args.disassemble and not args.text:
        from english_programming.bin.nlbc_disassembler import disassemble
        buf = open(args.file, 'rb').read()
        print(disassemble(buf))
        return 0

    # Compile
    if not args.text:
        print("\n[1/2] Compiling natural language to NLBC binary...")
        from english_programming.bin.nlp_compiler_bin import compile_english_to_binary
        with open(args.file, 'r') as f:
            lines = [ln.strip() for ln in f.readlines() if ln.strip()]
        nlb_out = args.file.rsplit('.', 1)[0] + '.nlbc'
        compile_english_to_binary(lines, nlb_out)
    else:
        print("\n[1/2] Compiling natural language to bytecode...")
        compiler.compile(args.file, output_file)
    
    # Stop here if compile-only mode
    if args.compile_only:
        print(f"\nCompilation completed. Bytecode saved to {output_file}")
        return 0
    
    # Execute
    print("\n[2/2] Executing...")
    print("\n----- Program Output -----")
    if not args.text:
        from english_programming.bin.nlvm_bin import parse_module, run_module
        buf = open(nlb_out, 'rb').read()
        _, _, _, consts, syms, code, funcs = parse_module(buf)
        run_module(consts, syms, code, funcs)
    else:
        vm.execute(output_file)
    print("------------------------")
    
    print(f"\nProgram execution completed successfully.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
