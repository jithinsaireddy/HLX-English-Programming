from flask import Flask, render_template, request
import sys
from io import StringIO
import contextlib
from runtime import Interpreter

app = Flask(__name__)
interpreter = Interpreter()

@app.route("/", methods=["GET", "POST"])
def index():
    output = ""
    code = ""
    if request.method == "POST":
        code = request.form["code"]
        lines = code.strip().split("\n")
        
        # Capture stdout to display print statements
        output_buffer = StringIO()
        with contextlib.redirect_stdout(output_buffer):
            try:
                interpreter.run(lines)
                captured_output = output_buffer.getvalue()
                
                # If there was any output, show it
                if captured_output:
                    output = f"Output:\n{captured_output}"
                else:
                    output = "Executed successfully. No output generated."
                    
                # Add environment display
                if interpreter.env:
                    output += "\n\nEnvironment:\n"
                    for var, value in interpreter.env.items():
                        output += f"{var} = {value}\n"
                        
            except Exception as e:
                output = f"Error: {str(e)}"
                
    return render_template("index.html", output=output, code=code)

if __name__ == "__main__":
    app.run(debug=True)