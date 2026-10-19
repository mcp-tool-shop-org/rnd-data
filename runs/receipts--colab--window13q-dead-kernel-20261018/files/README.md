# Window 13q: a dead kernel on real Colab, 2026-10-18

**Finding:** when the job's kernel dies, `colab status` keeps reading the exec as busy, and the exec never returns.
The only guard against a dead kernel is the stall on job.log: 20 minutes by default.

## What ran

- A CPU window (0.08/hr) through `smoke_window.sh` at role-set #91 `eb990bc`. The job was `mock_job.py`, which wrote
  a job.log line every 30 s, then at 300 s called `os._exit(137)`. Inside the kernel, that kills the kernel process
  itself, as an OOM kill would.
- Cap 0.1, margin 0.01, wall 3000 s.

## What happened

- job.log: 10 mock steps from 18:16:59, then "mock kernel killed" at 18:21:59. Nothing after it.
- `status.log` read `Status: BUSY (exec(…/mock_job.py))` at every check: 11 reads from 18:23:03 to 18:43:22.
- The exec never returned. The 20-minute stall ended the window at 18:43:22 (`end=stall`), with job.log saved.
- No pin-result.json, as expected. The session list was empty after the stop.
- Cost: 0.04 units (0.08/hr × ~27 min). The balance went 1141.11 → 1141.08.

## What it changed

- **#91 had a rule** that ended a window when the kernel read IDLE twice with no PIN_RESULT. It had passed only against
  the fake colab CLI, whose `status` I wrote to drop BUSY when the job ended. On real Colab, `status` follows the
  CLI's exec, not the kernel, so the rule could never fire. It was removed before merge (R&D, option (a)), with a
  comment at the stall check recording this window. Mistakes log #39.
- **Follow-up (R&D):** a shorter stall, a separate PR.
  - Audit every silent in-process step: the prefetch download, `snapshot_download`, the 30 GB sha256, the Q6_K path.
  - Give any step that can exceed 10 minutes a heartbeat tied to its own loop.
  - Then set `PIN_STALL_S` to about twice the heartbeat, and prove it with a CPU death run like this one.
- **A liveness channel** (for example whether `colab ls` can see the job's `/proc` entry) stays parked until a probe
  shows one exists.
