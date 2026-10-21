"""Post-run ledger capture for one sweep module.

Collects every r-address printed in stdout plus the state wallet, and every hash
recorded in tx_index or printed in stdout. Looks each hash up with `tx` and dumps
account_info/account_tx for each address. Reads public data only, never a seed.

Usage: python capture_sweep.py <run-dir>
"""
import json
import pathlib
import re
import sys
import urllib.request

URL = "https://s.altnet.rippletest.net:51234"
run = pathlib.Path(sys.argv[1])
led = run / "ledger"
led.mkdir(exist_ok=True)


def rpc(method, params):
    req = urllib.request.Request(
        URL, json.dumps({"method": method, "params": [params]}).encode(),
        {"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=30))["result"]


stdout = (run / "stdout.txt").read_text(encoding="utf-8", errors="replace")
state = json.loads((run / "state.json").read_text()) if (run / "state.json").exists() else {}
addrs = []
for a in [state.get("wallet_address", "")] + re.findall(r"\br[1-9A-HJ-NP-Za-km-z]{24,34}\b", stdout):
    if a and a not in addrs:
        addrs.append(a)
hashes = []
for h in [t.get("txid", "") for t in state.get("tx_index", [])] + re.findall(r"\b[0-9A-F]{64}\b", stdout):
    if re.fullmatch(r"[0-9A-F]{64}", h or "") and h not in hashes:
        hashes.append(h)

lookups = {}
for h in hashes:
    r = rpc("tx", {"transaction": h})
    lookups[h] = ({"error": r.get("error")} if r.get("error") else
                  {"TransactionType": r.get("TransactionType"), "Account": r.get("Account"),
                   "Destination": r.get("Destination"), "validated": r.get("validated"),
                   "ledger_index": r.get("ledger_index"), "Sequence": r.get("Sequence"),
                   "TransactionResult": r.get("meta", {}).get("TransactionResult")})
# Follow every Destination too, so unprinted addresses (e.g. a per-run practice recipient) get checked.
for v in lookups.values():
    d = v.get("Destination")
    if d and d not in addrs:
        addrs.append(d)

accounts = {}
for a in addrs:
    info = rpc("account_info", {"account": a, "ledger_index": "validated"})
    if info.get("error"):
        accounts[a] = {"error": info.get("error")}
        continue
    ad = info["account_data"]
    txs = rpc("account_tx", {"account": a, "ledger_index_min": -1, "ledger_index_max": -1, "limit": 100})
    rows = []
    for t in reversed(txs.get("transactions", [])):
        tj = t.get("tx_json") or t.get("tx") or {}
        rows.append({"ledger_index": t.get("ledger_index") or tj.get("ledger_index"),
                     "hash": t.get("hash") or tj.get("hash"), "TransactionType": tj.get("TransactionType"),
                     "Account": tj.get("Account"), "Destination": tj.get("Destination"),
                     "Sequence": tj.get("Sequence"), "Fee": tj.get("Fee"), "Flags": tj.get("Flags"),
                     "TransactionResult": t.get("meta", {}).get("TransactionResult")})
    accounts[a] = {k: ad.get(k) for k in ("Balance", "Sequence", "OwnerCount", "Flags")} | {"account_tx": rows}

vl = rpc("server_state", {})["state"]["validated_ledger"]
out = {"validated_ledger": {k: vl.get(k) for k in ("seq", "reserve_base", "reserve_inc")},
       "accounts": accounts, "tx_lookup": lookups,
       "tx_index": [{k: t.get(k) for k in ("txid", "success")} for t in state.get("tx_index", [])]}
(led / "ledger_evidence.json").write_text(json.dumps(out, indent=2))
for h, v in lookups.items():
    print(h[:10], v)
for a, v in accounts.items():
    print(a, {k: v.get(k) for k in ("Balance", "Sequence", "OwnerCount", "error")})
