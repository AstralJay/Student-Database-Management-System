from datetime import datetime, timezone
from database import supabase
from crypto.hashing import sha256_hash
from crypto.signatures import sign_text, verify_text
from .consensus import require_authorized_validator
from .block import Block

GENESIS_PREVIOUS_HASH = "0" * 64

def get_latest_block():
    result = (
        supabase.table("blocks")
        .select("*")
        .order("block_number", desc=True)
        .limit(1)
        .execute()
    )
    return result.data[0] if result.data else None

def ensure_genesis():
    latest = get_latest_block()
    if latest:
        return latest

    timestamp = datetime.now(timezone.utc).isoformat()
    payload = {
        "block_number": 0,
        "timestamp": timestamp,
        "previous_hash": GENESIS_PREVIOUS_HASH,
        "transaction_hash": sha256_hash("GENESIS"),
        "transaction_data": {"type": "GENESIS", "message": "Academic blockchain genesis block"},
        "validator_id": "SYSTEM",
    }
    block_hash = sha256_hash(payload)

    row = {
        **payload,
        "signature": "GENESIS",
        "block_hash": block_hash,
    }
    result = supabase.table("blocks").insert(row).execute()
    return result.data[0]

def add_block(transaction_data: dict, validator_id: str, private_key):
    require_authorized_validator(validator_id)
    latest = ensure_genesis()

    transaction_hash = sha256_hash(transaction_data)
    block_number = int(latest["block_number"]) + 1
    timestamp = datetime.now(timezone.utc).isoformat()

    payload = {
        "block_number": block_number,
        "timestamp": timestamp,
        "previous_hash": latest["block_hash"],
        "transaction_hash": transaction_hash,
        "transaction_data": transaction_data,
        "validator_id": validator_id,
    }

    block_hash = sha256_hash(payload)
    signature = sign_text(private_key, block_hash)

    row = {
        **payload,
        "signature": signature,
        "block_hash": block_hash,
    }
    result = supabase.table("blocks").insert(row).execute()
    return result.data[0]

def verify_chain():
    result = supabase.table("blocks").select("*").order("block_number").execute()
    blocks = result.data

    if not blocks:
        return False, "No blocks found."

    for i, block in enumerate(blocks):
        payload = {
            "block_number": block["block_number"],
            "timestamp": block["timestamp"],
            "previous_hash": block["previous_hash"],
            "transaction_hash": block["transaction_hash"],
            "transaction_data": block["transaction_data"],
            "validator_id": block["validator_id"],
        }
        recalculated = sha256_hash(payload)
        if recalculated != block["block_hash"]:
            return False, f"Block {block['block_number']} hash mismatch."

        if i == 0:
            if block["previous_hash"] != GENESIS_PREVIOUS_HASH:
                return False, "Invalid genesis block."
        else:
            previous = blocks[i - 1]
            if block["previous_hash"] != previous["block_hash"]:
                return False, f"Block {block['block_number']} previous-hash mismatch."

            authority = (
                supabase.table("authority_nodes")
                .select("public_key")
                .eq("user_id", block["validator_id"])
                .eq("status", "ACTIVE")
                .limit(1)
                .execute()
            )
            if not authority.data:
                return False, f"Block {block['block_number']} has unauthorized validator."

            from crypto.signatures import load_public_key_from_pem
            public_key = load_public_key_from_pem(authority.data[0]["public_key"])
            if not verify_text(public_key, block["block_hash"], block["signature"]):
                return False, f"Block {block['block_number']} signature invalid."

            if block["transaction_hash"] != sha256_hash(block["transaction_data"]):
                return False, f"Block {block['block_number']} transaction hash mismatch."

    return True, f"Blockchain valid. {len(blocks)} block(s) verified."
