"""Post-run ledger capture for an F9 run: account_tx/info/lines for wallet + issuer,
server_state reserves, and amm_info for XRP/LAB (Argon watch item: actNotFound after a
full withdraw). Reads only public addresses; never reads or writes a seed.

Usage: python capture_ledger.py <run-id>
"""
import json
import pathlib
import sys
import urllib.request

URL = "https://s.altnet.rippletest.net:51234"
PAD = pathlib.Path(__file__).parent
run_id = sys.argv[1]
run = pathlib.Path("E:/AI/xrpl-lab-runs") / run_id
led = run / "ledger"
led.mkdir(parents=True, exist_ok=True)

W = json.load(open(PAD / run_id / "home" / "state.json"))["wallet_address"]
I = json.load(open(PAD / run_id / "cwd" / ".xrpl-lab" / "issuer_wallet.json"))["address"]


def rpc(method, params):
    req = urllib.request.Request(
        URL, json.dumps({"method": method, "params": [params]}).encode(),
        {"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=30))["result"]


def dump(name, method, params):
    r = rpc(method, params)
    json.dump(r, open(led / f"{name}.json", "w"), indent=2)
    return r


vl = dump("server_state", "server_state", {})["state"]["validated_ledger"]
print("validated", vl.get("seq"), "reserve_base", vl.get("reserve_base"), "reserve_inc", vl.get("reserve_inc"))
for tag, a in (("wallet", W), ("issuer", I)):
    ad = dump(f"account_info_{tag}", "account_info", {"account": a, "ledger_index": "validated"}).get("account_data", {})
    print(tag, a, "bal", ad.get("Balance"), "seq", ad.get("Sequence"), "owners", ad.get("OwnerCount"), "flags", hex(ad.get("Flags", 0)))
    dump(f"account_lines_{tag}", "account_lines", {"account": a, "ledger_index": "validated"})
    tx = dump(f"account_tx_{tag}", "account_tx", {"account": a, "ledger_index_min": -1, "ledger_index_max": -1})
    for t in reversed(tx.get("transactions", [])):
        tj = t.get("tx_json") or t.get("tx") or {}
        m = t.get("meta", {})
        print("  ", t.get("ledger_index"), tj.get("TransactionType"), t.get("hash"), m.get("TransactionResult"),
              "fee", tj.get("Fee"), "flags", tj.get("Flags"), "seq", tj.get("Sequence"))
amm = dump("amm_info_after", "amm_info", {"asset": {"currency": "XRP"}, "asset2": {"currency": "LAB", "issuer": I}, "ledger_index": "validated"})
print("amm_info after run:", amm.get("error") or "pool exists", amm.get("error_message", ""))
