#!/usr/bin/env bash
# Launch stub rung 5b for one layout (R&D-approved env, 2026-10-18): bash -l stub_rung_launch.sh WA|WB
set -u
L="${1:?WA or WB}"
R=/mnt/e/AI/Publisher/receipts/colab
case "$L" in
  WA) D=$R/window12s6a-20261018; export PIN_SESSION=pinw12s6a
      export PIN_PILOT_WRITERS=qwen3.8-27b,gemma-4-31b-it,granite-4.2-30b,nemotron-3.5-bolt-74b-a9b
      export PIN_PILOT_CRITIC=muse-glimmer-30b
      WANT=3d8b7ed583a3d23ace92c9263a7d59e006f06dc246adabf27e5d66dbdd7f15c1
      WANT_PRIOR=ed8263776dc09b7e64688b37bcd097b415740895aafdc83beb2abc6bf23efc50 ;;
  WB) D=$R/window12s6b-20261018; export PIN_SESSION=pinw12s6b
      export PIN_PILOT_WRITERS=nemotron-3.5-lightning-30b-a3b,muse-glimmer-30b
      export PIN_PILOT_CRITIC_FOR=nemotron-3.5-lightning-30b-a3b=muse-glimmer-30b,muse-glimmer-30b=nemotron-3.5-lightning-30b-a3b
      WANT=1f5348940987c7facfb64b564a87c936c86d187f58603853d7e3b2ff0d4eec45
      WANT_PRIOR=2b49f6ac54e967a81342ff60cac76ed545ae047275ada2036d5d2ecb9d8aba5e ;;
  *) echo "WA or WB" >&2; exit 2 ;;
esac
[ "$(sha256sum "$D/resume.tar" | cut -d' ' -f1)" = "$WANT" ] || { echo "REFUSED: $D/resume.tar is not $WANT" >&2; exit 2; }
[ "$(sha256sum "$D/prior.tar" | cut -d' ' -f1)" = "$WANT_PRIOR" ] || { echo "REFUSED: $D/prior.tar is not $WANT_PRIOR" >&2; exit 2; }
export PIN_STUB=1 PIN_ROLE=pilot PIN_PILOT_WAVES=4 PIN_RESUME_WAVE=1 PIN_RESUME_DIR=/content/resume/pilot-w1
export PIN_ROLESET_COMMIT=c1cf4ae2caba722bf59cf79571bfc2fa4e558642
export PIN_RESUME_PRIOR_DIR=/content/prior/pilot-w0
export PIN_RND_COMMIT=018b6cf677aab0e41363d826b589be342d38d8b9
export PIN_PILOT_SLOT_IDS=T02-A-01,T02-C-01,T02-D-01,T02-E-01,T02-B-01,T02-A-02,T02-C-08,T02-D-05
export PIN_PILOT_TWIN_IDS=T04-C-AP-01,T04-D-AP-02
unset PIN_PILOT_TWINS
bash "$D/stub_rung.sh" "$D/pin_window.py" "$D" "$D/pack.tar" "$D/card-values.json" "$D/resume.tar" "$D/prior.tar" 2>&1 | tee "$D/rig.log"
