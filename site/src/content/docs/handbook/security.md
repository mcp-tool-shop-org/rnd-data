---
title: Security
description: What rnd-data holds and never holds, what writes to it, and how to report a problem.
sidebar:
  order: 5
---

## What it holds, and never holds

- **Holds:** run manifests, the runs' small public files, `store.json`, the MIT read-only package under `src/`,
  `verify.sh`, the workflows and this site.
- **Never holds:**
  - credentials of any kind;
  - a private file's bytes, or its hash;
  - a machine path. Each machine finds a store's root through its own gitignored `store.local.json` or
    `$RND_DATA_STORE_<NAME>`.

## What writes to it

- **rnd's ingest** (`rnd raw ingest`) writes every manifest and every file under `runs/`. Nothing else edits them.
- **The Publisher reviews** every ingest of its receipts before it lands.
- **The identity scan:** a file the studio's identity scan flags is private, for `identity`.
- **CI** runs `rnd raw verify --public-only` on every pull request, with read-only permissions and actions pinned by
  commit. See [Verifying](../verifying/).

There is no telemetry. The landing page and this handbook are static pages.

## Reporting a problem

Report, privately:
- a private file that reached this repository;
- a published hash of a private file;
- identity in a public file: a name, an account, a home-directory or machine path;
- a credential.

Use GitHub's private vulnerability reporting (the repository's **Security** tab → **Report a vulnerability**), or
email **64996768+mcp-tool-shop@users.noreply.github.com**. Please don't open a public issue.

| Action | Target |
|--------|--------|
| Acknowledge report | 48 hours |
| Assess severity | 7 days |
| Remove from `main` | 7 days |
| Rewrite history, if the file must not stay reachable | on the Director's go (a force-push) |

GitHub may keep a removed file reachable by its commit for a time; the report should say if it needs a history
rewrite.

The full policy is in
[SECURITY.md](https://github.com/mcp-tool-shop-org/rnd-data/blob/main/SECURITY.md).
