# reasoning gold set, PRs merged 2026-10-08

File: `reasoning-prs-2026-10-08.jsonl` (origin `prs-2026-10-08`, check_type `reasoning`).
Each line is a claim about what a code change does, with the code that decides it as `context`.

## Counts

| | supported | unsupported | cannot_tell | total |
|---|---|---|---|---|
| all | 182 | 182 | 10 | 374 |
| tune | 98 | 98 | 9 | 205 |
| heldout | 84 | 84 | 1 | 169 |
| offrig | 100 | 100 | 6 | 206 |
| aspire-si | 73 | 73 | 4 | 150 |
| role-os | 9 | 9 | 0 | 18 |

182 behaviours, each with one supported claim and one unsupported near-miss (every unsupported
item has `subtle: true`). 10 further behaviours have a single cannot_tell claim (2.7% of items).
A pair always shares a split. Split rule: sha256 of `"<repo>#<pr>#<behaviour-n>"`, first byte
even is tune, odd is heldout. Behaviour numbers 90 and above are the cannot_tell items.

Items by PR (supported / unsupported pairs): offrig#31 5, #32 2, #33 8, #34 26, #39 25, #40 13,
#41 21; aspire-si#53 12, #54 4, #55 7, #56 3, #58 7, #59 10, #61 15, #63 5, #64 10; role-os#24 9.

## Change kinds in the unsupported items (182)

| kind | count |
|---|---|
| swapped term / outcome / precedence / unit | 47 |
| negation | 42 |
| dropped or added condition or term | 38 |
| changed number, value or threshold | 31 |
| inclusive vs strict bound | 13 |
| wrong order of operations | 8 |
| wrong default | 2 |
| wrong owner (function) | 1 |

The exact kind of each item is the first words of its `notes` (`<kind>: <why the context contradicts it>`).
Supported items carry `entailed: <what in the context decides it>`.

## Source PRs and merge commits

All are in `mcp-tool-shop-org`. Context `source` is `<repo>#<PR>@<merge-sha7>:<path>#Lx-Ly`, with
line numbers taken from the file at the merge commit.

| PR | merge commit | title |
|---|---|---|
| offrig#31 | 83a5f21649c5d13fa31ca0efdec6886d8996cd33 | Job profiles take hf_token_secret |
| offrig#32 | db28ec428ddfabb4bdeb9f7cdd938c81b7ba8327 | Release builds compile without the watchdog poll warning |
| offrig#33 | b644ab739bedde7a4d2c1a54df894ee12928d65f | offrig budget: a terminal menu, and the cap never takes back a run's money |
| offrig#34 | 06aa1e37744022098b89a5d6a2b4fadd7220f952 | offrig_complete: an OpenRouter lane under the budget and ledger |
| offrig#39 | c320473b0b4fa4574379e71742d60397fbbb89bf | verifier phase 1: hybrid project index |
| offrig#40 | b6da05143c22ad894f028433c79d1667aa9b88a1 | RunPod REST v2, with offrig's own GPU fallback |
| offrig#41 | c58608835320136246b6874dbdbadf34902b8b2a | verifier phase 2: verdict contract |
| offrig#42 | a45fe53a126be76de42c342b7223315f5740c37d | site: plainer heading (skipped, see below) |
| aspire-si#53 | 8b21c5ee37e6705ec972b644dab2f70a87a0d6d7 | Skeptic: word-level paraphrase format |
| aspire-si#54 | e4800c632bbe30f2b1bc26dc7eda3f7db976f858 | Skeptic readout: size-matched margin |
| aspire-si#55 | 5cf7fa6ec1ce461becebdf316343f49096c0d5f6 | Auditor plan addendum 3: typicality match |
| aspire-si#56 | c1b62954fb1d40d710e817935b7723b2953dc1c5 | Typicality: the borderline rule |
| aspire-si#58 | c5ac2f1e25b9725d50a8183a491d75b282426173 | Addendum 4 step 1: surprisal-only baseline |
| aspire-si#59 | 8f0342a5d3b84153c1487a2052d7d6565b7af082 | Addendum 4: context-rich meaning re-check |
| aspire-si#61 | abb0eee611c6403363f955b5b541e0c6d227d84f | Addendum 4 step 2: two-sided matched set |
| aspire-si#63 | 319a549e4bae71f64781b37e40564eb3ca6c7aa9 | matched_set: grammar gate on grammar or usage errors only |
| aspire-si#64 | 7d2889490acb2b36b31e08f829803f05d5994613 | critic heads: --trainer eager / fast / graphs |
| role-os#24 | fc5222ae783ea95e3b1bc38c0576245eaf6fa7fe | release: role-os 2.12.0 |
| role-os#26 | ce91be8054c54a94c3cfaebe1e79d685e70f46cd | 2.12.0 translations changelog (skipped, see below) |

Skipped: offrig#42 (one heading string in `site-config.ts`, no behaviour) and role-os#26 (changelog
text only). docs and changelog hunks in the other PRs were not used.

## Method

