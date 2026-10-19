# Changelog

All notable changes to rnd-data are recorded here.

The format is based on [Keep a Changelog](https://keepachangelog.com/). rnd-data has no versions: each run is pinned
by its manifest, and the repository by its commit, so entries are dated.

## [Unreleased]

### Added

- `LICENSE` (CC BY 4.0, for the data) and `LICENSE-MIT` (for the scripts, `*.sh` and `*.py`); a third-party file keeps
  the licence its manifest names.
- `verify.sh`, which runs rnd's `rnd raw verify --public-only` (or the full check, with `--full`).
- CI (`ci.yml`): `bash verify.sh` and `atlas check` on every pull request, with rnd pinned to a commit.
- The landing page and a six-page handbook (`site/`), deployed by `pages.yml`.
- `SECURITY.md`, a "Security and trust" section and a "Licence" section in the README, `SHIP_GATE.md`,
  `SCORECARD.md`, and the repository's map in `atlas/`.

## 2026-10-19

### Added

- The scaffold: `README.md` and `store.json`, the stores that hold bytes outside the repository (`8ec6f8b`).
- Every file stored byte-exact (`* -text`), since manifests pin each file by SHA-256 (`4eecec8`).
- The weekly watch's runs, reports and GPU-stack briefs (`rnd-watch`: 4 runs, 7 files); its unpublished draft is in
  rnd-data-private (`3e50286`).
- The Publisher's receipts, public by rule only: 74 runs and 22 collections, 868 public files. A file is public only
  when rnd's receipt rules name it, it carries no `CALL_CHECKPOINT`, and the identity scan passed it (`2cf309d`).
- The rnd-data badge at the top of the README (#1, `bae30ba`).

### Changed

- rnd-data is public: the studio's research is open by default, and files with a named reason to be private are held
  in rnd-data-private (`aeeda07`, `c9090ef`).

### Fixed

- The README's account of private files: a file private for its content is left out and counted by reason in
  `private_files`, and a file private only for identity is listed by path and size with `"sha256": null`. No private
  file's hash is published (#1, `bae30ba`).
