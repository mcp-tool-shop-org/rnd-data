# rnd-data: how it works

Mapped at 2026-10-19 from commit bae30ba by Atlas 1.24.0.

## What this is

The raw data behind the studio's research: every run's receipts and outputs, with a manifest per run (rnd-data-run/v1) that pins each file by SHA-256. No code: rnd writes and checks it. (written by a person)

4 parts, mostly shell (78 files), Python (61), CSS (2), TypeScript (2), Astro (1) and JavaScript (1). Work enters through 2 doors; CI and Deploy site to GitHub Pages each reach 1 part, and CI is followed because a pull request goes through it. It deploys a site to GitHub Pages.

## What changed since the last map

This is the first map.

## What comes in

1. **CI.** On a pull request to main; on a push to main touching 5 paths; or by hand. Runs verify.sh.
2. **Deploy site to GitHub Pages.** On a push to main touching 2 paths; or by hand. Runs site/astro.config.mjs and site/src/.

## What happens through CI

1. The workflow runs verify.sh in the repository root.

## Who reads the results

CI writes nothing this map can see.

## The other doors

**Deploy site to GitHub Pages** runs site/astro.config.mjs and site/src/, and deploys the site.

## What breaks what

No part is imported by another part, and no part sits on the path of two doors.

## What tends to change together

No two source files changed together often enough to name.

Window: 180 days; a pair counts from 3 shared commits, since the window holds fewer than 30 qualifying commits.

## What no test touches

No test files were found by name.

## Written but never read

No place this map can see is written, so none goes unread.

## Helpers that look duplicated

No two parts export a helper that looks alike.

## Generated, never hand-edited

Nothing in this repository writes to a tracked place this map can see.

## Hand-authored

People write .github/, the repository root, runs/ and site/; 83 writes with paths built at run time may land here.

## Where to start

CI runs no code this map can follow, so there is no path of files to read in order.

## What this map cannot see

- 14 imports could not be resolved: `runs/receipts--colab--rung-prestep-muse-20261019--try5/files/prestep_fit_tokenizer.py` imports `pin_window`, which is no module on its import path and no declared dependency; `runs/receipts--colab--rung-prestep-muse-20261019--try5/files/rung_prestep_muse.py` imports `pin_window`, which is no module on its import path and no declared dependency; `runs/receipts--colab--rung-prestep-muse-20261019/files/derive_allow.py` imports `pin_window`, which is no module on its import path and no declared dependency; and 11 more.
- 83 writes and 143 reads use paths built at run time and are not named here.
- 6 writes and 84 reads go to a path their caller passes, not to this repository.
- Statistics confidence is low: fewer than 30 qualifying commits in the window, and fewer than 20 source files reach 10 revisions.

Regenerate with `npx --yes @dogfood-lab/atlas map`.
