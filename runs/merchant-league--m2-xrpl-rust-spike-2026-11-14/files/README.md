# M2 spike: xrpl-rust 1.3.0 on XRPL Testnet, 2026-11-14

The spike asked one question: can `xrpl-rust` 1.3.0 build, sign and submit every transaction Merchant League needs, on the live Testnet? It can: all ten transaction types worked, and the final ledger state matched the prediction exactly.

**But it cannot be adopted as it stands.** It carries a vulnerable dependency that has no fixed version it can use, and the repository's rule is that advisories are fixed by upgrading, never ignored. See "Why it is not adopted".

- **Code:** `testnet_spike.rs.txt` in this folder, run as an example of `league-ledger` on the branch `m2/testnet-spike`, based on `bd8a15b` (`raw/00_snapshot.txt`). It is kept here as evidence and is **not compiled**; xrpl-rust was taken back out of the build after the run.
- **Network:** the public Testnet, through `league-ledger`'s endpoints and its `require_testnet` guard (`network_id` 1, rippled 3.4.1).
- **Accounts:** two faucet accounts, an issuer and a merchant. Their seeds stayed in memory and were never printed or saved. The addresses below are public Testnet addresses.
- **Redaction:** local paths in the raw files read `<home>` or `<worktree>`.

## Verdict

**Works, not adopted.** Every step succeeded and validated; a deliberately wrong reveal was rejected by the ledger as designed. The library fails the security audit for reasons it cannot fix in its 1.x or 2.x line.

## What ran

| Step | Transaction | Result | Ledger |
| --- | --- | --- | --- |
| Network guard | `server_info` | `network_id` 1, accepted | |
| Issuer allows clawback | `AccountSet` (asfAllowTrustLineClawback) | `tesSUCCESS` | 22,311,281 |
| Issuer default ripple | `AccountSet` (asfDefaultRipple) | `tesSUCCESS` | 22,311,282 |
| Merchant trusts the issuer | `TrustSet` MRK, limit 1,000 | `tesSUCCESS` | 22,311,284 |
| Issuer pays 100 MRK | `Payment` | `tesSUCCESS` | 22,311,286 |
| An offer on the order book | `OfferCreate` 10 MRK for 1 XRP | `tesSUCCESS` | 22,311,288 |
| Its cancel | `OfferCancel` | `tesSUCCESS` | 22,311,290 |
| A contract | `CheckCreate` 5 MRK, issuer to merchant | `tesSUCCESS` | 22,311,292 |
| Delivery | `CheckCash` 5 MRK | `tesSUCCESS` | 22,311,294 |
| Dice commitment | `EscrowCreate`, locked to a secret's PREIMAGE-SHA-256 condition | `tesSUCCESS` | 22,311,296 |
| Reveal with the wrong secret | `EscrowFinish` | **`tecCRYPTOCONDITION_ERROR`**, validated | 22,311,298 |
| Reveal with the right secret | `EscrowFinish` | `tesSUCCESS` | 22,311,300 |
| Clawback | `Clawback` 3 MRK | `tesSUCCESS` | 22,311,302 |

Every transaction above is in a validated ledger (`raw/02_merchant_account_tx.json`, read back from the Testnet after the run). The condition and fulfillment came from `league-dice`'s encoding, tested against xrpl.org's example and an independent encoding.

**Final state, read from the validated ledger** (`raw/01_spike.out`, last line):

- Merchant's MRK balance: **102**. Predicted 100 + 5 − 3 = 102.
- Escrows, checks and offers left: **0** each.

## What the spike showed about the library

1. **Every transaction type the game needs is there**, and builds, signs and submits on the first try, including the crypto-condition escrow and clawback.
2. **A `tec` result comes back as an error, without the transaction's hash.** The wrong-secret finish was reported only as "Transaction submission failed: tecCRYPTOCONDITION_ERROR". Its hash had to be found afterwards in the account's history. In the game, a failed reveal is a scoring event, so whatever we use must hand back the hash, or let us compute it before submitting.
3. **Its helper error type does not implement `std::error::Error`**, so `?` cannot pass it on; every call needs a manual conversion.
4. **Weight:** the lock grew from 200 to 449 packages with xrpl-rust in.

## Why it is not adopted

With xrpl-rust in the lock, `cargo audit --deny warnings` fails (`raw/03_cargo_audit_with_xrpl_rust.txt`):

| Advisory | Crate | Through | Fix | Can we upgrade? |
| --- | --- | --- | --- | --- |
| RUSTSEC-2026-0387: timing variability in operations meant to be constant-time | crypto-bigint 0.5.5 | xrpl-rust itself (its key code), and elliptic-curve 0.13 | crypto-bigint 0.7.6 or later | **No.** xrpl-rust 1.3.0 requires `^0.5.1`; so does xrpl-sdk 2.0.0, its renamed successor |
| RUSTSEC-2023-0089: unmaintained | atomic-polyfill 1.0.3 | embedded-tls, via reqwless, xrpl-rust's JSON-RPC client | none: replace it | Only by not using xrpl-rust's HTTP client |

Ignoring an advisory is not allowed here. The timing issue is in key arithmetic, which is exactly where it matters.

## The alternative it points to

A thin layer of our own, with no big-integer cryptography:

- **ed25519 keys only.** The faucet issues ed25519 seeds, and deriving an ed25519 key needs only SHA-512, not the secp256k1 scalar arithmetic that pulls in crypto-bigint.
- **Our own binary serialization** for the transaction types listed above, checked against published test vectors. The standalone `xrpl_binary_codec` crate was last updated in November 2024 and is typed per transaction, so it is too stale to depend on.
- **Submission over plain JSON-RPC.** We compute each transaction's hash before submitting, which also closes gap 2 above.

The decision is the Publisher's; this receipt is the evidence for it.

## Layout

- `testnet_spike.rs.txt`: the spike's source, as it ran.
- `raw/00_snapshot.txt`: start and end times, and the base commit.
- `raw/01_spike.out`, `raw/01_spike.exit`: one JSON line per step; exit code 0.
- `raw/02_merchant_account_tx.json`: the merchant's validated transaction history, read back after the run.
- `raw/03_cargo_audit_with_xrpl_rust.txt`: the audit with xrpl-rust in the lock.
