#!/usr/bin/env bash
# A fake colab CLI: one VM under /tmp/fakecolab/vm, a background "job" per FAKE_MODE.
ST=${FAKE_ST:-/tmp/fakecolab}; VM=$ST/vm; mkdir -p $VM/content/pin
job() {  # writes job.log on the "VM"
  L=$VM/content/pin/job.log
  case "$FAKE_MODE" in
    streamcut|normal) for i in $(seq 1 12); do echo "step $i" >> $L; sleep 1; done
                      echo '{"ok": true}' > $VM/content/pin/pin-result.json; echo 'PIN_RESULT {"ok": true}' >> $L;;
    jobstall) echo "step 1" >> $L; echo "step 2" >> $L;;
    cap|gone) while [ -d $VM ]; do echo "step" >> $L; sleep 1; done;;
  esac
}
case "$1" in
  usage) if [ -f $ST/open ]; then r=5.30; else r=0.00; fi; echo "Current balance: 100.00 compute units"; echo "Usage rate: $r/hr";;
  new) touch $ST/open; echo "[colab] Session READY.";;
  sessions) [ -f $ST/open ] && echo "[fake] fake | Hardware: A100"; true;;
  stop) rm -f $ST/open; echo "[colab] Session terminated.";;
  upload) echo ok;;
  download) shift; [ "$1" = -s ] && shift 2; [ -n "$FAKE_SLOW_DL" ] && [ "${1##*/}" != job.log ] && sleep 30; if [ -f $ST/open ] && [ -f "$VM$1" ]; then cp "$VM$1" "$2"; echo "[colab] Downloaded"; echo "$1" >> $ST/downloads; else echo "[colab] Download failed: $1"; fi;;
  exec) job & JP=$!
        case "$FAKE_MODE" in
          normal) wait $JP; cat $VM/content/pin/job.log;;
          gone) sleep 6; rm -f $ST/open; sleep 3600;;
          *) echo "first line only"; sleep 3600;;
        esac;;
esac
