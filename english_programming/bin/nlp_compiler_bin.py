import re
import logging
from english_programming.bin.nlbc_encoder import write_module_with_funcs, write_module, CT_INT, CT_STR

# Optional spaCy normalization for flexible English
_NLP = None
_NLP_LOADED = False
def _load_spacy():
    global _NLP
    if _NLP is not None:
        return _NLP
    try:
        import spacy
        try:
            _NLP = spacy.load('en_core_web_sm')
            logging.getLogger('epl_bin').info('spaCy loaded: en_core_web_sm')
        except Exception:
            _NLP = spacy.blank('en')
            logging.getLogger('epl_bin').info('spaCy fallback: blank("en")')
        globals()['_NLP_LOADED'] = True
    except Exception:
        _NLP = None
        logging.getLogger('epl_bin').warning('spaCy unavailable; using regex only')
    return _NLP

def _normalize_text_with_spacy(s: str) -> str:
    nlp = _load_spacy()
    if not nlp:
        return s.lower()
    doc = nlp(s)
    lemmas = ' '.join(t.lemma_.lower() or t.text.lower() for t in doc)
    if logging.getLogger('epl_bin').isEnabledFor(logging.DEBUG):
        logging.getLogger('epl_bin').debug(f"normalize: src='{s}' -> '{lemmas}'")
    return lemmas

def _canonicalize_synonyms(s: str) -> str:
    # Map common synonyms to canonical phrases the regexes expect
    s = s.lower()
    replacements = [
        ('more than or equal to', 'greater than or equal to'),
        ('at least', 'greater than or equal to'),
        ('no less than', 'greater than or equal to'),
        ('at most', 'less than or equal to'),
        ('no more than', 'less than or equal to'),
        ('more than', 'greater than'),
        ('above', 'greater than'),
        ('below', 'less than'),
        ('equals', 'is equal to'),
        ('equal to', 'is equal to'),
    ]
    for a, b in replacements:
        s = re.sub(rf"\b{re.escape(a)}\b", b, s)
    # spaCy lemma may turn 'greater' -> 'great'
    s = re.sub(r"\bgreat than\b", "greater than", s)
    return s


