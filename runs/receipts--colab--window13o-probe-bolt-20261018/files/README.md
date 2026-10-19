# Window 13o: the Bolt fetch probe, 2026-10-18

**Result: pass.** No implicit Hub token is looked up any more. Bolt's public download went straight to the Hub, with
no token and no wait.

## What ran

- A CPU `--high-mem` window (0.26/hr) through `smoke_window.sh`, with `probe_bolt_fetch.py` as the job. No token
  variable reached the VM.
- The probe imported role-set #91's `pin_window.py` at `eb990bc` (sha256 `dc204e19…`, checked before import), then
  called the real `pw.fetch_model` for Bolt: `HfApi(token=False).list_repo_files`, then
  `hf_hub_download(token=False)`.

## Acceptance (from job.log)

| Check | W-A (13l), before #91 | 13o |
|---|---|---|
| "Error while fetching `HF_TOKEN` secret" line | present (the vault lookup timed out) | absent |
| unauthenticated-requests warning | present | absent |
| "before download" to "downloading" | 11 s (12:58:53 → 12:59:04) | 0 s (18:12:34 → 18:12:34) |
| Bolt's sha256 equals its pin `91d63363…` | yes | yes |

## Also recorded

- **Implicit token record:**
  - before `pin_window` was imported, `HF_HUB_DISABLE_IMPLICIT_TOKEN` was not set and `huggingface_hub` had not been
    imported;
  - after the import, the env read `1` and the module constant read `True`.
- **The kernel's `huggingface_hub` is 1.33.0.** The converter's install puts 0.36.2 on disk (13i), and the upload child
  runs whatever is on disk. The implicit-token switch held on 1.33.0. The hub-version difference goes into the next
  study's pin list (R&D).
- **Download speed:** 22.0 GB (22,018,326,528 bytes) in 61 s, about 360 MB/s, single file.
- **Cost:** about 0.01 units (0.26/hr × ~3 min). The balance was unchanged at 1141.11.
- **One fault of mine:** the probe's launch didn't export `PIN_ROLESET_COMMIT`, so its outcome draft said "unset";
  outcome.json carries `eb990bc`.
