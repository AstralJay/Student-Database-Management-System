import hashlib
import json

def canonical_json(data: dict) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), default=str)

def sha256_hash(data) -> str:
    if isinstance(data, dict):
        data = canonical_json(data)
    if not isinstance(data, (str, bytes)):
        data = str(data)
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()