1. Read each PR with `gh pr view` and `gh pr diff`, then read the merged files at the merge commit
   (blobless clone of each repo in the scratchpad, `git show <sha>:<path>`; no commits, pushes or
   PRs in any repo).
2. Picked specific, checkable behaviours (a default, a bound and whether it is strict, which branch
   refuses what, an order of operations, a retry count, a port, a guard).
3. Wrote by hand, for each, a plain-English supported claim and a near-miss with one change
   (changed number, strict vs inclusive, swapped term, dropped or added condition, negation, wrong
   order, wrong default, wrong owner), plus a few cannot_tell claims about code the hunk does not
   contain.
4. A script (not committed) assembled the JSONL: it cuts the context from the merge-commit file at
   the stated lines, so `text` is verbatim and each range is the real line range. Checked
   automatically: unique ids, schema fields, every range matches its line count, no home-directory
   paths. Checked by hand: each claim against its context, and the unsupported ones for a clear
   contradiction (two items found ambiguous on re-read were rewritten or dropped).
5. No model was called and no GPU used. All labels are the author's (one Claude session).

## Known limitations

- One author wrote the claims and the labels; nobody else has read them. Treat the set as
  calibrated by construction, not independently adjudicated.
- Near-misses are single deliberate edits, so they test careful reading of a hunk more than
  open-ended reasoning about a change. They are not examples of how real wrong PR descriptions
  go wrong.
- Many contexts include a doc comment that states the behaviour in words. Those items are easier
  than ones that rest on the code alone.
- Rust (offrig, 100 pairs) and Python (aspire-si, 73) dominate; role-os (JavaScript, 9 pairs) is thin.
  Several PRs touch the same files (aspire-si 53 to 56, 58, 59, 61, 63), so items from them share
  vocabulary.
- role-os#24 is a release PR: its diff is docs, data and a version bump. Its 9 pairs are read
  from `src/calibration.mjs` and `src/specialist/recipe-card.mjs` at the merge commit, the code
  the PR's README text describes, not from lines the PR changed.
- Many offrig#41 pairs describe the verifier's own quote rule and calibration thresholds. The
  role card's worked examples in `verify.rs` were not used as claims, but a model that reads this
  repo could have seen the code.
- A few supported claims are conjunctions of two facts (for example a bound and a default); the
  near-miss changes only one of them. Both facts are in the context.
- cannot_tell is 2.7% of items, so the abstain rate is barely measured here.
- Some claims name a debug-only or default value (for example "by default") because the context
  has a test override; they are decidable from the shown lines.


---

# Reasoning gold set, change semantics (diffs-2026-10)

File: `reasoning-diffs-2026-10.jsonl` (origin `diffs-2026-10`, check_type `reasoning`). Each line is a claim about what a code change does. `context` is two entries, the hunk **before** the change and the hunk **after** it, so the claim is decided by the difference. This answers the lesson of the set above, whose contexts were post-change code only and so tested "claim vs code at a SHA", not the change.

Context `source` is `<repo>#<PR or commit>@<sha7>:<path>#Lx-Ly (before|after)`. The before sha is the first parent of the merge commit, the after sha is the merge commit; line numbers are real for that file at that sha.

## Counts

| | supported | unsupported | cannot_tell | total |
|---|---|---|---|---|
| all | 96 | 96 | 16 | 208 |
| tune | 41 | 41 | 9 | 91 |
| heldout | 55 | 55 | 7 | 117 |
| offrig | 33 | 33 | 6 | 72 |
| aspire-si | 32 | 32 | 7 | 71 |
| role-os | 18 | 18 | 2 | 38 |
| rnd | 13 | 13 | 1 | 27 |

96 behaviours. Every behaviour has one supported claim and one unsupported near-miss (every unsupported item has `subtle: true`); 16 behaviours additionally have a cannot_tell claim (7.7% of items, 17% of behaviours). A behaviour's items share a split. Split rule: sha256 of `"<repo>#<PR or commit>#<n>"`, first byte even is tune, odd is heldout. `has_doc_comment` is true for 72 items (a comment or docstring in either hunk states the claim's key terms; the cannot_tell items are marked true only where a comment is about the claim).

## Change kinds in the unsupported items

| kind | count |
|---|---|
| negation | 18 |
| wrong new value, default or number | 16 |
| false "no behaviour change", or old/disclaimed behaviour credited to the change | 12 |
| dropped or added condition | 12 |
| scope wrong (conditional change stated as general, or the reverse) | 11 |
| swapped term, outcome or basis | 10 |
| direction reversed (old and new swapped) | 9 |
| wrong order of operations | 5 |
| strict vs inclusive bound | 3 |

The exact kind of each item is the first words of its `notes` (`<kind>: <why the hunks contradict it>`). Supported items carry `entailed: <what in the hunks decides it>`; cannot_tell items carry `cannot_tell: <what the hunks do not show>`.

## Source changes (24)

All are in `mcp-tool-shop-org`. `rnd` has no pull requests at all (`gh pr list --state all` is empty; work lands as direct commits on main), so its five units are single commits, keyed by the commit's short sha in place of a PR number.

