# xrpl-lab live-test harness

The Book Keeper used these scripts for the 2.6.0 AMM live-fire runs and the 2.6.1 sweeps (2026-10-20/21). The
receipts they produced are in xrpl-lab under `docs/receipts/2.6.0-amm-live-fire/`,
`docs/receipts/2.6.1-helper-wallet-sweep/` and `docs/receipts/2.6.1-release-sweep/`.

- **`sweep.sh <sha> <sweep-id> <gap-s> <module>...`** runs each module once, live on testnet, against the worktree
  at `WT`. For each module it:
  - checks that the worktree is at `<sha>`;
  - uses a fresh `XRPL_LAB_HOME` under `PAD`, which must be set to a scratch folder outside every repo and outside
    `xrpl-lab-runs` (wallet files live there, so it must never be ingested);
  - runs a preflight that the RPC/faucet env is unset, `classify_network` = testnet and the guard passes, and
    aborts the module if not;
  - runs `yes "" | xrpl-lab run <module>`, with the exit code from `PIPESTATUS[1]`;
  - copies state and report into `E:/AI/xrpl-lab-runs/<sweep-id>/<module>/`, writes the proof pack
    (`xrpl-lab proof-pack` → `proof_pack.json`), then runs `capture_sweep.py`.

  `LABEL=` names the branch in `command.txt`. Write `<module>@dry-run` to run a module offline:
  `xrpl-lab run` ignores a module's frontmatter `mode`, so a dry-run lesson needs the flag.
- **`capture_sweep.py <run-dir>`** does a read-only ledger capture: a `tx` lookup of every recorded or printed hash,
  plus `account_info` and `account_tx` for every printed address and every `Destination`. It reads no seeds.
- **`redact_tree.py <dir>`** replaces the local scratch path with `<scratch>` before files go into a receipt.
- **`run_f9.sh` / `capture_ledger.py`** are the original single-module AMM versions. Their paths are hard-coded to
  the 2026-10-20 session; `sweep.sh` supersedes them.

Before any push, run `python $USERPROFILE/.grok/bin/identity-scan.py <receipt-dir>` and grep for home paths. Wallet
files (`wallet.json`, `issuer_wallet.json`) never leave `PAD`.
