#!/usr/bin/env bash
# Window 13q = the dead-kernel window (R&D, 2026-10-18; #91 at eb990bc09b93c2bb7a32a0ff3f606cf031c04d60). CPU (0.08/hr), mock_job writes a job.log line
# every 30 s and dies with its kernel at 300 s (PIN_MOCK_DIE_AFTER_S), leaving no result while the exec hangs. The
# watcher must end the window as "died" at two IDLE checks (PIN_WATCH_S 120 here, so within about 4 minutes of the
# death), not at the 20-minute stall. outcome.draft.json records end "died". Cap 0.1 with 0.01 kept back (450 s at 0.08/hr holds the grace and the fetch): deadline at about 68 min, far past the death. About 0.02 units.
#   MSYS_NO_PATHCONV=1 wsl -d Ubuntu -e bash -l /mnt/e/AI/Publisher/receipts/colab/window13q-dead-kernel-20261018/launch.sh
set -uo pipefail
D=/mnt/e/AI/Publisher/receipts/colab/window13q-dead-kernel-20261018
cd "$D" || exit 2
check() { [ "$(sha256sum "$1" | cut -d' ' -f1)" = "$2" ] || { echo "REFUSED: $1 is not $2" >&2; exit 2; }; }
check smoke_window.sh fcb5aeffda24a20b0074600ad03fed32475d57dd1e51ecda1f4e92fe3545a991
check mock_job.py 98f73e3c69a72014afcf11017d9b0db14cc81a2e83723f4912caeeb13142eaa8
unset PIN_STUB PIN_STUB_CALL_S HF_TOKEN HF_TOKEN_GGUF_WRITE HF_TOKEN_GGUF_READ PIN_GGUF_REPO PIN_HF_TOKEN_FROM
export PIN_GPU=CPU PIN_SESSION=dead13q PIN_CAP_UNITS=0.1 PIN_CAP_MARGIN=0.01 PIN_WALL_S=3000 PIN_SKIP_BINARY=1 PIN_ROLESET_COMMIT=eb990bc09b93c2bb7a32a0ff3f606cf031c04d60
export PIN_JOB_SCRIPT=mock_job.py PIN_MOCK_S=1800 PIN_MOCK_EVERY_S=30 PIN_MOCK_DIE_AFTER_S=300 PIN_DOWNLOADS=pin-result.json
export PIN_GATE_MIN_HF_MBPS=60 PIN_GATE_MIN_RAM_GB=8
bash "$D/smoke_window.sh" /dev/null "$D" 2>&1 | tee "$D/rig.log"