| unit | before (parent) | after (merge or commit) | items | title |
|---|---|---|---|---|
| aspire-si#13 | 9b12d5398140900b0262027109fa484368dc9986 | bbc86289cefff04eeaaa3bfd98024e1c28a1bdbc | 7 | Load checkpoints with weights_only=True |
| aspire-si#29 | 4f96f3e714f13aa508d6a711d2fde78c383eea4a | 47b9c45ff1bf03134090aa94833b677328abb118 | 7 | Pod scripts take HF_HOME from the environment |
| aspire-si#31 | 62f3081ec7e438c908df19e86ecb0c83332befa5 | d137b756288d2e37f1b848011344f5464e05aec2 | 7 | probe_models records the probed models' training seed in its drift exports |
| aspire-si#47 | e53e970af3da3ad3cae6b1c57b06844e16ce7d97 | 1c2bfcf1d61ae1a81c9d05e2c99530a195246f0d | 11 | judge_eval for a 32 GB card: batched scoring, optional teacher scores |
| aspire-si#48 | 1c2bfcf1d61ae1a81c9d05e2c99530a195246f0d | 8a0fe3933c21baec1bf207c9a3b5fc33bc294017 | 11 | Auditor readout: noise-band accuracy, found Auditor AUC; step 4 memory fix |
| aspire-si#51 | b45bd7d960f3af3ad432999b2625f19dc2c859c4 | fe61fea957c16a0b69a3d5e75d28db86e073fa4d | 11 | Skeptic: a size gate on paraphrase edits (re-plant before any read) |
| aspire-si#66 | f95c7948c8b7c513e61204282e87fd0b3853f114 | f5699e8bccb1e0ed4e5049ed7d180b521381272d | 8 | build_equivalence: --url and --build, recorded per item |
| aspire-si#67 | f5699e8bccb1e0ed4e5049ed7d180b521381272d | fa6f5d7ba990268228fd77dc4da5a3f3e524c49a | 9 | build_equivalence: record the backend DLL hash; tests for identity and refusal |
| role-os#22 | 4d26cd92806bebedd45be8bd9c4225ed68144108 | d218de70a2c77995f8002eaf76c9a0e621c38ea0 | 15 | feat: learn pack choice from recorded run outcomes |
| role-os#23 | d218de70a2c77995f8002eaf76c9a0e621c38ea0 | ced8f13c8d14fc7cd8c46c7a036b8fea575cc41d | 23 | feat: recipe evidence gates the jury |
| offrig#3 | 0d8e8abbfa9d6ad2b8c378200ec237c31a926ae8 | 207a1048acf5394cd50b1535bb5a00c72d9f8f17 | 7 | Job pods: the pod's environment reaches each job; job-pod next step after launch |
| offrig#4 | e4fec092d73cdcaba66745b5f277da00609994b3 | 0d8e8abbfa9d6ad2b8c378200ec237c31a926ae8 | 4 | A jam profile for singing renders; job pods only on CUDA 12.8 hosts |
| offrig#13 | 1c76e709062a6a6f130490740a1ce78609f8ed85 | 9a4198b939b121cc84f1f594ad2c59fc3c5506d1 | 8 | Plan hardware limits: min_cuda, min_vram_gb, max_price_hr, no_fallback (#9, #10) |
| offrig#5 | 207a1048acf5394cd50b1535bb5a00c72d9f8f17 | 23ee566ea4510fdf4ce1c359f294e0a2cb142f78 | 11 | Per-project lanes: concurrent side-cars no longer collide (fixes #2) |
| offrig#8 | 23ee566ea4510fdf4ce1c359f294e0a2cb142f78 | 1c76e709062a6a6f130490740a1ce78609f8ed85 | 11 | One lane, one live plan: launch refuses a second pod, job tools take plan_id (fixes #7) |
| offrig#16 | de2c7d73708f4bbba611189042167ba4a177f4b8 | d59fceef93b4ff2f5bd8e9d5f3f652419cb83774 | 9 | Capacity wait, live launch progress, host CUDA from nvidia-smi (#15) |
| offrig#24 | b935def16ea19aacdc4620aa584d9173c98d4430 | 2e8cadbe7be40565657bba311883aaa6bdb5c7a5 | 9 | Auto-stop off survives a restart |
| offrig#28 | b2b89cdfafe3286d6dbf307425ca24b17f51fdf9 | 33f236964c471c3784c7c6ee4e496c3962275534 | 6 | Say why a launch stopped: error code, rented and billed, and what it cost |
| offrig#30 | ab31154662ad9d774d890b0f5b581f7b466708fc | 8e794aa81deb4be99d4a0f060c75a7bc54830e28 | 7 | Release: strip build-machine paths and link the C runtime statically |
| rnd@d7e5622 | b40ced71ee1676fcd8aec51cbb08c2122d289830 | d7e5622bf96df9602d128cb409569cb184786a7b | 7 | rnd 1.1.4.1.4: Kev cu134 passes the full band; graphed_heads seeds the CUDA RNG |
| rnd@89059db | 5850199b7dfe2507c2d4d86a7e55128169266df8 | 89059dbe822d0fb03e85c2f10bbebf91b9aaac00 | 4 | rnd 1.1.4.1.2: B200 probe, CUDA 13.4 under cuda-compat passes 9 of 9 |
| rnd@31fba10 | e8397129248511e5a44d986071321d3bc10056b7 | 31fba10d7ac53da0d2fb4f6df48915f8e97d459c | 6 | rnd 1.1.4.0.10: kev cu134 runs get their own output names |
| rnd@e839712 | 254b0c2eae5227088899e202037b867a971e64b2 | e8397129248511e5a44d986071321d3bc10056b7 | 4 | rnd 1.1.4.0.9: CUDA 13.4 training env for the Kev judge, with a pass band fixed before the run |
| rnd@b08dd43 | 126c420b82be430420d2f0374fba40593d57255e | b08dd43ecf0da6ddc6ea1643e18ead102105697b | 6 | rnd 1.1.4.0.4: screen2 full-run plan and bar, committed before the run |

