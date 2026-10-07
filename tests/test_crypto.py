from crypto.hashing import sha256_hash
from crypto.keys import generate_key_pair
from crypto.signatures import sign_text, verify_text

def test_hash_is_deterministic():
    assert sha256_hash("hello") == sha256_hash("hello")
    assert sha256_hash("hello") != sha256_hash("Hello")

def test_rsa_signature():
    private_key, public_key = generate_key_pair()
    message = sha256_hash({"record_id": "123", "marks": 95})
    signature = sign_text(private_key, message)
    assert verify_text(public_key, message, signature)
    assert not verify_text(public_key, message + "tampered", signature)