def compile_english_to_binary(english_lines, out_file="program.nlbc"):
    # Drop comment lines early
    english_lines = [ln for ln in english_lines if str(ln).strip() and not str(ln).strip().startswith('#')]

    constants = []    # (tag, value)
    symbols   = []    # names
    main_instrs = []  # stack VM ops (mnemonics)
    funcs = []        # list of (sym_idx, param_sym_indices, instrs)
    classes = []      # list of (class_sym_idx, field_syms, methods)

    def const_idx(tag, val):
        for i, (t, v) in enumerate(constants):
            if t == tag and v == val:
                return i
        constants.append((tag, val))
        return len(constants) - 1

    def sym_idx(name):
        if name not in symbols:
            symbols.append(name)
        return symbols.index(name)

    # Helpers for block parsing
    def indent_of(raw: str) -> int:
        return len(raw) - len(raw.lstrip(' '))

    def parse_condition(cond: str):
        # Try raw, synonyms, then spaCy-based normalization
        raw = cond.strip().rstrip(':').rstrip('.')
        candidates = []
        raw_low = raw.lower()
        candidates.append(raw_low)
        candidates.append(_canonicalize_synonyms(raw_low))
        norm_sp = _canonicalize_synonyms(_normalize_text_with_spacy(raw))
        if norm_sp and norm_sp not in candidates:
            candidates.append(norm_sp)

        def match_one(norm: str):
            # Normalize awkward lemma variants like "less than or is equal to", "be is equal to"
            norm = re.sub(r"\bor\s+is\s+equal to\b", "or equal to", norm)
            norm = re.sub(r"\b(?:is|be)\s+is\s+equal to\b", "is equal to", norm)
            # Allow RHS to be number or variable
            m = re.match(r"^(\w+)\s+(?:is|be) greater than\s+or\s+(?:is\s+)?equal to\s+(\w+|\-?\d+)$", norm)
            if m: return ('GE', m.group(1), m.group(2))
            m = re.match(r"^(\w+)\s+(?:is|be) greater than\s+(\w+|\-?\d+)$", norm)
            if m: return ('GT', m.group(1), m.group(2))
            m = re.match(r"^(\w+)\s+(?:is|be) less than\s+or\s+(?:is\s+)?equal to\s+(\w+|\-?\d+)$", norm)
            if m: return ('LE', m.group(1), m.group(2))
            m = re.match(r"^(\w+)\s+(?:is|be) less than\s+(\w+|\-?\d+)$", norm)
            if m: return ('LT', m.group(1), m.group(2))
            m = re.match(r"^(\w+)\s+(?:is|be) equal to\s+(\w+|\-?\d+)$", norm)
            if m: return ('EQ', m.group(1), m.group(2))
            m = re.match(r"^(\w+)\s*(>=|>|<=|<|==)\s*(\w+|\-?\d+)$", norm)
            if m:
                opmap = {'>':'GT','>=':'GE','<':'LT','<=':'LE','==':'EQ'}
                return (opmap[m.group(2)], m.group(1), m.group(3))
            return None

        for cand in candidates:
            res = match_one(cand)
            if res:
                return res
        raise ValueError(f"Unsupported condition: {cond}")

    def compile_condition(op, var, rhs):
        # Emit ops to evaluate condition and leave bool on stack
        def load_rhs(x):
            if isinstance(x, int) or (isinstance(x, str) and re.fullmatch(r"\-?\d+", x)):
                return [('LOAD_CONST', const_idx(CT_INT, int(x)))]
            else:
                return [('LOAD_NAME', sym_idx(str(x)))]
        if op == 'GT':
            # rhs < var
            return load_rhs(rhs) + [('LOAD_NAME', sym_idx(var)), ('LT',)]
        if op == 'GE':
            return [('LOAD_NAME', sym_idx(var))] + load_rhs(rhs) + [('GE',)]
        if op == 'LT':
            return [('LOAD_NAME', sym_idx(var))] + load_rhs(rhs) + [('LT',)]
        if op == 'LE':
            return [('LOAD_NAME', sym_idx(var))] + load_rhs(rhs) + [('LE',)]
        if op == 'EQ':
            return [('LOAD_NAME', sym_idx(var))] + load_rhs(rhs) + [('EQ',)]
        return []

    def compile_condition_expr(cond_str: str):
        # Recursive descent with parentheses and and/or
        norm = _canonicalize_synonyms(_normalize_text_with_spacy(cond_str)).strip().rstrip(':').rstrip('.')
        tokens = re.findall(r"\(|\)|>=|<=|==|>|<|\w+|\d+", norm)

        def parse_expr(i=0):  # OR-precedence
            i, ops = parse_term(i)
            while i < len(tokens) and tokens[i] == 'or':
                i += 1
                true_label = _new_label('ORTRUE')
                end_label = _new_label('OREND')
                ops += [('JUMP_IF_FALSE', true_label), ('LOAD_CONST', const_idx(CT_INT, 1)), ('JUMP', end_label), ('LABEL', true_label)]
                i, right = parse_term(i)
                ops += right + [('LABEL', end_label)]
            return i, ops

        def parse_term(i):  # AND-precedence
            i, ops = parse_factor(i)
            while i < len(tokens) and tokens[i] == 'and':
                i += 1
                false_label = _new_label('ANDFALSE')
                end_label = _new_label('ANDEND')
                ops += [('JUMP_IF_FALSE', false_label)]
                i, right = parse_factor(i)
                ops += right + [('JUMP', end_label), ('LABEL', false_label), ('LOAD_CONST', const_idx(CT_INT, 0)), ('LABEL', end_label)]
            return i, ops

        def parse_factor(i):  # '(' expr ')' | atomic
            if i < len(tokens) and tokens[i] == '(':
                i, eops = parse_expr(i + 1)
                if i < len(tokens) and tokens[i] == ')':
                    i += 1
                return i, eops
            # try to consume an atomic predicate greedily
            j = i
            acc = []
            best = None
            while j < len(tokens):
                acc.append(tokens[j]); j += 1
                try:
                    res = parse_condition(' '.join(acc))
                    best = (j, compile_condition(res[0], res[1], res[2]))
                except Exception:
                    continue
            if best is None:
                raise ValueError(f"Unsupported condition: {' '.join(tokens[i:])}")
            return best

        _, out = parse_expr(0)
        return out

    # Support colon/indent blocks inside arbitrary lists of lines
    def _compile_lines_blocks(lines):
        instrs = []
        i2 = 0
        while i2 < len(lines):
            raw2 = lines[i2]
            line2 = raw2.strip()
            low2 = line2.lower()
            # for each <var> in list <name>:
            mfe = re.match(r"^for each\s+(\w+)\s+in list\s+(\w+):$", low2)
            if mfe:
                itvar, lst = mfe.group(1), mfe.group(2)
                cur_indent = indent_of(raw2)
                body = []
                i2 += 1
                while i2 < len(lines):
                    r = lines[i2]
                    if r.strip() == '':
                        i2 += 1; continue
                    if indent_of(r) <= cur_indent:
                        break
                    body.append(r)
                    i2 += 1
                Lstart = _new_label('FOR')
                Lend = _new_label('ENDFOR')
                instrs += [('LOAD_NAME', sym_idx(lst)), ('ITER_NEW',), ('LABEL', Lstart), ('ITER_HAS_NEXT',), ('JUMP_IF_FALSE', Lend), ('ITER_NEXT',), ('STORE_NAME', sym_idx(itvar))]
                # compile body
                _, _, b_ins, _ = _compile_lines_blocks(body)
                instrs += b_ins + [('JUMP', Lstart), ('LABEL', Lend)]
                continue
            # while <cond>:
            m2 = re.match(r"while\s+(.+):$", low2)
            if m2:
                cur_indent = indent_of(raw2)
                cond_s = m2.group(1)
                body = []
                i2 += 1
                while i2 < len(lines):
                    r = lines[i2]
                    if r.strip() == '':
                        i2 += 1; continue
                    if indent_of(r) <= cur_indent:
                        break
                    body.append(r)
                    i2 += 1
                Lstart = _new_label('WH')
                Lend = _new_label('ENDWH')
                instrs += [('LABEL', Lstart)]
                instrs += compile_condition_expr(cond_s)
                instrs += [('JUMP_IF_FALSE', Lend)]
                _, _, b_ins, _ = _compile_lines_blocks(body)
                instrs += b_ins + [('JUMP', Lstart), ('LABEL', Lend)]
                continue
            # if/elif/else blocks
            m2 = re.match(r"if\s+(.+):$", low2)
            if m2:
                cur_indent = indent_of(raw2)
                cond = m2.group(1)
                then_block, elif_blocks, else_block = [], [], []
                i2 += 1
                while i2 < len(lines):
                    r = lines[i2]
                    if r.strip() == '':
                        i2 += 1; continue
                    if indent_of(r) <= cur_indent:
                        break
                    then_block.append(r)
                    i2 += 1
                while i2 < len(lines) and indent_of(lines[i2]) == cur_indent and lines[i2].strip().lower().startswith('elif '):
                    ec = lines[i2].strip()[5:].rstrip(':').strip()
                    eop, evar, enum = parse_condition(ec)
                    i2 += 1
                    blk = []
                    while i2 < len(lines):
                        r = lines[i2]
                        if r.strip() == '':
                            i2 += 1; continue
                        if indent_of(r) <= cur_indent:
                            break
                        blk.append(r)
                        i2 += 1
                    elif_blocks.append(((eop, evar, enum), blk))
                if i2 < len(lines) and lines[i2].strip().lower() == 'else:' and indent_of(lines[i2]) == cur_indent:
                    i2 += 1
                    while i2 < len(lines):
                        r = lines[i2]
                        if r.strip() == '':
                            i2 += 1; continue
                        if indent_of(r) <= cur_indent:
                            break
                        else_block.append(r)
                        i2 += 1
                Lend = _new_label('ENDIF')
                Lnext = _new_label('ELSE0')
                instrs += compile_condition_expr(cond)
                instrs += [('JUMP_IF_FALSE', Lnext)]
                _, _, t_ins, _ = _compile_lines_blocks(then_block)
                instrs += t_ins + [('JUMP', Lend), ('LABEL', Lnext)]
                for idx_e, (ct, blk) in enumerate(elif_blocks):
                    eop, evar, enum = ct
                    Lnext = _new_label(f'ELSE{idx_e+1}')
                    instrs += compile_condition(eop, evar, enum)
                    instrs += [('JUMP_IF_FALSE', Lnext)]
                    _, _, ei, _ = _compile_lines_blocks(blk)
                    instrs += ei + [('JUMP', Lend), ('LABEL', Lnext)]
                if else_block:
                    _, _, e_ins, _ = _compile_lines_blocks(else_block)
                    instrs += e_ins
                instrs += [('LABEL', Lend)]
                continue
            # fallback single-line
            lowered = _compile_stmt_with_cf(line2, constants, symbols)
            if lowered is not None:
                instrs += lowered
            else:
                _, _, ins, _ = _compile_line(line2, constants, symbols)
                instrs += ins
            i2 += 1
        return None, None, instrs, None

    # simple function parser: "Define function NAME(args)", body until "End function"
    i = 0
    while i < len(english_lines):
        raw = english_lines[i]
        line = raw.strip()
        low  = line.lower()
        if not line:
            i += 1
            continue

        # function start
        m = re.match(r"define function\s+(\w+)(?:\s*\(([^)]*)\))?\s*$", low)
        if m:
            fname = m.group(1)
            params_raw = (m.group(2) or '').strip()
            param_syms = []
            if params_raw:
                for p in [x.strip() for x in params_raw.split(',') if x.strip()]:
                    param_syms.append(sym_idx(p))
            body = []
            i += 1
            while i < len(english_lines):
                raw_line = english_lines[i]
                l2s = raw_line.strip()
                if l2s.lower() == 'end function':
                    break
                # Preserve indentation for colon/indent blocks inside functions
                body.append(raw_line)
                i += 1
            if i >= len(english_lines) or english_lines[i].strip().lower() != 'end function':
                raise ValueError("Unterminated function definition")
            # compile body recursively with colon blocks
            _, _, f_instrs, _ = _compile_lines_blocks(body)
            funcs.append((sym_idx(fname), param_syms, f_instrs))
            i += 1
            continue

        # class definition block
        class_def, new_i = _compile_class_block(english_lines, i, constants, symbols)
        if class_def is not None:
            classes.append(class_def)
            i = new_i + 1
            continue

        # try/catch block
        try_ir, new_i = _compile_try_block(english_lines, i, constants, symbols)
        if try_ir is not None:
            main_instrs += try_ir
            i = new_i + 1
            continue

        # Colon/indent If/Else blocks
        m = re.match(r"^if\s+(.+):$", low)
        if m:
            current_indent = indent_of(raw)
            cond = m.group(1)
            then_block = []
            elif_blocks = []  # list of tuples (cond_tuple, lines)
            else_block = []
            i += 1
            # collect then block
            while i < len(english_lines):
                r2 = english_lines[i]
                if r2.strip() == '':
                    i += 1; continue
                if indent_of(r2) <= current_indent:
                    break
                then_block.append(r2)
                i += 1
            # collect zero or more elif blocks
            while i < len(english_lines) and indent_of(english_lines[i]) == current_indent and english_lines[i].strip().lower().startswith('elif '):
                elif_cond_line = english_lines[i].strip()[5:].rstrip(':').strip()
                eop, evar, enum = parse_condition(elif_cond_line)
                i += 1
                block = []
                while i < len(english_lines):
                    r3 = english_lines[i]
                    if r3.strip() == '':
                        i += 1; continue
                    if indent_of(r3) <= current_indent:
                        break
                    block.append(r3)
                    i += 1
                elif_blocks.append(((eop, evar, enum), block))
            # optional else
            if i < len(english_lines) and english_lines[i].strip().lower() == 'else:' and indent_of(english_lines[i]) == current_indent:
                i += 1
                while i < len(english_lines):
                    r4 = english_lines[i]
                    if r4.strip() == '':
                        i += 1; continue
                    if indent_of(r4) <= current_indent:
                        break
                    else_block.append(r4)
                    i += 1
            # compile chain: if .. elif .. else
            end_label = _new_label('ENDIF')
            next_label = _new_label('ELSE0')
            # if
            main_instrs += compile_condition_expr(cond)
            main_instrs += [('JUMP_IF_FALSE', next_label)]
            _, _, t_ins, _ = _compile_lines_blocks(then_block)
            main_instrs += t_ins + [('JUMP', end_label), ('LABEL', next_label)]
            # elifs
            for idx_e, (ct, block) in enumerate(elif_blocks):
                eop, evar, enum = ct
                next_label = _new_label(f'ELSE{idx_e+1}')
                main_instrs += compile_condition(eop, evar, enum)
                main_instrs += [('JUMP_IF_FALSE', next_label)]
                _, _, ei, _ = _compile_lines_blocks(block)
                main_instrs += ei + [('JUMP', end_label), ('LABEL', next_label)]
            # else
            if else_block:
                _, _, e_ins, _ = _compile_lines_blocks(else_block)
                main_instrs += e_ins
            main_instrs += [('LABEL', end_label)]
            continue

        # Colon/indent While blocks
        m = re.match(r"^while\s+(.+):$", low)
        if m:
            current_indent = indent_of(raw)
            cond = m.group(1)
            body = []
            i += 1
            while i < len(english_lines):
                r2 = english_lines[i]
                if r2.strip() == '':
                    i += 1; continue
                if indent_of(r2) <= current_indent:
                    break
                body.append(r2)
                i += 1
            Lstart = _new_label('WH')
            Lend = _new_label('ENDWH')
            main_instrs += [('LABEL', Lstart)]
            main_instrs += compile_condition_expr(cond)
            main_instrs += [('JUMP_IF_FALSE', Lend)]
            _, _, b_ins, _ = _compile_lines_blocks(body)
            main_instrs += b_ins + [('JUMP', Lstart), ('LABEL', Lend)]
            continue

        # otherwise compile into main (with simple control-flow lowering)
        lowered = _compile_stmt_with_cf(line, constants, symbols)
        if lowered is not None:
            main_instrs += lowered
        else:
            _, _, instrs, _ = _compile_line(line, constants, symbols)
            main_instrs += instrs
        i += 1

    # Optional typed IR pre-verify hook (scaffold)
    try:
        from english_programming.src.compiler.typed_ir import TypedProgram, TypedValue, type_check_program
        typed_consts = []
        for tag, val in constants:
            if tag == 0:
                t = 'int'
            elif tag == 1:
                t = 'float'
            elif tag == 2:
                t = 'str'
            else:
                t = 'unknown'
            typed_consts.append(TypedValue(t, val))
        tp = TypedProgram(constants=typed_consts, symbols=symbols, main=[], functions=[], classes=[])
        type_check_program(tp)
    except Exception:
        # Typed IR is optional; failures should not block binary generation
        pass
    from english_programming.bin.nlbc_encoder import write_module_full
    write_module_full(out_file, constants, symbols, main_instrs, funcs, classes)


