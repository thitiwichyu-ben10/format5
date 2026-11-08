import json
from pathlib import Path
from jsonschema import Draft202012Validator
ROOT = Path(__file__).resolve().parents[1]
def validate_quotation(data):
    schema = json.loads((ROOT / "schemas" / "quotation.schema.json").read_text(encoding="utf-8"))
    errors = sorted(Draft202012Validator(schema).iter_errors(data), key=lambda e: list(e.path))
    if errors:
        details = [f"{'.'.join(map(str,e.path)) or '(root)'}: {e.message}" for e in errors]
        raise ValueError("ข้อมูลไม่ผ่านการตรวจสอบ:\\n- " + "\\n- ".join(details))
    return True
