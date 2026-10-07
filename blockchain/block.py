from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import json

@dataclass
class Block:
    block_number: int
    timestamp: str
    previous_hash: str
    transaction_hash: str
    transaction_data: dict
    validator_id: str
    signature: str
    block_hash: str = ""

    def payload(self) -> dict:
        return {
            "block_number": self.block_number,
            "timestamp": self.timestamp,
            "previous_hash": self.previous_hash,
            "transaction_hash": self.transaction_hash,
            "transaction_data": self.transaction_data,
            "validator_id": self.validator_id,
        }

    def to_dict(self):
        return asdict(self)

def utc_now_iso():
    return datetime.now(timezone.utc).isoformat()
