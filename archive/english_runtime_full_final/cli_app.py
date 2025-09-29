from nlp_compiler import compile_nl_to_nlc
from nlvm import execute_nlc
import os

def main():
    if os.path.exists("session.nlc"):
        os.remove("session.nlc")
    print("NLVM CLI. Type 'exit' to quit.")
    with open("session.nl","w") as sf: sf.write("")
    while True:
        line=input(">> ").strip()
        if line.lower()=="exit": break
        with open("session.nl","a") as sf:
            sf.write(line+"\n")
        compile_nl_to_nlc("session.nl","session.nlc")
        execute_nlc("session.nlc")

if __name__=="__main__":
    main()