Considered and not used. offrig: #1, #14, #17, #18, #27 (mostly new modules or new files, so there is no before hunk worth testing), #20-#23, #29 (icon, ship gate, coverage, docs), #31-#34 and #39-#42 (already in the set above). aspire-si: #26 and #28 (additive `host_check.py`), #36, #52, #65 (mostly new files or long prompt text), #53-#64 (already in the set above), and the many report, plan and readout PRs, which are docs. role-os: #20, #21 (new files), #24 (release, in the set above), #25 and #26 (docs), and the CI and dependency PRs #12-#19 (older than 30 days or CI-only). rnd: no PRs; of its commits only the five that change code or scripts in a way a before/after hunk can show were used (most of the others add data, notes or version bumps).

## Method

1. `gh pr list --state merged` for the four repos; read each candidate with `gh pr view` and `gh pr diff` and kept PRs that change behaviour. Blobless bare clones of each repo sat in the scratchpad; no commit, push, PR or stash in any repo.
2. For each change, the before hunk is read at the merge commit's first parent and the after hunk at the merge commit (`git show <sha>:<path>`), at line ranges chosen by pattern so the code decides the claim; ranges are real and the text is verbatim. For an added function or field the before hunk is the surrounding code where it went in.
3. Per behaviour, wrote by hand a supported claim (entailed by before vs after), an unsupported near-miss with one change-specific error (direction reversed, old behaviour credited to the change, false "no behaviour change", wrong new value or default, scope, negation, dropped condition, strict vs inclusive, order), and for about one behaviour in six a cannot_tell claim about something the hunks do not show (another file, a caller, a runtime or size effect).
4. A script (not committed) cut the hunks and assembled the JSONL. Checked automatically: unique ids; exact field set and order; label and subtle consistency; split recomputed from the sha256 rule; each source range equals the entry's line count; no home-directory paths. Checked by hand: every claim against both hunks, and a doc-comment pass. During that pass, claims whose key fact sat outside the chosen hunk (a size gate in a helper above `plant`, a constant defined just above `ollama_chat`, an inline check that was later extracted) were fixed by widening or moving the hunk, and several claims were reworded to what the hunks decide (for example "can apply to any profile" became a statement about which call is made).
5. No model was called and no GPU used. All labels are the author's (one Claude session).

## Known limitations

