from flask import Flask, render_template, request
from nlp_compiler import compile_nl_to_nlc
from nlvm import execute_nlc
import io, sys

app = Flask(__name__)

@app.route("/", methods=["GET","POST"])
def index():
    output=""
    if request.method=="POST":
        code = request.form["code"]
        with open("temp.nl","w") as f: f.write(code)
        compile_nl_to_nlc("temp.nl","temp.nlc")
        buf = io.StringIO(); old=sys.stdout; sys.stdout=buf
        execute_nlc("temp.nlc")
        sys.stdout=old; output=buf.getvalue()
    return render_template("index.html", output=output)

if __name__=="__main__":
    app.run(debug=True)
