# scripts/gen_keys.py
from Crypto.PublicKey import RSA
import argparse
from pathlib import Path


parser = argparse.ArgumentParser()
parser.add_argument('--outdir', default='keys')
parser.add_argument('--bits', type=int, default=2048)
args = parser.parse_args()


out = Path(args.outdir)
out.mkdir(parents=True, exist_ok=True)
key = RSA.generate(args.bits)
priv = key.export_key()
pub = key.publickey().export_key()


with open(out / 'issuer_private.pem', 'wb') as f:
    f.write(priv)
with open(out / 'issuer_public.pem', 'wb') as f:
    f.write(pub)


print(f'Keys written to {out.resolve()}')