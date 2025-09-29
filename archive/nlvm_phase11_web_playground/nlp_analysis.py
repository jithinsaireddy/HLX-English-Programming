#!/usr/bin/env python3
"""
NLP Analysis Tool for English Programming
This script helps analyze how the NLPEnhancedCompiler processes different natural language patterns
and identifies areas for improvement.
"""
import re
import sys
import os
import io
import json

# Add the English Programming system to the path
engprg_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if engprg_path not in sys.path:
    sys.path.insert(0, engprg_path)

# Import the NLPEnhancedCompiler and EnhancedNLVM
from english_programming.src.compiler.nlp_enhanced_compiler import NLPEnhancedCompiler
from english_programming.src.vm.enhanced_nlvm import EnhancedNLVM

def analyze_nlp_patterns():
    """Test and analyze how different natural language patterns are processed"""
    compiler = NLPEnhancedCompiler()
    
    # Categories of patterns to test
    test_patterns = {
        "Variable Creation": [
            "Create a variable x and set it to 42",
            "Set y to 100",
            "Let z be 'hello world'",
            "Define counter as 1"
        ],
        "Arithmetic Operations": [
            "Add x and y and store in sum",
            "Subtract 10 from x and store in result",
            "Multiply x by 2 and save in doubled",
            "Divide y by 4 and put in quarter"
        ],
        "String Operations": [
            "Join greeting and name to create message",
            "Set message to greeting + ' ' + name",
            "Combine 'Hello, ' with name into greeting",
            "Set full_name to first_name + ' ' + last_name"
        ],
        "Conditional Logic": [
            "If x is greater than 10: Print 'Large' Else: Print 'Small' End if",
            "When age is at least 18, print 'Adult'",
            "Check if name equals 'John', then print 'Hello John'",
            "If temperature < 32 then print 'Freezing'"
        ],
        "Loops and Counters": [
            "Set counter to 1",
            "While counter <= 5: Print counter, Increment counter, End while",
            "Increase counter by 2",
            "Add 1 to counter"
        ],
        "Complex Queries": [
            "What is the value of x?",
            "Show me the counter",
            "Tell me what y equals",
            "Display the result"
        ]
    }
    
    # Process each category and pattern
    results = {}
    
    for category, patterns in test_patterns.items():
        print(f"\n=== Testing {category} Patterns ===")
        category_results = []
        
        for pattern in patterns:
            print(f"\nPattern: \"{pattern}\"")
            
            # Create a temp file to compile
            test_filename = f"temp_{category.lower().replace(' ', '_')}.nl"
            with open(test_filename, "w") as f:
                f.write(pattern)
                
            output_filename = test_filename.replace(".nl", ".nlc")
            
            # Attempt to compile and capture result
            try:
                # Redirect stdout to capture compiler debug output
                original_stdout = sys.stdout
                debug_output = io.StringIO()
                sys.stdout = debug_output
                
                # Compile
                compiler.compile(test_filename, output_filename)
                
                # Restore stdout
                sys.stdout = original_stdout
                debug = debug_output.getvalue()
                
                # Read the bytecode
                with open(output_filename, "r") as f:
                    bytecode = [line.strip() for line in f.readlines()]
                
                success = len(bytecode) > 0
                pattern_result = {
                    "pattern": pattern,
                    "success": success,
                    "bytecode": bytecode,
                    "debug": debug
                }
                
                # Print the bytecode produced
                print("  Bytecode generated:")
                for line in bytecode:
                    print(f"    {line}")
                
                # Note if there was a warning
                if "Warning: Could not understand line" in debug:
                    print("  ⚠️ Compiler warning: Could not fully understand this pattern")
                    pattern_result["warning"] = True
                
                # Clean up files
                try:
                    os.remove(test_filename)
                    os.remove(output_filename)
                except:
                    pass
                    
            except Exception as e:
                print(f"  ❌ Error: {str(e)}")
                pattern_result = {
                    "pattern": pattern,
                    "success": False,
                    "error": str(e)
                }
            
            category_results.append(pattern_result)
        
        results[category] = category_results
    
    # Summarize results
    print("\n=== Summary of Pattern Support ===")
    for category, patterns in results.items():
        supported = sum(1 for p in patterns if p["success"] and not p.get("warning", False))
        partial = sum(1 for p in patterns if p["success"] and p.get("warning", True))
        failed = sum(1 for p in patterns if not p["success"])
        total = len(patterns)
        
        print(f"{category}:")
        print(f"  ✅ Fully supported: {supported}/{total} ({supported/total*100:.1f}%)")
        print(f"  ⚠️ Partially supported: {partial}/{total} ({partial/total*100:.1f}%)")
        print(f"  ❌ Not supported: {failed}/{total} ({failed/total*100:.1f}%)")
    
    # Write detailed results to a file for analysis
    with open("nlp_analysis_results.json", "w") as f:
        json.dump(results, f, indent=2)
        
    print("\nDetailed results saved to nlp_analysis_results.json")
    
    # Suggest improvements based on analysis
    suggest_improvements(results)
    
def suggest_improvements(results):
    """Generate improvement suggestions based on analysis results"""
    print("\n=== Suggested Improvements for NLPEnhancedCompiler ===")
    
    issues = []
    
    # Check for common patterns that failed
    arithmetic_support = sum(1 for p in results.get("Arithmetic Operations", []) 
                          if p["success"] and not p.get("warning", False))
    if arithmetic_support < 2:
        issues.append("- Improve support for arithmetic expressions (add, subtract, multiply, divide)")
    
    string_support = sum(1 for p in results.get("String Operations", []) 
                      if p["success"] and not p.get("warning", False))
    if string_support < 2:
        issues.append("- Enhance string concatenation support with various natural language patterns")
        
    counter_support = sum(1 for p in results.get("Loops and Counters", []) 
                       if p["success"] and not p.get("warning", False))
    if counter_support < 2:
        issues.append("- Add explicit handling for counter incrementing/decrementing operations")
        
    query_support = sum(1 for p in results.get("Complex Queries", []) 
                      if p["success"] and not p.get("warning", False))
    if query_support < 2:
        issues.append("- Improve question recognition for displaying variable values")
    
    # Print the identified issues
    if issues:
        print("The following improvements would enhance natural language support:")
        for issue in issues:
            print(issue)
        
        print("\nSpecific code improvements to consider:")
        print("1. Add specific handlers in normalize_with_nlp() for arithmetic expressions")
        print("2. Implement string concatenation recognition in analyze_with_nlp()")
        print("3. Create dedicated counter patterns in the compiler's pattern list")
        print("4. Enhance the question recognition system for variable queries")
    else:
        print("The compiler already has good support for the tested patterns.")

if __name__ == "__main__":
    analyze_nlp_patterns()
