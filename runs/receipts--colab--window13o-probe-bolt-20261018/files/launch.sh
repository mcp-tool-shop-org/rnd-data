#!/usr/bin/env bash
# Window 13o = the Bolt fetch probe (R&D, 2026-10-18; W-A consult Q1's acceptance). CPU --high-mem, no token variable.
# smoke_window runs probe_bolt_fetch.py as the job (as mock_job.py); it imports #91's pin_window.py (eb990bc09b93c2bb7a32a0ff3f606cf031c04d60, uploaded
# beside it and checked by sha256) and calls the real pw.fetch_model for Bolt (HfApi(token=False), then
# hf_hub_download(token=False)). Acceptance from job.log: no "Error while fetching HF_TOKEN secret", no
# unauthenticated-requests warning, under 2 s from "before download" to "downloading", Bolt's sha equal to its pin.
# 22 GB at 100-250 MB/s: a few minutes, about 0.03 units. Cap 0.3 with 0.03 kept back (415 s at 0.26/hr): deadline at about 62 min.
#   MSYS_NO_PATHCONV=1 wsl -d Ubuntu -e bash -l /mnt/e/AI/Publisher/receipts/colab/window13o-probe-bolt-20261018/launch.sh
set -uo pipefail
D=/mnt/e/AI/Publisher/receipts/colab/window13o-probe-bolt-20261018
cd "$D" || exit 2
check() { [ "$(sha256sum "$1" | cut -d' ' -f1)" = "$2" ] || { echo "REFUSED: $1 is not $2" >&2; exit 2; }; }
check pin_window.py dc204e1922afd9cb11ec7e437348b478c0e90f3b1c79de47f341c7c96e8f091b
grep -q "EXPECT_PIN_WINDOW_SHA256 = \"dc204e1922afd9cb11ec7e437348b478c0e90f3b1c79de47f341c7c96e8f091b\"" probe_bolt_fetch.py || { echo "REFUSED: the probe's pin isn't dc204e1922afd9cb11ec7e437348b478c0e90f3b1c79de47f341c7c96e8f091b" >&2; exit 2; }
unset PIN_STUB PIN_STUB_CALL_S HF_TOKEN HF_TOKEN_GGUF_WRITE HF_TOKEN_GGUF_READ PIN_GGUF_REPO PIN_GGUF_REVISION PIN_HF_TOKEN_FROM
export PIN_GPU=CPU PIN_HIGH_MEM=1 PIN_SESSION=probe13o PIN_CAP_UNITS=0.3 PIN_CAP_MARGIN=0.03 PIN_WALL_S=3000 PIN_SKIP_BINARY=1
export PIN_JOB_SCRIPT=probe_bolt_fetch.py PIN_DOWNLOADS=pin-result.json PIN_STALL_S=1200
export PIN_GATE_MIN_RAM_GB=40 PIN_GATE_MIN_HF_MBPS=60 PIN_GATE_MIN_DISK_GB=50
export PIN_UPLOADS="$D/pin_window.py"
bash "$D/smoke_window.sh" /dev/null "$D" 2>&1 | tee "$D/rig.log"
