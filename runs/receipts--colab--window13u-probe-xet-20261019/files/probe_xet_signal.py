"""The Xet write-pattern probe (R&D, 2026-10-19, Argon's critic-signal reply 6(d)). Run by smoke_window.sh as
PIN_JOB_SCRIPT on a CPU --high-mem VM. It imports role-set main's pin_window.py (uploaded beside it, sha256 checked
first), reads the READ token from /dev/shm as every window does, and downloads one hosted Q8_0 from the private repo
with hf_hub_download in a worker thread, exactly as prefetch_hosted does. Every 10 s it logs, as a PROBE line in
job.log: the bytes under the download's local_dir (hidden .cache files included), the bytes under HF_XET_CACHE, the
allocated bytes (st_blocks x 512) under both, and free disk. The record shows which signal moves steadily during a live
download, and whether the target file is preallocated. The file is sha-checked against its pin and deleted. This file
lives in the Publisher's receipts, not in role-set.
"""

import hashlib
import json
import os
import sys
import threading
import time
from pathlib import Path

EXPECT_PIN_WINDOW_SHA256 = "27b8f860d801847966fa044cd01f8c4d6f762611d29d98e9acb505d308dc1cff"
MODEL = os.environ.get("PROBE_MODEL", "qwen3.8-27b")
CONTENT = Path("/content")
WORK = CONTENT / "pin"
WORK.mkdir(parents=True, exist_ok=True)
os.environ["PIN_WORK"] = str(WORK)
XET = CONTENT / "xet-cache"
os.environ["HF_XET_CACHE"] = str(XET)  # a known place, outside the download's local_dir, so each signal is seen apart
LOG = WORK / "job.log"
result = {"probe": "xet-signal", "job_token": os.environ.get("PIN_JOB_TOKEN"), "model": MODEL, "rounds": []}


def line(text: str) -> None:
    with LOG.open("a", encoding="utf-8") as f:
        f.write(f"[{time.strftime('%H:%M:%S')}] {text}\n")


def tree(root: Path) -> tuple[int, int, int]:
    """(apparent bytes, allocated bytes, files) under root, hidden files included."""

    size = alloc = n = 0
    if root.exists():
        for dirpath, _dirs, files in os.walk(root):
            for f in files:
                try:
                    st = os.lstat(os.path.join(dirpath, f))
                except OSError:
                    continue
                size += st.st_size
                alloc += st.st_blocks * 512
                n += 1
    return size, alloc, n


pw = None
try:
    got = hashlib.sha256((CONTENT / "pin_window.py").read_bytes()).hexdigest()
    if got != EXPECT_PIN_WINDOW_SHA256:
        raise RuntimeError(f"pin_window.py is {got[:12]}, not the pinned {EXPECT_PIN_WINDOW_SHA256[:12]}")
    sys.path.insert(0, str(CONTENT))
    sys.modules.pop("pin_window", None)
    import pin_window as pw  # noqa: E402

    pw.read_token_file(needed=True)  # the READ token, from /dev/shm, as every window reads it
    token = pw.take_token()
    if token is None:
        raise RuntimeError("no token file reached the VM")
    import huggingface_hub
    from huggingface_hub import HfApi, hf_hub_download

    try:
        import hf_xet  # noqa: F401
        result["hf_xet"] = getattr(hf_xet, "__version__", "present")
    except ImportError:
        result["hf_xet"] = None
    result["hub_version"] = huggingface_hub.__version__
    repo, rev = os.environ["PIN_GGUF_REPO"], os.environ["PIN_GGUF_REVISION"]
    spec = next(m for m in pw.MODELS if m["served_as"] == MODEL)
    name = pw.hosted_name(MODEL)
    info = HfApi(token=token).get_paths_info(repo, [name], revision=rev)[0]
    result["file"] = {"name": name, "size": info.size, "xet_hash": getattr(info, "xet_hash", None) is not None,
                      "lfs": getattr(info, "lfs", None) is not None}
    line(f"PROBE file {json.dumps(result['file'])} hub {result['hub_version']} hf_xet {result['hf_xet']}")
    watch = WORK / "hosted"
    box: dict = {}

    def run() -> None:
        try:
            box["path"] = hf_hub_download(repo, name, revision=rev, token=token, local_dir=watch)
        except BaseException as e:  # noqa: BLE001 - reported below
            box["error"] = e

    t0 = time.time()
    worker = threading.Thread(target=run, daemon=True)
    worker.start()
    while worker.is_alive():
        worker.join(timeout=10)
        w_size, w_alloc, w_n = tree(watch)
        x_size, x_alloc, x_n = tree(XET)
        free = pw.shutil.disk_usage(str(CONTENT)).free
        row = {"t": round(time.time() - t0, 1), "watch_bytes": w_size, "watch_alloc": w_alloc, "watch_files": w_n,
               "xet_bytes": x_size, "xet_alloc": x_alloc, "xet_files": x_n, "free": free}
        result["rounds"].append(row)
        line("PROBE " + json.dumps(row))
    token = None
    if "error" in box:
        raise box["error"]
    path = Path(box["path"])
    got = pw.sha256(path)
    result.update(seconds=round(time.time() - t0), sha256=got, reproduced=got == spec["expect_sha256"])
    result["ok"] = result["reproduced"]
    path.unlink(missing_ok=True)
except Exception as e:  # noqa: BLE001 - reported in pin-result.json
    result.update(ok=False, error=f"{type(e).__name__}: {e}")
finally:
    if pw is not None:
        result["token_clean"] = pw.token_clean()
    (WORK / "pin-result.json").write_text(json.dumps(result, indent=1))
    with LOG.open("a", encoding="utf-8") as f:
        f.write("PIN_RESULT " + json.dumps({k: v for k, v in result.items() if k != "rounds"}) + "\n")
