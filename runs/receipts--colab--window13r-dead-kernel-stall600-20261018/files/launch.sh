#!/usr/bin/env bash
# Window 13r = the dead-kernel window again, after role-set #92 (69fc18a22bb5e032a383979eba64c31e9e2a64d8): the stall now defaults to 600 s. CPU (0.08/hr),
# mock_job writes a job.log line every 30 s and kills its kernel at 300 s, as an OOM kill would. 13q showed colab status
# stays BUSY and the exec hangs, so the stall is the only guard: acceptance is STALL about 10 minutes after the death (13q:
# 20). Cap 0.1 with 0.01 kept back (450 s at 0.08/hr holds the 60 s grace and the 120 s fetch). About 0.03 units.
#   MSYS_NO_PATHCONV=1 wsl -d Ubuntu -e bash -l /mnt/e/AI/Publisher/receipts/colab/window13r-dead-kernel-stall600-20261018/launch.sh
set -uo pipefail
D=/mnt/e/AI/Publisher/receipts/colab/window13r-dead-kernel-stall600-20261018
cd "$D" || exit 2
check() { [ "$(sha256sum "$1" | cut -d' ' -f1)" = "$2" ] || { echo "REFUSED: $1 is not $2" >&2; exit 2; }; }
check smoke_window.sh fabc476066a13bf5d5102d0763f8083ccc8d01e1bb1d085653ca32a0d8b24b43
check mock_job.py 98f73e3c69a72014afcf11017d9b0db14cc81a2e83723f4912caeeb13142eaa8
unset PIN_STUB PIN_STUB_CALL_S PIN_STALL_S HF_TOKEN HF_TOKEN_GGUF_WRITE HF_TOKEN_GGUF_READ PIN_GGUF_REPO PIN_HF_TOKEN_FROM
export PIN_GPU=CPU PIN_SESSION=dead13r PIN_CAP_UNITS=0.1 PIN_CAP_MARGIN=0.01 PIN_WALL_S=3000 PIN_SKIP_BINARY=1 PIN_ROLESET_COMMIT=69fc18a22bb5e032a383979eba64c31e9e2a64d8
export PIN_JOB_SCRIPT=mock_job.py PIN_MOCK_S=1800 PIN_MOCK_EVERY_S=30 PIN_MOCK_DIE_AFTER_S=300 PIN_DOWNLOADS=pin-result.json
export PIN_GATE_MIN_HF_MBPS=60 PIN_GATE_MIN_RAM_GB=8
bash "$D/smoke_window.sh" /dev/null "$D" 2>&1 | tee "$D/rig.log"
