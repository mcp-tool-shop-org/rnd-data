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

- [ ] `[cli|mcp|desktop]` SKIP: the `rnd-data` CLI is read-only (`ls`, `show`, `where`, `schema`); it has no kill, delete or restart action to gate
- [x] `[cli|mcp|desktop]` File operations constrained to known directories (2026-11-03) — reads only under `--root` (or `$RND_DATA`) and the file named by `schema --check`; writes nothing
- [ ] `[mcp]` SKIP: not an MCP server
- [ ] `[mcp]` SKIP: not an MCP server

## B. Error Handling

- [x] `[all]` Errors follow the Structured Error Shape: `code`, `message`, `hint` (2026-11-03) — `RndDataError` and `fail()` in `cli.py`, e.g. `NO_RUN`, `NOT_A_STORE`, `SCHEMA_INVALID`, `USAGE`
- [x] `[cli]` Exit codes: 0 ok · 1 user error · 2 runtime/usage error · 70 internal error (2026-11-03) — probed: unknown run 1, bad manifest 1, wrong root 2, unknown command 2; an internal bug exits 70. No command reports partial success, so 3 is unused
- [x] `[cli]` No raw stack traces without `--debug` (2026-11-03) — every input error probed (missing file, bad JSON, wrong root, unknown run, unknown command) prints code, message and hint; any other exception prints `error: INTERNAL: …` with a hint and exits 70, never a traceback (`test_internal_error_has_studio_shape_and_no_traceback`). There is no `--debug` flag
- [ ] `[mcp]` SKIP: not an MCP server
- [ ] `[mcp]` SKIP: not an MCP server
- [ ] `[desktop]` SKIP: not a desktop app
- [ ] `[vscode]` SKIP: not a VS Code extension

## C. Operator Docs

- [x] `[all]` README is current: what it does, install, usage, supported platforms + runtime versions (2026-10-19) — what's here, the run id, private files, checking a file by hand (`sha256sum`, `jq`) or with rnd
- [x] `[all]` CHANGELOG.md (Keep a Changelog format) (2026-10-19) — dated entries, no versions
- [x] `[all]` LICENSE file present and repo states support status (2026-10-19) — `LICENSE` (CC BY 4.0, the data) and `LICENSE-MIT` (the scripts); README "Licence" and "Status"
- [x] `[cli]` `--help` output accurate for all commands and flags (2026-11-03) — `rnd-data --help` lists `ls`, `show`, `where`, `schema`, `--root` and `--version`, each matching `cli.py`
- [ ] `[cli|mcp|desktop]` SKIP: no logging; the read-only CLI prints only its results and structured errors, and reads no secrets
- [ ] `[mcp]` SKIP: not an MCP server
- [ ] `[complex]` SKIP: not an operated service; the Starlight handbook covers the layout and the checks

## D. Shipping Hygiene

- [x] `[all]` `verify` script exists (test + build + smoke in one command) (2026-10-19) — `verify.sh` (`rnd raw verify --public-only`; `--full` on the rig), run in CI
- [x] `[all]` Version in manifest matches git tag (2026-11-03) — `rnd_data.__version__` 0.1.0 (dynamic in `pyproject.toml`); `release.yml` refuses to publish unless the version matches the tag
- [x] `[all]` Dependency scanning runs in CI (2026-11-03) — `pip-audit --strict` (pinned 2.10.1) in `ci.yml`, on the package's dependencies (none today; it fails if a vulnerable one is added); the site's npm tree is audited by `shipcheck deps`
- [x] `[all]` No known high/critical vulnerabilities in any dependency tree (2026-10-19) — site/: `npm audit` found 0 vulnerabilities; `shipcheck deps` passed (1 tree)
- [ ] `[all]` SKIP: org rule, no dependabot unless requested
- [ ] `[npm]` SKIP: not an npm package; `[pypi]` rnd-data publishes to PyPI by OIDC trusted publishing (`release.yml`, environment `pypi`, no stored token)
- [ ] `[npm]` SKIP: not an npm package (the site is not published to a registry)
- [x] `[pypi]` `python_requires` set (2026-11-03) — `requires-python = ">=3.10"`
- [x] `[pypi]` Clean wheel + sdist build; no lockfile, by design (2026-11-03) — a stdlib-only library has nothing to pin, so no `uv.lock` or `poetry.lock` is committed (`shipcheck manifest` reports the missing lockfile). `python -m build` makes `rnd_data-0.1.0-py3-none-any.whl` and `rnd_data-0.1.0.tar.gz`; `twine check --strict` passes both (also run in `release.yml`)
- [ ] `[vsix]` SKIP: not a VS Code extension
- [ ] `[desktop]` SKIP: not a desktop app

## E. Identity (soft gate — does not block ship)

- [x] `[all]` Logo in README header (2026-11-03) — `brand/logos/rnd-data/readme.png`
- [x] `[all]` Translations (polyglot-mcp, 8 languages) (2026-11-03) — README in English plus ja, zh, es, fr, hi, it and pt-BR, made locally by `translate-all.mjs` (translategemma:27b); one ja table cell hand-pinned in `.polyglot-pins.json` so every cell keeps its numbers
- [x] `[org]` Landing page (@mcptoolshop/site-theme) (2026-11-03) — `site/`, deployed by `pages.yml` to https://mcp-tool-shop-org.github.io/rnd-data/
- [x] `[all]` GitHub repo metadata: description, homepage, topics (2026-11-03) — description, the landing page as homepage, and 9 topics

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
