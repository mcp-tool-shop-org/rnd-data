# rnd-data

The raw data behind the studio's research: every run's receipts and outputs, with a manifest that pins each file by
SHA-256. **It's public, because the studio's research is open by default.** The few files with a named reason to
be private are listed here by path and hash, and held in the private companion, rnd-data-private.

It holds no code. rnd writes and reads it (`rnd raw ingest`, `rnd raw verify`, `rnd where`). rnd's index reads its
manifests when this checkout sits beside the rnd library, or is named by `$RND_DATA`.

## What's here

| Path | What |
|---|---|
| `runs/<id>/manifest.json` | One run's files (schema `rnd-data-run/v1`): each file's path, SHA-256, size, tier, licence and visibility, and every copy |
| `runs/<id>/files/…` | That run's small public files (256 KB or less), in git |
| `store.json` | The stores that hold bytes outside this repository, and how a machine finds each one |

- **Files over 256 KB** are stored once, by content, at `blobs/<sha256[:2]>/<sha256>`. Every run that has one names it
  by hash, so a build several windows used is stored once.
- **They go public as a Hugging Face dataset** at the next phase. Until then they're on the studio's backup drive.

## A run id

A run id is its source folder, with `/` written as `--`. For example, `receipts--colab--window14b-…-20261019` is the
Publisher's `receipts/colab/window14b-…-20261019`.
- **Its files.** A run's files are those under the nearest folder holding an `outcome.json`, so each retry
  (`try1/`) is its own run.
- **Files outside a run folder** are grouped under their window folder (for Colab), or under their top folder.

An experiment's `runs[].raw_manifest_id` in [rnd](https://github.com/mcp-tool-shop-org/rnd) names one of these ids.

## Private files

A file is private only for a named reason: sealed or held-out keys, blind files, item text, unapproved plans,
private projects, or content the studio's identity scan flags. Its manifest entry says `"visibility": "private"` and
gives the reason, and its copy is in rnd-data-private. Everything else is public.

## Copies and verifying

A file's copies are listed in its manifest's `copies`. Each store's root is found per machine, through
`store.local.json` (gitignored) or `$RND_DATA_STORE_<NAME>`, so no machine path is committed.

Every file's SHA-256 is in its run's manifest, so a downloaded copy can be checked without rnd, or with
`rnd raw verify`.

Nothing is deleted from the studio rig until two verified copies exist, a restore test has passed, and the Director
has given the go.

## Owners

- **R&D** owns the layout and the tooling.
- **The Publisher** owns its receipts, and reviews every ingest of them.
