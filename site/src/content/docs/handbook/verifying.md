---
title: Verifying
description: The public check CI runs on every pull request, the full check on the rig, and --deep.
sidebar:
  order: 4
---

Every check is rnd's. rnd-data's `verify.sh` only calls it, with `RND_DATA` set to the checkout:

```bash
bash verify.sh          # RND_DATA="$PWD" rnd raw verify --public-only
bash verify.sh --full   # RND_DATA="$PWD" rnd raw verify
```

It stops at the first failure and exits non-zero.

## The public check (CI)

`rnd raw verify --public-only` is what a public clone can check, and what CI runs.

- **Re-hashes every git copy** in every run manifest against its SHA-256.
- **Skips the blob store and the private companion,** which a public clone doesn't have, and prints how many copies
  it skipped in each store.
- **Fails on:**
  - a tracked file under `runs/` that no manifest names;
  - a private entry with a hash;
  - a file carrying the private tag, `T5-PRIVATE-DO-NOT-PUBLISH`;
  - a private-looking file name (see [Private files](../private-files/));
  - a machine path in a manifest.

### The workflow

`.github/workflows/ci.yml` runs on every pull request to `main` (it's a required check), on a push to `main` that
touches `runs/`, `store.json`, `verify.sh`, `atlas/` or a workflow, and by hand. It runs on `ubuntu-latest` with
Python 3.12, and:
1. installs rnd, pinned to a commit;
2. runs `bash verify.sh`;
3. runs `npx --yes @dogfood-lab/atlas@1.24.0 check`, which checks the repository's map in `atlas/`.

Its actions are pinned by commit, and it can only read the repository.

## The full check (the rig)

On the studio rig, where the blob store is configured, `bash verify.sh --full` runs `rnd raw verify`:
- every git copy is re-hashed, as above;
- every blob copy is found in its store and checked by size;
- every private entry with a hash is still a failure.

A store's root comes from `$RND_DATA_STORE_<NAME>` or from `store.local.json`. Without one, the check stops and names
the variable to set.

Where the private companion is checked out (named by `--private` or `$RND_DATA_PRIVATE`, or beside the rnd library
as `../rnd-data-private`), rnd checks its copies too, and says so in its last line:
`verified rnd-data and rnd-data-private: 0 problems`.

### `--deep`

```bash
RND_DATA="$PWD" rnd raw verify --deep
```

`--deep` re-hashes every blob as well, instead of only checking its size. It reads every byte in the blob store, so
it's slow.

### One run

```bash
RND_DATA="$PWD" rnd raw verify --run receipts--colab--window13l-20261018
```

`--run` checks one run's manifest only, without the private companion.
