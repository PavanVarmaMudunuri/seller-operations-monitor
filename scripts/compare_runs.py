import argparse, hashlib, json
from pathlib import Path

def manifest(path):
    out={}
    for p in sorted(Path(path).glob("*.csv")):
        out[p.name]=hashlib.sha256(p.read_bytes()).hexdigest()
    return out

ap=argparse.ArgumentParser()
ap.add_argument("run_a")
ap.add_argument("run_b")
a=manifest(ap.parse_args().run_a)
b=manifest(ap.parse_args().run_b)
print(json.dumps({"identical":a==b,"run_a":a,"run_b":b},indent=2))
