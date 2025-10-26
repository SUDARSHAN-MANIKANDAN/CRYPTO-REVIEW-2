from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class Certificate:
    student_name: str
    student_id: str
    degree: str
    grade: str
    issued_at: str # ISO timestamp
    issuer: str
    # Optional encrypted PII (dict with nonce/tag/ciphertext)
    encrypted_pii: Optional[dict] = None
    signature: Optional[str] = None # base64 signature
    issuer_pubkey_pem: Optional[str] = None


def to_dict(self):
    return asdict(self)