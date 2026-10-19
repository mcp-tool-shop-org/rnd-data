"""The Bolt fetch probe (R&D, 2026-10-18, W-A consult Q1's acceptance). Run by smoke_window.sh as PIN_JOB_SCRIPT on a
CPU --high-mem VM, as mock_job.py is. It imports the exact pin_window.py of role-set #91 (uploaded beside it and checked
by sha256 first) and calls the real pw.fetch_model maker path for Bolt: HfApi(token=False).list_repo_files, then
hf_hub_download(token=False). No token reaches this VM. Acceptance is read from job.log: no "Error while fetching HF_TOKEN
secret" line, no unauthenticated-requests warning, under 2 s from "before download" to "downloading", and Bolt's sha256
equal to its pin. This file lives in the Publisher's receipts, not in role-set.
"""

import hashlib
import json
import os
import sys
import time
from pathlib import Path

EXPECT_PIN_WINDOW_SHA256 = "dc204e1922afd9cb11ec7e437348b478c0e90f3b1c79de47f341c7c96e8f091b"
CONTENT = Path("/content")
WORK = CONTENT / "pin"
WORK.mkdir(parents=True, exist_ok=True)
os.environ["PIN_WORK"] = str(WORK)  # pin_window's WORK and resources() land in /content/pin
LOG = WORK / "job.log"
result = {"probe": "bolt-fetch", "job_token": os.environ.get("PIN_JOB_TOKEN")}
out, err = sys.stdout, sys.stderr
pw = None
try:
    src = CONTENT / "pin_window.py"
    got = hashlib.sha256(src.read_bytes()).hexdigest()
    result["pin_window_sha256"] = got
    if got != EXPECT_PIN_WINDOW_SHA256:
        raise RuntimeError(f"pin_window.py is {got[:12]}, not the pinned {EXPECT_PIN_WINDOW_SHA256[:12]}")
    env_before = "HF_HUB_DISABLE_IMPLICIT_TOKEN" in os.environ
    hub_before = "huggingface_hub" in sys.modules
    sys.path.insert(0, str(CONTENT))
    sys.modules.pop("pin_window", None)
    import pin_window as pw  # noqa: E402 - the import sets HF_HUB_DISABLE_IMPLICIT_TOKEN

    sys.stdout, sys.stderr = pw.Tee(out, LOG), pw.Tee(err, LOG)
    import huggingface_hub
    import huggingface_hub.constants as hub_constants

    result["implicit_token"] = {"env_set_before_import": env_before, "hub_imported_before": hub_before,
                                "env": os.environ.get("HF_HUB_DISABLE_IMPLICIT_TOKEN"),
                                "constant": hub_constants.HF_HUB_DISABLE_IMPLICIT_TOKEN,
                                "hub_version": huggingface_hub.__version__}
    pw.say(f"probe: implicit token {result['implicit_token']}")
    spec = next(m for m in pw.MODELS if m["served_as"] == "nemotron-3.5-bolt-74b-a9b")
    t0 = time.time()
    m = pw.fetch_model(spec, {})
    result.update({"seconds": round(time.time() - t0), "gguf_sha256": m["gguf_sha256"], "gguf_bytes": m["gguf_bytes"],
                   "reproduced": m["gguf_sha256"] == spec["expect_sha256"]})
    result["ok"] = result["reproduced"] and result["implicit_token"]["constant"] is True
    Path(m["path"]).unlink(missing_ok=True)
except Exception as e:  # noqa: BLE001 - reported in pin-result.json
    result.update({"ok": False, "error": f"{type(e).__name__}: {e}"})
finally:
    if pw is not None:
        result["resources"] = pw.RESOURCES
    sys.stdout, sys.stderr = out, err
    (WORK / "pin-result.json").write_text(json.dumps(result, indent=1))
    line = "PIN_RESULT " + json.dumps(result)
    with LOG.open("a", encoding="utf-8") as f:  # at the line's start: the rig's watcher reads ^PIN_RESULT
        f.write(line + "\n")
    print(line, flush=True)
