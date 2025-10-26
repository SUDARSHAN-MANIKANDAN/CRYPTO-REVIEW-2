import json
import hashlib
import os
from datetime import datetime
from crypto_utils import load_keys, sign_data

class Blockchain:
    def __init__(self, filename="chain.json"):
        self.filename = filename
        self.chain = []

        if os.path.exists(self.filename) and os.path.getsize(self.filename) > 0:
            try:
                with open(self.filename, "r") as f:
                    self.chain = json.load(f)
            except json.JSONDecodeError:
                self.create_genesis_block()
        else:
            self.create_genesis_block()

    def create_genesis_block(self):
        genesis = {
            "index": 0,
            "timestamp": str(datetime.now()),
            "transactions": [],
            "previous_hash": "0",
        }
        genesis["hash"] = self.hash_block(genesis)
        self.chain = [genesis]
        self.save_chain()

    def hash_block(self, block):
        block_copy = dict(block)
        block_copy.pop("hash", None)
        encoded = json.dumps(block_copy, sort_keys=True).encode()
        return hashlib.sha256(encoded).hexdigest()

    def add_certificate(self, student_data):
        private_key, _ = load_keys()
        cert_string = json.dumps(student_data, sort_keys=True)
        signature = sign_data(cert_string, private_key)
        student_data["signature"] = signature

        last_block = self.chain[-1]
        new_block = {
            "index": len(self.chain),
            "timestamp": str(datetime.now()),
            "transactions": [student_data],
            "previous_hash": last_block["hash"],
        }
        new_block["hash"] = self.hash_block(new_block)

        self.chain.append(new_block)
        self.save_chain()
        print(f"[+] Block {new_block['index']} mined automatically!")

    def save_chain(self):
        with open(self.filename, "w") as f:
            json.dump(self.chain, f, indent=4)
