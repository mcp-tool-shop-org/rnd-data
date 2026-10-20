---
title: Layout
description: runs/<id>/manifest.json and the schema rnd-data-run/v1, field by field; runs and collections; small files and blobs.
sidebar:
  order: 2
---

```text
runs/
  <id>/
    manifest.json        the run's manifest (rnd-data-run/v1)
    files/               the run's small public files, at their paths inside the run
store.json               the stores outside this repository (rnd-data-store/v1)
```

Every field below is read from real manifests: a run (`receipts--colab--window13l-20261018`), a collection
(`receipts--colab--rung-prestep-muse-20261019`) and a run with an identity-only private file
(`receipts--colab--rung-prestep-muse-20261019--try1-gate`).

## The run id

A run id is its source folder, with `/` written as `--`. `receipts--colab--window13l-20261018` is the Publisher's
`receipts/colab/window13l-20261018`.

- **A run** is the nearest folder holding an `outcome.json`. Its files are the ones under that folder, so each retry
  (`try1-gate/`, `try2-content-path/`) is its own run.
- **A collection** is every other group: files outside a run folder are grouped under their window folder (for
  Colab), or else under their top folder. `receipts--colab--rung-prestep-muse-20261019` collects the scripts and the
  `out/` folder beside that window's tries.

## The manifest, field by field

### Top level

| Field | What | Example |
|---|---|---|
| `schema` | Always `rnd-data-run/v1` | `"rnd-data-run/v1"` |
| `id` | The run id, the same as its folder under `runs/` | `"receipts--colab--window13l-20261018"` |
| `kind` | `run` (its folder holds an `outcome.json`) or `collection` | `"run"` |
| `source` | The folder it came from, under its ingest's prefix (`receipts`, `rnd-watch`) | `"receipts/colab/window13l-20261018"` |
| `models` | The models that generated its outputs; empty until they're recorded | `[]` |
| `licence_note` | A note on the licence of what the models generated | `"generating models not yet recorded for this run"` |
| `files` | One entry per file in the run, public or listed private ([below](#files)) | |
| `copies` | Where each public file's bytes are ([below](#copies)) | |
| `private_files` | Files private for their content, counted by reason, never named | `{"item-text": 6}` |
| `ingested` | The date rnd wrote the manifest | `"2026-10-19"` |
| `rnd_commit` | The rnd commit that wrote it | `"6c0ec58768b4114ee81804b04b8b5ec8c39e2b0f"` |

The four `rnd-watch` manifests were written by an earlier rnd (their `rnd_commit` is `96f1277…`) and don't carry
`kind`.

### `files`

| Field | What |
|---|---|
| `path` | The file's path inside the run, such as `outcome.json` or `upload/llama-server.gz` |
| `sha256` | Its SHA-256 in hex; `null` for a private file |
| `bytes` | Its size in bytes |
| `tier` | The data tier in rnd's scale plan. Every file here is `T4`, raw data |
| `licence` | The file's licence, such as `CC-BY-4.0` or `MIT`; `null` only on a private entry |
| `visibility` | `public`, or `private` for a file listed without its hash |
| `private_why` | Only on a private entry: why. In a public manifest this is always `identity` |

A public file and a listed private one, from `receipts--colab--window13l-20261018`:

```json
{
 "path": "upload/llama-server.gz",
 "sha256": "b35cb0bb3d0a5c28d31d5b4cd88c1068e72d8ad0571d8d87b3fdcf3adf4a0729",
 "bytes": 127456485,
 "tier": "T4",
 "licence": "MIT (llama.cpp, commit 620d2225)",
 "visibility": "public"
},
{
 "path": "job.log",
 "sha256": null,
 "bytes": 575188,
 "tier": "T4",
 "licence": null,
 "visibility": "private",
 "private_why": "identity"
}
```

### `copies`

| Field | What |
|---|---|
| `sha256` | The hash of the copy, matching a public entry in `files` |
| `store` | The store that holds it: `rnd-data` (this repository's git) or `d` (the blob store) |
| `location` | Where in that store: a path from this repository's root, or `blobs/<sha256[:2]>/<sha256>` |

Two files with the same bytes have the same hash, and each still has its own copy entry. A private file has no copy
entry in a public manifest.

## Small files and blobs

`store.json` sets the limit (`"small_file_limit": 262144`, 256 KB) and the blob layout.

- **256 KB or less:** the file is in git, at `runs/<id>/files/<path>`, and its copy says `"store": "rnd-data"`.
- **Larger:** it's stored once, by content, at `blobs/<sha256[:2]>/<sha256>` in the blob store, and its copy says
  `"store": "d"`. Every run that has the same file names the same blob, so a build several windows used is stored
  once. `upload/llama-server.gz` above is one, with its four split pieces.

### The stores

| Store | Kind | What |
|---|---|---|
| `rnd-data` | git | This repository (GitHub, public) |
| `rnd-data-private` | git | The private companion (GitHub, private): only files with a named reason |
| `d` | blobs | The studio rig's backup drive, a blob store by SHA-256 |

A machine finds a blob store's root through `$RND_DATA_STORE_D` or the key `d` in `store.local.json`, which git
ignores, so no machine path is ever committed. The public blobs go to a Hugging Face dataset at the next phase.
