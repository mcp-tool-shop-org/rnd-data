import json, sys, tarfile, io
from pathlib import Path
d = Path(sys.argv[1])
r = json.load(open(d / "pin-result.json", encoding="utf-8"))
print("stub", r["stub"], "ok", r["ok"], "token", r["job_token"], "model_errors", r["model_errors"], "prior_unpacked", r.get("prior_unpacked"), "role_set", r["role_set"]["commit"][:10])
for n, a in r["arms"].items():
    p = a.get("pilot", {})
    print("ARM", n, "last", (p.get("last") or "").rsplit("/", 1)[-1])
    for w in p.get("waves", []):
        res = w.get("result") or {}
        print("   pilot", w.get("wave"), "exit", w.get("exit"), res.get("states"), (w.get("stderr") or "")[-160:].strip())
    t = a.get("twins") or {}
    print("   twins", [(w.get("wave"), w.get("exit"), (w.get("result") or {}).get("states")) for w in t.get("waves", [])])
print("serves", {k: len(v) for k, v in r["serves"].items()})
tf = tarfile.open(d / "pilot-out.tar")
names = tf.getnames()
for n in names:
    if n.endswith("card-pins-chain.json"):
        s = json.load(tf.extractfile(n))
        print("SIDECAR", n, {k: (v if k != "pins" else sorted(v)) for k, v in s.items()})
    if n.endswith("/w2/wave-drafts.jsonl"):
        h = json.loads(tf.extractfile(n).readline())
        last = h["waves"][-1]
        print("W2", n, "waves", [w["wave"] for w in h["waves"]], "via", last.get("card_pins_via"), "prior", (last.get("card_pins_prior_sha256") or "")[:16],
              "card keys in writer_pins", sum(1 for k in h["writer_pins"] if k.startswith("card_") or k == "cards_sha256"))
    if n.endswith("/w3/receipts.jsonl"):
        rows = [json.loads(x) for x in tf.extractfile(n).read().splitlines() if x.strip()]
        print("W3 receipts", n, len(rows), "via", {x.get("card_pins_via") for x in rows}, "card keys min", min((sum(1 for k in x if k.startswith("card_") or k == "cards_sha256") for x in rows), default=None))
