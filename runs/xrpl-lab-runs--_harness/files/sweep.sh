#!/usr/bin/env bash
# Live sweep: run each listed testnet module once on a pinned commit, one fresh XRPL_LAB_HOME per module.
# Usage: sweep.sh <expected-sha> <sweep-id> <gap-seconds> <module>[@dry-run]...
# Raw: E:/AI/xrpl-lab-runs/<sweep-id>/<module>/ ; wallet files stay under $PAD, never in the raw folder.
set -u
HDIR="$(cd "$(dirname "$0")" && pwd)"
EXPECT="$1"; SWEEP="$2"; GAP="$3"; shift 3
WT=/e/AI/_worktrees/xrpl-lab-f9-livefire
PAD="${PAD:?set PAD to a scratch folder outside every repo and outside xrpl-lab-runs (wallet files live there)}"
ROOT="/e/AI/xrpl-lab-runs/$SWEEP"
HEAD=$(git -C "$WT" rev-parse HEAD)
case "$HEAD" in "$EXPECT"*) ;; *) echo "ABORT: worktree at $HEAD, expected $EXPECT"; exit 2;; esac
mkdir -p "$ROOT"
unset XRPL_LAB_RPC_URL XRPL_LAB_FAUCET_URL
export PYTHONUTF8=1 COLUMNS=160
first=1
for SPEC in "$@"; do
  M="${SPEC%@dry-run}"; FLAGS=""
  [ "$M" != "$SPEC" ] && FLAGS="--dry-run"   # <module>@dry-run: xrpl-lab run ignores frontmatter mode
  [ $first -eq 1 ] || { echo "[sweep] spacing ${GAP}s for the faucet"; sleep "$GAP"; }
  first=0
  SCR="$PAD/$SWEEP/$M"; RUN="$ROOT/$M"
  mkdir -p "$SCR/home" "$SCR/cwd" "$RUN"
  export XRPL_LAB_HOME; XRPL_LAB_HOME="$(cygpath -w "$SCR/home")"
  cd "$SCR/cwd"
  "$WT/.venv/Scripts/python.exe" - > "$RUN/preflight.txt" <<'EOF'
import os
from xrpl_lab.transport.xrpl_testnet import get_rpc_url, get_faucet_url, classify_network, XRPLTestnetTransport
from xrpl_lab.state import get_home_dir
t = XRPLTestnetTransport(); g = t._network_guard()
print("XRPL_LAB_RPC_URL set:", "XRPL_LAB_RPC_URL" in os.environ)
print("XRPL_LAB_FAUCET_URL set:", "XRPL_LAB_FAUCET_URL" in os.environ)
print("rpc_url:", get_rpc_url()); print("faucet_url:", get_faucet_url())
print("classify_network(rpc):", classify_network(get_rpc_url()))
print("network_guard:", g or "PASS (no refusal)")
print("home_is_scratch:", "scratch" in str(get_home_dir()))
if g or classify_network(get_rpc_url()) != "testnet" or "scratch" not in str(get_home_dir()):
    raise SystemExit("PREFLIGHT FAILED")
EOF
  if [ $? -ne 0 ]; then echo "[sweep] $M ABORT: preflight failed"; echo "PREFLIGHT_FAILED" > "$RUN/exit_code"; continue; fi
  { echo "cwd: <scratch>/$SWEEP/$M/cwd  (outside every repo)"
    echo "XRPL_LAB_HOME=<scratch>/$SWEEP/$M/home   (wallet.json stays here, never copied)"
    echo "XRPL_LAB_RPC_URL=<unset>  XRPL_LAB_FAUCET_URL=<unset>  PYTHONUTF8=1"
    echo "code: mcp-tool-shop-org/xrpl-lab @ ${HEAD:0:7} (${LABEL:-v2.6.0}), worktree _worktrees/xrpl-lab-f9-livefire"
    echo "cmd:  yes \"\" | xrpl-lab run $FLAGS $M"
    echo "started_utc: $(date -u +%Y-%m-%dT%H:%M:%SZ)"; } > "$RUN/command.txt"
  yes "" | timeout 900 "$WT/.venv/Scripts/xrpl-lab.exe" run $FLAGS "$M" > "$RUN/stdout.txt" 2> "$RUN/stderr.txt"
  RC=${PIPESTATUS[1]}
  echo "xrpl_lab_exit_code: $RC   (read from PIPESTATUS[1])" >> "$RUN/command.txt"
  echo "finished_utc: $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$RUN/command.txt"
  echo "$RC" > "$RUN/exit_code"
  cp "$SCR/home/state.json" "$RUN/state.json" 2>/dev/null
  cp "$SCR/cwd/.xrpl-lab/reports/$M.md" "$RUN/module_report.md" 2>/dev/null
  "$WT/.venv/Scripts/xrpl-lab.exe" proof-pack > "$RUN/proof_pack.log" 2>&1
  cp "$SCR/cwd/.xrpl-lab/proofs/xrpl_lab_proof_pack.json" "$RUN/proof_pack.json" 2>/dev/null
  "$WT/.venv/Scripts/python.exe" -I "$HDIR/capture_sweep.py" "$RUN" > "$RUN/capture.log" 2>&1
  echo "[sweep] $M exit=$RC  $(grep -h '^Steps:' "$RUN/module_report.md" 2>/dev/null)  $(grep -h '^Transactions:' "$RUN/module_report.md" 2>/dev/null | tail -1)"
done
echo "[sweep] done"
