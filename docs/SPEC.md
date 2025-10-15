## Arithmetic: MOD

- New opcode: `OP_MOD (0x17)`
- Mnemonic: `MOD` (stack: a, b -> a % b)
- Verifier: numeric-only, returns int
- Optimizer: folds `LOAD_CONST i, LOAD_CONST j, MOD` to constant when safe

## Predicates

Supported in conditions (via spaCy normalization):
- `x is even` => `x % 2 == 0`
- `x is odd` => `x % 2 == 1`
- `x divisible by y` => `x % y == 0`
- `x is prime` => inline trial-division loop, leaves boolean

## Range List Builder

Natural phrases:
- `create/build a list L from A to B`
- `create a list L from B down to A`

Lowering:
- `L = []`; inclusive loop over i; `LIST_APPEND` each i.

## Filter and Sum Lowerings

- `filter numbers from A to B where <cond> into L`
  - L initialized to []
  - inclusive loop; if `<cond>(i)` then append i to L
- `sum numbers from A to B where <cond> into R`
  - R initialized to 0
  - inclusive loop; if `<cond>(i)` then `R = R + i`

## Normalization Pipeline (spaCy mandatory)

- Every line: spaCy tokenize + lemma (preserve quotes) → curated synonyms (`config/synonyms.yml` and `synonyms.generated.yml`) → compiler patterns.
- No LLM usage. Deterministic behavior.


