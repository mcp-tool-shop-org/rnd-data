# Security Policy

## Supported Versions

rnd-data has no versions and no releases. Each run is pinned by its manifest, and the repository by its commit.

| Branch | Supported |
|--------|-----------|
| `main` | Yes       |

## What to report

rnd-data is public raw data, so the risks are about what reaches it. Report:
- **A private file in this repository:** a file that should be in rnd-data-private (sealed or held-out keys, blind
  files, item text, unapproved plans, private projects), or a file carrying the private tag
  `T5-PRIVATE-DO-NOT-PUBLISH`.
- **A published hash of a private file:** a private entry in a manifest with a `sha256`, or a private file's hash
  anywhere else here.
- **Identity in a public file:** a name, account, address, home-directory or machine path, or anything else that
  identifies a person or a machine.
- **A credential:** a token, key or password in any file.

## Reporting a Vulnerability

Report it privately, through GitHub's private vulnerability reporting (the repository's **Security** tab →
**Report a vulnerability**), or by email: **64996768+mcp-tool-shop@users.noreply.github.com**

Please don't open a public issue, which would repeat the material.

Include:
- The file's path and the commit you saw it at
- What it exposes (no need to quote it)
- How you came across it

### Response timeline

| Action | Target |
|--------|--------|
| Acknowledge report | 48 hours |
| Assess severity | 7 days |
| Release fix | 30 days |

## Scope

rnd-data holds data, not code.

- **Data held:** run manifests (`runs/<id>/manifest.json`), the runs' small public files, and `store.json`.
- **Never held:** credentials; private files' bytes or hashes; machine paths (each machine finds a store through its
  own gitignored `store.local.json` or `$RND_DATA_STORE_<NAME>`).
- **What writes to it:** rnd's `rnd raw ingest`, with the Publisher's review of every ingest of its receipts. CI
  re-checks every pull request with `rnd raw verify --public-only`.
- **No telemetry** is collected or sent. The landing page and handbook are static pages on GitHub Pages.
