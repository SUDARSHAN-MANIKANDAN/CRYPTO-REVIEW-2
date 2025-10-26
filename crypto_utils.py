import base64
import hashlib
import json
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256

# ---------------- RSA keys ----------------
def generate_rsa_keys():
    key = RSA.generate(2048)
    private_key = key.export_key()
    public_key = key.publickey().export_key()

    with open("private.pem", "wb") as f:
        f.write(private_key)
    with open("public.pem", "wb") as f:
        f.write(public_key)
    print("[+] RSA keypair generated")

def load_keys():
    with open("private.pem", "rb") as f:
        private_key = RSA.import_key(f.read())
    with open("public.pem", "rb") as f:
        public_key = RSA.import_key(f.read())
    return private_key, public_key

# ---------------- RSA sign / verify ----------------
def sign_data(data: str, private_key):
    h = SHA256.new(data.encode())
    signature = pkcs1_15.new(private_key).sign(h)
    return base64.b64encode(signature).decode()

def verify_signature(data: str, signature: str, public_key):
    h = SHA256.new(data.encode())
    try:
        pkcs1_15.new(public_key).verify(h, base64.b64decode(signature))
        return True
    except (ValueError, TypeError):
        return False

# ---------------- SHA256 file hash ----------------
def sha256_file(file_bytes):
    return hashlib.sha256(file_bytes).hexdigest()
