import json, sys
from jsonschema import validate

# Minimal WoT TD schema placeholder; for real validation, integrate official TD schema.
TD_SCHEMA = {
  "type": "object",
  "required": ["title", "@type", "properties"],
}

def main(path):
    data = json.load(open(path))
    try:
        validate(instance=data, schema=TD_SCHEMA)
        print(json.dumps({"ok": True}))
    except Exception as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        return 1

if __name__ == '__main__':
    sys.exit(main(sys.argv[1]))
