# Window 13v: the critic-eval stub rung, 2026-10-19

**Result: pass.** `PIN_ROLE=critic-eval` at role-set main `47a5882` (#96 merged), run as a stub on standard CPU VMs in
three parts. StubLlama served Muse's name as the critic over R&D's sealed gold set (`perturb-s0/items.jsonl` `cdce4a8a`,
66 GPU items), packed as `critic-eval-inputs.tar.gz` (`ead500b1`). Total cost 0.05 units.

| Part | What it tested | Result |
|---|---|---|
| A (13v-a) | Muse prefetched with the READ token; seeds 0,1 at 3 s a call | 29.6 GB in 510 s, sha `c321320a` = pin; token_clean all true; critic_card present; each seed 52 scored, 14 skipped, 89 calls. Both seeds finished before the deadline, so no cut here. |
| B (13v-b) | Resume from A's tar; fresh seed 2 at 10 s a call, cut by the deadline | Seeds 0,1: reused 89, called 0, `critic-eval.jsonl` byte-identical to A. Seed 2: CUT AT THE DEADLINE 05:46:40 after 667 s, 66 of 89 calls journaled; out tar returned in `finally`; ok=false by design. |
| C (13v-c) | Resume from B's tar, including the cut seed 2 | Seeds 0,1 replayed again (called 0, byte-identical to A); seed 2 reused 66, called 23 (exactly its unfinished calls) and finished: 52 scored, 14 skipped. ok=true. |

token_clean was all true in all three parts. Thinking counts are null (unmeasured) on the stub, as ruled.

## Findings for the paid run (R&D's rulings, 2026-10-19)

- **Same-family skips are kept.** Muse wrote 5 source rows (P1-038, -044, -051, -039, -043), so 14 items are skipped.
  Muse reads 52; the 14 are read only if the design's conditional Lightning step runs. Report 52 and 14 apart; never pool across critics.
- **Calls per seed:** 89 with Muse on the stub. The mock's 149 was its VOID retries. A paid seed projects as 89 calls,
  up to 2x with VOID retries, at the A100's measured time per call; the cap goes on the high end plus 30% while fewer than
  four slots are measured.
- Muse's download took 510 s on a standard CPU against ~223 s on a high-mem CPU (13m).