def _compile_lines(lines, constants, symbols):
    instrs = []
    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        lowered = _compile_stmt_with_cf(line, constants, symbols)
        if lowered is not None:
            instrs += lowered
        else:
            _, _, ins, _ = _compile_line(line, constants, symbols)
            instrs += ins
    return None, None, instrs, None


def _compile_line(line, constants, symbols):
    instrs = []
    # Skip comments
    if not line or line.strip().startswith('#'):
        return None, None, instrs, None
    low = line.lower().strip()

    # Helpers must be defined before first use inside this function
    def const_idx_local(tag, val):
        for i, (t, v) in enumerate(constants):
            if t == tag and v == val:
                return i
        constants.append((tag, val))
        return len(constants) - 1

    def sym_idx_local(name):
        if name not in symbols:
            symbols.append(name)
        return symbols.index(name)

    # Generic no-op for pure comment-only lines that slipped through
    if low == '':
        return None, None, instrs, None

    # OOP field set/get should take precedence over generic set/get
    m = re.match(r"set\s+(\w+)\.(\w+)\s+to\s+(.+)$", low)
    if m:
        obj, field, val = m.group(1), m.group(2), m.group(3).strip()
        # object first
        instrs += [('LOAD_NAME', sym_idx_local(obj))]
        # then value
        if val.isdigit():
            instrs += [('LOAD_CONST', const_idx_local(CT_INT, int(val)))]
        elif (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
            instrs += [('LOAD_CONST', const_idx_local(CT_STR, val[1:-1]))]
        else:
            instrs += [('LOAD_NAME', sym_idx_local(val))]
        instrs += [('SETFIELD', sym_idx_local(field))]
        return None, None, instrs, None
    m = re.match(r"get\s+(\w+)\.(\w+)\s+store in\s+(\w+)$", low)
    if m:
        obj, field, dst = m.group(1), m.group(2), m.group(3)
        instrs += [('LOAD_NAME', sym_idx_local(obj)), ('GETFIELD', sym_idx_local(field))]
        instrs += [('STORE_NAME', sym_idx_local(dst))]
        return None, None, instrs, None

    # (helpers moved to top of function)

    m = re.match(r"(?:set|create a variable called)\s+(\w+)\s+(?:and set it to|to|as)\s+(.+)$", low)
    if m:
        name = m.group(1)
        val  = m.group(2).strip()
        if val.isdigit():
            cidx = const_idx_local(CT_INT, int(val))
            instrs += [('LOAD_CONST', cidx)]
        elif (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
            v2 = val[1:-1]
            cidx = const_idx_local(CT_STR, v2)
            instrs += [('LOAD_CONST', cidx)]
        else:
            # treat as variable reference
            instrs += [('LOAD_NAME', sym_idx_local(val))]
        instrs += [('STORE_NAME', sym_idx_local(name))]
        return None, None, instrs, None

    m = re.match(r"add\s+(\w+)\s+and\s+(\w+|\d+)\s+and store (?:the )?(?:result|outcome)\s+in\s+(\w+)$", low)
    if m:
        a, b, dst = m.group(1), m.group(2), m.group(3)
        if a.isdigit():
            instrs += [('LOAD_CONST', const_idx_local(CT_INT, int(a)))]
        else:
            instrs += [('LOAD_NAME', sym_idx_local(a))]
        if b.isdigit():
            instrs += [('LOAD_CONST', const_idx_local(CT_INT, int(b)))]
        else:
            instrs += [('LOAD_NAME', sym_idx_local(b))]
        instrs += [('ADD',)]
        instrs += [('STORE_NAME', sym_idx_local(dst))]
        return None, None, instrs, None

    for opname, opcode in (("subtract","SUB"),("multiply","MUL"),("divide","DIV")):
        m = re.match(fr"{opname}\s+(\w+|\d+)\s+(?:and|by)\s+(\w+|\d+)\s+and store (?:the )?(?:result|outcome)\s+in\s+(\w+)$", low)
        if m:
            a, b, dst = m.group(1), m.group(2), m.group(3)
            if a.isdigit():
                instrs += [('LOAD_CONST', const_idx_local(CT_INT, int(a)))]
            else:
                instrs += [('LOAD_NAME', sym_idx_local(a))]
            if b.isdigit():
                instrs += [('LOAD_CONST', const_idx_local(CT_INT, int(b)))]
            else:
                instrs += [('LOAD_NAME', sym_idx_local(b))]
            instrs += [(opcode,)]
            instrs += [('STORE_NAME', sym_idx_local(dst))]
            return None, None, instrs, None

    m = re.match(r"concatenate\s+(.+)\s+and\s+(.+)\s+and store in\s+(\w+)$", low)
    if m:
        a, b, dst = m.group(1).strip(), m.group(2).strip(), m.group(3)
        for tok in (a, b):
            if tok.isdigit():
                instrs += [('LOAD_CONST', const_idx_local(CT_INT, int(tok)))]
            elif (tok.startswith('"') and tok.endswith('"')) or (tok.startswith("'") and tok.endswith("'")):
                instrs += [('LOAD_CONST', const_idx_local(CT_STR, tok[1:-1]))]
            else:
                instrs += [('LOAD_NAME', sym_idx_local(tok))]
        instrs += [('CONCAT',)]
        if dst not in symbols:
            symbols.append(dst)
        instrs += [('STORE_NAME', sym_idx_local(dst))]
        return None, None, instrs, None

    # trim <name> and store it in <dst>
    m = re.match(r"trim\s+(\w+)\s+and store (?:it )?in\s+(\w+)$", low)
    if m:
        src, dst = m.group(1), m.group(2)
        instrs += [('LOAD_NAME', sym_idx_local(src)), ('STRTRIM',)]
        if dst not in symbols:
            symbols.append(dst)
        instrs += [('STORE_NAME', sym_idx_local(dst))]
        return None, None, instrs, None

    # make the <name> uppercase and store it in <dst>
    m = re.match(r"make\s+the\s+(\w+)\s+uppercase\s+and store (?:it )?in\s+(\w+)$", low)
    if m:
        src, dst = m.group(1), m.group(2)
        instrs += [('LOAD_NAME', sym_idx_local(src)), ('STRUPPER',)]
        if dst not in symbols:
            symbols.append(dst)
        instrs += [('STORE_NAME', sym_idx_local(dst))]
        return None, None, instrs, None

    m = re.match(r"length of\s+(\w+)\s+store in\s+(\w+)$", low)
    if m:
        name, dst = m.group(1), m.group(2)
        instrs += [('LOAD_NAME', sym_idx_local(name)), ('LEN',)]
        if dst not in symbols:
            symbols.append(dst)
        instrs += [('STORE_NAME', sym_idx_local(dst))]
        return None, None, instrs, None

    for pat, opcode in ((r"is equal to","EQ"),(r"is less than or equal to","LE"),(r"is greater than or equal to","GE")):
        m = re.match(fr"if\s+(\w+)\s+{pat}\s+(\d+)\s+then print\s+(\w+)$", low)
        if m:
            var, num, toprint = m.group(1), int(m.group(2)), m.group(3)
            end = _new_label('ENDIF')
            if var not in symbols:
                symbols.append(var)
            if toprint not in symbols:
                symbols.append(toprint)
            return [
                ('LOAD_NAME', sym_idx_local(var)),
                ('LOAD_CONST', const_idx_local(CT_INT, num)),
                (opcode,),
                ('JUMP_IF_FALSE', end),
                ('LOAD_NAME', sym_idx_local(toprint)),
                ('PRINT',),
                ('LABEL', end),
            ]

    # CRUD
    m = re.match(r"write file\s+(\w+)\s+with content\s+(.+)$", low)
    if m:
        fname, content = m.group(1), m.group(2)
        if (content.startswith('"') and content.endswith('"')) or (content.startswith("'") and content.endswith("'")):
            content = content[1:-1]
        instrs += [('LOAD_CONST', const_idx_local(CT_STR, content)), ('LOAD_NAME', sym_idx_local(fname)), ('WRITEFILE',)]
        return None, None, instrs, None
    m = re.match(r"append to file\s+(\w+)\s+content\s+(.+)$", low)
    if m:
        fname, content = m.group(1), m.group(2)
        if (content.startswith('"') and content.endswith('"')) or (content.startswith("'") and content.endswith("'")):
            content = content[1:-1]
        instrs += [('LOAD_CONST', const_idx_local(CT_STR, content)), ('LOAD_NAME', sym_idx_local(fname)), ('APPENDFILE',)]
        return None, None, instrs, None
    m = re.match(r"read file\s+(\w+)\s+store in\s+(\w+)$", low)
    if m:
        fname, dst = m.group(1), m.group(2)
        instrs += [('LOAD_NAME', sym_idx_local(fname)), ('READFILE',)]
        if dst not in symbols:
            symbols.append(dst)
        instrs += [('STORE_NAME', sym_idx_local(dst))]
        return None, None, instrs, None
    m = re.match(r"delete file\s+(\w+)$", low)
    if m:
        fname = m.group(1)
        instrs += [('LOAD_NAME', sym_idx_local(fname)), ('DELETEFILE',)]
        return None, None, instrs, None

    # HTTP GET/POST
    m = re.match(r"http get\s+(.+)\s+store in\s+(\w+)$", low)
    if m:
        url, dst = m.group(1).strip(), m.group(2)
        if (url.startswith('"') and url.endswith('"')) or (url.startswith("'") and url.endswith("'")):
            url = url[1:-1]
        instrs += [('LOAD_CONST', const_idx_local(CT_STR, url)), ('HTTPGET',)]
        if dst not in symbols:
            symbols.append(dst)
        instrs += [('STORE_NAME', sym_idx_local(dst))]
        return None, None, instrs, None

    # Async forms: async read file <name> await store in <dst>
    m = re.match(r"async read file\s+(\w+)\s+await store in\s+(\w+)$", low)
    if m:
        fname, dst = m.group(1), m.group(2)
        instrs += [('LOAD_NAME', sym_idx_local(fname)), ('ASYNC_READFILE',), ('AWAIT',)]
        if dst not in symbols:
            symbols.append(dst)
        instrs += [('STORE_NAME', sym_idx_local(dst))]
        return None, None, instrs, None
    m = re.match(r"async http get\s+(.+)\s+await store in\s+(\w+)$", low)
    if m:
        url, dst = m.group(1).strip(), m.group(2)
        if (url.startswith('"') and url.endswith('"')) or (url.startswith("'") and url.endswith("'")):
            url = url[1:-1]
            instrs += [('LOAD_CONST', const_idx_local(CT_STR, url))]
        else:
            instrs += [('LOAD_NAME', sym_idx_local(url))]
        instrs += [('ASYNC_HTTPGET',), ('AWAIT',)]
        if dst not in symbols:
            symbols.append(dst)
        instrs += [('STORE_NAME', sym_idx_local(dst))]
        return None, None, instrs, None
    m = re.match(r"http post\s+(.+)\s+with body\s+(.+)\s+store in\s+(\w+)$", low)
    if m:
        url, body, dst = m.group(1).strip(), m.group(2).strip(), m.group(3)
        if (url.startswith('"') and url.endswith('"')) or (url.startswith("'") and url.endswith("'")):
            url = url[1:-1]
        if (body.startswith('"') and body.endswith('"')) or (body.startswith("'") and body.endswith("'")):
            body = body[1:-1]
        instrs += [('LOAD_CONST', const_idx_local(CT_STR, body)), ('LOAD_CONST', const_idx_local(CT_STR, url)), ('HTTPPOST',)]
        if dst not in symbols:
            symbols.append(dst)
        instrs += [('STORE_NAME', sym_idx_local(dst))]
        return None, None, instrs, None

    # IMPORTURL (local file or http url) -> store content
    m = re.match(r"import from url\s+(.+)\s+store in\s+(\w+)$", low)
    if m:
        url, dst = m.group(1).strip(), m.group(2)
        if (url.startswith('"') and url.endswith('"')) or (url.startswith("'") and url.endswith("'")):
            url = url[1:-1]
        instrs += [('LOAD_CONST', const_idx_local(CT_STR, url)), ('IMPORTURL',)]
        if dst not in symbols:
            symbols.append(dst)
        instrs += [('STORE_NAME', sym_idx_local(dst))]
        return None, None, instrs, None

    m = re.match(r"(?:print|show|display)\s+(.+)$", low)
    if m:
        what = m.group(1).strip()
        if what.isdigit():
            instrs += [('LOAD_CONST', const_idx_local(CT_INT, int(what)))]
        else:
            if (what.startswith('"') and what.endswith('"')) or (what.startswith("'") and what.endswith("'")):
                instrs += [('LOAD_CONST', const_idx_local(CT_STR, what[1:-1]))]
            else:
                instrs += [('LOAD_NAME', sym_idx_local(what))]
        instrs += [('PRINT',)]
        return None, None, instrs, None

    m = re.match(r"create a list called\s+(\w+)\s+with values\s+(.+)$", low)
    if m:
        name = m.group(1)
        values = [v.strip() for v in m.group(2).split(',')]
        count = 0
        for v in values:
            if v.isdigit():
                instrs += [('LOAD_CONST', const_idx_local(CT_INT, int(v)))]
            else:
                instrs += [('LOAD_NAME', sym_idx_local(v))]
            count += 1
        instrs += [('BUILD_LIST', count), ('STORE_NAME', sym_idx_local(name))]
        return None, None, instrs, None

    # create a list called <name> (empty)
    m = re.match(r"create a list called\s+(\w+)$", low)
    if m:
        name = m.group(1)
        instrs += [('BUILD_LIST', 0), ('STORE_NAME', sym_idx_local(name))]
        return None, None, instrs, None

    # create a list called <name> (empty)
    m = re.match(r"create a list called\s+(\w+)$", low)
    if m:
        name = m.group(1)
        instrs += [('BUILD_LIST', 0), ('STORE_NAME', sym_idx_local(name))]
        return None, None, instrs, None

    # create a map called <name>
    m = re.match(r"create a map called\s+(\w+)$", low)
    if m:
        name = m.group(1)
        instrs += [('BUILD_MAP', 0), ('STORE_NAME', sym_idx_local(name))]
        return None, None, instrs, None

    # map put <map> <key> <val> store in <map>
    m = re.match(r"map put\s+(\w+)\s+(.+)\s+(.+)\s+store in\s+(\w+)$", low)
    if m:
        mp, key, val, dst = m.group(1), m.group(2).strip(), m.group(3).strip(), m.group(4)
        instrs += [('LOAD_NAME', sym_idx_local(mp))]
        # key
        if key.isdigit():
            instrs += [('LOAD_CONST', const_idx_local(CT_INT, int(key)))]
        elif (key.startswith("'") and key.endswith("'")) or (key.startswith('"') and key.endswith('"')):
            instrs += [('LOAD_CONST', const_idx_local(CT_STR, key[1:-1]))]
        else:
            instrs += [('LOAD_NAME', sym_idx_local(key))]
        # value
        if val.isdigit():
            instrs += [('LOAD_CONST', const_idx_local(CT_INT, int(val)))]
        elif (val.startswith("'") and val.endswith("'")) or (val.startswith('"') and val.endswith('"')):
            instrs += [('LOAD_CONST', const_idx_local(CT_STR, val[1:-1]))]
        else:
            instrs += [('LOAD_NAME', sym_idx_local(val))]
        instrs += [('MAP_PUT',)]
        instrs += [('STORE_NAME', sym_idx_local(dst))]
        return None, None, instrs, None

    # map get <map> <key> store in <dst>
    m = re.match(r"map get\s+(\w+)\s+(.+)\s+store in\s+(\w+)$", low)
    if m:
        mp, key, dst = m.group(1), m.group(2).strip(), m.group(3)
        instrs += [('LOAD_NAME', sym_idx_local(mp))]
        if key.isdigit():
            instrs += [('LOAD_CONST', const_idx_local(CT_INT, int(key)))]
        elif (key.startswith("'") and key.endswith("'")) or (key.startswith('"') and key.endswith('"')):
            instrs += [('LOAD_CONST', const_idx_local(CT_STR, key[1:-1]))]
        else:
            instrs += [('LOAD_NAME', sym_idx_local(key))]
        instrs += [('MAP_GET',)]
        instrs += [('STORE_NAME', sym_idx_local(dst))]
        return None, None, instrs, None

    # append <val> to list <name> store in <name>
    m = re.match(r"append\s+(.+)\s+to list\s+(\w+)\s+store in\s+(\w+)$", low)
    if m:
        val, name, dst = m.group(1).strip(), m.group(2), m.group(3)
        instrs += [('LOAD_NAME', sym_idx_local(name))]
        if val.isdigit():
            instrs += [('LOAD_CONST', const_idx_local(CT_INT, int(val)))]
        elif (val.startswith("'") and val.endswith("'")) or (val.startswith('"') and val.endswith('"')):
            instrs += [('LOAD_CONST', const_idx_local(CT_STR, val[1:-1]))]
        else:
            instrs += [('LOAD_NAME', sym_idx_local(val))]
        instrs += [('LIST_APPEND',)]
        instrs += [('STORE_NAME', sym_idx_local(dst))]
        return None, None, instrs, None

    # pop from list <name> store in <dst>
    m = re.match(r"pop from list\s+(\w+)\s+store in\s+(\w+)$", low)
    if m:
        name, dst = m.group(1), m.group(2)
        instrs += [('LOAD_NAME', sym_idx_local(name)), ('LIST_POP',)]
        instrs += [('STORE_NAME', sym_idx_local(dst))]
        return None, None, instrs, None

    # get <name> store in <dst>
    m = re.match(r"get\s+(\w+)\s+store in\s+(\w+)$", low)
    if m:
        src, dst = m.group(1), m.group(2)
        instrs += [('LOAD_NAME', sym_idx_local(src)), ('STORE_NAME', sym_idx_local(dst))]
        return None, None, instrs, None

    # simple numeric comparisons for if/while: "if x is equal to 0:" handled in parse_condition_expr

    # Sets
    m = re.match(r"create a set called\s+(\w+)$", low)
    if m:
        name = m.group(1)
        instrs += [('SET_NEW',)]
        instrs += [('STORE_NAME', sym_idx_local(name))]
        return None, None, instrs, None
    m = re.match(r"add\s+(\w+|\d+|'[^']*'|\"[^\"]*\")\s+to set\s+(\w+)$", low)
    if m:
        val, name = m.group(1), m.group(2)
        # push set first, then value (SET_ADD pops value then set)
        instrs += [('LOAD_NAME', sym_idx_local(name))]
        if val.isdigit():
            instrs += [('LOAD_CONST', const_idx_local(CT_INT, int(val)))]
        elif (val.startswith("'") and val.endswith("'")) or (val.startswith('"') and val.endswith('"')):
            instrs += [('LOAD_CONST', const_idx_local(CT_STR, val[1:-1]))]
        else:
            instrs += [('LOAD_NAME', sym_idx_local(val))]
        instrs += [('SET_ADD',)]
        return None, None, instrs, None
    m = re.match(r"check if\s+(\w+|\d+|'[^']*'|\"[^\"]*\")\s+in set\s+(\w+)\s+store in\s+(\w+)$", low)
    if m:
        val, name, dst = m.group(1), m.group(2), m.group(3)
        # push set first, then value (SET_CONTAINS pops value then set)
        instrs += [('LOAD_NAME', sym_idx_local(name))]
        if val.isdigit():
            instrs += [('LOAD_CONST', const_idx_local(CT_INT, int(val)))]
        elif (val.startswith("'") and val.endswith("'")) or (val.startswith('"') and val.endswith('"')):
            instrs += [('LOAD_CONST', const_idx_local(CT_STR, val[1:-1]))]
        else:
            instrs += [('LOAD_NAME', sym_idx_local(val))]
        instrs += [('SET_CONTAINS',)]
        if dst not in symbols:
            symbols.append(dst)
        instrs += [('STORE_NAME', sym_idx_local(dst))]
        return None, None, instrs, None

    # CSV/YAML
    m = re.match(r"parse csv\s+(\w+)\s+store in\s+(\w+)$", low)
    if m:
        src, dst = m.group(1), m.group(2)
        instrs += [('LOAD_NAME', sym_idx_local(src)), ('CSV_PARSE',)]
        instrs += [('STORE_NAME', sym_idx_local(dst))]
        return None, None, instrs, None

    # Pattern matching: case <var> of <value>: set dst to <x> else set dst to <y>
    m = re.match(r"case\s+(\w+)\s+of\s+('.*?'|\d+)\s*:\s*set\s+(\w+)\s+to\s+('.*?'|\d+)\s+(?:elif\s+('.*?'|\d+)\s*:\s*set\s+(\w+)\s+to\s+('.*?'|\d+)\s+)?else\s+set\s+(\w+)\s+to\s+('.*?'|\d+)$", low)
    if m:
        var, val, dst1, x = m.group(1), m.group(2), m.group(3), m.group(4)
        elif_val, elif_dst, elif_x = m.group(5), m.group(6), m.group(7)
        dst2, y = m.group(8), m.group(9)
        elif_label = _new_label('ELIF') if elif_val else None
        else_label = _new_label('ELSE')
        end_label = _new_label('ENDCASE')
        # LOAD var and const, EQ, JUMP_IF_FALSE else
        instrs += [('LOAD_NAME', sym_idx_local(var))]
        if val.isdigit():
            instrs += [('LOAD_CONST', const_idx_local(CT_INT, int(val)))]
        else:
            instrs += [('LOAD_CONST', const_idx_local(CT_STR, val.strip("'")))]
        instrs += [('EQ',), ('JUMP_IF_FALSE', elif_label or else_label)]
        # then branch
        if x.isdigit():
            instrs += [('LOAD_CONST', const_idx_local(CT_INT, int(x)))]
        else:
            instrs += [('LOAD_CONST', const_idx_local(CT_STR, x.strip("'")))]
        instrs += [('STORE_NAME', sym_idx_local(dst1)), ('JUMP', end_label)]
        # optional elif branch
        if elif_val:
            instrs += [('LABEL', elif_label), ('LOAD_NAME', sym_idx_local(var))]
            if elif_val.isdigit():
                instrs += [('LOAD_CONST', const_idx_local(CT_INT, int(elif_val)))]
            else:
                instrs += [('LOAD_CONST', const_idx_local(CT_STR, elif_val.strip("'")))]
            instrs += [('EQ',), ('JUMP_IF_FALSE', else_label)]
            if elif_x.isdigit():
                instrs += [('LOAD_CONST', const_idx_local(CT_INT, int(elif_x)))]
            else:
                instrs += [('LOAD_CONST', const_idx_local(CT_STR, elif_x.strip("'")))]
            instrs += [('STORE_NAME', sym_idx_local(elif_dst)), ('JUMP', end_label)]
        # else branch
        instrs += [('LABEL', else_label)]
        if y.isdigit():
            instrs += [('LOAD_CONST', const_idx_local(CT_INT, int(y)))]
        else:
            instrs += [('LOAD_CONST', const_idx_local(CT_STR, y.strip("'")))]
        instrs += [('STORE_NAME', sym_idx_local(dst2)), ('LABEL', end_label)]
        return None, None, instrs, None
    m = re.match(r"stringify csv\s+(\w+)\s+store in\s+(\w+)$", low)
    if m:
        src, dst = m.group(1), m.group(2)
        instrs += [('LOAD_NAME', sym_idx_local(src)), ('CSV_STRINGIFY',)]
        instrs += [('STORE_NAME', sym_idx_local(dst))]
        return None, None, instrs, None
    m = re.match(r"parse yaml\s+(\w+)\s+store in\s+(\w+)$", low)
    if m:
        src, dst = m.group(1), m.group(2)
        instrs += [('LOAD_NAME', sym_idx_local(src)), ('YAML_PARSE',)]
        instrs += [('STORE_NAME', sym_idx_local(dst))]
        return None, None, instrs, None
    m = re.match(r"stringify yaml\s+(\w+)\s+store in\s+(\w+)$", low)
    if m:
        src, dst = m.group(1), m.group(2)
        instrs += [('LOAD_NAME', sym_idx_local(src)), ('YAML_STRINGIFY',)]
        instrs += [('STORE_NAME', sym_idx_local(dst))]
        return None, None, instrs, None

    # For-each loop: For each <var> in list <name> do <stmt>
    m = re.match(r"for each\s+(\w+)\s+in list\s+(\w+)\s+do\s+(.+)$", low)
    if m:
        itvar, lst, stmt = m.group(1), m.group(2), m.group(3)
        start = _new_label('FOR')
        end = _new_label('ENDFOR')
        # iterator setup
        instrs += [('LOAD_NAME', sym_idx_local(lst)), ('ITER_NEW',), ('LABEL', start), ('ITER_HAS_NEXT',), ('JUMP_IF_FALSE', end), ('ITER_NEXT',), ('STORE_NAME', sym_idx_local(itvar))]
        # compile the single statement body
        lowered = _compile_stmt_with_cf(stmt, constants, symbols)
        if lowered is not None:
            instrs += lowered
        else:
            _, _, ins, _ = _compile_line(stmt, constants, symbols)
            instrs += ins
        instrs += [('JUMP', start), ('LABEL', end)]
        return None, None, instrs, None

    # For-each block: For each <var> in list <name>:
    m = re.match(r"^for each\s+(\w+)\s+in list\s+(\w+):$", low)
    if m:
        itvar, lst = m.group(1), m.group(2)
        cur_indent = 0  # caller guarantees correct slicing; handled in _compile_lines_blocks
        # This branch is only used from _compile_lines_blocks, so just return a marker
        # and let the block parser handle body collection.
        instrs += [('__FOREACH_BLOCK_START__', itvar, lst)]
        return None, None, instrs, None

    # For each over set: For each v in set s do <stmt>
    m = re.match(r"for each\s+(\w+)\s+in set\s+(\w+)\s+do\s+(.+)$", low)
    if m:
        itvar, st, stmt = m.group(1), m.group(2), m.group(3)
        start = _new_label('FORSET')
        end = _new_label('ENDFORSET')
        instrs += [('LOAD_NAME', sym_idx_local(st)), ('ITER_NEW',), ('LABEL', start), ('ITER_HAS_NEXT',), ('JUMP_IF_FALSE', end), ('ITER_NEXT',), ('STORE_NAME', sym_idx_local(itvar))]
        lowered = _compile_stmt_with_cf(stmt, constants, symbols)
        if lowered is not None:
            instrs += lowered
        else:
            _, _, ins, _ = _compile_line(stmt, constants, symbols)
            instrs += ins
        instrs += [('JUMP', start), ('LABEL', end)]
        return None, None, instrs, None

    m = re.match(r"get item at index\s+(\w+|\d+)\s+from list\s+(\w+)\s+and\s+(?:store in\s+(\w+)|print it)$", low)
    if m:
        idx, lst, dst = m.group(1), m.group(2), m.group(3)
        instrs += [('LOAD_NAME', sym_idx_local(lst))]
        if idx.isdigit():
            instrs += [('LOAD_CONST', const_idx_local(CT_INT, int(idx)))]
        else:
            instrs += [('LOAD_NAME', sym_idx_local(idx))]
        instrs += [('INDEX',)]
        if dst:
            instrs += [('STORE_NAME', sym_idx_local(dst))]
        else:
            instrs += [('PRINT',)]
        return None, None, instrs, None

    # return <name|int>
    m = re.match(r"return\s+(\w+|\d+)$", low)
    if m:
        what = m.group(1)
        if what.isdigit():
            instrs += [('LOAD_CONST', const_idx_local(CT_INT, int(what)))]
        else:
            instrs += [('LOAD_NAME', sym_idx_local(what))]
        instrs += [('RETURN',)]
        return None, None, instrs, None

    # OOP usage lowering (simple forms)
    # new <ClassName> store in <var>
    m = re.match(r"new\s+(\w+)\s+store in\s+(\w+)$", line, re.I)
    if m:
        # preserve class name case from source to match class registry
        cname, dst = m.group(1), m.group(2)
        instrs += [('NEW', _ensure_sym(symbols, cname))]
        instrs += [('STORE_NAME', _ensure_sym(symbols, dst))]
        return None, None, instrs, None
    # new <ClassName> with args a, b store in var
    m = re.match(r"new\s+(\w+)\s+with args\s+([^)]*)\s+store in\s+(\w+)$", line, re.I)
    if m:
        cname, args_s, dst = m.group(1), m.group(2).strip(), m.group(3)
        instrs += [('NEW', _ensure_sym(symbols, cname))]
        # call constructor __init__(self, ...)
        argc = 0
        if args_s:
            for a in [x.strip() for x in args_s.split(',') if x.strip()]:
                if a.isdigit():
                    instrs += [('LOAD_CONST', _const_index(constants, CT_INT, int(a)))]
                elif (a.startswith("'") and a.endswith("'")) or (a.startswith('"') and a.endswith('"')):
                    instrs += [('LOAD_CONST', _const_index(constants, CT_STR, a[1:-1]))]
                else:
                    instrs += [('LOAD_NAME', _ensure_sym(symbols, a))]
                argc += 1
        instrs += [('CALL_METHOD', _ensure_sym(symbols, '__init__'), argc)]
        instrs += [('STORE_NAME', _ensure_sym(symbols, dst))]
        return None, None, instrs, None
    # set <obj>.<field> to <value>
    m = re.match(r"set\s+(\w+)\.(\w+)\s+to\s+(\w+|\d+|'[^']*'|\"[^\"]*\")$", line, re.I)
    if m:
        oname, field, val = m.group(1), m.group(2), m.group(3)
        instrs += [('LOAD_NAME', _ensure_sym(symbols, oname))]
        if val.isdigit():
            instrs += [('LOAD_CONST', _const_index(constants, CT_INT, int(val)))]
        elif (val.startswith("'") and val.endswith("'")) or (val.startswith('"') and val.endswith('"')):
            instrs += [('LOAD_CONST', _const_index(constants, CT_STR, val[1:-1]))]
        else:
            instrs += [('LOAD_NAME', _ensure_sym(symbols, val))]
        instrs += [('SETFIELD', _ensure_sym(symbols, field))]
        return None, None, instrs, None
    # get <obj>.<field> store in <var>
    m = re.match(r"get\s+(\w+)\.(\w+)\s+store in\s+(\w+)$", line, re.I)
    if m:
        oname, field, dst = m.group(1), m.group(2), m.group(3)
        instrs += [('LOAD_NAME', _ensure_sym(symbols, oname)), ('GETFIELD', _ensure_sym(symbols, field))]
        instrs += [('STORE_NAME', _ensure_sym(symbols, dst))]
        return None, None, instrs, None
    # call method <obj>.<method>(args...) store in <dst>
    m = re.match(r"call method\s+(\w+)\.(\w+)\(([^)]*)\)\s+store in\s+(\w+)$", line, re.I)
    if m:
        oname, mname, args_s, dst = m.group(1), m.group(2), m.group(3).strip(), m.group(4)
        instrs += [('LOAD_NAME', _ensure_sym(symbols, oname))]
        argc = 0
        if args_s:
            for a in [x.strip() for x in args_s.split(',') if x.strip()]:
                if a.isdigit():
                    instrs += [('LOAD_CONST', _const_index(constants, CT_INT, int(a)))]
                elif (a.startswith("'") and a.endswith("'")) or (a.startswith('"') and a.endswith('"')):
                    instrs += [('LOAD_CONST', _const_index(constants, CT_STR, a[1:-1]))]
                else:
                    instrs += [('LOAD_NAME', _ensure_sym(symbols, a))]
                argc += 1
        instrs += [('CALL_METHOD', _ensure_sym(symbols, mname), argc)]
        instrs += [('STORE_NAME', _ensure_sym(symbols, dst))]
        return None, None, instrs, None

    # (control flow constructs reserved for future pass)

    raise ValueError(f"Don't understand: {line}")


_label_counter = 0


def _new_label(prefix='L'):
    global _label_counter
    _label_counter += 1
    return f"{prefix}{_label_counter}"


def _compile_stmt_with_cf(line, constants, symbols):
    low = line.lower().strip()
    # if <name> is less than <num> then print <name>
    m = re.match(r"if\s+(\w+)\s+is less than\s+(\d+)\s+then print\s+(\w+)$", low)
    if m:
        var, num, toprint = m.group(1), int(m.group(2)), m.group(3)
        end = _new_label('ENDIF')
        return [
            ('LOAD_NAME', symbols.index(var) if var in symbols else symbols.append(var) or symbols.index(var)),
            ('LOAD_CONST', _const_index(constants, CT_INT, num)),
            ('LT',),
            ('JUMP_IF_FALSE', end),
            ('LOAD_NAME', symbols.index(toprint) if toprint in symbols else symbols.append(toprint) or symbols.index(toprint)),
            ('PRINT',),
            ('LABEL', end),
        ]
    # while <name> is less than <num> do print <name>
    m = re.match(r"while\s+(\w+)\s+is less than\s+(\d+)\s+do print\s+(\w+)$", low)
    if m:
        var, num, toprint = m.group(1), int(m.group(2)), m.group(3)
        start = _new_label('WH')
        end = _new_label('ENDWH')
        return [
            ('LABEL', start),
            ('LOAD_NAME', symbols.index(var) if var in symbols else symbols.append(var) or symbols.index(var)),
            ('LOAD_CONST', _const_index(constants, CT_INT, num)),
            ('LT',),
            ('JUMP_IF_FALSE', end),
            ('LOAD_NAME', symbols.index(toprint) if toprint in symbols else symbols.append(toprint) or symbols.index(toprint)),
            ('PRINT',),
            ('JUMP', start),
            ('LABEL', end),
        ]
    # if <name> is less than <num> then set <var> to <int> else set <var> to <int>
    # if <name> is greater than <num>:\n  set dst to "..." else: set dst to "..."
    m = re.match(r"if\s+(\w+)\s+is greater than\s+(\d+):$", low)
    if m:
        var, num = m.group(1), int(m.group(2))
        else_label = _new_label('ELSE')
        end = _new_label('ENDIF')
        ops = [
            ('LOAD_NAME', symbols.index(var) if var in symbols else symbols.append(var) or symbols.index(var)),
            ('LOAD_CONST', _const_index(constants, CT_INT, num)),
            ('LT',),  # a < b; we want a > b → not(a <= b). Simpler: compute (b < a)
        ]
        # Replace with b < a
        ops = [
            ('LOAD_CONST', _const_index(constants, CT_INT, num)),
            ('LOAD_NAME', symbols.index(var) if var in symbols else symbols.append(var) or symbols.index(var)),
            ('LT',),
        ]
        ops += [('JUMP_IF_FALSE', else_label)]
        return ops

    # handle indented next lines: "set dst to 'Adult'" and else block
    m = re.match(r"set\s+(\w+)\s+to\s+(\"[^\"]*\"|'[^']*'|\d+)$", low)
    if m:
        dst, val = m.group(1), m.group(2)
        if val.isdigit():
            ops = [('LOAD_CONST', _const_index(constants, CT_INT, int(val)))]
        else:
            ops = [('LOAD_CONST', _const_index(constants, CT_STR, val.strip('"').strip("'")))]
        if dst not in symbols:
            symbols.append(dst)
        ops += [('STORE_NAME', symbols.index(dst))]
        return ops

    m = re.match(r"if\s+(\w+)\s+is less than\s+(\d+)\s+then set\s+(\w+)\s+to\s+(\d+)\s+else set\s+(\w+)\s+to\s+(\d+)$", low)
    if m:
        var, num, dst1, val1, dst2, val2 = m.group(1), int(m.group(2)), m.group(3), int(m.group(4)), m.group(5), int(m.group(6))
        else_label = _new_label('ELSE')
        end = _new_label('ENDIF')
        # ensure dst names exist in symbols
        if dst1 not in symbols:
            symbols.append(dst1)
        if dst2 not in symbols:
            symbols.append(dst2)
        return [
            ('LOAD_NAME', symbols.index(var) if var in symbols else symbols.append(var) or symbols.index(var)),
            ('LOAD_CONST', _const_index(constants, CT_INT, num)),
            ('LT',),
            ('JUMP_IF_FALSE', else_label),
            ('LOAD_CONST', _const_index(constants, CT_INT, val1)),
            ('STORE_NAME', symbols.index(dst1)),
            ('JUMP', end),
            ('LABEL', else_label),
            ('LOAD_CONST', _const_index(constants, CT_INT, val2)),
            ('STORE_NAME', symbols.index(dst2)),
            ('LABEL', end),
        ]

    # if <name> is greater than <num> then set <dst1> to <val1> else set <dst2> to <val2>
    m = re.match(r"if\s+(\w+)\s+is greater than\s+(\d+)\s+then set\s+(\w+)\s+to\s+(\"[^\"]*\"|'[^']*'|\d+)\s+else set\s+(\w+)\s+to\s+(\"[^\"]*\"|'[^']*'|\d+)$", low)
    if m:
        var, num, dst1, val1, dst2, val2 = m.group(1), int(m.group(2)), m.group(3), m.group(4), m.group(5), m.group(6)
        else_label = _new_label('ELSE')
        end = _new_label('ENDIF')
        if dst1 not in symbols:
            symbols.append(dst1)
        if dst2 not in symbols:
            symbols.append(dst2)
        ops = [
            # compute (num < var) to represent var > num
            ('LOAD_CONST', _const_index(constants, CT_INT, num)),
            ('LOAD_NAME', symbols.index(var) if var in symbols else symbols.append(var) or symbols.index(var)),
            ('LT',),
            ('JUMP_IF_FALSE', else_label),
        ]
        # then branch
        if val1.isdigit():
            ops += [('LOAD_CONST', _const_index(constants, CT_INT, int(val1)))]
        else:
            ops += [('LOAD_CONST', _const_index(constants, CT_STR, val1.strip('"').strip("'")))]
        ops += [('STORE_NAME', symbols.index(dst1)), ('JUMP', end), ('LABEL', else_label)]
        # else branch
        if val2.isdigit():
            ops += [('LOAD_CONST', _const_index(constants, CT_INT, int(val2)))]
        else:
            ops += [('LOAD_CONST', _const_index(constants, CT_STR, val2.strip('"').strip("'")))]
        ops += [('STORE_NAME', symbols.index(dst2)), ('LABEL', end)]
        return ops

    # call function <name> with <args> and store in <dst>
    m = re.match(r"call function\s+(\w+)\s+with\s+(.+)\s+and store in\s+(\w+)$", low)
    if m:
        fname = m.group(1)
        args_s = m.group(2)
        dst = m.group(3)
        if dst not in symbols:
            symbols.append(dst)
        argc = 0
        for a in [x.strip() for x in args_s.split(',') if x.strip()]:
            if a.isdigit():
                argc += 1
                yield_operand = ('LOAD_CONST', _const_index(constants, CT_INT, int(a)))
            else:
                argc += 1
                if a not in symbols:
                    symbols.append(a)
                yield_operand = ('LOAD_NAME', symbols.index(a))
            # push arg
            # Note: we return a flat list, so collect
            # We'll build the list now
            if 'ops' not in locals():
                ops = []
            ops.append(yield_operand)
        # finalize ops
        if 'ops' not in locals():
            ops = []
        if fname not in symbols:
            symbols.append(fname)
        ops.append(('CALL', symbols.index(fname), argc))
        if dst not in symbols:
            symbols.append(dst)
        ops.append(('STORE_NAME', symbols.index(dst)))
        return ops
    return None


def _ensure_sym(symbols, name):
    if name not in symbols:
        symbols.append(name)
    return symbols.index(name)


def _compile_class_block(lines, i, constants, symbols):
    # Grammar:
    # Define class ClassName with fields: a, b
    # Method greet(name)
    #   Return name
    # End method
    # End class
    header = lines[i].strip()
    m = re.match(r"define class\s+(\w+)(?:\s+extends\s+(\w+))?(?:\s+with fields:\s*(.*))?\s*$", header.lower())
    if not m:
        return None, i
    parts = None
    tokens = header.split()
    cname = tokens[2]
    base = None
    if 'extends' in header.lower():
    	# naive parse for base name
        try:
            base = tokens[tokens.index('extends') + 1]
        except Exception:
            base = None
    fields = []
    if 'with fields:' in header.lower():
        parts = header.lower().split('with fields:')[1].strip()
        if parts:
            for f in [x.strip() for x in parts.split(',') if x.strip()]:
                fields.append(_ensure_sym(symbols, f))
    class_sym = _ensure_sym(symbols, cname)
    base_sym = _ensure_sym(symbols, base) if base else None
    methods = []
    i += 1
    while i < len(lines):
        ln = lines[i].strip()
        if ln.lower() == 'end class':
            break
        mm = re.match(r"method\s+(\w+)\(([^)]*)\)\s*$", ln.lower())
        if mm:
            mname = ln.split()[1].split('(')[0]
            params_raw = (ln[ln.find('(')+1:ln.find(')')]).strip()
            param_syms = []
            if params_raw:
                for p in [x.strip() for x in params_raw.split(',') if x.strip()]:
                    param_syms.append(_ensure_sym(symbols, p))
            body = []
            i += 1
            while i < len(lines):
                l2 = lines[i].strip()
                if l2.lower() == 'end method':
                    break
                body.append(l2)
                i += 1
            _, _, minst, _ = _compile_lines(body, constants, symbols)
            methods.append((_ensure_sym(symbols, mname), param_syms, minst))
        i += 1
    return (class_sym, base_sym, fields, methods), i


def _compile_try_block(lines, i, constants, symbols):
    # Try \n  <body lines> \n Catch store in <err> \n End try
    if lines[i].strip().lower() != 'try':
        return None, i
    body = []
    i += 1
    while i < len(lines):
        ln = lines[i].strip()
        if ln.lower().startswith('catch store in '):
            err = ln.split()[-1]
            i += 1
            if i >= len(lines) or lines[i].strip().lower() != 'end try':
                raise ValueError('Unterminated try block')
            # Lowering: SETUP_CATCH Lcatch; body; END_TRY; JUMP Lend; LABEL Lcatch; LOAD_NAME exception; STORE_NAME err; LABEL Lend
            Lcatch = _new_label('CATCH')
            Lend = _new_label('ENDTRY')
            instrs = [('SETUP_CATCH', Lcatch)]
            # compile body lines
            for b in body:
                lowered = _compile_stmt_with_cf(b, constants, symbols)
                if lowered is not None:
                    instrs += lowered
                else:
                    _, _, ins, _ = _compile_line(b, constants, symbols)
                    instrs += ins
            instrs += [('END_TRY',), ('JUMP', Lend), ('LABEL', Lcatch)]
            _ensure_sym(symbols, 'exception')
            instrs += [('LOAD_NAME', symbols.index('exception'))]
            _ensure_sym(symbols, err)
            instrs += [('STORE_NAME', symbols.index(err)), ('LABEL', Lend)]
            return instrs, i
        else:
            body.append(ln)
            i += 1
    raise ValueError('Missing catch/end try')


def _const_index(constants, tag, val):
    for i, (t, v) in enumerate(constants):
        if t == tag and v == val:
            return i
    constants.append((tag, val))
    return len(constants) - 1


if __name__ == "__main__":
    program = [
        "Set x to 2",
        "Add x and 3 and store the result in y",
        "Print y",
        "Create a list called numbers with values 1, 2, 3",
        "Get item at index 2 from list numbers and print it"
    ]
    compile_english_to_binary(program, "program.nlbc")
    print("Wrote program.nlbc")

