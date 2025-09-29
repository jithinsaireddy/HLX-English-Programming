from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import re
import os
import sys
import io
import json
import tempfile
import subprocess
from typing import Dict, List, Any, Tuple, Optional

# Add the English Programming system to the path
engprg_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if engprg_path not in sys.path:
    sys.path.insert(0, engprg_path)

# Try to import the ImprovedNLPCompiler and ImprovedNLVM
try:
    from english_programming.src.compiler.improved_nlp_compiler import ImprovedNLPCompiler
    from english_programming.src.vm.improved_nlvm import ImprovedNLVM
    NLP_AVAILABLE = True
    print("Successfully imported Enhanced English Programming system components with improved VM!")
except ImportError as e:
    # Try just the improved compiler
    try:
        from english_programming.src.compiler.improved_nlp_compiler import ImprovedNLPCompiler
        from english_programming.src.vm.enhanced_nlvm import EnhancedNLVM
        NLP_AVAILABLE = True
        print("Successfully imported Enhanced English Programming compiler (without improved VM)")
    except ImportError as e:
        # Fall back to the original NLPEnhancedCompiler
        try:
            from english_programming.src.compiler.nlp_enhanced_compiler import NLPEnhancedCompiler
            from english_programming.src.vm.enhanced_nlvm import EnhancedNLVM
            NLP_AVAILABLE = True
            print("Successfully imported English Programming system components! (fallback mode)")
        except ImportError as e:
            NLP_AVAILABLE = False
            print(f"Warning: Could not import English Programming components: {e}")
            print("Falling back to subprocess mode")

app = Flask(__name__)
# Enable CORS for all routes
CORS(app)

# Sample examples for the playground
EXAMPLES = {
    "variables": """Create a variable x and set it to 42
Print x""",
    
    "arithmetic": """Set a to 15
Set b to 27
Add a and b and store in result
Print result""",
    
    "conditional": """Set age to 25
If age is less than 18:
    Print 'You are too young'
Else:
    Print 'You are an adult'""",
    
    "file_ops": """Set content to 'Hello, World!'
Write content to file hello.txt
Read hello.txt and store in result
Print result""",
    
    "api": """Set city to 'San Francisco'
Get weather for city and store in weather_data
Print 'Weather in:'
Print city
Print weather_data""",
    
    "nlp_flex": """Make a variable called total with a value of 100
Take total and divide it by 4
Show me the result""",
    
    "nlp_vars": """Let x be 10
Define y as 20
Assign the sum of x and y to a variable named result
Display the result""",
    
    "nlp_natural": """Create a counter with initial value 1
Increment the counter by 5
I want to see what the counter is now""",
    
    "nlp_complex": """Let's make a variable color and set it to 'blue'
Create another variable called sky with the value of color
Tell me the sky color"""
}

