# Window 13r: a dead kernel with the stall at 600 s, 2026-10-18

**Result: pass.** After role-set #92 (`69fc18a`, merged as `b3b75b0`), a job whose kernel dies ends its window
**10–12 minutes** after the death. Before, it took 20–22 minutes. The bound is `PIN_STALL_S` (600 s) plus up to one
watcher poll (`PIN_WATCH_S`, 120 s): the stall counts from the last growth of job.log the watcher saw, not from the last
line the job wrote.

## What ran

- A CPU window (0.08/hr) through `smoke_window.sh` at `69fc18a`, with the stall at its new default of 600 s.
- The job was `mock_job.py`: a job.log line every 30 s, then `os._exit(137)` at 300 s, which kills the kernel itself, as
  an OOM kill would. It's the same as window 13q, which ran with the old 1200 s stall.
- Cap 0.1, margin 0.01, wall 3000 s.

## What happened

| | 13q (stall 1200 s) | 13r (stall 600 s) |
|---|---|---|
| Kernel killed | 18:21:59 | 20:16:26 |
| STALL | 18:43:22 | 20:27:40 |
| Death to stall | 21 min 23 s | 11 min 14 s |

- As in 13q, `colab status` read the exec as busy and the exec never returned, so the stall is what ends the window.
- `exec exit=124`, `end=stall`. job.log was saved (10 steps, then "mock kernel killed"); there was no pin-result, as
  expected. The session list was empty after the stop.
- Cost: 0.02 units (0.08/hr × ~17 min). The balance went 1141.08 → 1141.06; the study stands at 161.23.

The handbook gets the 10–12 minute bound in R&D's next batch of page changes.
