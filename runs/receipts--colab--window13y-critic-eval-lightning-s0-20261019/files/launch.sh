#!/usr/bin/env bash
# Window 13y = critic-signal, Lightning step 1, seed 0 (R&D's GO, 2026-10-19, conservative variant), per
# docs/drafts/critic-eval-lightning-step1-plan-2026-10-19.md: PIN_ROLE=critic-eval at role-set main 47a58822 on an A100,
# no stub, window1's llama-server sha-checked. Lightning isn't hosted: it converts in-window from its BF16 (a9904d24),
# byte-matched to its pin 5bea2069, as in 13t; no token is sent. Items cdce4a8a (inputs ead500b1): 55 scored, 11
# nemotron-family skips, 93 calls before retries. Projection 3.82 to 8.83 units; cap 13.82 (Muse's p90 31.3 s: 186 calls
# + 1,401 s setup, x1.3), wall 9400, margin 0.3. A3: 15.82 needed, 127.56 left of 300 (172.44 spent).
#   MSYS_NO_PATHCONV=1 wsl -d Ubuntu -e bash -l /mnt/e/AI/Publisher/receipts/colab/window13y-critic-eval-lightning-s0-20261019/launch.sh
set -uo pipefail
D=/mnt/e/AI/Publisher/receipts/colab/window13y-critic-eval-lightning-s0-20261019
cd "$D" || exit 2
check() { [ "$(sha256sum "$1" | cut -d' ' -f1)" = "$2" ] || { echo "REFUSED: $1 is not $2" >&2; exit 2; }; }
check critic-eval-inputs.tar.gz ead500b16c4ec9240cb05548abb86e1841cfe120ea81a2c1fde6ff4f322feee0
check pack.tar aa11101c9d47e45f3d5626342906090f5360dc2809da80c8318e6bdc21f90fbb
check card-values.json 36cd89bbd95f2918528ae40b6ebfc1b91c3f17daccc0db708f36251b0bc9e207
check pin_window.py d8f131e9b8ef92641bba82ff8a11183e454c04f4716f11a33af5acf09075df9d
check smoke_window.sh a74821aa2d6aef573277147f427dafb6f5d4f3b1559824ef1bf06eb3f977336d
check /mnt/e/AI/Publisher/receipts/colab/window1-20261016/build/llama-server b4659b3fc74037deb96b2148c455753121fa21dde174d7124547e2bf9ffd37c3
check vm_gate.py 2c5a02b7de78929de12312d2dcb10ef11505a06a1bc38c5f29f699a5622858c0
unset PIN_STUB PIN_STUB_CALL_S PIN_SKIP_BINARY PIN_ONLY PIN_HIGH_MEM PIN_CRITIC_EVAL_RESUME PIN_CRITIC_EVAL_ITEMS HF_TOKEN HF_TOKEN_GGUF_WRITE HF_TOKEN_GGUF_READ PIN_GGUF_REPO PIN_GGUF_REVISION PIN_HF_TOKEN_FROM
export PIN_GPU=A100 PIN_SESSION=pinw13y PIN_CAP_UNITS=13.82 PIN_CAP_MARGIN=0.3 PIN_WALL_S=9400
export PIN_GATE_MIN_DISK_GB=121 PIN_GATE_MIN_HF_MBPS=60
export PIN_ROLE=critic-eval
export PIN_ROLESET_COMMIT=47a58822d55a8bb498224797d71c37c82ca11a84
export PIN_RND_COMMIT=018b6cf677aab0e41363d826b589be342d38d8b9
export PIN_CRITIC_EVAL_CRITIC=nemotron-3.5-lightning-30b-a3b PIN_CRITIC_SEEDS=0
export PIN_CRITIC_EVAL_INPUTS=/content/critic-eval-inputs.tar.gz
export PIN_CRITIC_EVAL_SHAS=items.jsonl=cdce4a8adef288ea6e7503d4e7d2ae7923d7b3b68e8ac8a01df7aa73ede32f97
export PIN_UPLOADS="$D/pack.tar $D/card-values.json $D/critic-eval-inputs.tar.gz" PIN_DOWNLOADS="pin-result.json critic-eval-out.tar"
bash "$D/smoke_window.sh" /mnt/e/AI/Publisher/receipts/colab/window1-20261016/build/llama-server "$D" 2>&1 | tee "$D/rig.log"
