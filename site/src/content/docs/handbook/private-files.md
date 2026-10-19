---
title: Private files
description: The reasons a file is private, what a public manifest says about each kind, the hash rule, and the rules for the Publisher's receipts.
sidebar:
  order: 3
---

The studio's research is open by default. A file is private only for a named reason, and its copy is then in the
private companion, rnd-data-private (or, over 256 KB, in the studio's blob store). Nothing from either enters this
repository.

## The reasons

rnd's ingest takes a reasons file that maps paths, or `folder/` prefixes, to one of six reasons:

| Reason | What |
|---|---|
| `sealed` | A key held out for a blind test that is still running |
| `blind` | A blind file: one a blind test needs kept unseen |
| `item-text` | Items with their answers, drafts and generations of items, and anything that carries them |
| `unapproved` | A plan or file no rule has made public yet; the default for the Publisher's receipts |
| `private-project` | A file from a project that isn't public |
| `identity` | A file the studio's identity scan flags |

A file whose name looks private is held back even if the reasons file misses it.

A published benchmark's labels are public. Only a **sealed** key, held out for a blind test that's still running, is
private.

## What a public manifest says

- **Private for its content** (`sealed`, `blind`, `item-text`, `unapproved`, `private-project`): it's left out of
  `files`, and counted by reason in the manifest's `private_files`, such as `{"item-text": 6}`. Its name, size and hash
  don't appear.
- **Private only for identity:** it's listed, so the run stays complete, by path and size, with no hash and no copy:

```json
{
 "path": "window.log",
 "sha256": null,
 "bytes": 895,
 "tier": "T4",
 "licence": null,
 "visibility": "private",
 "private_why": "identity"
}
```

That entry is from `receipts--colab--rung-prestep-muse-20261019--try1-gate`.

## The hash rule

**No private file's hash is ever published,** in a manifest or anywhere else here. A short label file has few
possible contents, so its SHA-256 would let anyone confirm a guess at them. The private companion keeps its own
manifest, with the hashes, and it's private too.

## The private tag and private-looking names

- **The private tag**, `T5-PRIVATE-DO-NOT-PUBLISH`, marks a private text file: as a `"tier"` field in JSON, or as a
  first-line comment in a `.md`, `.txt`, `.py` or `.sh` file. Data files aren't tagged, since the tag would change
  their bytes.
- **Private-looking names:** `*blind*`, `*sealed*`, `*gold[-_]key*`, `*item[-_]text*`, `*itemtext*` and
  `*review[-_]items*`.

No file in this repository may carry the tag or a private-looking name. CI checks both on every pull request; see
[Verifying](../verifying/).

## The Publisher's receipts

What of the Publisher's receipts may be public is set by rnd's
[`docs/raw-data-rules/receipts.json`](https://github.com/mcp-tool-shop-org/rnd/blob/main/docs/raw-data-rules/receipts.json),
agreed with the Publisher on 2026-10-19. Either side changes it only by agreement.

**Deny by default for content.** A receipt is public only when a public rule names it, it carries no content marker,
and the identity scan passed it. The rules are checked in order:

1. **identity**, from the reasons file;
2. **private** rules, such as item files (`items.jsonl*`), window tars, drafts, generations, lesson plans, rescore
   and critic-eval files, all as `item-text`;
3. **content markers:** a file holding `CALL_CHECKPOINT` (gzip and base64 call-journal checkpoints, which carry drafts
   in an encoding no scan reads) is `item-text`;
4. **public** rules: window records (`outcome.json`), plan summaries, the VM gate's readings, model pin checks, card
   values, the spending ledger, launch and job scripts, logs and launch output without a content marker, stamps,
   commit ids, hashes of builds and weights, the llama.cpp build, window READMEs, and Argon's code reviews.

Anything left is private as `unapproved`.

Two of the public rules are the Director's ruling of 2026-10-19: verifier-gold's sources and the critic's
known-answer set v1 are R&D's published benchmark data, where "held-out" is a calibration split, not a sealed blind
test.

The same file sets licences by name: `llama-server*` carries `MIT (llama.cpp, commit 620d2225)`.
