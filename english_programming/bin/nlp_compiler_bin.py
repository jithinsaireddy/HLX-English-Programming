import re
import difflib
import logging
import os
from english_programming.bin.nlbc_encoder import write_module_with_funcs, write_module, CT_INT, CT_STR, write_module_full_with_debug

# Mandatory spaCy normalization for flexible English
_NLP = None
_NLP_LOADED = False
def _load_spacy():
    global _NLP
    if _NLP is not None:
        return _NLP
    import spacy
    try:
        _NLP = spacy.load('en_core_web_sm')
        logging.getLogger('epl_bin').info('spaCy loaded: en_core_web_sm')
    except Exception:
        import sys, subprocess
        subprocess.run([sys.executable, '-m', 'spacy', 'download', 'en_core_web_sm'], check=True)
        import spacy as _sp2
        _NLP = _sp2.load('en_core_web_sm')
        logging.getLogger('epl_bin').info('spaCy downloaded and loaded: en_core_web_sm')
    globals()['_NLP_LOADED'] = True
    return _NLP

def _normalize_text_with_spacy(s: str) -> str:
    # Mandatory spaCy normalization for all lines
    nlp = _load_spacy()
    if not nlp:
        raise RuntimeError('spaCy not loaded')
    # Preserve quoted strings by temporary placeholders
    placeholders = {}
    def _stash_quotes(text: str) -> str:
        import re as _re
        idx = 0
        def repl(m):
            nonlocal idx
            key = f"__Q{idx}__"; idx += 1
            placeholders[key] = m.group(0)
            return key
        return _re.sub(r"(\"[^\"]*\"|'[^']*')", repl, text)
    def _unstash(text: str) -> str:
        for k, v in placeholders.items():
            text = text.replace(k, v)
        return text
    s2 = _stash_quotes(s)
    doc = nlp(s2)
    lemmas = ' '.join(t.lemma_.lower() or t.text.lower() for t in doc)
    lemmas = _unstash(lemmas)
    if logging.getLogger('epl_bin').isEnabledFor(logging.DEBUG):
        logging.getLogger('epl_bin').debug(f"normalize: src='{s}' -> '{lemmas}'")
    return lemmas

def _canonicalize_synonyms(s: str) -> str:
    # Map config-driven and common synonyms to canonical phrases
    s = s.lower()
    # 1) Built-in phrase-level regex replacements (broad but safe)
    for pat, repl in _builtin_phrase_replacements():
        try:
            s = re.sub(pat, repl, s)
        except Exception:
            continue
    # 2) Dynamic from synonyms.yml (live-reload) – curated overrides
    try:
        for a, b in _load_synonyms_yaml().items():
            s = re.sub(rf"\b{re.escape(a)}\b", b, s)
    except Exception:
        pass
    # 3) Static replacements (comparators)
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
    # 4) Similarity-based keyword normalization (very conservative)
    try:
        s = _canonicalize_by_similarity(s)
    except Exception:
        pass
    return s

def _builtin_phrase_replacements():
    """Return a list of (regex_pattern, replacement) for broad, safe, phrase-level normalization.
    Keep patterns order stable; use \b for word boundaries to avoid corrupting values.
    """
    return [
        # Collections
        (r"\bsize of\b", "length of"),
        (r"\bcount of\b", "length of"),
        (r"\bnumber of items in\b", "length of"),
        (r"\bnumber of elements in\b", "length of"),
        # Collapse type qualifiers after 'length of'
        (r"\blength of\s+(?:list|array|sequence|series|vector)\s+(\w+)\b", r"length of \1"),
        (r"\bdictionary\b", "map"),
        (r"\bdict\b", "map"),
        (r"\bpush\b", "append"),
        (r"\bremove last item from list\b", "take the last item from list"),
        (r"\bexists in\b", "exists in"),  # idempotent
        (r"\bcontains\b", "exists in"),
        # Reorder: insert X into (list|array|sequence) Y  -> append X to list Y
        (r"\binsert\s+(.+?)\s+into\s+(?:list|array|sequence)\s+(\w+)\b", r"append \1 to list \2"),
        # Reorder: insert X into Y -> append X to Y (generic; list word may be omitted)
        (r"\binsert\s+(.+?)\s+into\s+(\w+)\b", r"append \1 to \2"),
        # Reorder: place/put/stick/attach/affix X into (list|array|sequence|series|vector) Y
        (r"\b(?:place|put|stick|attach|affix)\s+(.+?)\s+(?:into|to)\s+(?:list|array|sequence|series|vector)\s+(\w+)\b", r"append \1 to list \2"),
        # Reorder: place/put/stick/attach/affix X into Y -> append X to Y (generic)
        (r"\b(?:place|put|stick|attach|affix)\s+(.+?)\s+(?:into|to)\s+(\w+)\b", r"append \1 to \2"),
        # Functions
        (r"\bcreate function\b", "define function"),
        (r"\bbuild function\b", "define function"),
        (r"\bmake function\b", "define function"),
        (r"\bend operation\b", "end function"),
        (r"\bend procedure\b", "end function"),
        (r"\bend routine\b", "end function"),
        (r"\bend op\b", "end function"),
        # Comparators (additional safety)
        (r"\bno fewer than\b", "greater than or equal to"),
        (r"\bno greater than\b", "less than or equal to"),
        (r"\bnot less than\b", "greater than or equal to"),
        (r"\bnot more than\b", "less than or equal to"),
        # Booleans
        (r"\bis equal to\b", "is equal to"),  # idempotent
        (r"\bis not equal to\b", "is not equal to"),
    ]

def _canonicalize_by_similarity(text: str) -> str:
    """Conservatively map near-miss keywords to canonical tokens using difflib.
    Only alphabetic tokens with length>=4 are considered, and mapping requires a high cutoff.
    """
    canonical = [
        # structures
        'define','create','build','make','function','procedure','routine','operation','op','end',
        'class','method','extends','fields','return','call','invoke','run','with',
        # control flow
        'if','elif','else','while','for','repeat','each','case','of',
        # collections and ops
        'list','map','dictionary','dict','set','append','pop','take','last','item','from','store','in',
        'put','get','add','check','exists','length','size','new','get','set',
        # comparators
        'greater','less','equal','equals','than','or','and',
    ]
    canon_set = sorted(set(canonical))
    parts = text.split()
    out = []
    for w in parts:
        w_clean = w.strip()
        # skip quoted tokens and non-alpha tokens
        if (w_clean.startswith("'") and w_clean.endswith("'")) or (w_clean.startswith('"') and w_clean.endswith('"')):
            out.append(w)
            continue
        base = re.sub(r"[^A-Za-z]", "", w_clean)
        if len(base) >= 4 and base.isalpha():
            match = difflib.get_close_matches(base.lower(), canon_set, n=1, cutoff=0.92)
            if match:
                # replace only the alphabetic core; keep surrounding punctuation
                rep = match[0]
                w2 = re.sub(base + r"$", rep, w_clean, flags=re.I)
                out.append(w2)
                continue
        out.append(w)
    return ' '.join(out)

# --------- Config-driven synonyms (YAML) ---------
_SYN_MAP = None
_SYN_MTIME = None  # can be tuple
_SYN_PATH = None   # can be tuple
def _synonym_paths():
    here = os.path.abspath(os.path.dirname(__file__))
    cfg_dir = os.path.abspath(os.path.join(here, '..', 'config'))
    cwd_dir = os.path.abspath(os.getcwd())
    # Merge order (earlier can be overridden by later):
    # 1) config/synonyms.generated.yml (generated suggestions)
    # 2) config/synonyms.yml (curated defaults)
    # 3) CWD synonyms.generated.yml
    # 4) CWD synonyms.yml (highest precedence)
    return [
        os.path.join(cfg_dir, 'synonyms.generated.yml'),
        os.path.join(cfg_dir, 'synonyms.yml'),
        os.path.join(cwd_dir, 'synonyms.generated.yml'),
        os.path.join(cwd_dir, 'synonyms.yml'),
    ]

def _load_synonyms_yaml():
    global _SYN_MAP, _SYN_MTIME, _SYN_PATH
    try:
        paths = [p for p in _synonym_paths() if os.path.exists(p)]
        if not paths:
            _SYN_MAP = _SYN_MAP or {}
            return _SYN_MAP
        fingerprint = tuple((p, os.path.getmtime(p)) for p in paths)
        if _SYN_PATH == fingerprint and _SYN_MTIME == fingerprint and _SYN_MAP is not None:
            return _SYN_MAP
        try:
            import yaml as _yaml
        except Exception:
            return _SYN_MAP or {}
        mapping = {}
        for path in paths:
            try:
                data = _yaml.safe_load(open(path, 'r')) or {}
            except Exception:
                continue
            if isinstance(data, dict):
                # Interpret a single rule {from: X, to: Y}
                if 'from' in data and 'to' in data and len(data) <= 2:
                    fr = str(data.get('from', '')).strip().lower()
                    to = str(data.get('to', '')).strip().lower()
                    if fr and to and fr not in ('to','from'):
                        mapping[fr] = to
                else:
                    for k, v in data.items():
                        if isinstance(k, str) and isinstance(v, str):
                            if k.lower().strip() in ('to', 'from'):
                                continue
                            mapping[k.lower()] = v.lower()
            elif isinstance(data, list):
                for row in data:
                    if isinstance(row, dict) and 'from' in row and 'to' in row:
                        fr = str(row['from']).lower().strip()
                        to = str(row['to']).lower().strip()
                        if fr and to and fr not in ('to','from'):
                            mapping[fr] = to
        _SYN_MAP, _SYN_MTIME, _SYN_PATH = mapping, fingerprint, fingerprint
        return _SYN_MAP
    except Exception:
        return _SYN_MAP or {}


def _canonical_variants(s: str) -> list:
    """Produce increasingly aggressive normalized variants for matching.
    Order: original, canonicalized(lower), spaCy-lemma+canonical.
    """
    outs = []
    try:
        if s and s not in outs:
            outs.append(s)
        low = s.lower()
        if low and low not in outs:
            outs.append(low)
        canon = _canonicalize_synonyms(low)
        if canon and canon not in outs:
            outs.append(canon)
        try:
            norm = _normalize_text_with_spacy(s)
            canon2 = _canonicalize_synonyms(norm)
            if canon2 and canon2 not in outs:
                outs.append(canon2)
        except Exception:
            pass
    except Exception:
        outs = [s]
    return outs


