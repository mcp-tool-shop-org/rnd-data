---
title: Overview
description: What rnd-data is, what it holds and never holds, and who owns it.
sidebar:
  order: 0
---

rnd-data is the raw data behind the studio's research: every run's receipts and outputs, with a manifest per run
that pins each file by SHA-256. The studio is an AI and SI research studio that also makes tooling for games, and its
research is open by default, so its raw data is public.

A few files have a named reason to be private: sealed or held-out keys, blind files, item text, unapproved plans,
private projects, and content the studio's identity scan flags. Those sit in the private companion,
rnd-data-private, and **no private file's hash is ever published** here.

## What it holds

| Path | What |
|---|---|
| `runs/<id>/manifest.json` | One run's files (schema `rnd-data-run/v1`): each file's path, SHA-256, size, tier, licence and visibility, and every copy |
| `runs/<id>/files/…` | That run's small public files (256 KB or less), in git |
| `store.json` | The stores that hold bytes outside this repository, and how a machine finds each one |
| `verify.sh` | The check CI runs, through rnd |
| `site/` | This handbook and the landing page |

Files over 256 KB are stored once, by content, in a blob store, and every run that has one names it by hash. They go
public as a Hugging Face dataset at the next phase; until then they're on the studio's backup drive.

## It holds no code

Everything that writes or checks the data is [rnd](https://github.com/mcp-tool-shop-org/rnd)'s:
- `rnd raw ingest` writes runs into rnd-data, and their private files into rnd-data-private;
- `rnd raw verify` re-hashes every copy against its manifest;
- `rnd where <sha256 or path>` names every copy of a file, and rnd's index reads the manifests when this checkout sits
  beside the rnd library, or is named by `$RND_DATA`.

The repository's own scripts are `verify.sh` and its two workflows. The `.sh` and `.py` files under `runs/` are
receipts: the scripts a run used, kept as data.

## Who owns what

- **R&D** owns the layout and the tooling. Manifests are only ever written by rnd.
- **The Publisher** owns its receipts, and reviews every ingest of them.
- **The Director** rules on what is public, and gives the go before anything is deleted from the studio rig. Nothing
  is deleted until two verified copies exist and a restore test has passed.

## Licence

The data is [CC BY 4.0](https://github.com/mcp-tool-shop-org/rnd-data/blob/main/LICENSE), and the scripts (`*.sh`,
`*.py`) are [MIT](https://github.com/mcp-tool-shop-org/rnd-data/blob/main/LICENSE-MIT). A third-party file keeps
the licence its manifest names: the llama.cpp build is MIT (commit 620d2225).

A file's manifest `licence` field is the final word for that file. Every public file's manifest names its licence
(`CC-BY-4.0`, `MIT`, or the llama.cpp build's MIT); private entries carry `"licence": null`, because they aren't
published.

## Where next

- [Getting started](./getting-started/): clone, find a run, and check a file.
- [Layout](./layout/): the manifest, field by field.
- [Private files](./private-files/): the reasons, and what a manifest says about each.
- [Verifying](./verifying/): what CI checks, and the full check on the rig.
- [Security](./security/): what to report, and how.
