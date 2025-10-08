#!/usr/bin/env python3
"""
Generate curated synonyms into a YAML file, blending:
- Safe, domain-specific phrase templates for EPL
- NLTK WordNet for conservative expansions where safe

Output: english_programming/config/synonyms.generated.yml

Usage:
  python -m english_programming.tools.generate_synonyms \
    --output english_programming/config/synonyms.generated.yml \
    --cap 1000

Notes:
- We avoid generic single-word mappings (e.g., 'add' -> 'append') to prevent ambiguity
- We prefer phrase-level mappings with context (e.g., 'add to list' -> 'append to list')
- YAML precedence: curated synonyms.yml overrides generated; cwd files override config
"""
import argparse
import os
import re
import sys
from typing import List, Dict, Tuple, Set

# Optional WordNet imports (download on-demand)
def _ensure_wordnet():
    try:
        import nltk  # type: ignore
        from nltk.corpus import wordnet as wn  # type: ignore
        try:
            _ = wn.synsets('test')
        except LookupError:
            nltk.download('wordnet')
            nltk.download('omw-1.4')
        return wn
    except Exception:
        return None

SAFE_STOP: Set[str] = {
    'to','from','in','on','of','and','or','is','be','have','do','with','by','for',
    'a','an','the','at','as','not','no','more','less','than'
}

LIST_WORDS = ['list','array','sequence']
MAP_WORDS = ['map','dictionary','dict','hash','hashtable']
SET_WORDS = ['set','collection']

# Canonical target phrases (right-hand side)
CANON = {
    # collections
    'append': [
        # phrase seeds mapped to 'append'
        'push',
        'append to {list}',
        'push to {list}',
        'add to {list}',  # phrase-level only
        'insert into {list}',
    ],
    'length of': [
        'size of', 'count of', 'number of items in', 'number of elements in'
    ],
    'take the last item from list': [
        'remove last item from list',
        'take last element from list',
        'pop from list',
    ],
    'exists in': [
        'contains', 'present in', 'is in'
    ],
    # functions
    'define function': [
        'create function','build function','make function'
    ],
    'end function': [
        'end operation','end procedure','end routine','end op'
    ],
    'call': [
        'call','invoke','run'
    ],
    # classes/methods
    'define class': ['create class','make class','build class'],
    'method': ['function','routine','operation'],
    # comparators (keep to phrases)
    'greater than or equal to': [
        'at least','no less than','not less than'
    ],
    'less than or equal to': [
        'at most','no more than','not more than','no greater than'
    ],
}

# Extra template families to expand total count safely
TEMPLATES: List[Tuple[str, str]] = [
    # left: pattern (with {list}), right: canonical phrase
    ('add to {list}', 'append'),
    ('append to {list}', 'append'),
    ('push to {list}', 'append'),
    ('insert into {list}', 'append'),
    ('remove last item from {list}', 'take the last item from list'),
    ('take last element from {list}', 'take the last item from list'),
    ('size of {list}', 'length of'),
    ('count of {list}', 'length of'),
    ('number of items in {list}', 'length of'),
    ('number of elements in {list}', 'length of'),
    # map dictionary
    ('dictionary', 'map'),
    ('dict', 'map'),
    ('insert into {map}', 'map put'),
    ('put into {map}', 'map put'),
    ('get from {map}', 'map get'),
    # set
    ('add to {set}', 'add'),  # keep canonical 'add' for set ops (safe context)
    ('is in {set}', 'exists in'),
]

# WordNet expansions where safe (single words only, with filters)
WN_TARGETS: Dict[str, List[str]] = {
    'append': ['append','attach','affix','add_on','supplement'],
    'map': ['map','mapping'],
    'set': ['set','collection','grouping'],
}


def build_pairs(cap: int) -> List[Tuple[str, str]]:
    pairs: List[Tuple[str, str]] = []
    seen: Set[Tuple[str, str]] = set()

    def add(fr: str, to: str):
        key = (fr.strip().lower(), to.strip().lower())
        if not key[0] or not key[1]:
            return
        if any(tok in SAFE_STOP for tok in key[0].split()):
            # extremely generic phrase; skip
            return
        if key[0] in ('to','from'):
            return
        if key not in seen:
            seen.add(key)
            pairs.append(key)

    # 1) Canonical seed phrases
    for canon, seeds in CANON.items():
        for s in seeds:
            if '{list}' in s:
                for lw in LIST_WORDS:
                    add(s.format(list=lw), canon)
            elif '{map}' in s:
                for mw in MAP_WORDS:
                    add(s.format(map=mw), canon)
            elif '{set}' in s:
                for sw in SET_WORDS:
                    add(s.format(set=sw), canon)
            else:
                add(s, canon)
            if len(pairs) >= cap:
                return pairs

    # 2) Templates expansion
    for tmpl, canon in TEMPLATES:
        if '{list}' in tmpl:
            for lw in LIST_WORDS:
                add(tmpl.format(list=lw), canon)
                if len(pairs) >= cap:
                    return pairs
        elif '{map}' in tmpl:
            for mw in MAP_WORDS:
                add(tmpl.format(map=mw), canon)
                if len(pairs) >= cap:
                    return pairs
        elif '{set}' in tmpl:
            for sw in SET_WORDS:
                add(tmpl.format(set=sw), canon)
                if len(pairs) >= cap:
                    return pairs
        else:
            add(tmpl, canon)
            if len(pairs) >= cap:
                return pairs

    # 3) WordNet (conservative)
    wn = _ensure_wordnet()
    if wn is not None:
        for canon, seeds in WN_TARGETS.items():
            for seed in seeds:
                try:
                    for ss in wn.synsets(seed):
                        for lemma in ss.lemma_names():
                            w = lemma.replace('_', ' ').lower()
                            if w == canon:
                                continue
                            # Avoid ambiguous tokens
                            if w in SAFE_STOP or len(w) < 4:
                                continue
                            # Avoid raw 'add' ambiguities, unless contextual templates already created
                            if w == 'add':
                                continue
                            add(w, canon)
                            if len(pairs) >= cap:
                                return pairs
                except Exception:
                    continue

    # 4) Morphology variants for selected verbs (phrase-level only)
    def variants(base: str) -> List[str]:
        return [base, base+'s', base+'ed', base+'ing']

    for lw in LIST_WORDS:
        for v in variants('append'):
            add(f"{v} to {lw}", 'append')
            if len(pairs) >= cap:
                return pairs
        for v in variants('insert'):
            add(f"{v} into {lw}", 'append')
            if len(pairs) >= cap:
                return pairs

    return pairs


def write_yaml(pairs: List[Tuple[str, str]], output: str):
    import yaml
    rows = [{'from': a, 'to': b} for (a,b) in pairs]
    with open(output, 'w') as fh:
        yaml.safe_dump(rows, fh, sort_keys=False, allow_unicode=True)


def main(argv: List[str]):
    ap = argparse.ArgumentParser()
    ap.add_argument('--output', default='english_programming/config/synonyms.generated.yml')
    ap.add_argument('--cap', type=int, default=1000)
    args = ap.parse_args(argv)

    pairs = build_pairs(cap=args.cap)
    # Ensure output directory exists
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    write_yaml(pairs, args.output)
    print(f"Wrote {len(pairs)} mappings to {args.output}")


if __name__ == '__main__':
    main(sys.argv[1:])
