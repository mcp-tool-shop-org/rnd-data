#!/usr/bin/env bash
# Window 13p = the deadline rung at role-set eb990bc09b93c2bb7a32a0ff3f606cf031c04d60 (#91; R&D, 2026-10-18). W-A's layout as a stub on CPU --high-mem,
# no private repo (13m proved the prefetch; token_clean still runs on the no-repo branch). PIN_STUB_CALL_S=30 makes each
# stub call take 30 s, so the waves run from about minute 3 to minute 34. Cap 0.07 with 0.03 kept back puts the
# deadline about 9.2 min after the session opens (0.04 units at 0.26/hr), mid-wave. It measures: cut_at_deadline (arm,
# label), the seconds from the deadline to PIN_RESULT (the cut, the tar, the result), and the exit fetch's seconds.
# Budget: 0.03 at 0.26/hr is 415 s, which holds the 180 s grace and the 90 s fetch allowance. About 0.07 units.
#   MSYS_NO_PATHCONV=1 wsl -d Ubuntu -e bash -l /mnt/e/AI/Publisher/receipts/colab/window13p-rung-deadline-20261018/launch.sh
set -uo pipefail
D=/mnt/e/AI/Publisher/receipts/colab/window13p-rung-deadline-20261018
cd "$D" || exit 2
check() { [ "$(sha256sum "$1" | cut -d' ' -f1)" = "$2" ] || { echo "REFUSED: $1 is not $2" >&2; exit 2; }; }
check resume.tar 3d8b7ed583a3d23ace92c9263a7d59e006f06dc246adabf27e5d66dbdd7f15c1
check prior.tar ed8263776dc09b7e64688b37bcd097b415740895aafdc83beb2abc6bf23efc50
check pack.tar aa11101c9d47e45f3d5626342906090f5360dc2809da80c8318e6bdc21f90fbb
check card-values.json 36cd89bbd95f2918528ae40b6ebfc1b91c3f17daccc0db708f36251b0bc9e207
check pin_window.py dc204e1922afd9cb11ec7e437348b478c0e90f3b1c79de47f341c7c96e8f091b
unset PIN_PILOT_TWINS PIN_ONLY PIN_PILOT_CRITIC_FOR HF_TOKEN HF_TOKEN_GGUF_WRITE HF_TOKEN_GGUF_READ PIN_GGUF_REPO PIN_GGUF_REVISION PIN_HF_TOKEN_FROM
export PIN_STUB=1 PIN_STUB_CALL_S=30 PIN_GPU=CPU PIN_HIGH_MEM=1 PIN_SESSION=pinw13p PIN_WALL_S=1800
export PIN_CAP_UNITS=0.07 PIN_CAP_MARGIN=0.03
export PIN_SKIP_BINARY=1 PIN_STALL_S=2400 PIN_GATE_MIN_RAM_GB=40 PIN_GATE_MIN_HF_MBPS=60
export PIN_ROLE=pilot
export PIN_ROLESET_COMMIT=eb990bc09b93c2bb7a32a0ff3f606cf031c04d60
export PIN_RND_COMMIT=018b6cf677aab0e41363d826b589be342d38d8b9
export PIN_PILOT_WRITERS=qwen3.8-27b,gemma-4-31b-it,granite-4.2-30b,nemotron-3.5-bolt-74b-a9b
export PIN_PILOT_CRITIC=muse-glimmer-30b
export PIN_PILOT_SLOT_IDS=T02-A-01,T02-C-01,T02-D-01,T02-E-01,T02-B-01,T02-A-02,T02-C-08,T02-D-05
export PIN_PILOT_TWIN_IDS=T04-C-AP-01,T04-D-AP-02
export PIN_PILOT_WAVES=4 PIN_RESUME_WAVE=1
export PIN_RESUME_DIR=/content/resume/pilot-w1 PIN_RESUME_PRIOR_DIR=/content/prior/pilot-w0
export PIN_UPLOADS="$D/pack.tar $D/card-values.json $D/resume.tar $D/prior.tar"
bash "$D/smoke_window.sh" /dev/null "$D" 2>&1 | tee "$D/rig.log"
