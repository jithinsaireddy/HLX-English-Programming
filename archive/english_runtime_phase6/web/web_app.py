from flask import Flask, render_template, request
from runtime import Interpreter

app = Flask(__name__)
interpreter = Interpreter()

@app.route("/", methods=["GET", "POST"])
def index():
    output = ""
    if request.method == "POST":
        code = request.form["code"]
        lines = code.strip().split("\n")
        try:
            interpreter.run(lines)
            output = "Executed successfully. See terminal for output."
        except Exception as e:
            output = f"Error: {str(e)}"
    return render_template("index.html", output=output)

if __name__ == "__main__":
    app.run(debug=True)