"""Manual hard stops before any critic call (R&D, 2026-10-19), composed from pin_window's own functions only:
1. the hosted Q8_0, fetched exactly as prefetch_hosted does (get_paths_info, with_heartbeat around hf_hub_download into
   WORK/hosted, so pin_window's later call finds it in place), checked against its pin; the READ token file is read
   once, deleted and dropped, then token_clean;
2. llama-server via start_server at CRITIC_CTX, wait_for_log, then all_on_gpu and slots: the FIT STOP;
3. tokenizer_check: the 50 TOKENIZER_STRINGS through /tokenize against recorded HF ids: the TOKENIZER STOP;
4. stop_server, always. A failure exits 1 and prints PRESTEP_RESULT; nothing is ever called on the critic.

Settings (env): PIN_CONTENT (required, no default), PRESTEP_NAME (served_as; default Super-VL), PRESTEP_IDS and PRESTEP_IDS_SHA (the recorded HF ids file),
PRESTEP_BASE (where pin_window.py sits), PRESTEP_SKIP_DOWNLOAD=1 (reuse WORK/hosted's file, sha-checked, no token).
PRESTEP_ALLOW_MISMATCH (comma-separated string indices whose mismatch is reported, not stopped on).
Rung-only, to prove each stop fires (R&D): PRESTEP_WANT_CTX (the per-slot context demanded of slots), PRESTEP_TAMPER=1
(the first recorded id is altered before the compare)."""
import hashlib
import json
import os
import sys
from pathlib import Path

if not os.environ.get("PIN_CONTENT"):
    # No default (R&D, 2026-10-19): /root/content is right on the pod and wrong on Colab (/content); rung try 2 lost all
    # three cases to that default. The launch names the layout.
    print("PRESTEP_RESULT " + json.dumps({"ok": False, "error": "REFUSED: set PIN_CONTENT; nothing ran"}), flush=True)
    sys.exit(2)
sys.path.insert(0, os.environ.get("PRESTEP_BASE", "/workspace/job/content"))
import pin_window as pw  # noqa: E402

NAME = os.environ.get("PRESTEP_NAME", "nemotron-3.5-super-vl-120b-a12b")
IDS = Path(os.environ.get("PRESTEP_IDS", "/workspace/job/content/tokenizer_hf-super-vl.json"))
IDS_SHA = os.environ.get("PRESTEP_IDS_SHA", "578793a973ac163baa30e6b96eba5a7e3b60c839eb8f39c8f5a668e3f5242138")
WANT_CTX = int(os.environ.get("PRESTEP_WANT_CTX") or pw.CRITIC_CTX)
out: dict = {"name": NAME, "want_ctx": WANT_CTX, "tamper": os.environ.get("PRESTEP_TAMPER") == "1"}
proc = log_fh = None
try:
    pw.WORK.mkdir(parents=True, exist_ok=True)
    spec = next(m for m in pw.MODELS if m["served_as"] == NAME)
    path = pw.WORK / "hosted" / pw.hosted_name(NAME)
    if os.environ.get("PRESTEP_SKIP_DOWNLOAD") == "1":
        out["download"] = "skipped: file in place"
    else:
        repo, rev = os.environ["PIN_GGUF_REPO"], os.environ["PIN_GGUF_REVISION"]
        out["repo_revision"] = rev
        pw.read_token_file(needed=True)
        token = pw.take_token()
        if not token:
            raise RuntimeError("no READ token reached the machine")
        from huggingface_hub import HfApi, hf_hub_download

        try:
            size = {i.path: i.size for i in HfApi(token=token).get_paths_info(repo, [pw.hosted_name(NAME)], revision=rev)}[pw.hosted_name(NAME)]
            pw.resources(f"prestep {NAME}: before hosted download")
            path = Path(pw.with_heartbeat(
                lambda: hf_hub_download(repo, pw.hosted_name(NAME), revision=rev, token=token, local_dir=pw.WORK / "hosted"),
                f"hosted:{NAME}", pw.download_timeout(size), watch=pw.WORK / "hosted"))
        finally:
            token = None
        pw.check_token_clean(out)
    got = pw.sha256(path)
    out["gguf"] = {"path": str(path), "sha256": got, "bytes": path.stat().st_size}
    if got != spec["expect_sha256"]:
        raise RuntimeError(f"hosted GGUF {got[:12]} isn't the pin {spec['expect_sha256'][:12]}")
    built = pw.runtime()
    out["llama_server"] = {k: built.get(k) for k in ("sha256", "commit")}
    proc, log_fh, log = pw.start_server(built, {"served_as": NAME, "path": str(path)}, pw.CRITIC_CTX, pw.CRITIC_PORT)
    pw.wait_for_log(log)
    out["offload_lines"] = pw._offload_lines(log)
    out["fit"] = fit = pw.all_on_gpu(out["offload_lines"])
    out["slots"] = sl = pw.slots(pw.CRITIC_PORT, WANT_CTX)
    out["nvidia_smi"] = pw.sh("nvidia-smi --query-gpu=name,memory.used,memory.total --format=csv,noheader")
    if not fit["ok"] or not sl["ok"]:
        raise RuntimeError(f"FIT STOP: fit {fit}, slots {sl}")
    if hashlib.sha256(IDS.read_bytes()).hexdigest() != IDS_SHA:
        raise RuntimeError(f"the recorded HF ids file isn't {IDS_SHA[:12]}")
    ids = json.loads(IDS.read_text(encoding="utf-8"))
    if out["tamper"]:
        ids[0] = [ids[0][0] + 1] + ids[0][1:]
    out["tokenizer"] = tok = pw.tokenizer_check(pw.CRITIC_PORT, {"tokenizer_hf": ids})
    # R&D, 2026-10-19: a mismatch is allowed only on a string in a script the items don't use (PRESTEP_ALLOW_MISMATCH,
    # derived once from TOKENIZER_STRINGS: every letter non-Latin). Each allowed one is reported; any other stops.
    allow = {int(x) for x in os.environ.get("PRESTEP_ALLOW_MISMATCH", "").split(",") if x.strip()}
    out["allow_mismatch"] = sorted(allow)
    out["allowed_mismatches"] = [m for m in tok["mismatches"] if m["i"] in allow]
    blocking = [m for m in tok["mismatches"] if m["i"] not in allow]
    if len(tok["mismatches"]) >= 10:  # tokenizer_check keeps 10: a full list could hide a blocking one past it
        raise RuntimeError(f"TOKENIZER STOP: {len(tok['mismatches'])} mismatches listed, too many to classify")
    if blocking:
        raise RuntimeError(f"TOKENIZER STOP: {blocking[:3]}")
    out["ok"] = True
except Exception as e:  # noqa: BLE001 - reported, and the exit code says so
    out["ok"], out["error"] = False, f"{type(e).__name__}: {e}"
finally:
    if proc is not None:
        pw.stop_server(proc, log_fh)
        out["server_stopped"] = proc.poll() is not None
print("PRESTEP_RESULT " + json.dumps(out, default=str), flush=True)
sys.exit(0 if out.get("ok") else 1)
