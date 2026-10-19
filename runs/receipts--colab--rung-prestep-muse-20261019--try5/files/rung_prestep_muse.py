# Rung for the H200 pre-step (R&D, 2026-10-19, condition 1): prestep_fit_tokenizer.py on Muse from the Apache repo on a
# Colab A100. Muse's tokenizer_hf is recorded first from its snapshot at the pinned revision (transformers 5.20.1, as in
# its MODELS env). Then the runs, each with the non-Latin allowance: normal (must pass, listing string 38 as allowed), tampered ids (must hit TOKENIZER STOP), and a demanded per-slot
# context of 10**9 (must hit FIT STOP), and no PIN_CONTENT (must refuse, exit 2). Each must stop its server. Writes /content/pin/pin-result.json and a PIN_RESULT
# line, as smoke_window's watcher expects.
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, "/content")
import pin_window as pw  # noqa: E402

NAME = "muse-glimmer-30b"
res = {"role": "rung-prestep", "job_token": os.environ.get("PIN_JOB_TOKEN"), "started": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
pw.WORK.mkdir(parents=True, exist_ok=True)
_out, _err = sys.stdout, sys.stderr
sys.stdout, sys.stderr = pw.Tee(_out, pw.JOB_LOG), pw.Tee(_err, pw.JOB_LOG)  # as main(): the watcher reads job.log
try:
    res["machine"] = pw.machine_line()
    spec = next(m for m in pw.MODELS if m["served_as"] == NAME)
    # 1. Muse's HF ids, the maker's tokenizer at the pinned revision, in a venv with its pinned transformers.
    pw.say("recording Muse's tokenizer_hf")
    venv = pw.WORK / "env-tok"
    pw.sh(f"{sys.executable} -m pip install -q 'virtualenv==20.29.3'", timeout=600)
    pw.sh(f"{sys.executable} -m virtualenv -q {venv}", timeout=300)
    py = str(venv / "bin" / "python")
    pw.sh(f"{py} -m pip install -q 'transformers==5.20.1' 'jinja2'", timeout=1200)
    from huggingface_hub import snapshot_download

    snap = Path(snapshot_download(spec["repo"], revision=spec["revision"], local_dir=pw.WORK / "muse-tok", token=False,
                                  allow_patterns=["*.json", "*.jinja", "*.model", "*.txt", "*.py", "*.tiktoken"]))
    ids = pw.hf_token_ids(py, snap)
    idf = pw.WORK / "tokenizer_hf-muse.json"
    idf.write_text(json.dumps(ids), encoding="utf-8")
    ids_sha = hashlib.sha256(idf.read_bytes()).hexdigest()
    res["muse_ids"] = {"strings": len(ids), "sha256": ids_sha,
                       "transformers": pw.sh(f"{py} -c 'import transformers; print(transformers.__version__)'"),
                       "tokenizers": pw.sh(f"{py} -c 'import tokenizers; print(tokenizers.__version__)'")}
    # 2. The three runs, each a fresh interpreter, as on the H200.
    base = {**os.environ, "PRESTEP_NAME": NAME, "PRESTEP_IDS": str(idf), "PRESTEP_IDS_SHA": ids_sha, "PRESTEP_BASE": "/content", "PIN_CONTENT": "/content",
            "PRESTEP_ALLOW_MISMATCH": "32,33,34,35,36,37,38"}  # R&D: the non-Latin-script strings
    cases = [("normal", {}, None), ("tamper", {"PRESTEP_SKIP_DOWNLOAD": "1", "PRESTEP_TAMPER": "1"}, "TOKENIZER STOP"),
             ("impossible_ctx", {"PRESTEP_SKIP_DOWNLOAD": "1", "PRESTEP_WANT_CTX": str(10**9)}, "FIT STOP"),
             ("no_content", {"PRESTEP_SKIP_DOWNLOAD": "1", "PIN_CONTENT": None}, "REFUSED: set PIN_CONTENT")]
    res["cases"] = {}
    for label, extra, want_stop in cases:
        pw.say(f"prestep case {label}")
        env = {k: v for k, v in {**base, **extra}.items() if v is not None}  # None removes a variable
        r = pw.run_proc([sys.executable, "/content/prestep_fit_tokenizer.py"], env=env, timeout=3600)
        line = [x for x in (r.stdout or "").splitlines() if x.startswith("PRESTEP_RESULT ")]
        got = json.loads(line[-1].removeprefix("PRESTEP_RESULT ")) if line else {"error": (r.stderr or "")[-800:]}
        left = subprocess.run(["pgrep", "-f", "llama-server"], capture_output=True, text=True).stdout.strip()
        if want_stop is None:
            # The green branch (R&D): ok true, and Muse's known string-38 divergence listed as allowed, not silent.
            ok = (r.returncode == 0 and got.get("ok") and got.get("server_stopped") is True
                  and any(m.get("i") == 38 for m in got.get("allowed_mismatches") or []))
        elif want_stop.startswith("REFUSED"):  # refused before anything ran: exit 2, no server ever started
            ok = r.returncode == 2 and want_stop in (got.get("error") or "") and "server_stopped" not in got
        else:
            ok = r.returncode == 1 and want_stop in (got.get("error") or "") and got.get("server_stopped") is True
        ok = bool(ok) and not left
        res["cases"][label] = {"rc": r.returncode, "pass": bool(ok), "server_left": left, "result": got}
        pw.say(f"prestep case {label}: rc {r.returncode}, pass {ok}")
    res["ok"] = all(c["pass"] for c in res["cases"].values())
except Exception as e:  # noqa: BLE001 - reported
    res["ok"], res["error"] = False, f"{type(e).__name__}: {e}"
res["ended"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
(pw.WORK / "pin-result.json").write_text(json.dumps(res, default=str), encoding="utf-8")  # the file first, as main()
print("PIN_RESULT " + json.dumps(res, default=str), flush=True)
sys.stdout, sys.stderr = _out, _err
