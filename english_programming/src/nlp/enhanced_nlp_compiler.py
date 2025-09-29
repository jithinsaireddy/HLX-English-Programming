"""
Enhanced NLP Compiler for English Programming
Uses spaCy for advanced natural language processing
"""
import spacy
import re
import os
import sys
from typing import List, Dict, Tuple, Optional, Any

class EnhancedNLPCompiler:
    """
    Enhanced NLP Compiler that uses spaCy for better natural language understanding
    """
    def __init__(self):
        """Initialize the NLP compiler with the spaCy model"""
        print("Loading spaCy model... (This may take a moment)")
        self.nlp = spacy.load("en_core_web_sm")
        print("spaCy model loaded successfully!")
        
        # Define common patterns for variable names and operations
        self.var_patterns = [
            r"(?:create|make|define|set up|establish) (?:a|the|an)? (?:variable|var) (?:called|named) (.+?) (?:to|as|with|equal to|equals|=) (.+)",
            r"(?:set|make|let) (.+?) (?:to|be|equal to|equals|=) (.+)",
        ]
        
        # Define operation patterns
        self.add_patterns = [
            r"(?:add|sum|combine|plus|increment) (.+?) (?:and|with|to) (.+?)(?:,| and)? (?:store|save|put|place) (?:the)? (?:result|sum|outcome|value) (?:in|into|to) (.+)",
            r"(?:add|sum|plus|increment) (.+?) (?:by|with) (.+?) (?:store|save|put) (?:in|into|to) (.+)",
            r"(?:increment|increase) (.+?) (?:by|with) (.+)"
        ]
        
        self.subtract_patterns = [
            r"(?:subtract|minus|take away|reduce) (.+?) (?:from) (.+?)(?:,| and)? (?:store|save|put) (?:the)? (?:result|outcome|value) (?:in|into|to) (.+)",
            r"(?:decrease|reduce) (.+?) (?:by|with) (.+)"
        ]
        
        self.multiply_patterns = [
            r"(?:multiply|times) (.+?) (?:by|with|and) (.+?)(?:,| and)? (?:store|save|put) (?:the)? (?:result|product|outcome|value) (?:in|into|to) (.+)",
        ]
        
        self.divide_patterns = [
            r"(?:divide) (.+?) (?:by|with) (.+?)(?:,| and)? (?:store|save|put) (?:the)? (?:result|quotient|outcome|value) (?:in|into|to) (.+)",
        ]
        
        self.print_patterns = [
            r"(?:print|show|display|output) (.+?)[\?\.\!]?$",
            r"(?:what is|what's|show me|tell me) (?:the value of)? (.+?)[\?\.\!]?$"
        ]
        
        self.file_write_patterns = [
            r"(?:write|save|put) (.+?) (?:to|into|in) (?:file|the file) (.+)",
        ]
        
        self.file_read_patterns = [
            r"(?:read|load|get) (?:file|the file) (.+?) (?:and|,)? (?:store|save|put) (?:the)? (?:content|result|data|text) (?:in|into|to) (.+)",
        ]
        
        self.conditional_patterns = [
            r"(?:if) (.+?) (?:then) (.+)",
            r"(?:check|verify) (?:if|whether) (.+)"
        ]
        
        self.loop_patterns = [
            r"(?:repeat|loop|do) (.+?) (?:times|iterations)",
            r"(?:while) (.+?) (?:do|repeat|loop|continue)",
            r"(?:for each|for every) (.+?) (?:in|from) (.+?) (?:do|execute)"
        ]
        
        self.api_patterns = [
            r"(?:get|fetch|retrieve) (?:weather|the weather) (?:for|in|at) (.+?) (?:and|,)? (?:store|save|put) (?:the|this)? (?:result|data|information) (?:in|into|to) (.+)",
        ]
    
    def extract_verb_action(self, doc) -> str:
        """Extract the main verb from a sentence to determine the action"""
        for token in doc:
            if token.pos_ == "VERB":
                return token.lemma_.lower()
        return ""
    
    def extract_variable_references(self, doc) -> List[str]:
        """Extract potential variable references from a sentence"""
        variables = []
        for chunk in doc.noun_chunks:
            # Consider noun chunks that aren't part of prepositional phrases
            if not any(token.dep_ == "pobj" for token in chunk):
                variables.append(chunk.text)
        return variables
    
    def analyze_sentence_structure(self, doc) -> Dict:
        """Analyze the sentence structure to determine command intent"""
        result = {
            'action': None,
            'subject': None,
            'object': None,
            'targets': [],
            'conditions': [],
            'values': []
        }
        
        # Find the root verb
        for token in doc:
            if token.dep_ == "ROOT" and token.pos_ == "VERB":
                result['action'] = token.lemma_
            
            # Find direct objects
            if token.dep_ == "dobj":
                result['object'] = token.text
                
            # Find subjects
            if token.dep_ == "nsubj":
                result['subject'] = token.text
                
            # Extract values (numbers, etc.)
            if token.like_num or token.pos_ == "NUM":
                result['values'].append(token.text)
                
        # Find prepositional attachments
        for token in doc:
            if token.dep_ == "pobj" and token.head.dep_ == "prep":
                prep = token.head.text
                if prep in ["to", "into", "in"]:
                    result['targets'].append(token.text)
        
        return result
    
    def extract_condition(self, text: str) -> str:
        """Extract and normalize condition expressions"""
        # Handle common condition phrasings
        text = text.lower()
        text = re.sub(r"is equal to|equals|is the same as", "==", text)
        text = re.sub(r"is not equal to|is different from|does not equal", "!=", text)
        text = re.sub(r"is greater than", ">", text)
        text = re.sub(r"is less than", "<", text)
        text = re.sub(r"is greater than or equal to", ">=", text)
        text = re.sub(r"is less than or equal to", "<=", text)
        text = re.sub(r"and", "and", text)
        text = re.sub(r"or", "or", text)
        return text
    
    def normalize_line_with_nlp(self, line: str) -> Optional[str]:
        """
        Use spaCy NLP to understand the intent of a line and convert to bytecode
        """
        # Skip comments and empty lines
        if not line or line.startswith("#"):
            return None
            
        # Process the line with spaCy
        doc = self.nlp(line)
        
        # Extract key linguistic features
        verb_action = self.extract_verb_action(doc)
        sentence_analysis = self.analyze_sentence_structure(doc)
        
        # Log the analysis for debugging
        # print(f"Line: {line}")
        # print(f"Verb: {verb_action}")
        # print(f"Analysis: {sentence_analysis}")
        
        # Try to match variable assignment patterns
        for pattern in self.var_patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                var_name = match.group(1).strip()
                value = match.group(2).strip()
                return f"SET {var_name} {value}"
        
        # Try to match addition patterns
        for pattern in self.add_patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match and len(match.groups()) >= 2:
                if len(match.groups()) == 2:  # Format: "increment x by 5"
                    var = match.group(1).strip()
                    value = match.group(2).strip()
                    return f"ADD {value} {var} {var}"
                else:  # Format: "add x and y, store in z"
                    x = match.group(1).strip()
                    y = match.group(2).strip()
                    result = match.group(3).strip()
                    return f"ADD {x} {y} {result}"
        
        # Try to match subtraction patterns
        for pattern in self.subtract_patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                if len(match.groups()) == 2:  # Format: "decrease x by 5"
                    var = match.group(1).strip()
                    value = match.group(2).strip()
                    return f"SUB {value} {var} {var}"
                else:  # Format: "subtract x from y, store in z"
                    x = match.group(1).strip()
                    y = match.group(2).strip()
                    result = match.group(3).strip()
                    return f"SUB {x} {y} {result}"
        
        # Try to match multiplication patterns
        for pattern in self.multiply_patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                x = match.group(1).strip()
                y = match.group(2).strip()
                result = match.group(3).strip()
                return f"MUL {x} {y} {result}"
        
        # Try to match division patterns
        for pattern in self.divide_patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                x = match.group(1).strip()
                y = match.group(2).strip()
                result = match.group(3).strip()
                return f"DIV {x} {y} {result}"
        
        # Try to match print patterns
        for pattern in self.print_patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                var = match.group(1).strip()
                # Check if this is a string literal (has quotes)
                if (var.startswith('"') and var.endswith('"')) or (var.startswith("'") and var.endswith("'")):
                    # It's a string literal
                    return f"PRINTSTR {var[1:-1]}"
                else:
                    # It's a variable reference
                    return f"PRINT {var}"
        
        # Try to match file write patterns
        for pattern in self.file_write_patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                content = match.group(1).strip()
                filename = match.group(2).strip()
                return f"WRITEFILE {content} {filename}"
        
        # Try to match file read patterns
        for pattern in self.file_read_patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                filename = match.group(1).strip()
                var = match.group(2).strip()
                return f"READFILE {filename} {var}"
        
        # Try to match API patterns
        for pattern in self.api_patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                location = match.group(1).strip()
                result_var = match.group(2).strip()
                return f"APICALL WEATHER {location} {result_var}"
        
        # If we reach here, we couldn't match the pattern with regex, try NLP-based understanding
        if verb_action in ["create", "set", "make", "define", "let"]:
            # Try to determine variable creation/assignment
            for entity in doc.ents:
                if entity.label_ == "CARDINAL" or entity.text.isdigit():
                    # Found a number, likely a value assignment
                    for token in doc:
                        if token.pos_ == "NOUN" and token.dep_ != "pobj":
                            return f"SET {token.text} {entity.text}"
        
        if verb_action in ["print", "show", "display", "output"]:
            # Try to find what to print
            for token in doc:
                if token.dep_ == "dobj":
                    return f"PRINT {token.text}"
        
        if verb_action in ["add", "sum", "plus", "increment"]:
            # Try NLP-based extraction for addition
            targets = sentence_analysis['targets']
            if sentence_analysis['object'] and len(targets) > 0:
                return f"ADD {sentence_analysis['object']} {targets[0]} {targets[0]}"
        
        # Nothing matched
        return None
    
    def compile(self, input_file: str, output_file: str) -> str:
        """Compile a natural language source file to bytecode"""
        print(f"Compiling {input_file} using enhanced NLP...")
        
        # Read input file
        with open(input_file, "r") as f:
            lines = [line.strip() for line in f.readlines()]
        
        # Process lines
        bytecode = []
        for i, line in enumerate(lines):
            if not line or line.startswith("#"):
                continue
                
            norm = self.normalize_line_with_nlp(line)
            if norm:
                bytecode.append(norm)
            else:
                print(f"Warning: Could not understand line {i+1}: '{line}'")
        
        # Write output
        with open(output_file, "w") as f:
            for code in bytecode:
                f.write(code + "\n")
        
        print(f"Compiled {len(bytecode)} instructions to {output_file}")
        return output_file

def main():
    """Main function to run the compiler"""
    if len(sys.argv) > 2:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
    else:
        # Default behavior
        input_file = "program_nlp.nl"
        output_file = "program_nlp.nlc"
        if len(sys.argv) > 1:
            input_file = sys.argv[1]
            output_file = os.path.splitext(input_file)[0] + ".nlc"
    
    compiler = EnhancedNLPCompiler()
    compiler.compile(input_file, output_file)

if __name__ == "__main__":
    main()
