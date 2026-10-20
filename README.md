<p align="center">
  <img src="https://raw.githubusercontent.com/mcp-tool-shop-org/brand/main/logos/rnd-data/readme.png" alt="rnd-data" width="400">
</p>

<p align="center">
  <a href="https://github.com/mcp-tool-shop-org/rnd-data/actions/workflows/ci.yml"><img src="https://github.com/mcp-tool-shop-org/rnd-data/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-CC_BY_4.0-blue.svg" alt="CC BY 4.0 License"></a>
  <a href="https://mcp-tool-shop-org.github.io/rnd-data/"><img src="https://img.shields.io/badge/Landing_Page-live-blue" alt="Landing Page"></a>
</p>

# rnd-data

The raw data behind the studio's research: every run's receipts and outputs, with a manifest that pins each file by
SHA-256. **It's public, because the studio's research is open by default.** The few files with a named reason to
be private are held in the private companion, rnd-data-private, and no private file's hash is published here.

It holds no code. rnd writes and reads it (`rnd raw ingest`, `rnd raw verify`, `rnd where`). rnd's index reads its
manifests when this checkout sits beside the rnd library, or is named by `$RND_DATA`. The repository's own scripts
are `verify.sh` and its two workflows; the `.sh` and `.py` files under `runs/` are receipts of runs, kept as data.

The [handbook](https://mcp-tool-shop-org.github.io/rnd-data/handbook/) has the manifest field by field, the
private-file rules and the checks.

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
private projects, or content the studio's identity scan flags. Its copy is in rnd-data-private, and its run's
manifest says only this much about it:
- **Private for its content:** it's left out, and counted by reason in the manifest's `private_files`.
- **Private only for identity:** it's listed by path and size, with `"visibility": "private"`, `"private_why": "identity"` and `"sha256": null`.

No private file's hash is published, since a short label file's hash could be matched by guessing. Everything else
is public.

## Copies and verifying

A file's copies are listed in its manifest's `copies`. Each store's root is found per machine, through
`store.local.json` (gitignored) or `$RND_DATA_STORE_<NAME>`, so no machine path is committed.

Every public file's SHA-256 is in its run's manifest, so a downloaded copy can be checked without rnd, or with
`rnd raw verify`. By hand, from the repository root (any platform with `sha256sum`; `jq` for the second):

```bash
sha256sum runs/<id>/files/<path>      # compare with that file's "sha256" in runs/<id>/manifest.json
jq -r '.copies[] | select(.store == "rnd-data") | "\(.sha256)  \(.location)"' runs/*/manifest.json \
  | sha256sum -c --quiet              # every git copy at once; silent when all match
```

With rnd installed, `bash verify.sh` runs `rnd raw verify --public-only`, as CI does on every pull request: it
re-hashes every git copy, skips the stores a public clone doesn't have, and fails on a tracked file under `runs/`
that no manifest names, a private entry with a hash, the private tag, a private-looking file name, or a machine path
in a manifest. On the rig, where the blob store is configured, `bash verify.sh --full` runs the full `rnd raw verify`.

Nothing is deleted from the studio rig until two verified copies exist, a restore test has passed, and the Director
has given the go.

## Owners

- **R&D** owns the layout and the tooling.
- **The Publisher** owns its receipts, and reviews every ingest of them.

## Security and trust

- **What it holds:** run manifests, the runs' small public files, `store.json`, `verify.sh`, two workflows and the
  site.
- **What it never holds:** credentials; a private file's bytes or its hash; machine paths.
- **What touches it:** rnd's ingest (`rnd raw ingest`) writes every manifest and every file under `runs/`, with the
  Publisher's review of every ingest of its receipts. CI checks every pull request with read-only permissions.
- **No telemetry** is collected or sent; the site is static.

To report a private file that reached this repository, a published hash of a private file, or identity in a public
file, see [SECURITY.md](SECURITY.md).

## Licence

rnd-data is licensed like rnd:
- **The data** is [CC BY 4.0](LICENSE).
- **The scripts** (`*.sh`, `*.py`) are [MIT](LICENSE-MIT).
- **A third-party file** keeps the licence its manifest names. The llama.cpp build is MIT (commit 620d2225).

A file's manifest `licence` field is the final word for that file. Every public file's manifest names its licence;
private entries carry `"licence": null`, because they aren't published.

## Status

Maintained, and growing with each ingest. There are no releases: each run is pinned by its manifest, and the
repository by its commit. [CHANGELOG.md](CHANGELOG.md) lists the changes by date.
