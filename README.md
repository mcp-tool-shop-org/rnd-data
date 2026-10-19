# rnd-data

The studio's private raw-data store: tier T4 (raw run outputs) and T5 (private files) of the rnd data layout. **It's
private, and never public.** It holds no code: rnd writes and reads it (`rnd raw ingest`, `rnd raw verify`,
`rnd where`), and rnd's index reads its manifests when this checkout sits beside the rnd library, or is named by
`$RND_DATA`.

## What's here

| Path | What |
|---|---|
| `runs/<id>/manifest.json` | One run's files (schema `rnd-data-run/v1`): each file's path, SHA-256, size, tier and licence, and every copy |
| `runs/<id>/files/…` | That run's small files (256 KB or less), in git |
| `private/manifest.json` | The private files (schema `rnd-data-private/v1`) |
| `private/<source>/…` | The private files themselves, in git |
| `store.json` | The stores that hold bytes outside git, and how a machine finds each one |

**What isn't in git:** files over 256 KB. Each is stored once, by content, in the blob store at
`<store root>/blobs/<sha256[:2]>/<sha256>`, and every run that has it names it in its manifest by hash.
- The same 122 MB build used by four windows is stored once.
- No run points inside another run's folder.

## A run id

A run id is its source folder, with `/` written as `--`. For example, `receipts--colab--window14b-…-20261019` is the
Publisher's `receipts/colab/window14b-…-20261019`.
- **Its files.** A run's files are those under the nearest folder holding an `outcome.json`, so each retry
  (`try1/`) is its own run.
- **Files outside a run folder** are grouped under their window folder (for Colab), or under their top folder.

An experiment's `runs[].raw_manifest_id` in rnd names one of these ids.

## Copies

A file's copies are listed in its manifest's `copies`:
- `rnd-data` is this repository's git;
- `d` is the backup drive's store. Its root is found per machine, through `store.local.json` (gitignored) or
  `$RND_DATA_STORE_D`, so no machine path is committed.

**An off-site copy is the next phase (P4).** Nothing here is deleted from the rig until two verified copies exist, a
restore test has passed, and the Director has given the go.

## Owners

- **R&D** owns the layout and the tooling.
- **The Publisher** owns its receipts. Every ingest of them is reviewed by the Publisher before it lands.
