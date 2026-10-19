#!/usr/bin/env bash
# Stub rung 5b driver (R&D, 2026-10-18), beside smoke_window.sh, which stays unchanged. From the rig in WSL Ubuntu:
#   PIN_STUB=1 PIN_SESSION=<s> PIN_*=... bash -l stub_rung.sh <pin_window.py> <out dir> <upload>...
# One Colab CPU session (0.08 units/hr). Uploads the inputs, then under one PIN_JOB_TOKEN:
#   exec A and exec B started 3 s apart: exactly one may run waves; the other must log a JOB ALREADY line
#     (the wait path if the kernel overlaps them, the up-front check if it queues them; the log says which);
#   exec C after both end: must stop at once on this window's pin-result.json.
# Then fetches job.log, pin-result.json and pilot-out.tar. The session is stopped in a trap and the list checked.
set -u
[ "${PIN_STUB:-0}" = 1 ] || { echo "REFUSED: stub_rung.sh runs PIN_STUB=1 only" >&2; exit 2; }
JOB="${1:?usage: stub_rung.sh <pin_window.py> <out dir> <upload>...}"
OUT="${2:?usage: stub_rung.sh <pin_window.py> <out dir> <upload>...}"
shift 2
S="${PIN_SESSION:?PIN_SESSION is required}"
WALL_S="${PIN_WALL_S:-900}"
mkdir -p "$OUT"
export COLUMNS=150
bal() { colab usage 2>&1 | grep -oP 'balance: \K[0-9.]+'; }
stop_all() {
  echo "stopping $S"; colab stop -s "$S" 2>&1 | tail -1
  sleep 5; echo "sessions after stop:"; colab sessions 2>&1 | tail -4
}
trap stop_all EXIT
START=$(bal); echo "start balance $START $(date -u +%FT%TZ)"
timeout 300 colab new -s "$S" 2>&1 | tail -2 || { echo "no CPU runtime assigned"; exit 2; }
sleep 10; colab usage 2>&1 | grep -E "rate|assign"
export PIN_JOB_TOKEN="$S-$(date +%s)"
echo "job token $PIN_JOB_TOKEN"
for f in "$@"; do
  ok=0
  for try in 1 2 3 4; do
    if timeout 600 colab upload -s "$S" "$f" "/content/$(basename "$f")" 2>&1 | tail -1 | grep -qv -i "fail\|error"; then ok=1; break; fi
    echo "upload of $(basename "$f") failed (try $try)"; sleep 10
  done
  [ "$ok" = 1 ] || { echo "UPLOAD FAILED: $(basename "$f")"; exit 3; }
  echo "uploaded $(basename "$f") $(sha256sum "$f" | cut -c1-16)"
done
ENV_ARGS=()
for v in $(compgen -e | grep '^PIN_' | grep -v -E '^PIN_(SESSION|WALL_S)$'); do ENV_ARGS+=(--env "$v=${!v}"); done
exec_one() {  # $1: the exec's name; its output goes to exec-<name>.log
  local t0=$(date +%s) rc
  timeout --signal=SIGINT --kill-after=30s "$WALL_S" colab exec -s "$S" "${ENV_ARGS[@]}" -f "$JOB" --timeout "$WALL_S" \
    > "$OUT/exec-$1.log" 2>&1
  rc=$?
  echo "exec $1 rc=$rc wall=$(( $(date +%s) - t0 ))s started=$(date -u -d @"$t0" +%T)"
}
exec_one A & PA=$!
sleep 3
exec_one B & PB=$!
wait $PA; wait $PB
exec_one C
for f in job.log pin-result.json pilot-out.tar; do
  timeout 300 colab download -s "$S" "/content/pin/$f" "$OUT/$f" 2>&1 | tail -1
done
echo "end balance $(bal) (start $START)"
