# Window 13u: how a Xet download writes, 2026-10-19

**Result: `with_heartbeat`'s signal holds for Xet downloads, so no fix is needed.** A real Xet-backed download from the
private repo wrote its bytes steadily into the download's own folder. It did not preallocate, and almost nothing went
to the Xet cache.

This answers Argon's critic-signal reply, item 6(d), which asked whether Xet writes would hide progress from the
heartbeat.

## What ran

- A CPU `--high-mem` VM. `probe_xet_signal.py` imported role-set main's `pin_window.py` (`3b9609c`, sha256 `27b8f860`)
  and read the READ token from `/dev/shm`, as windows do.
- It downloaded `qwen3.8-27b`'s hosted Q8_0 (29,047,084,448 bytes) from the private repo at `d847f5b8`, in a worker
  thread, as `prefetch_hosted` does. `HF_XET_CACHE` was set to `/content/xet-cache`, outside the download folder.
- The file is Xet-backed: it has a `xet_hash`, `hf_xet` is present, and the hub is 1.33.0.
- Every 10 s the probe logged the bytes and the allocated bytes (`st_blocks × 512`) under each place, and free disk.

## The record (job.log, PROBE lines)

| t (s) | download folder, bytes | allocated | Xet cache, bytes | free disk (GB) |
|---|---|---|---|---|
| 10 | 3,148,058,816 | 3,148,070,912 | 186,585 | 217.3 |
| 20 | 6,595,117,248 | 6,595,133,440 | 322,963 | 213.9 |
| 30 | 10,180,772,032 | 10,180,788,224 | 431,736 | 210.3 |
| 40 | 13,931,921,600 | 13,931,933,696 | 542,741 | 206.5 |
| 50 | 17,554,870,464 | 17,554,882,560 | 637,545 | 202.9 |
| 60 | 21,123,764,416 | 21,123,776,512 | 747,139 | 199.3 |
| 70 | 24,396,013,760 | 24,396,025,856 | 851,610 | 196.1 |
| 80 | 28,268,867,776 | 28,268,879,872 | 906,707 | 192.2 |
| 82.4 | 29,047,084,765 | 29,047,103,488 | 907,105 | 191.4 |

- **Steady growth:** about 3.5 GB every 10 s, roughly 350 MB/s.
- **No preallocation:** the allocated bytes track the real bytes at every reading.
- **The Xet cache stays tiny:** it holds under 1 MB of metadata, and the chunks are not stored there.
- **Free disk falls in step** with the download.
- Argon's "double count" doesn't arise: the file is written in the download folder's `.cache` and renamed into place
  (4 files, then 5 at the end), with no jump.

## Checks and cost

- sha256 `2ab268e0…` equals the pin, and the file was deleted afterwards.
- `token_clean` was all true. The session list was empty after the stop.
- One run only: 9 PROBE lines and one result.
  - The watcher's "EXEC NEVER STARTED, re-running once" line was a false alarm I caused. The probe writes nothing until
    its first 10 s round (after the hub import and a metadata call), so the watcher's first look found an empty
    job.log.
  - A probe should write a line at its very start.
- Cost: about 0.03 units (0.26/hr × ~7 min). The balance went 1136.54 → 1136.53. The study stands at 165.88 of 300.
