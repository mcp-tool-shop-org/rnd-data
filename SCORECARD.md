# Scorecard

> Score a repo before remediation. Fill this out first, then use SHIP_GATE.md to fix.

**Repo:** rnd-data
**Date:** 2026-10-19
**Type tags:** `[all]` (data only: no code, no package, nothing published to a registry)

## Pre-Remediation Assessment

| Category | Score | Notes |
|----------|-------|-------|
| A. Security | 5/10 | The private-file rule held in the manifests, but no SECURITY.md and no threat model in the README |
| B. Error Handling | n/a | No code; rnd raw verify carries the errors |
| C. Operator Docs | 5/10 | A good README, but no licence, no changelog and no support status |
| D. Shipping Hygiene | 2/10 | No verify script and no CI: nothing re-checked the manifests on a change |
| E. Identity (soft) | 3/10 | The badge in the README (#1); no landing page, translations or correct metadata |
| **Overall** | **15/40** | B not scored |

## Key Gaps

1. No licence: the data was public with no terms of reuse.
2. No CI: a pull request could add a file no manifest names, or a private file's hash, unchecked.
3. No SECURITY.md: no way to report a private file or identity that reached the public repo.
4. The repo description still said "private raw-data store".

## Remediation Priority

| Priority | Item | Estimated effort |
|----------|------|-----------------|
| 1 | LICENSE (CC BY 4.0) and LICENSE-MIT; the README's licence section | small |
| 2 | verify.sh and ci.yml, through rnd raw verify --public-only, as a required check | small (rnd's flag is R&D's) |
| 3 | SECURITY.md, the README threat model, the changelog | small |
| 4 | Landing page and handbook; atlas map | medium |

## Post-Remediation

| Category | Before | After |
|----------|--------|-------|
| A. Security | 5/10 | 10/10 |
| B. Error Handling | n/a | n/a |
| C. Operator Docs | 5/10 | 10/10 |
| D. Shipping Hygiene | 2/10 | 9/10 (CI's rnd pin is held for R&D) |
| E. Identity (soft) | 3/10 | 6/10 (translations and metadata are R&D's, after review) |
| **Overall** | 15/40 | 35/40 |