def compile_english_to_binary(english_lines, out_file="program.nlbc", with_debug: bool = True):
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
            # predicates: even/odd/divisible/prime
            m = re.match(r"^(\w+)\s+(?:is|be)?\s*even$", norm)
            if m: return ('EVEN', m.group(1), None)
            m = re.match(r"^(\w+)\s+(?:is|be)?\s*odd$", norm)
            if m: return ('ODD', m.group(1), None)
            m = re.match(r"^(\w+)\s+(?:is|be)?\s*(?:divisible\s+by|multiple\s+of)\s+(\w+|\-?\d+)$", norm)
            if m: return ('DIVBY', m.group(1), m.group(2))
            m = re.match(r"^(\w+)\s+(?:is|be)?\s*prime$", norm)
            if m: return ('PRIME', m.group(1), None)
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
        if op == 'EVEN':
            return [('LOAD_NAME', sym_idx(var)), ('LOAD_CONST', const_idx(CT_INT, 2)), ('MOD',), ('LOAD_CONST', const_idx(CT_INT, 0)), ('EQ',)]
        if op == 'ODD':
            return [('LOAD_NAME', sym_idx(var)), ('LOAD_CONST', const_idx(CT_INT, 2)), ('MOD',), ('LOAD_CONST', const_idx(CT_INT, 1)), ('EQ',)]
        if op == 'DIVBY':
            return [('LOAD_NAME', sym_idx(var))] + load_rhs(rhs) + [('MOD',), ('LOAD_CONST', const_idx(CT_INT, 0)), ('EQ',)]
        if op == 'PRIME':
            # Inline trial division: returns bool on stack
            # n = var; if n < 2 -> False
            n_sym = sym_idx(f"__n_{var}")
            d_sym = sym_idx(f"__d_{var}")
            LFalse = _new_label('PR_FALSE')
            LTrue = _new_label('PR_TRUE')
            LLoop = _new_label('PR_LOOP')
            LEnd  = _new_label('PR_END')
            out = []
            out += [('LOAD_NAME', sym_idx(var)), ('STORE_NAME', n_sym)]
            out += [('LOAD_NAME', n_sym), ('LOAD_CONST', const_idx(CT_INT, 2)), ('LT',), ('JUMP_IF_FALSE', LLoop)]
            out += [('LABEL', LFalse), ('LOAD_CONST', const_idx(CT_INT, 0)), ('JUMP', LEnd)]
            # d = 2
            out += [('LABEL', LLoop), ('LOAD_CONST', const_idx(CT_INT, 2)), ('STORE_NAME', d_sym)]
            # while d*d <= n
            LCheck = _new_label('PR_CHECK')
            LNext  = _new_label('PR_NEXT')
            out += [('LABEL', LCheck), ('LOAD_NAME', d_sym), ('LOAD_NAME', d_sym), ('MUL',), ('LOAD_NAME', n_sym), ('LE',), ('JUMP_IF_FALSE', LTrue)]
            # if n % d == 0 -> False
            out += [('LOAD_NAME', n_sym), ('LOAD_NAME', d_sym), ('MOD',), ('LOAD_CONST', const_idx(CT_INT, 0)), ('EQ',), ('JUMP_IF_FALSE', LNext)]
            out += [('JUMP', LFalse)]
            # d = d + 1; loop
            out += [('LABEL', LNext), ('LOAD_NAME', d_sym), ('LOAD_CONST', const_idx(CT_INT, 1)), ('ADD',), ('STORE_NAME', d_sym), ('JUMP', LCheck)]
            # True
            out += [('LABEL', LTrue), ('LOAD_CONST', const_idx(CT_INT, 1))]
            out += [('LABEL', LEnd)]
            return out
        return []

    def compile_condition_expr(cond_str: str):
        # Try simple atomic predicate first using raw text to avoid pronoun lemma issues
        try:
            _op0, _var0, _rhs0 = parse_condition(cond_str)
            return compile_condition(_op0, _var0, _rhs0)
        except Exception:
            pass
        # Recursive descent with parentheses and and/or
        norm = _canonicalize_synonyms(_normalize_text_with_spacy(cond_str)).strip().rstrip(':').rstrip('.')
        tokens = re.findall(r"\(|\)|>=|<=|==|>|<|\w+|\d+", norm)

        def parse_expr(i=0):  # OR-precedence with single common end label
            term_ops = []
            i, first = parse_term(i)
            term_ops.append(first)
            while i < len(tokens) and tokens[i] == 'or':
                i += 1
                i, nxt = parse_term(i)
                term_ops.append(nxt)
            if len(term_ops) == 1:
                return i, term_ops[0]
            end_label = _new_label('OREND')
            ops = []
            for t in term_ops[:-1]:
                cont = _new_label('ORCONT')
                ops += t + [('JUMP_IF_FALSE', cont), ('LOAD_CONST', const_idx(CT_INT, 1)), ('JUMP', end_label), ('LABEL', cont)]
            ops += term_ops[-1] + [('LABEL', end_label)]
            return i, ops

        def parse_term(i):  # AND-precedence with single common false label
            factors = []
            i, first = parse_factor(i)
            factors.append(first)
            while i < len(tokens) and tokens[i] == 'and':
                i += 1
                i, nxt = parse_factor(i)
                factors.append(nxt)
            if len(factors) == 1:
                return i, factors[0]
            end_label = _new_label('ANDEND')
            false_label = _new_label('ANDFALSE')
            ops = []
            for f in factors[:-1]:
                ops += f + [('JUMP_IF_FALSE', false_label)]
            ops += factors[-1] + [('JUMP', end_label), ('LABEL', false_label), ('LOAD_CONST', const_idx(CT_INT, 0)), ('LABEL', end_label)]
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
    instr_line_map = []  # instruction index -> 1-based source line
    def _compile_lines_blocks(lines):
        instrs = []
        i2 = 0
        while i2 < len(lines):
            raw2 = lines[i2]
            line2 = raw2.strip()
            low2 = line2.lower()
            # Split natural-English sequences on commas/then (avoid splitting inside lists by requiring explicit 'then' or semicolon)
            if (' then ' in low2 or ';' in line2) and not low2.endswith(':'):
                parts = re.split(r",\s*then\s+|\s+then\s+|;\s*", line2, flags=re.I)
                sub_instrs = []
                for sub in parts:
                    if not sub.strip():
                        continue
                    # Recurse single-line compile on each sub
                    _, _, one_ins, _ = _compile_lines_blocks([sub])
                    sub_instrs += one_ins
                if sub_instrs:
                    instrs += sub_instrs
                    i2 += 1
                    continue
            # repeat <n> times:
            mrep = re.match(r"^repeat\s+(\w+|\d+)\s+times:$", low2)
            if mrep:
                count_tok = mrep.group(1)
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
                # hidden loop counter symbol unique per loop
                hidden_sym = f"__rep_{_new_label('CNT')}"
                Lstart = _new_label('REP')
                Lend = _new_label('ENDREP')
                # init counter = 0
                instrs += [('LOAD_CONST', const_idx(CT_INT, 0)), ('STORE_NAME', sym_idx(hidden_sym))]
                # loop start and condition: counter < N
                instrs += [('LABEL', Lstart), ('LOAD_NAME', sym_idx(hidden_sym))]
                if re.fullmatch(r"\-?\d+", count_tok):
                    instrs += [('LOAD_CONST', const_idx(CT_INT, int(count_tok)))]
                else:
                    instrs += [('LOAD_NAME', sym_idx(str(count_tok)))]
                instrs += [('LT',), ('JUMP_IF_FALSE', Lend)]
                # body
                _, _, b_ins, _ = _compile_lines_blocks(body)
                instrs += b_ins
                # increment and jump back
                instrs += [('LOAD_NAME', sym_idx(hidden_sym)), ('LOAD_CONST', const_idx(CT_INT, 1)), ('ADD',), ('STORE_NAME', sym_idx(hidden_sym)), ('JUMP', Lstart), ('LABEL', Lend)]
                continue
            # for <var> from <a> to <b>:
            mrange = re.match(r"^for\s+(\w+)\s+from\s+(\w+|\-?\d+)\s+to\s+(\w+|\-?\d+)\s*:$", low2)
            if mrange:
                var_name, start_tok, end_tok = mrange.group(1), mrange.group(2), mrange.group(3)
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
                Lstart = _new_label('FORR')
                Lend = _new_label('ENDFORR')
                # init i = start
                if re.fullmatch(r"\-?\d+", start_tok):
                    instrs += [('LOAD_CONST', const_idx(CT_INT, int(start_tok)))]
                else:
                    instrs += [('LOAD_NAME', sym_idx(str(start_tok)))]
                instrs += [('STORE_NAME', sym_idx(var_name))]
                # loop start: i <= end (inclusive)
                instrs += [('LABEL', Lstart), ('LOAD_NAME', sym_idx(var_name))]
                if re.fullmatch(r"\-?\d+", end_tok):
                    instrs += [('LOAD_CONST', const_idx(CT_INT, int(end_tok)))]
                else:
                    instrs += [('LOAD_NAME', sym_idx(str(end_tok)))]
                instrs += [('LE',), ('JUMP_IF_FALSE', Lend)]
                # body
                _, _, b_ins, _ = _compile_lines_blocks(body)
                instrs += b_ins
                # i = i + 1; jump back
                instrs += [('LOAD_NAME', sym_idx(var_name)), ('LOAD_CONST', const_idx(CT_INT, 1)), ('ADD',), ('STORE_NAME', sym_idx(var_name)), ('JUMP', Lstart), ('LABEL', Lend)]
                continue
            # create/build list <name> from <a> to <b> OR create a list of <name> from A to B
            mbuild = re.match(r"^(?:create|build|make)\s+(?:a\s+)?list\s+(\w+)\s+from\s+(\w+|\-?\d+)\s+(?:down\s+to|to)\s+(\w+|\-?\d+)\.?$", low2)
            if not mbuild:
                mbuild = re.match(r"^(?:create|build|make)\s+(?:a\s+)?list\s+of\s+(\w+)\s+from\s+(\w+|\-?\d+)\s+(?:down\s+to|to)\s+(\w+|\-?\d+)\.?$", low2)
            if mbuild:
                lst, a_tok, b_tok = mbuild.group(1), mbuild.group(2), mbuild.group(3)
                descending = 'down to' in low2
                # L = []
                instrs += [('LOAD_CONST', const_idx(CT_INT, 0)), ('BUILD_LIST', 0), ('STORE_NAME', sym_idx(lst))]
                # hidden loop var
                it = f"__it_{_new_label('R')}"
                Lstart = _new_label('RANGE')
                Lend = _new_label('ENDRANGE')
                # init i = a
                if re.fullmatch(r"\-?\d+", a_tok):
                    instrs += [('LOAD_CONST', const_idx(CT_INT, int(a_tok)))]
                else:
                    instrs += [('LOAD_NAME', sym_idx(str(a_tok)))]
                instrs += [('STORE_NAME', sym_idx(it))]
                # loop start condition inclusive
                instrs += [('LABEL', Lstart), ('LOAD_NAME', sym_idx(it))]
                if re.fullmatch(r"\-?\d+", b_tok):
                    instrs += [('LOAD_CONST', const_idx(CT_INT, int(b_tok)))]
                else:
                    instrs += [('LOAD_NAME', sym_idx(str(b_tok)))]
                if descending:
                    instrs += [('GE',), ('JUMP_IF_FALSE', Lend)]
                else:
                    instrs += [('LE',), ('JUMP_IF_FALSE', Lend)]
                # append
                instrs += [('LOAD_NAME', sym_idx(lst)), ('LOAD_NAME', sym_idx(it)), ('LIST_APPEND',), ('STORE_NAME', sym_idx(lst))]
                # step
                if descending:
                    instrs += [('LOAD_NAME', sym_idx(it)), ('LOAD_CONST', const_idx(CT_INT, 1)), ('SUB',), ('STORE_NAME', sym_idx(it)), ('JUMP', Lstart), ('LABEL', Lend)]
                else:
                    instrs += [('LOAD_NAME', sym_idx(it)), ('LOAD_CONST', const_idx(CT_INT, 1)), ('ADD',), ('STORE_NAME', sym_idx(it)), ('JUMP', Lstart), ('LABEL', Lend)]
                i2 += 1
                continue
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
                hidden_it = f"__it_{_new_label('I')}"
                # iterator setup and store into hidden symbol
                instrs += [('LOAD_NAME', sym_idx(lst)), ('ITER_NEW',), ('STORE_NAME', sym_idx(hidden_it))]
                # loop
                instrs += [('LABEL', Lstart), ('LOAD_NAME', sym_idx(hidden_it)), ('ITER_HAS_NEXT',), ('JUMP_IF_FALSE', Lend),
                           ('LOAD_NAME', sym_idx(hidden_it)), ('ITER_NEXT',), ('STORE_NAME', sym_idx(itvar))]
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
            # compute a modulo b and store the result in r
            mmod = re.match(r"^(?:compute|calculate)?\s*(\w+)\s+(?:mod|modulo)\s+(\w+)\s+(?:and\s+store\s+(?:the\s+)?result\s+in|store\s+in)\s+(\w+)\.?$", low2)
            if mmod:
                a, b, dst = mmod.group(1), mmod.group(2), mmod.group(3)
                load_a = [('LOAD_CONST', const_idx(CT_INT, int(a)))] if re.fullmatch(r"\-?\d+", a) else [('LOAD_NAME', sym_idx(a))]
                load_b = [('LOAD_CONST', const_idx(CT_INT, int(b)))] if re.fullmatch(r"\-?\d+", b) else [('LOAD_NAME', sym_idx(b))]
                instrs += load_a + load_b + [('MOD',), ('STORE_NAME', sym_idx(dst))]
                i2 += 1
                continue
            # If <cond> then Set <var> to <value>
            mifset = re.match(r"^if\s+(.+?)\s+then\s+set\s+(\w+)\s+to\s+(\-?\d+|\"[^\"]*\"|'[^']*')\.?$", low2)
            if mifset:
                cond_s, dst, val = mifset.group(1), mifset.group(2), mifset.group(3)
                Lafter = _new_label('IFEND')
                instrs += compile_condition_expr(cond_s) + [('JUMP_IF_FALSE', Lafter)]
                if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                    instrs += [('LOAD_CONST', const_idx(CT_STR, val[1:-1]))]
                else:
                    instrs += [('LOAD_CONST', const_idx(CT_INT, int(val)))]
                instrs += [('STORE_NAME', sym_idx(dst)), ('LABEL', Lafter)]
                i2 += 1
                continue
            # filter for even numbers and calculate their sum (default list 'numbers', sum into 'sum')
            msent = re.match(r"^filter\s+for\s+even\s+numbers\s+and\s+(?:calculate|compute)\s+their\s+sum\.?$", low2)
            if msent:
                sum_var = 'sum'
                list_var = 'numbers'
                instrs += [('LOAD_CONST', const_idx(CT_INT, 0)), ('STORE_NAME', sym_idx(sum_var))]
                hidden_it = f"__it_{_new_label('E')}"
                Lstart = _new_label('EVENL')
                Lend = _new_label('ENDEVENL')
                instrs += [('LOAD_NAME', sym_idx(list_var)), ('ITER_NEW',), ('STORE_NAME', sym_idx(hidden_it))]
                instrs += [('LABEL', Lstart), ('LOAD_NAME', sym_idx(hidden_it)), ('ITER_HAS_NEXT',), ('JUMP_IF_FALSE', Lend), ('LOAD_NAME', sym_idx(hidden_it)), ('ITER_NEXT',), ('STORE_NAME', sym_idx('i'))]
                # Alias i and compile generic even condition via compiler
                Lskip = _new_label('SKIP')
                instrs += compile_condition_expr('i is even') + [('JUMP_IF_FALSE', Lskip)]
                instrs += [('LOAD_NAME', sym_idx(sum_var)), ('LOAD_NAME', sym_idx('i')), ('ADD',), ('STORE_NAME', sym_idx(sum_var))]
                instrs += [('LABEL', Lskip), ('JUMP', Lstart), ('LABEL', Lend)]
                i2 += 1
                continue
            # filter number(s) from A to B where <cond> into L
            mfilter = re.match(r"^filter\s+numbers?\s+from\s+(\w+|\-?\d+)\s+(?:down\s+to|to)\s+(\w+|\-?\d+)\s+where\s+(.+?)\s+into\s+(\w+)\.?$", low2)
            if mfilter:
                a_tok, b_tok, cond_s, lst = mfilter.group(1), mfilter.group(2), mfilter.group(3), mfilter.group(4)
                descending = 'down to' in low2
                # L = []
                instrs += [('LOAD_CONST', const_idx(CT_INT, 0)), ('BUILD_LIST', 0), ('STORE_NAME', sym_idx(lst))]
                # loop i
                it = f"__it_{_new_label('F')}"
                Lstart = _new_label('FLT')
                Lend = _new_label('ENDFLT')
                if re.fullmatch(r"\-?\d+", a_tok):
                    instrs += [('LOAD_CONST', const_idx(CT_INT, int(a_tok)))]
                else:
                    instrs += [('LOAD_NAME', sym_idx(str(a_tok)))]
                instrs += [('STORE_NAME', sym_idx(it))]
                instrs += [('LABEL', Lstart), ('LOAD_NAME', sym_idx(it))]
                if re.fullmatch(r"\-?\d+", b_tok):
                    instrs += [('LOAD_CONST', const_idx(CT_INT, int(b_tok)))]
                else:
                    instrs += [('LOAD_NAME', sym_idx(str(b_tok)))]
                instrs += ([('GE',)] if descending else [('LE',)]) + [('JUMP_IF_FALSE', Lend)]
                # alias i = it then predicate check; prime via OR-expansion when small (mirror SUM path)
                instrs += [('LOAD_NAME', sym_idx(it)), ('STORE_NAME', sym_idx('i'))]
                Lskip = _new_label('SKIP')
                import re as _re
                _normc = _canonicalize_synonyms(_normalize_text_with_spacy(cond_s)).strip().rstrip(':').rstrip('.')
                # Special-case fast prime expansion into explicit branch chain for correctness with JIT
                if _re.fullmatch(r"i\s+(?:is|be)?\s*prime", _normc) and re.fullmatch(r"\-?\d+", b_tok or ""):
                    try:
                        limit = int(b_tok)
                        if limit <= 200:
                            def _primes_up_to(n):
                                ps = []
                                for x in range(2, n+1):
                                    ok = True
                                    for d in range(2, int(x**0.5)+1):
                                        if x % d == 0:
                                            ok = False; break
                                    if ok:
                                        ps.append(x)
                                return ps
                            primes = _primes_up_to(limit)
                            Lok = _new_label('OK')
                            for idxp, p in enumerate(primes):
                                Lnextp = _new_label(f'NX{idxp}')
                                instrs += [('LOAD_NAME', sym_idx('i')), ('LOAD_CONST', const_idx(CT_INT, p)), ('EQ',), ('JUMP_IF_FALSE', Lnextp), ('JUMP', Lok), ('LABEL', Lnextp)]
                            instrs += [('JUMP', Lskip), ('LABEL', Lok)]
                            # append if true
                            instrs += [('LOAD_NAME', sym_idx(lst)), ('LOAD_NAME', sym_idx(it)), ('LIST_APPEND',), ('STORE_NAME', sym_idx(lst)), ('LABEL', Lskip)]
                    except Exception:
                        # Fallback to generic condition compiler
                        instrs += compile_condition_expr(cond_s) + [('JUMP_IF_FALSE', Lskip)]
                        instrs += [('LOAD_NAME', sym_idx(lst)), ('LOAD_NAME', sym_idx(it)), ('LIST_APPEND',), ('STORE_NAME', sym_idx(lst)), ('LABEL', Lskip)]
                else:
                    instrs += compile_condition_expr(cond_s) + [('JUMP_IF_FALSE', Lskip)]
                    # append if true
                    instrs += [('LOAD_NAME', sym_idx(lst)), ('LOAD_NAME', sym_idx(it)), ('LIST_APPEND',), ('STORE_NAME', sym_idx(lst)), ('LABEL', Lskip)]
                # step and loop
                step_op = ('SUB',) if descending else ('ADD',)
                instrs += [('LOAD_NAME', sym_idx(it)), ('LOAD_CONST', const_idx(CT_INT, 1)), step_op, ('STORE_NAME', sym_idx(it)), ('JUMP', Lstart), ('LABEL', Lend)]
                i2 += 1
                continue
            # sum number(s) from A to B where <cond> into R
            msum = re.match(r"^sum\s+numbers?\s+from\s+(\w+|\-?\d+)\s+(?:down\s+to|to)\s+(\w+|\-?\d+)\s+where\s+(.+?)\s+into\s+(\w+)\.?$", low2)
            if msum:
                a_tok, b_tok, cond_s, res = msum.group(1), msum.group(2), msum.group(3), msum.group(4)
                descending = 'down to' in low2
                # R = 0
                instrs += [('LOAD_CONST', const_idx(CT_INT, 0)), ('STORE_NAME', sym_idx(res))]
                # loop i
                it = f"__it_{_new_label('S')}"
                Lstart = _new_label('SUM')
                Lend = _new_label('ENDSUM')
                if re.fullmatch(r"\-?\d+", a_tok):
                    instrs += [('LOAD_CONST', const_idx(CT_INT, int(a_tok)))]
                else:
                    instrs += [('LOAD_NAME', sym_idx(str(a_tok)))]
                instrs += [('STORE_NAME', sym_idx(it))]
                instrs += [('LABEL', Lstart), ('LOAD_NAME', sym_idx(it))]
                if re.fullmatch(r"\-?\d+", b_tok):
                    instrs += [('LOAD_CONST', const_idx(CT_INT, int(b_tok)))]
                else:
                    instrs += [('LOAD_NAME', sym_idx(str(b_tok)))]
                instrs += ([('GE',)] if descending else [('LE',)]) + [('JUMP_IF_FALSE', Lend)]
                # alias i = it then predicate check; prime via OR-expansion when small
                instrs += [('LOAD_NAME', sym_idx(it)), ('STORE_NAME', sym_idx('i'))]
                Lskip = _new_label('SKIP')
                import re as _re
                _normc = _canonicalize_synonyms(_normalize_text_with_spacy(cond_s)).strip().rstrip(':').rstrip('.')
                cond_expr2 = cond_s
                if _re.fullmatch(r"i\s+(?:is|be)?\s*prime", _normc) and re.fullmatch(r"\-?\d+", b_tok or ""):
                    try:
                        limit = int(b_tok)
                        if limit <= 200:
                            def _primes_up_to(n):
                                ps = []
                                for x in range(2, n+1):
                                    ok = True
                                    for d in range(2, int(x**0.5)+1):
                                        if x % d == 0:
                                            ok = False; break
                                    if ok:
                                        ps.append(x)
                                return ps
                            cond_expr2 = ' or '.join([f"i == {p}" for p in _primes_up_to(limit)]) or "i == -1"
                    except Exception:
                        pass
                instrs += compile_condition_expr(cond_expr2) + [('JUMP_IF_FALSE', Lskip)]
                # R = R + i
                instrs += [('LOAD_NAME', sym_idx(res)), ('LOAD_NAME', sym_idx(it)), ('ADD',), ('STORE_NAME', sym_idx(res))]
                instrs += [('LABEL', Lskip)]
                # step and loop
                step_op = ('SUB',) if descending else ('ADD',)
                instrs += [('LOAD_NAME', sym_idx(it)), ('LOAD_CONST', const_idx(CT_INT, 1)), step_op, ('STORE_NAME', sym_idx(it)), ('JUMP', Lstart), ('LABEL', Lend)]
                i2 += 1
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

    # Optional fuzzy hints prolog
    if os.getenv('EP_FUZZY', '0') == '1' and os.getenv('EP_FUZZY_HINTS', '1') == '1':
        main_instrs += [('BUILD_LIST', 0), ('STORE_NAME', sym_idx('_hints'))]

    # simple function parser: "Define function NAME(args)", body until "End function" (with synonyms)
    i = 0
    while i < len(english_lines):
        raw = english_lines[i]
        line = raw.strip()
        low  = line.lower()
        if not line:
            i += 1
            continue

        # function start (synonyms for verb and noun)
        m = re.match(r"^(define|create|build|make)\s+(function|procedure|routine|operation|op)\s+(\w+)(?:\s*\(([^)]*)\))?\s*$", low)
        if m:
            fname = m.group(3)
            params_raw = (m.group(4) or '').strip()
            param_syms = []
            if params_raw:
                for p in [x.strip() for x in params_raw.split(',') if x.strip()]:
                    param_syms.append(sym_idx(p))
            body = []
            i += 1
            while i < len(english_lines):
                raw_line = english_lines[i]
                l2s = raw_line.strip()
                if re.fullmatch(r"end\s+(function|procedure|routine|operation|op)", l2s.lower()):
                    break
                # Preserve indentation for colon/indent blocks inside functions
                body.append(raw_line)
                i += 1
            if i >= len(english_lines) or not re.fullmatch(r"end\s+(function|procedure|routine|operation|op)", english_lines[i].strip().lower()):
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

        # Colon/indent: for each <var> in list <name>:
        m = re.match(r"^for each\s+(\w+)\s+in list\s+(\w+):$", low)
        if m:
            current_indent = indent_of(raw)
            itvar, lst = m.group(1), m.group(2)
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
            Lstart = _new_label('FOR')
            Lend = _new_label('ENDFOR')
            hidden_it = f"__it_{_new_label('I')}"
            main_instrs += [('LOAD_NAME', sym_idx(lst)), ('ITER_NEW',), ('STORE_NAME', sym_idx(hidden_it))]
            main_instrs += [('LABEL', Lstart), ('LOAD_NAME', sym_idx(hidden_it)), ('ITER_HAS_NEXT',), ('JUMP_IF_FALSE', Lend), ('LOAD_NAME', sym_idx(hidden_it)), ('ITER_NEXT',), ('STORE_NAME', sym_idx(itvar))]
            _, _, b_ins, _ = _compile_lines_blocks(body)
            main_instrs += b_ins + [('JUMP', Lstart), ('LABEL', Lend)]
            continue

        # Colon/indent: repeat <n> times
        m = re.match(r"^repeat\s+(\w+|\d+)\s+times:$", low)
        if m:
            current_indent = indent_of(raw)
            count_tok = m.group(1)
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
            hidden_sym = f"__rep_{_new_label('CNT')}"
            Lstart = _new_label('REP')
            Lend = _new_label('ENDREP')
            main_instrs += [('LOAD_CONST', const_idx(CT_INT, 0)), ('STORE_NAME', sym_idx(hidden_sym))]
            main_instrs += [('LABEL', Lstart), ('LOAD_NAME', sym_idx(hidden_sym))]
            if re.fullmatch(r"\-?\d+", count_tok):
                main_instrs += [('LOAD_CONST', const_idx(CT_INT, int(count_tok)))]
            else:
                main_instrs += [('LOAD_NAME', sym_idx(str(count_tok)))]
            main_instrs += [('LT',), ('JUMP_IF_FALSE', Lend)]
            _, _, b_ins, _ = _compile_lines_blocks(body)
            main_instrs += b_ins
            main_instrs += [('LOAD_NAME', sym_idx(hidden_sym)), ('LOAD_CONST', const_idx(CT_INT, 1)), ('ADD',), ('STORE_NAME', sym_idx(hidden_sym)), ('JUMP', Lstart), ('LABEL', Lend)]
            continue

        # Colon/indent: for <var> from <a> to <b>
        m = re.match(r"^for\s+(\w+)\s+from\s+(\w+|\-?\d+)\s+to\s+(\w+|\-?\d+)\s*:$", low)
        if m:
            current_indent = indent_of(raw)
            var_name, start_tok, end_tok = m.group(1), m.group(2), m.group(3)
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
            Lstart = _new_label('FORR')
            Lend = _new_label('ENDFORR')
            if re.fullmatch(r"\-?\d+", start_tok):
                main_instrs += [('LOAD_CONST', const_idx(CT_INT, int(start_tok)))]
            else:
                main_instrs += [('LOAD_NAME', sym_idx(str(start_tok)))]
            main_instrs += [('STORE_NAME', sym_idx(var_name))]
            main_instrs += [('LABEL', Lstart), ('LOAD_NAME', sym_idx(var_name))]
            if re.fullmatch(r"\-?\d+", end_tok):
                main_instrs += [('LOAD_CONST', const_idx(CT_INT, int(end_tok)))]
            else:
                main_instrs += [('LOAD_NAME', sym_idx(str(end_tok)))]
            main_instrs += [('LE',), ('JUMP_IF_FALSE', Lend)]
            _, _, b_ins, _ = _compile_lines_blocks(body)
            main_instrs += b_ins
            main_instrs += [('LOAD_NAME', sym_idx(var_name)), ('LOAD_CONST', const_idx(CT_INT, 1)), ('ADD',), ('STORE_NAME', sym_idx(var_name)), ('JUMP', Lstart), ('LABEL', Lend)]
            continue

        # otherwise compile into main (with simple control-flow lowering)
        lowered = _compile_stmt_with_cf(line, constants, symbols)
        if lowered is not None:
            main_instrs += lowered
            instr_line_map.extend([i+1] * len(lowered))
        else:
            compiled = None
            try:
                _, _, instrs, _ = _compile_line(line, constants, symbols)
                compiled = instrs
            except Exception:
                pass
            used_cand = None
            if compiled is None and os.getenv('EP_FUZZY', '0') == '1':
                for cand in _canonical_variants(line):
                    try:
                        l2 = _compile_stmt_with_cf(cand, constants, symbols)
                        if l2 is not None:
                            compiled = l2; used_cand = cand
                            break
                        _, _, instrs, _ = _compile_line(cand, constants, symbols)
                        compiled = instrs; used_cand = cand
                        break
                    except Exception:
                        continue
            if compiled is None:
                if os.getenv('EP_FUZZY', '0') == '1':
                    # Log hint into _hints list instead of printing
                    if os.getenv('EP_FUZZY_HINTS', '1') == '1':
                        main_instrs += [('LOAD_NAME', sym_idx('_hints')), ('LOAD_CONST', const_idx(CT_STR, f"Unknown: {line}")), ('LIST_APPEND',), ('STORE_NAME', sym_idx('_hints'))]
                        instr_line_map.extend([i+1] * 4)
                    # else: silent no-op
                else:
                    # strict mode: surface error
                    raise ValueError(f"Don't understand: {line}")
            else:
                main_instrs += compiled
                instr_line_map.extend([i+1] * len(compiled))
                # If we used a canonical variant different from user input, add a gentle hint
                if used_cand and os.getenv('EP_FUZZY', '0') == '1' and os.getenv('EP_FUZZY_HINTS', '1') == '1' and used_cand.strip() != line.strip():
                    main_instrs += [('LOAD_NAME', sym_idx('_hints')), ('LOAD_CONST', const_idx(CT_STR, f"Normalized: {line} -> {used_cand}")), ('LIST_APPEND',), ('STORE_NAME', sym_idx('_hints'))]
                    instr_line_map.extend([i+1] * 4)
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
    if with_debug:
        try:
            write_module_full_with_debug(out_file, constants, symbols, main_instrs, funcs, classes, instr_line_map, [])
        except Exception:
            write_module_full(out_file, constants, symbols, main_instrs, funcs, classes)
    else:
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
            compiled = None
            try:
                _, _, ins, _ = _compile_line(line, constants, symbols)
                compiled = ins
            except Exception:
                pass
            used_cand = None
            if compiled is None and os.getenv('EP_FUZZY', '0') == '1':
                for cand in _canonical_variants(line):
                    try:
                        l2 = _compile_stmt_with_cf(cand, constants, symbols)
                        if l2 is not None:
                            compiled = l2; used_cand = cand
                            break
                        _, _, ins, _ = _compile_line(cand, constants, symbols)
                        compiled = ins; used_cand = cand
                        break
                    except Exception:
                        continue
            if compiled is None:
                if os.getenv('EP_FUZZY', '0') == '1':
                    if os.getenv('EP_FUZZY_HINTS', '1') == '1':
                        instrs += [('LOAD_NAME', _ensure_sym(symbols, '_hints')), ('LOAD_CONST', _const_index(constants, CT_STR, f"Unknown: {line}")), ('LIST_APPEND',), ('STORE_NAME', _ensure_sym(symbols, '_hints'))]
                else:
                    raise ValueError(f"Don't understand: {line}")
            else:
                instrs += compiled
                if used_cand and os.getenv('EP_FUZZY', '0') == '1' and os.getenv('EP_FUZZY_HINTS', '1') == '1' and used_cand.strip() != line.strip():
                    instrs += [('LOAD_NAME', _ensure_sym(symbols, '_hints')), ('LOAD_CONST', _const_index(constants, CT_STR, f"Normalized: {line} -> {used_cand}")), ('LIST_APPEND',), ('STORE_NAME', _ensure_sym(symbols, '_hints'))]
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

    # Multi-variable declaration/assignment: set x and y to 2 and 3
    m = re.match(r"^(?:set|create(?: a)? variables?(?: called)?)\s+(.+?)\s+(?:and set (?:it|them) to|to|as)\s+(.+)$", low)
    if m:
        names_raw = m.group(1).strip().rstrip('.')
        vals_raw  = m.group(2).strip().rstrip('.')
        # split names by comma or 'and'
        names = [n.strip() for n in re.split(r"\s*(?:,|and)\s*", names_raw) if n.strip()]
        # split values by comma first, else 'and'
        if ',' in vals_raw:
            vals = [v.strip() for v in vals_raw.split(',') if v.strip()]
        else:
            vals = [v.strip() for v in re.split(r"\s+and\s+", vals_raw) if v.strip()]
        if not names:
            return None, None, instrs, None
        if len(vals) == 0:
            raise ValueError("No values provided for assignment")
        # broadcast or pairwise
        if len(vals) not in (1, len(names)):
            raise ValueError("Variable/value count mismatch")
        for idx, nm in enumerate(names):
            v = vals[0] if len(vals) == 1 else vals[idx]
            if v.isdigit() or re.fullmatch(r"\-?\d+", v):
                cidx = const_idx_local(CT_INT, int(v))
                instrs += [('LOAD_CONST', cidx)]
            elif (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
                v2 = v[1:-1]
                cidx = const_idx_local(CT_STR, v2)
                instrs += [('LOAD_CONST', cidx)]
            else:
                # identifier-like -> variable ref; else treat as raw string (paths/URLs)
                if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", v):
                    instrs += [('LOAD_NAME', sym_idx_local(v))]
                else:
                    cidx = const_idx_local(CT_STR, v)
                    instrs += [('LOAD_CONST', cidx)]
            instrs += [('STORE_NAME', sym_idx_local(nm))]
        return None, None, instrs, None

    # Special-case: assignment with unquoted path/URL should be literal string, not variable ref
    m = re.match(r"(?:set|create a variable called)\s+(\w+)\s+(?:and set it to|to|as)\s+(.+)$", line, re.I)
    if m:
        name = m.group(1)
        val_raw  = m.group(2).strip()
        # numeric
        if val_raw.isdigit() or re.fullmatch(r"\-?\d+", val_raw):
            cidx = const_idx_local(CT_INT, int(val_raw))
            instrs += [('LOAD_CONST', cidx)]
        # quoted string
        elif (val_raw.startswith('"') and val_raw.endswith('"')) or (val_raw.startswith("'") and val_raw.endswith("'")):
            v2 = val_raw[1:-1]
            cidx = const_idx_local(CT_STR, v2)
            instrs += [('LOAD_CONST', cidx)]
        else:
            # if identifier-like, treat as variable ref; else treat as raw string (paths/URLs)
            if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", val_raw):
                instrs += [('LOAD_NAME', sym_idx_local(val_raw))]
            else:
                cidx = const_idx_local(CT_STR, val_raw)
                instrs += [('LOAD_CONST', cidx)]
        instrs += [('STORE_NAME', sym_idx_local(name))]
        return None, None, instrs, None

    # Arithmetic with dotted operands and destination support
    def _emit_load_token(tok: str):
        t = tok.strip()
        md = re.fullmatch(r"(\w+)\.(\w+)", t)
        if md:
            obj, fld = md.group(1), md.group(2)
            instrs.append(('LOAD_NAME', sym_idx_local(obj)))
            instrs.append(('GETFIELD', sym_idx_local(fld)))
        elif t.isdigit() or re.fullmatch(r"\-?\d+", t):
            instrs.append(('LOAD_CONST', const_idx_local(CT_INT, int(t))))
        elif (t.startswith('"') and t.endswith('"')) or (t.startswith("'") and t.endswith("'")):
            instrs.append(('LOAD_CONST', const_idx_local(CT_STR, t[1:-1])))
        else:
            instrs.append(('LOAD_NAME', sym_idx_local(t)))

    def _store_result_to(dst_tok: str):
        t = dst_tok.strip()
        md = re.fullmatch(r"(\w+)\.(\w+)", t)
        if not md:
            instrs.append(('STORE_NAME', sym_idx_local(t)))
        else:
            obj, fld = md.group(1), md.group(2)
            tmp = f"__tmp{len(symbols)}"
            instrs.append(('STORE_NAME', sym_idx_local(tmp)))
            instrs.append(('LOAD_NAME', sym_idx_local(obj)))
            instrs.append(('LOAD_NAME', sym_idx_local(tmp)))
            instrs.append(('SETFIELD', sym_idx_local(fld)))

    m = re.match(r"add\s+(.+?)\s+and\s+(.+?)\s+and store (?:the )?(?:result|outcome)\s+in\s+(.+)$", line, re.I)
    if m:
        a, b, dst = m.group(1).strip(), m.group(2).strip(), m.group(3).strip()
        _emit_load_token(a)
        _emit_load_token(b)
        instrs.append(('ADD',))
        _store_result_to(dst)
        return None, None, instrs, None

    for opname, opcode in (("subtract","SUB"),("multiply","MUL"),("divide","DIV")):
        m = re.match(fr"{opname}\s+(.+?)\s+(?:and|by)\s+(.+?)\s+and store (?:the )?(?:result|outcome)\s+in\s+(.+)$", line, re.I)
        if m:
            a, b, dst = m.group(1).strip(), m.group(2).strip(), m.group(3).strip()
            _emit_load_token(a)
            _emit_load_token(b)
            instrs.append((opcode,))
            _store_result_to(dst)
            return None, None, instrs, None

    # Synonym forms with implicit store-back to the left operand
    m = re.match(r"^(increase|increment|add)\s+(.+?)\s+by\s+(.+?)$", line, re.I)
    if m:
        dst, src = m.group(2).strip(), m.group(3).strip()
        _emit_load_token(dst)
        _emit_load_token(src)
        instrs.append(('ADD',))
        _store_result_to(dst)
        return None, None, instrs, None
    m = re.match(r"^(decrease|decrement|reduce|subtract)\s+(.+?)\s+by\s+(.+?)$", line, re.I)
    if m:
        dst, src = m.group(2).strip(), m.group(3).strip()
        _emit_load_token(dst)
        _emit_load_token(src)
        instrs.append(('SUB',))
        _store_result_to(dst)
        return None, None, instrs, None
    m = re.match(r"^(multiply|times)\s+(.+?)\s+(?:by|with)\s+(.+?)$", line, re.I)
    if m:
        dst, src = m.group(2).strip(), m.group(3).strip()
        _emit_load_token(dst)
        _emit_load_token(src)
        instrs.append(('MUL',))
        _store_result_to(dst)
        return None, None, instrs, None
    m = re.match(r"^(divide)\s+(.+?)\s+by\s+(.+?)$", line, re.I)
    if m:
        dst, src = m.group(2).strip(), m.group(3).strip()
        _emit_load_token(dst)
        _emit_load_token(src)
        instrs.append(('DIV',))
        _store_result_to(dst)
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

    # return <obj>.<field>
    m = re.match(r"return\s+(\w+)\.(\w+)$", line, re.I)
    if m:
        obj, field = m.group(1), m.group(2)
        instrs += [('LOAD_NAME', sym_idx_local(obj)), ('GETFIELD', sym_idx_local(field)), ('RETURN',)]
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

    # return [expr] (support dotted field e.g., return self.value)
    m = re.match(r"return\s*(.*)$", line, re.I)
    if m:
        expr = m.group(1).strip()
        if expr:
            md = re.fullmatch(r"(\w+)\.(\w+)$", expr)
            if md:
                obj, field = md.group(1), md.group(2)
                instrs += [('LOAD_NAME', sym_idx_local(obj)), ('GETFIELD', sym_idx_local(field))]
            elif expr.isdigit() or re.fullmatch(r"\-?\d+", expr):
                instrs += [('LOAD_CONST', const_idx_local(CT_INT, int(expr)))]
            elif (expr.startswith('"') and expr.endswith('"')) or (expr.startswith("'") and expr.endswith("'")):
                instrs += [('LOAD_CONST', const_idx_local(CT_STR, expr[1:-1]))]
            else:
                instrs += [('LOAD_NAME', sym_idx_local(expr))]
        instrs += [('RETURN',)]
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

    # create a dictionary called <name>
    m = re.match(r"create a (?:dict|dictionary) called\s+(\w+)$", line, re.I)
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

    # put <key> maps to <val> in <map> [store in <dst>]
    m = re.match(r"put\s+(.+)\s+maps?\s+to\s+(.+)\s+in\s+(\w+)(?:\s+store in\s+(\w+))?$", line, re.I)
    if m:
        key, val, mp, dst = m.group(1).strip(), m.group(2).strip(), m.group(3), m.group(4) or m.group(3)
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

    # append <val> to list <name> (implicit store-back)
    m = re.match(r"append\s+(.+)\s+to\s+(?:list\s+)?(\w+)$", line, re.I)
    if m:
        val, name = m.group(1).strip(), m.group(2)
        instrs += [('LOAD_NAME', sym_idx_local(name))]
        if val.isdigit():
            instrs += [('LOAD_CONST', const_idx_local(CT_INT, int(val)))]
        elif (val.startswith("'") and val.endswith("'")) or (val.startswith('"') and val.endswith('"')):
            instrs += [('LOAD_CONST', const_idx_local(CT_STR, val[1:-1]))]
        else:
            instrs += [('LOAD_NAME', sym_idx_local(val))]
        instrs += [('LIST_APPEND',)]
        instrs += [('STORE_NAME', sym_idx_local(name))]
        return None, None, instrs, None

    # pop from list <name> store in <dst>
    m = re.match(r"pop from list\s+(\w+)\s+store in\s+(\w+)$", low)
    if m:
        name, dst = m.group(1), m.group(2)
        instrs += [('LOAD_NAME', sym_idx_local(name)), ('LIST_POP',)]
        instrs += [('STORE_NAME', sym_idx_local(dst))]
        return None, None, instrs, None

    # take the last item from list <name> store in <dst>
    m = re.match(r"(?:take|get)\s+(?:the\s+)?(?:last|end)\s+item\s+from\s+list\s+(\w+)\s+store in\s+(\w+)$", line, re.I)
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

    # check if <val> exists in set <name> store in <dst>
    m = re.match(r"check if\s+(\w+|\d+|'[^']*'|\"[^\"]*\")\s+exists in set\s+(\w+)\s+store in\s+(\w+)$", line, re.I)
    if m:
        val, name, dst = m.group(1), m.group(2), m.group(3)
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

    # call function <name> with a, b [and] store in <dst>
    m = re.match(r"(?:call|invoke|run)\s+(?:function|procedure|routine|operation|op)\s+(\w+)(?:\s+with\s+(.+?))?\s+(?:and\s+)?store\s+in\s+(\w+)$", line, re.I)
    if m:
        fname, args_s, dst = m.group(1), (m.group(2) or '').strip(), m.group(3)
        argc = 0
        if args_s:
            for a in [x.strip() for x in args_s.split(',') if x.strip()]:
                if a.isdigit():
                    instrs += [('LOAD_CONST', const_idx_local(CT_INT, int(a)))]
                elif (a.startswith("'") and a.endswith("'")) or (a.startswith('"') and a.endswith('"')):
                    instrs += [('LOAD_CONST', const_idx_local(CT_STR, a[1:-1]))]
                else:
                    instrs += [('LOAD_NAME', sym_idx_local(a))]
                argc += 1
        instrs += [('CALL', sym_idx_local(fname), argc)]
        instrs += [('STORE_NAME', sym_idx_local(dst))]
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
        # allocate and store object first
        instrs += [('NEW', _ensure_sym(symbols, cname)), ('STORE_NAME', _ensure_sym(symbols, dst))]
        # load object and call constructor __init__(self, ...)
        instrs += [('LOAD_NAME', _ensure_sym(symbols, dst))]
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
        # do not overwrite dst with constructor return (usually None)
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
    # Local simple condition parser/emitter to avoid referencing inner-scope helpers
    def _parse_simple_condition(cond: str):
        raw = str(cond).strip().rstrip(':').rstrip('.')
        cands = []
        raw_low = raw.lower()
        cands.append(raw_low)
        try:
            cands.append(_canonicalize_synonyms(raw_low))
        except Exception:
            pass
        try:
            norm = _normalize_text_with_spacy(raw)
            cands.append(_canonicalize_synonyms(norm))
        except Exception:
            pass
        for norm in cands:
            # even/odd/divisible/prime and basic comparators
            m = re.match(r"^(\w+)\s+(?:is|be)\s+even$", norm)
            if m: return ('EVEN', m.group(1), None)
            m = re.match(r"^(\w+)\s+(?:is|be)\s+odd$", norm)
            if m: return ('ODD', m.group(1), None)
            m = re.match(r"^(\w+)\s+(?:is|be)\s+(?:divisible\s+by|multiple\s+of)\s+(\w+|\-?\d+)$", norm)
            if m: return ('DIVBY', m.group(1), m.group(2))
            m = re.match(r"^(\w+)\s+(?:is|be)\s+prime$", norm)
            if m: return ('PRIME', m.group(1), None)
            m = re.match(r"^(\w+)\s*(>=|>|<=|<|==)\s*(\w+|\-?\d+)$", norm)
            if m:
                opmap = {'>':'GT','>=':'GE','<':'LT','<=':'LE','==':'EQ'}
                return (opmap[m.group(2)], m.group(1), m.group(3))
        raise ValueError('unsupported')

    def _emit_simple_condition(op, var, rhs):
        def _load_rhs(x):
            if isinstance(x, int) or (isinstance(x, str) and re.fullmatch(r"\-?\d+", x)):
                return [('LOAD_CONST', _const_index(constants, CT_INT, int(x)))]
            return [('LOAD_NAME', _ensure_sym(symbols, str(x)))]
        if op == 'GT':
            return _load_rhs(rhs) + [('LOAD_NAME', _ensure_sym(symbols, var)), ('LT',)]
        if op == 'GE':
            return [('LOAD_NAME', _ensure_sym(symbols, var))] + _load_rhs(rhs) + [('GE',)]
        if op == 'LT':
            return [('LOAD_NAME', _ensure_sym(symbols, var))] + _load_rhs(rhs) + [('LT',)]
        if op == 'LE':
            return [('LOAD_NAME', _ensure_sym(symbols, var))] + _load_rhs(rhs) + [('LE',)]
        if op == 'EQ':
            return [('LOAD_NAME', _ensure_sym(symbols, var))] + _load_rhs(rhs) + [('EQ',)]
        if op == 'EVEN':
            return [('LOAD_NAME', _ensure_sym(symbols, var)), ('LOAD_CONST', _const_index(constants, CT_INT, 2)), ('MOD',), ('LOAD_CONST', _const_index(constants, CT_INT, 0)), ('EQ',)]
        if op == 'ODD':
            return [('LOAD_NAME', _ensure_sym(symbols, var)), ('LOAD_CONST', _const_index(constants, CT_INT, 2)), ('MOD',), ('LOAD_CONST', _const_index(constants, CT_INT, 1)), ('EQ',)]
        if op == 'DIVBY':
            return [('LOAD_NAME', _ensure_sym(symbols, var))] + _load_rhs(rhs) + [('MOD',), ('LOAD_CONST', _const_index(constants, CT_INT, 0)), ('EQ',)]
        if op == 'PRIME':
            # Emit explicit OR-chain for small positive literals of var when available in env at runtime is not known.
            # Fallback to trial division when used directly on variables (outside known numeric ranges).
            # Here, we conservatively emit the trial-division version (used outside range loops).
            n_sym = _ensure_sym(symbols, f"__n_{var}")
            d_sym = _ensure_sym(symbols, f"__d_{var}")
            LFalse = _new_label('PR_FALSE')
            LTrue = _new_label('PR_TRUE')
            LLoop = _new_label('PR_LOOP')
            LEnd  = _new_label('PR_END')
            out = []
            out += [('LOAD_NAME', _ensure_sym(symbols, var)), ('STORE_NAME', n_sym)]
            out += [('LOAD_NAME', n_sym), ('LOAD_CONST', _const_index(constants, CT_INT, 2)), ('LT',), ('JUMP_IF_FALSE', LLoop)]
            out += [('LABEL', LFalse), ('LOAD_CONST', _const_index(constants, CT_INT, 0)), ('JUMP', LEnd)]
            out += [('LABEL', LLoop), ('LOAD_CONST', _const_index(constants, CT_INT, 2)), ('STORE_NAME', d_sym)]
            LCheck = _new_label('PR_CHECK'); LNext = _new_label('PR_NEXT')
            out += [('LABEL', LCheck), ('LOAD_NAME', d_sym), ('LOAD_NAME', d_sym), ('MUL',), ('LOAD_NAME', n_sym), ('LE',), ('JUMP_IF_FALSE', LTrue)]
            out += [('LOAD_NAME', n_sym), ('LOAD_NAME', d_sym), ('MOD',), ('LOAD_CONST', _const_index(constants, CT_INT, 0)), ('EQ',), ('JUMP_IF_FALSE', LNext)]
            out += [('JUMP', LFalse)]
            out += [('LABEL', LNext), ('LOAD_NAME', d_sym), ('LOAD_CONST', _const_index(constants, CT_INT, 1)), ('ADD',), ('STORE_NAME', d_sym), ('JUMP', LCheck)]
            out += [('LABEL', LTrue), ('LOAD_CONST', _const_index(constants, CT_INT, 1)), ('LABEL', LEnd)]
            return out
        return [('LOAD_CONST', _const_index(constants, CT_INT, 0))]
    def compile_condition_expr(cond_str: str):
        # Try simple atomic using local parser first
        try:
            _op0, _var0, _rhs0 = _parse_simple_condition(cond_str)
            return _emit_simple_condition(_op0, _var0, _rhs0)
        except Exception:
            pass
        # Choose base string for tokenization: preserve explicit operators if present
        base = cond_str if any(op in cond_str for op in ['==', '>=', '<=', '>', '<']) else _canonicalize_synonyms(_normalize_text_with_spacy(cond_str))
        base = base.strip().rstrip(':').rstrip('.')
        tokens = re.findall(r"\(|\)|>=|<=|==|>|<|\w+|\d+", base)

        def parse_expr(i=0):  # OR-precedence
            i, ops = parse_term(i)
            while i < len(tokens) and tokens[i] == 'or':
                i += 1
                true_label = _new_label('ORTRUE')
                end_label = _new_label('OREND')
                ops += [('JUMP_IF_FALSE', true_label), ('LOAD_CONST', _const_index(constants, CT_INT, 1)), ('JUMP', end_label), ('LABEL', true_label)]
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
                ops += right + [('JUMP', end_label), ('LABEL', false_label), ('LOAD_CONST', _const_index(constants, CT_INT, 0)), ('LABEL', end_label)]
            return i, ops

        def parse_factor(i):  # '(' expr ')' | atomic
            if i < len(tokens) and tokens[i] == '(':
                i, eops = parse_expr(i + 1)
                if i < len(tokens) and tokens[i] == ')':
                    i += 1
                return i, eops
            # greedy atomic consume
            j = i
            acc = []
            best = None
            while j < len(tokens):
                acc.append(tokens[j]); j += 1
                expr_txt = ' '.join(acc)
                # First, try direct operator match without normalization (to keep '==')
                mdir = re.match(r"^(\w+)\s*(>=|>|<=|<|==)\s*(\w+|\-?\d+)$", expr_txt)
                if mdir:
                    opmap = {'>':'GT','>=':'GE','<':'LT','<=':'LE','==':'EQ'}
                    best = (j, _emit_simple_condition(opmap[mdir.group(2)], mdir.group(1), mdir.group(3)))
                    continue
                try:
                    _op, _var, _rhs = _parse_simple_condition(expr_txt)
                    best = (j, _emit_simple_condition(_op, _var, _rhs))
                except Exception:
                    continue
            if best is None:
                raise ValueError(f"Unsupported condition: {' '.join(tokens[i:])}")
            return best

        _, out = parse_expr(0)
        return out
    # Split natural-English sequences only when explicit sequencing keywords present (avoid splitting basic comma lists)
    if (re.search(r",\s*then\s+", line, flags=re.I) or ' then ' in low or ';' in line) and not low.endswith(':'):
        parts = re.split(r",\s*then\s+|\s+then\s+|,\s*and\s+then\s+|;\s*", line, flags=re.I)
        ops = []
        for sub in [p.strip() for p in parts if p.strip()]:
            lowered = _compile_stmt_with_cf(sub, constants, symbols)
            if lowered is not None:
                ops += lowered
                continue
            try:
                _, _, ins, _ = _compile_line(sub, constants, symbols)
                ops += ins
            except Exception:
                pass
        if ops:
            return ops
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
    # compute a modulo b and store the result in r
    m = re.match(r"^(?:compute|calculate)?\s*(\w+)\s+(?:mod|modulo)\s+(\w+)\s+(?:and\s+store\s+(?:the\s+)?result\s+in|store\s+in)\s+(\w+)\.?$", low)
    if m:
        a, b, dst = m.group(1), m.group(2), m.group(3)
        ops = []
        if re.fullmatch(r"\-?\d+", a):
            ops += [('LOAD_CONST', _const_index(constants, CT_INT, int(a)))]
        else:
            ops += [('LOAD_NAME', _ensure_sym(symbols, a))]
        if re.fullmatch(r"\-?\d+", b):
            ops += [('LOAD_CONST', _const_index(constants, CT_INT, int(b)))]
        else:
            ops += [('LOAD_NAME', _ensure_sym(symbols, b))]
        ops += [('MOD',), ('STORE_NAME', _ensure_sym(symbols, dst))]
        return ops
    # If <var> is even/odd/divisible by y then set <dst> to <val>
    m = re.match(r"^if\s+(\w+)\s+is\s+even\s+then\s+set\s+(\w+)\s+to\s+(\-?\d+|\"[^\"]*\"|'[^']*')\.?$", low)
    if m:
        var, dst, val = m.group(1), m.group(2), m.group(3)
        L = _new_label('IFEND')
        ops = [('LOAD_NAME', _ensure_sym(symbols, var)), ('LOAD_CONST', _const_index(constants, CT_INT, 2)), ('MOD',), ('LOAD_CONST', _const_index(constants, CT_INT, 0)), ('EQ',), ('JUMP_IF_FALSE', L)]
        if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
            ops += [('LOAD_CONST', _const_index(constants, CT_STR, val[1:-1]))]
        else:
            ops += [('LOAD_CONST', _const_index(constants, CT_INT, int(val)))]
        ops += [('STORE_NAME', _ensure_sym(symbols, dst)), ('LABEL', L)]
        return ops
    m = re.match(r"^if\s+(\w+)\s+is\s+odd\s+then\s+set\s+(\w+)\s+to\s+(\-?\d+|\"[^\"]*\"|'[^']*')\.?$", low)
    if m:
        var, dst, val = m.group(1), m.group(2), m.group(3)
        L = _new_label('IFEND')
        ops = [('LOAD_NAME', _ensure_sym(symbols, var)), ('LOAD_CONST', _const_index(constants, CT_INT, 2)), ('MOD',), ('LOAD_CONST', _const_index(constants, CT_INT, 1)), ('EQ',), ('JUMP_IF_FALSE', L)]
        if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
            ops += [('LOAD_CONST', _const_index(constants, CT_STR, val[1:-1]))]
        else:
            ops += [('LOAD_CONST', _const_index(constants, CT_INT, int(val)))]
        ops += [('STORE_NAME', _ensure_sym(symbols, dst)), ('LABEL', L)]
        return ops
    m = re.match(r"^if\s+(\w+)\s+(?:is\s+)?divisible\s+by\s+(\w+|\-?\d+)\s+then\s+set\s+(\w+)\s+to\s+(\-?\d+|\"[^\"]*\"|'[^']*')\.?$", low)
    if m:
        var, rhs, dst, val = m.group(1), m.group(2), m.group(3), m.group(4)
        L = _new_label('IFEND')
        ops = [('LOAD_NAME', _ensure_sym(symbols, var))]
        if re.fullmatch(r"\-?\d+", rhs):
            ops += [('LOAD_CONST', _const_index(constants, CT_INT, int(rhs)))]
        else:
            ops += [('LOAD_NAME', _ensure_sym(symbols, rhs))]
        ops += [('MOD',), ('LOAD_CONST', _const_index(constants, CT_INT, 0)), ('EQ',), ('JUMP_IF_FALSE', L)]
        if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
            ops += [('LOAD_CONST', _const_index(constants, CT_STR, val[1:-1]))]
        else:
            ops += [('LOAD_CONST', _const_index(constants, CT_INT, int(val)))]
        ops += [('STORE_NAME', _ensure_sym(symbols, dst)), ('LABEL', L)]
        return ops
    # create/build/make a list (of) <name> from A..B
    m = re.match(r"^(?:create|build|make)\s+(?:a\s+)?list\s+(?:of\s+)?(\w+)\s+from\s+(\w+|\-?\d+)\s+(?:down\s+to|to)\s+(\w+|\-?\d+)\.?$", low)
    if m:
        lst, a_tok, b_tok = m.group(1), m.group(2), m.group(3)
        descending = 'down to' in low
        ops = [('LOAD_CONST', _const_index(constants, CT_INT, 0)), ('BUILD_LIST', 0), ('STORE_NAME', _ensure_sym(symbols, lst))]
        it = f"__it_{_new_label('R')}"
        Lstart = _new_label('RANGE')
        Lend = _new_label('ENDRANGE')
        if re.fullmatch(r"\-?\d+", a_tok):
            ops += [('LOAD_CONST', _const_index(constants, CT_INT, int(a_tok)))]
        else:
            ops += [('LOAD_NAME', _ensure_sym(symbols, str(a_tok)))]
        ops += [('STORE_NAME', _ensure_sym(symbols, it)), ('LABEL', Lstart), ('LOAD_NAME', _ensure_sym(symbols, it))]
        if re.fullmatch(r"\-?\d+", b_tok):
            ops += [('LOAD_CONST', _const_index(constants, CT_INT, int(b_tok)))]
        else:
            ops += [('LOAD_NAME', _ensure_sym(symbols, str(b_tok)))]
        ops += ([('GE',)] if descending else [('LE',)]) + [('JUMP_IF_FALSE', Lend)]
        ops += [('LOAD_NAME', _ensure_sym(symbols, lst)), ('LOAD_NAME', _ensure_sym(symbols, it)), ('LIST_APPEND',), ('STORE_NAME', _ensure_sym(symbols, lst))]
        step = ('SUB',) if descending else ('ADD',)
        ops += [('LOAD_NAME', _ensure_sym(symbols, it)), ('LOAD_CONST', _const_index(constants, CT_INT, 1)), step, ('STORE_NAME', _ensure_sym(symbols, it)), ('JUMP', Lstart), ('LABEL', Lend)]
        return ops
    # filter numbers from A..B where <cond> into L
    m = re.match(r"^filter\s+numbers?\s+from\s+(\w+|\-?\d+)\s+(?:down\s+to|to)\s+(\w+|\-?\d+)\s+where\s+(.+?)\s+into\s+(\w+)\.?$", low)
    if m:
        a_tok, b_tok, cond_s, lst = m.group(1), m.group(2), m.group(3).strip(), m.group(4)
        descending = 'down to' in low
        ops = [('LOAD_CONST', _const_index(constants, CT_INT, 0)), ('BUILD_LIST', 0), ('STORE_NAME', _ensure_sym(symbols, lst))]
        it = f"__it_{_new_label('F')}"
        Lstart = _new_label('FLT')
        Lend = _new_label('ENDFLT')
        if re.fullmatch(r"\-?\d+", a_tok):
            ops += [('LOAD_CONST', _const_index(constants, CT_INT, int(a_tok)))]
        else:
            ops += [('LOAD_NAME', _ensure_sym(symbols, str(a_tok)))]
        ops += [('STORE_NAME', _ensure_sym(symbols, it)), ('LABEL', Lstart), ('LOAD_NAME', _ensure_sym(symbols, it))]
        if re.fullmatch(r"\-?\d+", b_tok):
            ops += [('LOAD_CONST', _const_index(constants, CT_INT, int(b_tok)))]
        else:
            ops += [('LOAD_NAME', _ensure_sym(symbols, str(b_tok)))]
        ops += ([('GE',)] if descending else [('LE',)]) + [('JUMP_IF_FALSE', Lend)]
        # Use shared condition compiler; for small numeric limits, expand prime to OR of equals
        Lskip = _new_label('SKIP')
        ops += [('LOAD_NAME', _ensure_sym(symbols, it)), ('STORE_NAME', _ensure_sym(symbols, 'i'))]
        import re as _re
        _normc = _canonicalize_synonyms(_normalize_text_with_spacy(cond_s)).strip().rstrip(':').rstrip('.')
        cond_expr = cond_s
        if _re.fullmatch(r"i\s+(?:is|be)?\s*prime", _normc) and re.fullmatch(r"\-?\d+", b_tok or ""):
            try:
                limit = int(b_tok)
                if limit <= 200:
                    def _primes_up_to(n):
                        ps = []
                        for x in range(2, n+1):
                            ok = True
                            for d in range(2, int(x**0.5)+1):
                                if x % d == 0:
                                    ok = False; break
                            if ok:
                                ps.append(x)
                        return ps
                    cond_expr = ' or '.join([f"i == {p}" for p in _primes_up_to(limit)]) or "i == -1"
            except Exception:
                pass
        ops += _compile_stmt_with_cf.compile_condition_expr(cond_expr) if False else []
        # We cannot call inner function directly; reuse local helper
        # Compile condition using local helper; avoid referencing out-of-scope names
        compiled = compile_condition_expr(cond_expr)
        ops += compiled + [('JUMP_IF_FALSE', Lskip)]
        ops += [('LOAD_NAME', _ensure_sym(symbols, lst)), ('LOAD_NAME', _ensure_sym(symbols, it)), ('LIST_APPEND',), ('STORE_NAME', _ensure_sym(symbols, lst)), ('LABEL', Lskip)]
        step = ('SUB',) if descending else ('ADD',)
        ops += [('LOAD_NAME', _ensure_sym(symbols, it)), ('LOAD_CONST', _const_index(constants, CT_INT, 1)), step, ('STORE_NAME', _ensure_sym(symbols, it)), ('JUMP', Lstart), ('LABEL', Lend)]
        return ops

    # natural: filter for even numbers and calculate their sum (default list 'numbers', sum into 'sum')
    m = re.match(r"^filter\s+for\s+even\s+numbers\s+and\s+(?:calculate|compute)\s+their\s+sum\.?$", low)
    if m:
        sum_var = 'sum'
        list_var = 'numbers'
        ops = [('LOAD_CONST', _const_index(constants, CT_INT, 0)), ('STORE_NAME', _ensure_sym(symbols, sum_var))]
        hidden_it = f"__it_{_new_label('E')}"
        Lstart = _new_label('EVENL')
        Lend = _new_label('ENDEVENL')
        ops += [('LOAD_NAME', _ensure_sym(symbols, list_var)), ('ITER_NEW',), ('STORE_NAME', _ensure_sym(symbols, hidden_it))]
        ops += [('LABEL', Lstart), ('LOAD_NAME', _ensure_sym(symbols, hidden_it)), ('ITER_HAS_NEXT',), ('JUMP_IF_FALSE', Lend), ('LOAD_NAME', _ensure_sym(symbols, hidden_it)), ('ITER_NEXT',), ('STORE_NAME', _ensure_sym(symbols, 'i'))]
        Lskip = _new_label('SKIP')
        ops += compile_condition_expr('i is even') + [('JUMP_IF_FALSE', Lskip)]
        ops += [('LOAD_NAME', _ensure_sym(symbols, sum_var)), ('LOAD_NAME', _ensure_sym(symbols, 'i')), ('ADD',), ('STORE_NAME', _ensure_sym(symbols, sum_var))]
        ops += [('LABEL', Lskip), ('JUMP', Lstart), ('LABEL', Lend)]
        return ops
    # sum numbers from A..B where <cond> into R
    m = re.match(r"^sum\s+numbers?\s+from\s+(\w+|\-?\d+)\s+(?:down\s+to|to)\s+(\w+|\-?\d+)\s+where\s+(.+?)\s+into\s+(\w+)\.?$", low)
    if m:
        a_tok, b_tok, cond_s, res = m.group(1), m.group(2), m.group(3).strip(), m.group(4)
        descending = 'down to' in low
        ops = [('LOAD_CONST', _const_index(constants, CT_INT, 0)), ('STORE_NAME', _ensure_sym(symbols, res))]
        it = f"__it_{_new_label('S')}"
        Lstart = _new_label('SUM')
        Lend = _new_label('ENDSUM')
        if re.fullmatch(r"\-?\d+", a_tok):
            ops += [('LOAD_CONST', _const_index(constants, CT_INT, int(a_tok)))]
        else:
            ops += [('LOAD_NAME', _ensure_sym(symbols, str(a_tok)))]
        ops += [('STORE_NAME', _ensure_sym(symbols, it)), ('LABEL', Lstart), ('LOAD_NAME', _ensure_sym(symbols, it))]
        if re.fullmatch(r"\-?\d+", b_tok):
            ops += [('LOAD_CONST', _const_index(constants, CT_INT, int(b_tok)))]
        else:
            ops += [('LOAD_NAME', _ensure_sym(symbols, str(b_tok)))]
        ops += ([('GE',)] if descending else [('LE',)]) + [('JUMP_IF_FALSE', Lend)]
        Lskip = _new_label('SKIP')
        # Alias i and inline predicate evaluation via normalized text
        ops += [('LOAD_NAME', _ensure_sym(symbols, it)), ('STORE_NAME', _ensure_sym(symbols, 'i'))]
        from re import fullmatch as _fullmatch
        _norm = _canonicalize_synonyms(_normalize_text_with_spacy(cond_s)).strip().rstrip(':').rstrip('.')
        if _fullmatch(r"i\s+(?:is|be)?\s*even", _norm):
            ops += [('LOAD_NAME', _ensure_sym(symbols, it)), ('LOAD_CONST', _const_index(constants, CT_INT, 2)), ('MOD',), ('LOAD_CONST', _const_index(constants, CT_INT, 0)), ('EQ',)]
        elif _fullmatch(r"i\s+(?:is|be)?\s*odd", _norm):
            ops += [('LOAD_NAME', _ensure_sym(symbols, it)), ('LOAD_CONST', _const_index(constants, CT_INT, 2)), ('MOD',), ('LOAD_CONST', _const_index(constants, CT_INT, 1)), ('EQ',)]
        elif _fullmatch(r"i\s+(?:is|be)?\s*prime", _norm):
            _n = _ensure_sym(symbols, '__n_i'); _d = _ensure_sym(symbols, '__d_i')
            _LFalse = _new_label('PR_FALSE'); _LTrue = _new_label('PR_TRUE'); _LCheck = _new_label('PR_CHECK'); _LNext = _new_label('PR_NEXT'); _LEnd = _new_label('PR_END')
            ops += [('LOAD_NAME', _ensure_sym(symbols, it)), ('STORE_NAME', _n)]
            ops += [('LOAD_NAME', _n), ('LOAD_CONST', _const_index(constants, CT_INT, 2)), ('LT',), ('JUMP_IF_FALSE', _LCheck)]
            ops += [('LABEL', _LFalse), ('LOAD_CONST', _const_index(constants, CT_INT, 0)), ('JUMP', _LEnd)]
            ops += [('LABEL', _LCheck), ('LOAD_CONST', _const_index(constants, CT_INT, 2)), ('STORE_NAME', _d)]
            _LWhile = _new_label('PR_WHILE')
            ops += [('LABEL', _LWhile), ('LOAD_NAME', _d), ('LOAD_NAME', _d), ('MUL',), ('LOAD_NAME', _n), ('LE',), ('JUMP_IF_FALSE', _LTrue)]
            ops += [('LOAD_NAME', _n), ('LOAD_NAME', _d), ('MOD',), ('LOAD_CONST', _const_index(constants, CT_INT, 0)), ('EQ',), ('JUMP_IF_FALSE', _LNext)]
            ops += [('JUMP', _LFalse)]
            ops += [('LABEL', _LNext), ('LOAD_NAME', _d), ('LOAD_CONST', _const_index(constants, CT_INT, 1)), ('ADD',), ('STORE_NAME', _d), ('JUMP', _LWhile)]
            ops += [('LABEL', _LTrue), ('LOAD_CONST', _const_index(constants, CT_INT, 1)), ('LABEL', _LEnd)]
        else:
            import re as _re
            mm = _re.fullmatch(r"i\s+(?:is\s+|be\s+)?divisible\s+by\s+(\w+|\-?\d+)", _norm)
            if mm:
                rhs = mm.group(1)
                ops += [('LOAD_NAME', _ensure_sym(symbols, it))]
                if rhs.isdigit() or (rhs.startswith('-') and rhs[1:].isdigit()):
                    ops += [('LOAD_CONST', _const_index(constants, CT_INT, int(rhs)))]
                else:
                    ops += [('LOAD_NAME', _ensure_sym(symbols, rhs))]
                ops += [('MOD',), ('LOAD_CONST', _const_index(constants, CT_INT, 0)), ('EQ',)]
            else:
                ops += [('LOAD_CONST', _const_index(constants, CT_INT, 0))]
        ops += [('JUMP_IF_FALSE', Lskip)]
        ops += [('LOAD_NAME', _ensure_sym(symbols, res)), ('LOAD_NAME', _ensure_sym(symbols, it)), ('ADD',), ('STORE_NAME', _ensure_sym(symbols, res)), ('LABEL', Lskip)]
        step = ('SUB',) if descending else ('ADD',)
        ops += [('LOAD_NAME', _ensure_sym(symbols, it)), ('LOAD_CONST', _const_index(constants, CT_INT, 1)), step, ('STORE_NAME', _ensure_sym(symbols, it)), ('JUMP', Lstart), ('LABEL', Lend)]
        return ops
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
            # auto-increment the loop variable to guarantee progress and termination
            ('LOAD_NAME', symbols.index(var) if var in symbols else symbols.append(var) or symbols.index(var)),
            ('LOAD_CONST', _const_index(constants, CT_INT, 1)),
            ('ADD',),
            ('STORE_NAME', symbols.index(var) if var in symbols else symbols.append(var) or symbols.index(var)),
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
    # Accept synonyms for class and extends and fields
    m = re.match(r"^(define|create|build|make)\s+(class|blueprint|type|object)\s+(\w+)(?:\s+(?:extends|inherits from|from)\s+(\w+))?(?:\s+with\s+(?:fields|members|properties):\s*(.*))?\s*$", header.lower())
    if not m:
        return None, i
    parts = None
    tokens = header.split()
    # tokens: <verb> <noun> <Name> ...
    cname = tokens[2]
    base = None
    low_hdr = header.lower()
    if ('extends' in low_hdr) or ('inherits from' in low_hdr) or re.search(r"\bfrom\b", low_hdr):
        try:
            low_toks = [t.lower() for t in tokens]
            if 'extends' in low_toks:
                base = tokens[low_toks.index('extends') + 1]
            elif 'inherits' in low_toks and 'from' in low_toks:
                base = tokens[low_toks.index('from') + 1]
            elif 'from' in low_toks:
                base = tokens[low_toks.index('from') + 1]
        except Exception:
            base = None
    fields = []
    if re.search(r"with\s+(fields|members|properties):", header, flags=re.I):
        parts = re.split(r"with\s+(?:fields|members|properties):", header, flags=re.I)[1].strip().lower()
        if parts:
            for f in [x.strip() for x in parts.split(',') if x.strip()]:
                fields.append(_ensure_sym(symbols, f))
    class_sym = _ensure_sym(symbols, cname)
    base_sym = _ensure_sym(symbols, base) if base else None
    methods = []
    i += 1
    while i < len(lines):
        ln = lines[i].strip()
        if re.fullmatch(r"end\s+(class|blueprint|type|object)", ln.lower()):
            break
        mm = re.match(r"(method|function|routine|operation|op)\s+(\w+)\(([^)]*)\)\s*$", ln.lower())
        if mm:
            # Preserve original case of method name from source line
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
                if re.fullmatch(r"end\s+(method|function|routine|operation|op)", l2.lower()):
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

