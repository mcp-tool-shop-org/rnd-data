---
title: The Python package
description: Install the stdlib-only rnd-data package and use ls, show, where and schema from the command line or Python.
sidebar:
  order: 2
---

`rnd-data` (import name `rnd_data`) is a stdlib-only, read-only Python 3.10+ package under `src/rnd_data/`, licensed
under [MIT](https://github.com/mcp-tool-shop-org/rnd-data/blob/main/LICENSE-MIT). Its built wheel and sdist ship only
the code and schemas under `src/` and `LICENSE-MIT`—never the data files under `runs/` or `store.json`.

## Install it

From a checkout of this repository:

```bash
python -m pip install .
```

The package has no runtime dependencies.

## Finding the store root

Every command accepts `rnd-data [--root <path>] <command>`. The store root resolves in this order:
1. `--root <path>`
2. `$RND_DATA`
3. the current working directory, when it holds `store.json`

When none of those holds `store.json`, `rnd-data` exits with code `2` and a usage error in the studio shape (`code`,
`message` and `hint`).

## Commands

### `ls [--kind run|collection] [--source <prefix>] [--licence <id>]`

Lists runs and collections with their kind, public and private file counts, public byte total, and the full text of
every public licence in each manifest. The four early `rnd-watch` manifests (`rnd-watch`, `rnd-watch--argon-gpu-stack`,
`rnd-watch--reports` and `rnd-watch--runs`) predate the `kind` field and are shown as `(no kind)`.

```bash
rnd-data ls
rnd-data ls --kind run
rnd-data ls --source receipts
rnd-data ls --licence MIT
rnd-data ls --licence CC-BY-4.0
```

#### How `--licence` matches

Licences in manifests are free text. On `main` there are four forms across the 871 public file entries:
- `CC-BY-4.0` (557 files)
- `MIT (llama.cpp, commit 620d2225)` (171 files)
- `MIT` (138 files)
- `CC-BY-4.0 (the code excerpts in context are MIT, from offrig, aspire-si and role-os)` (5 files)

`--licence` matches a file's **leading licence identifier**—the text before the first `" ("`, or the whole value when
there is none—compared exactly with no case folding:
- `MIT` covers the 309 files whose licence is `MIT` or `MIT (llama.cpp, commit 620d2225)`.
- `CC-BY-4.0` covers the 562 files whose licence begins with `CC-BY-4.0`.
- A licence named only inside the parenthetical note does not count: **the 5 `CC-BY-4.0 (the code excerpts in context are MIT, …)` files do not match `MIT`.**
- `ls --licence X` lists a manifest when any of its public file entries has leading identifier `X`. Private entries
  (`"licence": null`) and manifests with no public files never match. On `main`: `MIT` lists 69 manifests, `CC-BY-4.0`
  lists 88, 67 hold both, and 10 have no public files.
- Each row's licence column always shows the full text of every public licence in that manifest, never only the
  matched one.
- A filter that matches nothing prints an empty list and exits `0`, with a `stderr` hint listing the leading
  identifiers present in the store.

### `show <run>`

Prints one run or collection manifest in plain words: its source, ingestion date and commit, public files (with their
SHA-256, byte size, tier and licence), listed private entries (`private_why: identity`, without any hash), content
private counts by reason (`private_files`), and declared copies.

```bash
rnd-data show receipts--colab--rung-prestep-muse-20261019--try1-gate
```

### `where <sha256|path>`

Finds every manifest name and declared copy of a public file by SHA-256 (8+ lowercase hex characters) or file path.

```bash
rnd-data where df19ad096ad0
rnd-data where outcome.json
```

`where` resolves `blobs/<sha256[0:2]>/<sha256>` only for hashes declared on public entries in public manifests, and
never walks, lists, stats or opens `blobs/`. For a hash that no public entry declares, `where` answers `"not declared"`
from the manifests alone and exits `1`.

### `schema [--check <file>]`

Prints the bundled JSON Schemas (`rnd-data-run/v1` and `rnd-data-store/v1`), or validates a manifest or `store.json`
file with the stdlib validator. An unknown `schema` value is refused.

```bash
rnd-data schema
rnd-data schema --check store.json
rnd-data schema --check runs/receipts--colab--window13l-20261018/manifest.json
```

## Python API

`rnd_data.Store(root)` mirrors the CLI:

```python
from rnd_data import Store

store = Store(".")
runs = store.runs(licence="MIT")
manifest = store.manifest("receipts--colab--window13l-20261018")
locations = store.where("outcome.json")
schemas = store.schema()
problems = store.schema(check="store.json")
```
