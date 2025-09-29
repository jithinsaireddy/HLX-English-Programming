import os
from nlp_compiler import compile_nl_to_nlc
from nlvm import execute_nlc

def main():
    open("session.nl","w").close()
    while True:
        line = input(">> ").strip()
        if line.lower()=="exit": break
        with open("session.nl","a") as sf: sf.write(line+"\n")
        compile_nl_to_nlc("session.nl","session.nlc")
        execute_nlc("session.nlc")

if __name__=="__main__":
    main()
