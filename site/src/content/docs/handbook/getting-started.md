---
title: Getting started
description: Clone rnd-data, find a run, and check a file by hand or with rnd.
sidebar:
  order: 1
---

## Clone it

```bash
git clone https://github.com/mcp-tool-shop-org/rnd-data
cd rnd-data
```

Every file is stored byte-exact (`.gitattributes` has `* -text`), so git never converts line endings and every hash
in a manifest holds on any platform.

## Find a run

Each folder under `runs/` is one run or collection, named by its run id: its source folder with `/` written as `--`.

```bash
ls runs/
cat runs/receipts--colab--rung-prestep-muse-20261019--try1-gate/manifest.json
```

That run, from the Publisher's `receipts/colab/rung-prestep-muse-20261019/try1-gate`, lists three files:
`gate.jsonl` and `outcome.json` are public, with their hashes and a copy each under `files/`; `window.log` is private
for identity, listed by path and size with `"sha256": null`. See [Layout](../layout/) for every field.

An experiment in [rnd](https://github.com/mcp-tool-shop-org/rnd) names its runs here by `raw_manifest_id`, and
`rnd where` finds every copy of a file by its hash or path.

## Check a file by hand

A file's SHA-256 is in its run's manifest, under `files` and again under `copies`. Hash the file and compare:

```bash
sha256sum runs/receipts--colab--rung-prestep-muse-20261019--try1-gate/files/gate.jsonl
# df19ad096ad0add77162cce929506d10da112b78c5398e69b86e801532da120b

grep -A1 '"path": "gate.jsonl"' runs/receipts--colab--rung-prestep-muse-20261019--try1-gate/manifest.json
#    "path": "gate.jsonl",
#    "sha256": "df19ad096ad0add77162cce929506d10da112b78c5398e69b86e801532da120b",
```

Each copy's `location` is relative to the repository root, so every git copy can be checked at once with `jq`:

```bash
jq -r '.copies[] | select(.store == "rnd-data") | "\(.sha256)  \(.location)"' runs/*/manifest.json \
  | sha256sum -c --quiet
```

It prints nothing when every copy matches, and names each one that doesn't. A file larger than 256 KB has its copy in
the blob store (`"store": "d"`, at `blobs/<sha256[:2]>/<sha256>`), not in git; once the blobs are public on Hugging
Face, a downloaded one is checked the same way, against the `sha256` its manifest names.

## Check it with rnd

[Install rnd](https://github.com/mcp-tool-shop-org/rnd), then, from the root of this checkout:

```bash
bash verify.sh                                   # what CI runs: the public check
RND_DATA="$PWD" rnd raw verify --public-only     # the same, by hand
RND_DATA="$PWD" rnd raw verify --run receipts--colab--rung-prestep-muse-20261019--try1-gate
```

`--public-only` re-hashes every git copy and checks the private-file rules, and skips the stores a public clone
doesn't have. [Verifying](../verifying/) has the details, and the full check the rig runs.