- One author wrote the claims and the labels; nobody else has read them. Treat the set as calibrated by construction, not independently adjudicated.
- Near-misses are single deliberate edits, so they test careful reading of a before/after pair more than open-ended reasoning about a change. They are not examples of how real wrong PR descriptions go wrong.
- Several PRs are chained (offrig #3, #4, #5, #8, #13 and #16; aspire-si #47, #48, #66 and #67; role-os #22 and #23), so an after hunk of one can be the before hunk of the next and vocabulary repeats across items. Some behaviours share one hunk pair (up to five), so the contexts are not independent.
- Many contexts contain a doc comment or docstring that states the behaviour in words (about 72 of 208 items are flagged); those are easier than ones that rest on the code alone.
- A few supported claims are conjunctions (a bound and a default, or a new value and an unchanged argument); the near-miss changes only one part. Both parts are in the hunks.
- For pure additions (a new function, field or flag) the before hunk shows the surrounding code, not the thing added; those claims rest on the after hunk plus the absence in before.
- Rust (offrig) and Python (aspire-si, rnd) dominate; role-os is JavaScript, the release workflow is YAML and two rnd units are shell. rnd contributes commits, not PRs.
- cannot_tell is 7.7% of items; whether a model abstains correctly on these depends on whether it takes "not shown in these hunks" as cannot_tell rather than unsupported, which a few of the items (a caller, an effect in another file) are meant to probe.
- This set was built from material dated 2026-10-07 to 2026-10-08, so it overlaps in time and repos with the earlier set; PRs were chosen to avoid reusing the same ones, not the same files.


---

# Hard batch (diffs-2026-10-hard)

File: `reasoning-diffs-hard-2026-10.jsonl` (origin `diffs-2026-10-hard`, check_type `reasoning`). Same fields, id style (`diffhard-<repo>-<unit>-<n><s|u|c>`), split rule (sha256 of `"<repo>#<unit>#<n>"`, first byte even is tune; a behaviour's items share a split) and before/after context convention as the batch above. A third context entry labelled `(after, related)` holds the second hop where the effect is not on the changed line. It was added because a blind relabel by a strong model got all 208 earlier items right; these items are meant to need a careful trace, not a skim, and each `notes` field names its pattern as `hard: <pattern>`.

## Counts

| | supported | unsupported | cannot_tell | total |
|---|---|---|---|---|
| all | 15 | 15 | 8 | 38 |
| tune | 9 | 9 | 3 | 21 |
| heldout | 6 | 6 | 5 | 17 |
| aspire-si | 4 | 4 | 2 | 10 |
| role-os | 10 | 10 | 5 | 25 |
| rnd | 1 | 1 | 1 | 3 |

15 behaviours, each with a supported and an unsupported item (every unsupported item has `subtle: true`); 8 of them also carry a cannot_tell claim (21% of items). With these 15 the diffs reasoning type goes from 96 to 111 unsupported items. `has_doc_comment` is true for 22 items.

## Pattern tally (15 behaviours; the cannot_tell items are all pattern 1)

| pattern | behaviours | where |
|---|---|---|
| subtle change (suffix rule, `??` short-circuit, whole-argument equality, boundary, bool is int, what sits inside a `try`) | 6 | aspire-si#52 lexical_guard; role-os 39de253 `??`; 4342dff `--help`; 51afdca bound and bool; 6a9bade loadManifest |
| multi-part claim, one small part fails | 4 | aspire-si#52 size gate floor; role-os 9aa1490 hints; 39de253 halt event; rnd 7fba56f must-check |
| indirect effect (value or effect two hops from the changed line; both hops in context) | 3 | aspire-si#52 verify and attempt_round; role-os 6a9bade clear-halt |
| doc comment overclaims (label follows the code) | 2 | role-os 9aa1490 "always carry expires"; 39de253 "refuse anything else" |
| outside-the-hunk dependence (cannot_tell) | 8 items | `plant_errors` sampling, `extract_json_object`, `summarize`, the CLI switch, `MAX_FALSE_CONFORMANT`, `loadState` on a missing file, `evidence()`, the loadManifest caller |

Change kinds in the 15 unsupported items: scope wrong 4, negation 4, swapped term/outcome/basis 3, dropped or added condition 2, strict vs inclusive bound 1, direction reversed 1. The first words of `notes` give the kind, as before.

## Sources (all `mcp-tool-shop-org`; before is the first parent)

| unit | before | after | items | change |
|---|---|---|---|---|
| aspire-si#52 | fe61fea957c16a0b69a3d5e75d28db86e073fa4d | d00079df73e78bc8d5bde2152e938d7970ee38df | 10 | Skeptic: lexical guard, per-answer size cap, claim-changed question, attempt round (`skeptic_pairs.py`) |
| role-os 9aa1490 | 7976f2d (first parent) | 9aa149040a84fd21c46e168abd0528859ced8ae3 | 4 | capability-gate deny hints by grant problem |
| role-os 39de253 | 1861943 (first parent) | 39de253aaaedd2663945b1b3437461c0498f32c2 | 7 | shadow config from env, contrastive halt names both summaries |
| role-os 4342dff | 7976f2d (first parent) | 4342dffa0055be0737536f76c87146a688f87beb | 3 | post-verb `--help` intercepted before dispatch |
| role-os 51afdca | 7976f2d (first parent) | 51afdca3bb7dd02e9018ac0b287fcceb42c0d626 | 5 | certify receipts stamped, `is_ship_pin` |
| role-os 6a9bade | 1861943 (first parent) | 6a9badedcd758fb98ac232133b68ec3ebbf89997 | 6 | unreadable JSON named (loadManifest, clear-halt) |
| rnd 7fba56f | 6343105 (first parent) | 7fba56f612fd3060ed89a1b1c822d3f3438685de | 3 | `build_grounded.py` multi-span facts |

`source` strings use the 7-character shas of the file as read. rnd has no PRs, so its unit is a direct commit. The role-os commits are direct commits on main (not PRs) and were not used in the earlier batch (which used role-os #22, #23, #24). aspire-si#52 was listed there as "considered and not used". Hunks are verbatim from `git show <sha>:<path>`; ranges are real and were checked to equal each entry's line count.

## Method and limits

1. Read each commit's diff with `git show`, then the files at both shas; no commit, push, PR or stash in any repo. Picked behaviours where the visible text of one hunk misleads (a different `try` scope, `??`, a `>` against a prose bound, a hint text that differs by branch) and wrote the claim and its near-miss from a trace of the code.
2. A script (not committed) cut the hunks by anchor and wrote the JSONL. Checked automatically: unique ids against both earlier files, field set and order, label/`subtle` consistency, split recomputed from the sha256 rule, each range equal to its line count, no home-directory paths. Checked by hand: every claim traced against its context; claims that a careful engineer could label two ways were reworded or dropped (for example a cannot_tell about `plant_errors` batching, a claim about the default of an opt-in flag, and a `Date.parse` claim that needed outside knowledge).
3. No model was called and no GPU used. All labels are the author's (one Claude session), so this batch has the same single-author limit as the others, and it has not been blind-relabelled: whether it is harder than the first set is untested.
4. Four supported/unsupported pairs rest on language facts a careful engineer is expected to know (`isinstance(True, int)`, `??` short-circuiting, `>` boundaries, `readFileSync` before `try`). The cannot_tell items have no deciding code in the context by construction, but a reader who guesses a plausible implementation of the missing function could still pick a label; that is what they probe.
5. Several items share one hunk pair (up to five), and the aspire-si and role-os units are small, so contexts are not independent.


---

# Batch 2 (diffs-2026-10-b2)

File: `reasoning-diffs-b2-2026-10.jsonl` (origin `diffs-2026-10-b2`, check_type `reasoning`). Same fields, before/after context convention and split rule as the two batches above (sha256 of `"<repo>#<unit>#<n>"`, first byte even is tune, odd is heldout; a behaviour's items share a split). Ids are `diff2-<repo>-<sha7>-<n><s|u|c>`; the unit is a commit short sha because most of these changes are direct commits (the four aspire-si units are squash-merges of PRs #28, #38, #43 and #68, keyed by sha here). The batch was built to lift the `reasoning` gold set to at least 100 unsupported items in each split, from sources that are not offrig-heavy and with a mix of difficulty.

## Counts

| | supported | unsupported | cannot_tell | total |
|---|---|---|---|---|
| all | 100 | 100 | 13 | 213 |
| tune | 53 | 53 | 5 | 111 |
| heldout | 47 | 47 | 8 | 102 |
| role-os | 41 | 41 | 6 | 88 |
| rnd | 24 | 24 | 3 | 51 |
| aspire-si | 21 | 21 | 3 | 45 |
| offrig | 14 | 14 | 1 | 29 |

100 behaviours, each with one supported claim and one unsupported near-miss (every unsupported item has `subtle: true`); 13 of them also carry a cannot_tell claim (6.1% of items). Unsupported items by repo and split: role-os 22 tune / 19 heldout, rnd 14 / 10, aspire-si 12 / 9, offrig 5 / 9. `has_doc_comment` is true for 116 of the 213 items (a comment or docstring in a hunk states the claim's key terms; for cannot_tell items it is true only where a comment is about the claim).

## Combined `reasoning` diffs totals after this batch

The three diffs files together (`reasoning-diffs-2026-10.jsonl` 208 items, `reasoning-diffs-hard-2026-10.jsonl` 38, this batch 213; 459 items):

| | supported | unsupported | cannot_tell |
|---|---|---|---|
| all | 211 | 211 | 37 |
| tune | 103 | 103 | 17 |
| heldout | 108 | 108 | 20 |

Before this batch the unsupported counts were 111 total, 50 tune and 61 heldout. The earlier PR-based set (`reasoning-prs-2026-10-08.jsonl`, post-change code only, 182 unsupported) is a different kind of item and is not counted here.

## Difficulty mix

About two thirds of the behaviours are standard change-semantics near-misses; 31 of the 100 use a hard pattern, named in `notes` as `hard: <pattern>` (the supported item and the unsupported one carry it; the cannot_tell items are all the outside-the-hunk kind).

| hard pattern | behaviours |
|---|---|
| subtle change (operator, boundary, regex anchor, truthiness, language fact, order inside a function) | 20 |
| indirect effect (the decisive code is two hops from the changed line) | 7 |
| multi-part claim with one part false | 3 |
| doc comment overclaims (the label follows the code, not the comment) | 1 |

All 13 cannot_tell items depend on something the hunks do not show (a caller, a helper defined elsewhere, a runtime result, a downstream consumer); each `notes` ends `hard: outside-the-hunk dependence`. Ten behaviours carry a third `(after, related)` context entry: six of the seven indirect-effect behaviours use it for the second hop (the seventh, aspire-si 4d45a08 behaviour 7, traces within one hunk), and four carry it as extra context.

Change kinds in the 100 unsupported items (first words of `notes`, grouped):

| kind | count |
|---|---|
| negation | 20 |
| scope wrong (conditional change stated as general, or the reverse) | 15 |
| wrong value, default, unit or number | 14 |
| swapped term, outcome or basis | 12 |
| dropped or added condition | 11 |
| wrong order of operations | 8 |
| old behaviour credited to the change, or false "no behaviour change" | 7 |
| wrong outcome, mechanism or source | 7 |
| strict vs inclusive bound | 4 |
| direction reversed | 2 |

## Sources (all `mcp-tool-shop-org`; before is the first parent unless noted)

Context `source` is `<repo>#<sha7>@<file-sha7>:<path>#Lx-Ly (before|after|after, related)`, with line numbers from the file at that sha. Hunks are verbatim from `git show <sha>:<path>` (blobless clones in the scratchpad; no commit, push, PR or stash in any repo).

| unit | before | after | behaviours | change |
|---|---|---|---|---|
| role-os 467b98d | 80c532c24c30bd259a07f2684370a4a99879c261 | 467b98deb0481f3f6e5d83ed8f0cdcb4f31dd169 | 7 | curriculum honesty ladder: n>=3, sign consistency, confirmed-negative (`training-programs.mjs`, `crew-cmd.mjs`) |
| role-os 7550c7c | b68e8e1d01f788df4f7dc5b8b36fbbeaf24a92b8 | 7550c7c61135b9c8a955818d7ce54e1f1841a8d1 | 5 | mission hardening: block downstream steps, last-match escalation, role catalog check |
| role-os 0a13ed4 | 86e7682544a36ec2ab7e880e21d57a9e67478836 | 0a13ed4dcc71db3ad5d32b619be848f4d5a059f5 | 5 | calibration pass: excludeWhen, integration regex, verdict rename |
| role-os 3075814 | b580be9a660f704f7b161a6b4106cbb5dc63e6a4 | 307581426db4a6fc73c9ac102d0d486f3b2655e1 | 2 | route: "Not triggered" line behind `--verbose` |
| role-os 00b4ee5 | 7fd1602abaf5bca99ab6d0954b8c385e14d61871 | 00b4ee5dc3d0aaf06b68a5d1314132578b16e68d | 2 | USER_ERROR stays a JSON blob |
| role-os 54f6a32 | b3c39f6a2e09a6e20b40b0a5505b2a9e3f9076e2 | 54f6a32d5a1bb19bb98b5f7bb62cef7214650152 | 4 | citation gate: local panel on non-blocking gates, panel seats, findings distribution |
| role-os 365da74 | 23c37ec1d379de65b8d54a40cee076de153fe7db | 365da7409893bcab29da39838634a7512ed70faf | 6 | automatic knowledge retrieval in persistent runs |
| role-os 80c532c | 63925fca94a258e6571327fc27087a98dd932fdd | 80c532c24c30bd259a07f2684370a4a99879c261 | 3 | cross-trained technique from registered versions |
| role-os 4a804eb | 882989040cb9c2c08cbf597fb29aa59448a51ac5 | 4a804eb2f09c3b8ccd17efabc25fe99e15a5a7f6 | 3 | cross-train cosine as a pre-run flag |
| role-os 2f39c72 | 816c39366dd89b5585b5d327174824b6e3b13673 | 2f39c72389b531035192030058dc00fa8b2d083d | 2 | exitCondition as a completion gate |
| role-os 69406f4 | 25d9bb83fe23a05c2410eb14bdfa06a669b984ba | 69406f4def4e2e793bcc81968a7bb101e4435169 | 2 | request hash in the claims receipt chain |
| rnd 922b886 | f7c6ece7c22043f4ed68d8b3bf3e7cc6ae0f2c89 | 922b8861bbd8758b509c7e7228ba5632b6d3fdef | 4 | library discovery (`find_root`, `--library`) |
| rnd 081e92f | af9ab1d8fe91e694918807871759df71f793b0b9 | 081e92f5cf5386965a9ee49a57101d59389f7a4d | 6 | muse-glimmer as a screen judge (`build.py`) |
| rnd 519679e | d6959e1db4ba533838aafa1e15274b3ba61dcd1c | 519679e10addd6d56f9202a93d5b33de3fc12257 | 4 | within-mix AUC (`compare.py`) |
| rnd b7bccc8 | 5bfaf9dd7d5a89f6d7ca48b87b19bcf5c7962a23 | b7bccc87ba1e27bc5e0d4cca274667d505796f67 | 10 | natural-errors p2 run command (`p2_parse`, `cmd_p2`, `chat_full`) |
| aspire-si 4d45a08 (#38) | 7d76159b9ab1399cfba4d4371d4b214a29e054b5 | 4d45a083490d1cd5f01ffc1a4aa67f683a3bb326 | 8 | host speed check measures the real download path (`host_check.py`) |
| aspire-si 8b95b9e (#68) | fa6f5d7ba990268228fd77dc4da5a3f3e524c49a | 8b95b9e062a9a7c5c391a1f184681d45d7d51a23 | 5 | grammar pre-screen escalation is for the whole pass (`matched_set.py`) |
| aspire-si 78cc26f (#43) | bd5e119a741bc17d4d26fa1b3ca038e24205ebc8 | 78cc26fdd230b0aa72b66324cca81639cb3b7114 | 5 | `CriticConfig.init_seed`, critic built on its own seeded stream |
| aspire-si 4f96f3e (#28) | 0c0ac38d08c11305cb98aa73569863838359c2da | 4f96f3e714f13aa508d6a711d2fde78c383eea4a | 3 | write-speed probe and `rate_problem` (`host_check.py`; additive) |
| offrig 73ea7ba | f6c709c70e1d05563fa2f917ec558c35b7cb64fb | 73ea7baab7bed3b6fc98d615b1a1d13ea82106ad | 5 | `NoRepeats` padding guard, `effective_checks` |
| offrig 51eda1c | 73ea7baab7bed3b6fc98d615b1a1d13ea82106ad | 51eda1c7e1ed468092ce1028eec732f680038095 | 4 | stalled-revision stop |
| offrig 65ef665 | 0983cc35c14934f1d8e3f0d9a9553c5e521a1683 | 65ef665fd8261e4fbab96cfb98e1d7a170959934 | 5 | refuse profiles whose models exist locally (`local_conflicts`) |

Repos used: role-os, rnd, aspire-si, offrig. No other org repo (ai-jam-sessions, loadout-os, scalarscope) was needed to reach the counts. rnd has no PRs, so its units are direct commits; the early role-os commits (2026-03) and the offrig commits (2026-10-02) are direct commits on `main`. None of these units, and none of their behaviours, appears in the two earlier diffs files (checked on repo plus commit or PR; aspire-si #28 and #38 were listed there as "considered and not used").

## Method

1. Surveyed `git log --first-parent` with `--numstat` for code files on the four repos, read candidate diffs, and kept commits with real behaviour changes (guards, defaults, thresholds, ordering, a parsing rule, a condition that moved); docs-only, data-only and release commits were skipped.
2. For each behaviour wrote by hand one supported claim and one near-miss with a single deliberate error, and for 13 behaviours a cannot_tell claim about code the hunks do not contain. Hard items were written to need a trace: a default argument that empties a list, `any()` of an empty sequence, `rsplit`, a regex anchor or word boundary, `isinstance(True, int)`, `JSON.stringify(null)`, `!== false` against a missing field, an error swallowed by `if let Ok`, a guard that sits in another function (indirect, with a related hunk).
3. A script (not committed) cut the hunks by anchor from the bare clones, built the JSONL and computed ids and splits. Checked automatically: ids unique across all three files, exact field set and order, label/`subtle` consistency, split recomputed from the sha256 rule, every source range equal to its text's line count, every side 10 to 60 lines, first two context entries labelled before then after, no home-directory path or user name in any field, notes prefixes by label.
4. Checked by hand: each claim re-read against both hunks with every part required to hold. Claims that depended on a library fact outside the hunks, or that two readings could decide differently, were reworded or dropped (for example a claim about what `hf_hub_download` does with a cached shard, and one about `cmd_select` reading the extra-judge file, were not used).
5. About 113 behaviours were drafted. 13 (mostly heldout, standard difficulty) were dropped to stay near the requested size once both thresholds were met with margin, so the final split balance is the hash outcome minus those drops. The split of every kept behaviour is still the hash of its `<repo>#<unit>#<n>`.
6. No model was called and no GPU used. All labels are the author's (one Claude session).

## Known limitations

- One author wrote the claims and the labels; nobody else has read them and the batch has not been blind-relabelled, so whether its hard third is hard for a strong model is untested.
- Near-misses are single deliberate edits, so they test careful reading of a before/after pair more than open-ended reasoning about a change; they are not examples of how wrong PR descriptions go wrong.
- Many units share hunks (up to 10 behaviours on one hunk pair, for example rnd b7bccc8), and two units are chained (offrig 73ea7ba is the before of 51eda1c). Contexts and vocabulary are not independent.
- Nine units add a function or option (offrig `NoRepeats`, `stalled` and `local_conflicts`; rnd `p2_parse`, `cmd_p2` and `within_mix_auc`; aspire-si `escalate` and the host-check probes; role-os `readCompatibility`). Their before hunk shows the surrounding code, not the thing added, so those claims rest on the after hunk plus the absence in before.
- Some claims need language facts a careful engineer is expected to know (Python truthiness and `bool` as `int`, `any([])`, `ZeroDivisionError`, `rsplit`, JS `??` and `JSON.stringify(null)`, regex anchors and `\b`, Rust `Option` and `if let Ok`). A few claims also do arithmetic on constants shown in the hunks (the host_check floors, `probe_timeout`).
- The doc-comment-overclaims pattern has one behaviour only (role-os 467b98d, the "mixed-sign stays unverified" comment against a code path that returns spurious for a thin witness); the other hard patterns are better covered.
- The cannot_tell items probe abstaining on a missing caller, helper or runtime result; at 6.1% of items the abstain rate is still barely measured, and a reader who guesses a plausible implementation of the missing code can pick a label (that is what they test).
- JavaScript (role-os), Python (rnd, aspire-si) and Rust (offrig) only; role-os is 41% of the unsupported items. The March 2026 role-os commits (7550c7c, 0a13ed4, 3075814, 365da74) are old and their code has since moved on; the claims are about those commits, not about current `main`.
