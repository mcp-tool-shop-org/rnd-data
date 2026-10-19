#!/usr/bin/env bash
# Prebuilds after 13f (R&D's ruling (a), 2026-10-18): Gemma 4 on CPU --high-mem (own venv, torch +cpu as on its pin's
# host); then Qwen3.8 and Granite 4.2 on an A100, whose image's system python (torch 2.11.0+cu130) made their pins.
# One window at a time, cc71286's scripts; each must report ok, reproduced and uploaded at its expect_sha256, or the
# chain stops there. A100 windows: cap 3, gate HF floor 60 (R&D: the gate's 200 MB short read undersells the pipe
# about 2.7x; 60 still rejects a truly slow one), disk floor = conversion peak + 20 GB. From Git Bash:
#   bash /e/AI/Publisher/receipts/colab/prebuild_chain2.sh
set -uo pipefail
R=/e/AI/Publisher/receipts/colab
SRC=$R/window13e-prebuild-muse-20261018
HF_TOKEN_GGUF_WRITE="$(powershell.exe -NoProfile -Command "[Environment]::GetEnvironmentVariable('HF_TOKEN_GGUF_WRITE','User')" | tr -d '\r\n')"
export HF_TOKEN_GGUF_WRITE WSLENV=HF_TOKEN_GGUF_WRITE
# served_as | window | gpu | cap | disk floor GB | expected sha256
for row in "gemma-4-31b-it|13g|CPU|1|117|e357a45071c2cbbc44b97506dfadc34bac0d5f6592f1d500edfaa9647f01e7bf" \
           "qwen3.8-27b|13i|A100|3|105|2ab268e0bd3f8e5daf1280e2243ac19abd5e3bb34e8444f5cfff5147fab977d4" \
           "granite-4.2-30b|13j|A100|3|110|1b5c47835f6f8b8732550541dc432d0a351e3f706961ff3c750d3ee1987b9b4c"; do
  IFS='|' read -r model win gpu cap floor want <<< "$row"
  D=$R/window$win-prebuild-${model%%-*}-$( [ "$gpu" = A100 ] && echo a100- )20261018
  mkdir -p "$D"
  cp "$SRC"/{smoke_window.sh,pin_window.py,vm_gate.py,apache-2.0.txt} "$D/"
  hm=1; [ "$gpu" = A100 ] && hm=0
  sed -e "s#window13e-prebuild-muse-20261018#$(basename "$D")#g" \
      -e "s#PIN_ONLY=muse-glimmer-30b#PIN_ONLY=$model#" \
      -e "s#PIN_GPU=CPU PIN_HIGH_MEM=1#PIN_GPU=$gpu PIN_HIGH_MEM=$hm#" \
      -e "s#PIN_SESSION=pb-muse#PIN_SESSION=pb-${model%%-*}-${gpu,,}#" \
      -e "s#PIN_CAP_UNITS=1#PIN_CAP_UNITS=$cap#" \
      -e "s#PIN_GATE_MIN_DISK_GB=111#PIN_GATE_MIN_DISK_GB=$floor#" \
      -e "s#Prebuild 1 of 4: Muse#Prebuild ($model on $gpu)#" \
      -e "s#expect_sha256 c321320a...#expect_sha256 ${want:0:8}...#" "$SRC/launch.sh" > "$D/launch.sh"
  echo "== $model on $gpu -> $(basename "$D") $(date -u +%T)"
  MSYS_NO_PATHCONV=1 wsl -d Ubuntu -e bash -l "/mnt/e/AI/Publisher/receipts/colab/$(basename "$D")/launch.sh" > /dev/null 2>&1
  verdict=$(python -I - "$D/pin-result.json" "$want" <<'PY'
import json, sys
try:
    r = json.load(open(sys.argv[1], encoding="utf-8"))
except Exception as e:
    print(f"FAIL no pin-result ({type(e).__name__})"); sys.exit()
u, m = r.get("uploaded") or {}, (r.get("models") or [{}])[0]
ok = r.get("ok") and m.get("reproduced") and m.get("gguf_sha256") == sys.argv[2] and u.get("sha256") == sys.argv[2]
print(("OK commit " + str(u.get("commit")) + " files " + ",".join(u.get("files") or [])) if ok
      else f"FAIL ok={r.get('ok')} reproduced={m.get('reproduced')} sha={str(m.get('gguf_sha256'))[:12]} error={str(r.get('error'))[:160]}")
PY
)
  echo "$model: $verdict"
  grep -E "own rate|end balance|exec exit|VM gate" "$D/rig.log" | sed 's/^/   /'
  case "$verdict" in OK*) ;; *) echo "CHAIN STOPPED at $model"; exit 1;; esac
done
echo "CHAIN DONE $(date -u +%T)"
