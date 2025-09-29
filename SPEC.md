# English Programming Language - Spec v1 (Draft)

## Source Grammar (informal)
- Variable assignment:
  - "create a variable called X and set it to Y"
  - "set X to Y"
- Arithmetic:
  - "add A and B and store the result in R"
  - "add N to X" (mutates X)
- Strings:
  - "concatenate A and B and store it in R"
  - "make the X uppercase and store it in R" => STRUPPER X R
  - "make the X lowercase and store it in R" => STRLOWER X R
  - "trim X and store it in R" => STRTRIM X R
- Lists/Dictionaries:
  - "create a list called L with values ..."
  - "create a dictionary called D with ..."
  - "get item at index I from L and store it in R"
  - "get D KEY and store it in R"
- Functions:
  - "define a function called F with inputs a and b: ... return X"
  - "call F with values a and b and store result in r"
- Conditionals:
  - "if X is greater than 5:" ... "else:" ...
- Files:
  - "write "TEXT" to file FILE"
  - "read file FILE and store contents in VAR"
- HTTP:
  - "http get from URL and store result in VAR"

## Bytecode Instructions (v1.1)
- SET name value
- ADD a b r
- SUB a b r
- MUL a b r
- DIV a b r
- CONCAT s1 s2 r
- LIST name items...
- DICT name key:value,...
- GET dict key r
- INDEX list idx r
- BUILTIN LENGTH var r
- BUILTIN SUM list r
- PRINT value_or_var
- FUNC_DEF name params...
- CALL name args... result
- RETURN var
- IF var1 OP var2
- ELSE / END_IF
- END_FUNC
- STRUPPER src dst
- STRLOWER src dst
- STRTRIM src dst
- HTTPGET url_or_var dst
- HTTPPOST url_or_var json_body_or_var dst [HEADER:key=value ...]
- HTTPSETHEADER key value
- JSONPARSE src dst
- JSONSTRINGIFY src dst
- JSONGET obj key dst
- JSONKEYS obj dst
- JSONVALUES obj dst
- NOW dst
- REGEXMATCH value pattern dst
- REGEXCAPTURE value pattern groupIndex dst
- REGEXREPLACE value pattern replacement dst
- DATEFORMAT source format dst

### OOP/Modules (from extensions)
- CLASS_START name parent
- CLASS_END
- METHOD_START name params...
- METHOD_END
- CREATE_OBJECT class obj args...
- CALL_METHOD obj method args...
- GET_PROPERTY obj prop
- SET_PROPERTY obj prop value
- IMPORT_MODULE name
- IMPORT_SYMBOLS module symbols
- EXPORT_SYMBOLS symbols
- MODULE_DECLARATION name

## VM Semantics (summary)
- Global env across main; functions execute with local env; RETURN returns value to caller env.
- Strings may be quoted in bytecode; VM removes quotes for SET/CONCAT handling as needed.
- HTTPGET/HTTPPOST use default headers; HTTPSETHEADER mutates defaults. POST encodes JSON by default and stores text response (or None on error).

