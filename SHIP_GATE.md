# Ship Gate

> No repo is "done" until every applicable line is checked.
> Copy this into your repo root. Check items off per-release.

**Tags:** `[all]` every repo · `[npm]` `[pypi]` `[vsix]` `[desktop]` `[container]` published artifacts · `[mcp]` MCP servers · `[cli]` CLI tools

---

## A. Security Baseline

- [x] `[all]` SECURITY.md exists (report email, supported versions, response timeline) (2026-10-19) — what to report (a private file, a private file's hash, identity), GitHub private vulnerability reporting or rnd's email, rnd's timeline; `shipcheck security-docs` executed
- [x] `[all]` README includes threat model paragraph (data touched, data NOT touched, permissions required) (2026-10-19) — README "Security and trust"
- [x] `[all]` No secrets, tokens, or credentials in source or diagnostics output (2026-10-19) — `shipcheck secrets` skips (no publishable package); identity scan RESULT CLEAN on the tracked tree; `rnd raw verify --public-only` fails on a machine path in a manifest
- [x] `[all]` No telemetry by default (2026-10-19) — stated in README and SECURITY.md

### Default safety posture

- [ ] `[cli|mcp|desktop]` SKIP: no code; rnd carries every action on the data
- [ ] `[cli|mcp|desktop]` SKIP: no code; rnd carries every action on the data
- [ ] `[mcp]` SKIP: not an MCP server
- [ ] `[mcp]` SKIP: not an MCP server

## B. Error Handling

- [ ] `[all]` SKIP: no code; rnd raw verify carries the errors
- [ ] `[cli]` SKIP: no code; rnd raw verify carries the errors
- [ ] `[cli]` SKIP: no code; rnd raw verify carries the errors
- [ ] `[mcp]` SKIP: not an MCP server
- [ ] `[mcp]` SKIP: not an MCP server
- [ ] `[desktop]` SKIP: not a desktop app
- [ ] `[vscode]` SKIP: not a VS Code extension

## C. Operator Docs

- [x] `[all]` README is current: what it does, install, usage, supported platforms + runtime versions (2026-10-19) — what's here, the run id, private files, checking a file by hand (`sha256sum`, `jq`) or with rnd
- [x] `[all]` CHANGELOG.md (Keep a Changelog format) (2026-10-19) — dated entries, no versions
- [x] `[all]` LICENSE file present and repo states support status (2026-10-19) — `LICENSE` (CC BY 4.0, the data) and `LICENSE-MIT` (the scripts); README "Licence" and "Status"
- [ ] `[cli]` SKIP: no code; rnd raw verify carries the errors
- [ ] `[cli|mcp|desktop]` SKIP: no code; rnd raw verify carries the errors
- [ ] `[mcp]` SKIP: not an MCP server
- [ ] `[complex]` SKIP: not an operated service; the Starlight handbook covers the layout and the checks

## D. Shipping Hygiene

- [x] `[all]` `verify` script exists (test + build + smoke in one command) (2026-10-19) — `verify.sh` (`rnd raw verify --public-only`; `--full` on the rig), run in CI
- [ ] `[all]` SKIP: no package; each run is pinned by its manifest, and the repo by its commit
- [ ] `[all]` SKIP: no code and no runtime dependencies; CI installs rnd pinned to a commit, and the site's npm tree is covered by `shipcheck deps`
- [x] `[all]` No known high/critical vulnerabilities in any dependency tree (2026-10-19) — site/: `npm audit` found 0 vulnerabilities; `shipcheck deps` passed (1 tree)
- [ ] `[all]` SKIP: org rule, no dependabot unless requested
- [ ] `[npm]` SKIP: nothing is published to a registry
- [ ] `[npm]` SKIP: nothing is published to a registry
- [ ] `[npm]` SKIP: nothing is published to a registry
- [ ] `[npm]` SKIP: nothing is published to a registry (site/package-lock.json is committed)
- [ ] `[vsix]` SKIP: not a VS Code extension
- [ ] `[desktop]` SKIP: not a desktop app

## E. Identity (soft gate — does not block ship)

- [ ] `[all]` Logo in README header
- [ ] `[all]` Translations (polyglot-mcp, 8 languages)
- [ ] `[org]` Landing page (@mcptoolshop/site-theme)
- [ ] `[all]` GitHub repo metadata: description, homepage, topics

---

## Gate Rules

**Hard gate (A–D):** Must pass before any version is tagged or published.
If a section doesn't apply, mark `SKIP:` with justification — don't leave it unchecked.

**Soft gate (E):** Should be done. Product ships without it, but isn't "whole."

**Executed vs attested.** `shipcheck audit` only *counts these checkboxes* — it does not read your repo, so a box can be green while the fact is false. The lines that say **"executed by `npx @mcptoolshop/shipcheck <gate>`"** are backed by a command that reads the real artifact and exits 1 on the real defect. Run those gates (they are wired into shipcheck's own `verify`); don't just tick their boxes. Executed today: **A1/A2** (`security-docs`), **A3** (`secrets`), **D2/D6/D7** (`manifest`), **D3-config + OIDC/provenance** (`ci`), **real vulnerabilities + alerting** (`deps`), **D5** (`pack`), plus front-door (`front-door`) and dogfood freshness (`dogfood`). Every other line is still an attestation you are vouching for. Note the two dependency layers: `ci` proves a scanner is *configured*; `deps` proves there are *no known vulnerabilities* — a repo can pass the first while failing the second.

**Checking off:**
```
- [x] `[all]` SECURITY.md exists (2026-02-27)
```

**Skipping:**
```
- [ ] `[pypi]` SKIP: not a Python project
```