# Main compile and run function that uses the official English Programming system
def compile_and_run(nl_code):
    result = {
        "compilation": "",
        "execution": "",
        "success": True,
        "error": "",
        "full_output": "",
        "variables": {},
        "nlp_enabled": NLP_AVAILABLE
    }
    
    if NLP_AVAILABLE:
        # Use the imported system components directly
        try:
            # Create temporary files for input and output
            with tempfile.NamedTemporaryFile(mode='w', suffix='.nl', delete=False) as tmp_in:
                tmp_in.write(nl_code)
                input_file = tmp_in.name
                
            output_file = input_file.replace('.nl', '.nlc')
            
            # Redirect stdout to capture compiler output
            stdout_buffer = io.StringIO()
            original_stdout = sys.stdout
            sys.stdout = stdout_buffer
            
            # Compile the code using ImprovedNLPCompiler if available, otherwise NLPEnhancedCompiler
            if 'ImprovedNLPCompiler' in globals():
                compiler = ImprovedNLPCompiler()
            else:
                compiler = NLPEnhancedCompiler()
            compiler.compile(input_file, output_file)
            
            # Create VM and execute
            # Redirect stdout to capture VM output
            stdout_buffer2 = io.StringIO()
            sys.stdout = stdout_buffer2
            # Create VM and execute using the improved VM if available
            if 'ImprovedNLVM' in globals():
                vm = ImprovedNLVM()
                print("Using ImprovedNLVM for execution...")
            else:
                vm = EnhancedNLVM()
                print("Using standard EnhancedNLVM for execution...")
            vm_output = vm.execute(output_file)
            
            # Get VM output and restore stdout
            execution_output = stdout_buffer2.getvalue()
            # If using ImprovedNLVM, we should also get the output from the vm_output variable
            if 'ImprovedNLVM' in globals() and vm_output and isinstance(vm_output, str):
                execution_output += vm_output
            
            # Restore stdout
            sys.stdout = original_stdout
            compiler_output = stdout_buffer.getvalue()
            
            # Read bytecode file
            with open(output_file, 'r') as f:
                bytecode = f.read()
                
            # Clean up temporary files
            if os.path.exists(input_file):
                os.unlink(input_file)
            if os.path.exists(output_file):
                os.unlink(output_file)
                
            # Populate result
            result["compilation"] = bytecode
            result["execution"] = execution_output
            result["full_output"] = f"Compiler Output:\n{compiler_output}\n\nBytecode:\n{bytecode}\n\nExecution Output:\n{execution_output}"
            result["variables"] = vm.variables if hasattr(vm, 'variables') else {}
            
        except Exception as e:
            result["success"] = False
            result["error"] = str(e)
            result["execution"] = f"Error: {str(e)}"
    else:
        # Fall back to using subprocess to run the main script
        try:
            # Create a temporary file with the code
            with tempfile.NamedTemporaryFile(mode='w', suffix='.nl', delete=False) as tmp_in:
                tmp_in.write(nl_code)
                input_file = tmp_in.name
            
            # Run the English Programming system via subprocess
            run_english_path = os.path.join(engprg_path, 'english_programming', 'run_english.py')
            cmd = [sys.executable, run_english_path, input_file, '--debug']
            
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            
            stdout_str = stdout.decode('utf-8')
            stderr_str = stderr.decode('utf-8')
            
            # Check for the compiled bytecode file
            output_file = input_file.replace('.nl', '.nlc')
            bytecode = ""
            if os.path.exists(output_file):
                with open(output_file, 'r') as f:
                    bytecode = f.read()
            
            # Extract program output (between the markers)
            program_output = ""
            if "----- Program Output -----" in stdout_str and "------------------------" in stdout_str:
                program_output = stdout_str.split("----- Program Output -----")[1].split("------------------------")[0].strip()
            
            # Populate result
            result["compilation"] = bytecode
            result["execution"] = program_output
            result["full_output"] = f"Stdout:\n{stdout_str}\n\nStderr:\n{stderr_str}\n\nBytecode:\n{bytecode}"
            
            # Clean up temporary files
            if os.path.exists(input_file):
                os.unlink(input_file)
            if os.path.exists(output_file):
                os.unlink(output_file)
                
        except Exception as e:
            result["success"] = False
            result["error"] = str(e)
            result["execution"] = f"Error: {str(e)}"
    
    return result

@app.route("/", methods=["GET", "POST"])
def index():
    result = {}
    bytecode = ""
    output = ""
    examples_json = EXAMPLES
    nlp_status = "enabled" if NLP_AVAILABLE else "disabled"
    
    if request.method == "POST":
        code = request.form.get("code", "")
        if code.strip():
            result = compile_and_run(code)
            # Extract results
            output = result.get("execution", "")
            bytecode = result.get("compilation", "")
            # Handle errors
            if not result.get("success", True):
                error = result.get("error", "Unknown error")
                output = f"Error: {error}\n{output}"
    
    return render_template("index.html", 
                          output=output, 
                          bytecode=bytecode, 
                          examples=examples_json,
                          full_output=result.get("full_output", ""),
                          nlp_status=nlp_status)

@app.route("/api/run", methods=["POST"])
def api_run():
    """API endpoint for testing with curl - handles both JSON and form data"""
    # Get the code from either JSON or form data
    if request.is_json:
        if not request.json or 'code' not in request.json:
            return jsonify({'error': 'Missing code parameter in JSON'}), 400
        code = request.json['code']
    else:
        if 'code' not in request.form:
            return jsonify({'error': 'Missing code parameter in form data'}), 400
        code = request.form['code']
        
    # Process the code
    result = compile_and_run(code)
    
    # Return the result
    return jsonify({
        'bytecode': result.get("compilation", ""),
        'output': result.get("execution", ""),
        'success': result.get("success", True),
        'variables': result.get("variables", {}),
        'nlp_enabled': NLP_AVAILABLE
    })

if __name__ == "__main__":
    print(f"Starting English Programming Web Playground")
    print(f"NLP Enhancement: {'ENABLED' if NLP_AVAILABLE else 'DISABLED'}")
    app.run(debug=True)