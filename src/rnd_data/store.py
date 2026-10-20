"""Read-only store reader for rnd-data."""

from __future__ import annotations

import json
import os
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from .schema import (
    RUN_SCHEMA,
    STORE_SCHEMA,
    load_schemas,
    validate_document,
    validate_file,
)

_HEX_RE = re.compile(r"^[0-9a-f]+$")
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_SAFE_RUN_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


class RndDataError(Exception):
    """Structured error in the studio shape: code, message, hint and exit_code."""

    def __init__(self, code: str, message: str, hint: str = "", exit_code: int = 1) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.hint = hint
        self.exit_code = exit_code


def leading_licence_id(licence: str) -> str:
    """Return a licence string's leading identifier (the text before the first `' ('`).

    Compared with no case folding. Parenthetical notes never count as the identifier.
    """
    return licence.split(" (", 1)[0]


def blob_rel(sha256: str) -> str:
    """Return the content-addressed relative blob path `blobs/<sha256[0:2]>/<sha256>`."""
    if not isinstance(sha256, str) or not _SHA256_RE.match(sha256):
        raise RndDataError(
            "BAD_SHA256",
            "blob path requires a 64-character lowercase hex SHA-256",
            "provide the full 64-character lowercase hex digest of a public entry",
            exit_code=2,
        )
    return f"blobs/{sha256[:2]}/{sha256}"


def resolve_root(
    root: str | Path | None = None,
    *,
    env: Mapping[str, str] | None = None,
    cwd: Path | None = None,
) -> Path:
    """Resolve the rnd-data root in order: `--root`, `$RND_DATA`, then cwd if it holds `store.json`."""
    environ = os.environ if env is None else env
    explicit = root if root is not None else environ.get("RND_DATA")
    if explicit is not None and str(explicit).strip() != "":
        candidate = Path(explicit)
        if not (candidate / "store.json").is_file():
            raise RndDataError(
                "NOT_A_STORE",
                "specified root does not hold store.json",
                "pass --root <dir> pointing to an rnd-data checkout, or set $RND_DATA",
                exit_code=2,
            )
        return candidate

    here = Path.cwd() if cwd is None else Path(cwd)
    if (here / "store.json").is_file():
        return here

    raise RndDataError(
        "NO_STORE",
        "no rnd-data store found (no store.json in the current directory)",
        "pass --root <dir>, set $RND_DATA, or run inside an rnd-data checkout",
        exit_code=2,
    )


class Store:
    """Read-only interface to an rnd-data checkout."""

    def __init__(
        self,
        root: str | Path | None = None,
        *,
        env: Mapping[str, str] | None = None,
        cwd: Path | None = None,
    ) -> None:
        self.root = resolve_root(root, env=env, cwd=cwd)
        self._store_data = self._load_store_json()

    def _load_store_json(self) -> dict[str, Any]:
        store_path = self.root / "store.json"
        schema_id, problems = validate_file(store_path)
        if problems or schema_id != STORE_SCHEMA:
            detail = "; ".join(problems) if problems else f"expected schema {STORE_SCHEMA!r}"
            raise RndDataError(
                "STORE_INVALID",
                f"store.json failed schema validation: {detail}",
                "run `rnd-data schema --check store.json` to inspect every problem",
                exit_code=1,
            )
        return json.loads(store_path.read_text(encoding="utf-8"))

    def store_manifest(self) -> dict[str, Any]:
        """Return a copy of the validated `store.json` document."""
        return dict(self._store_data)

    def manifest_ids(self) -> list[str]:
        """Return the sorted list of manifest directory names under `runs/`."""
        runs_dir = self.root / "runs"
        if not runs_dir.is_dir():
            return []
        return sorted(p.parent.name for p in runs_dir.glob("*/manifest.json") if p.is_file())

    def manifest(self, run_id: str) -> dict[str, Any]:
        """Load and validate one run or collection manifest (`runs/<id>/manifest.json`)."""
        if not isinstance(run_id, str) or not _SAFE_RUN_ID_RE.match(run_id) or ".." in run_id:
            raise RndDataError(
                "BAD_RUN_ID",
                f"invalid run id {run_id!r}",
                "run `rnd-data ls` to see valid run and collection ids",
                exit_code=2,
            )
        mpath = self.root / "runs" / run_id / "manifest.json"
        if not mpath.is_file():
            raise RndDataError(
                "NO_RUN",
                f"no run {run_id!r} in this store",
                "run `rnd-data ls` to list available run and collection ids",
                exit_code=1,
            )
        schema_id, problems = validate_file(mpath)
        if problems or schema_id != RUN_SCHEMA:
            detail = "; ".join(problems) if problems else f"expected schema {RUN_SCHEMA!r}"
            raise RndDataError(
                "MANIFEST_INVALID",
                f"runs/{run_id}/manifest.json failed schema validation: {detail}",
                f"run `rnd-data schema --check runs/{run_id}/manifest.json` to inspect every problem",
                exit_code=1,
            )
        data = json.loads(mpath.read_text(encoding="utf-8"))
        if data.get("id") != run_id:
            raise RndDataError(
                "MANIFEST_ID_MISMATCH",
                f"runs/{run_id}/manifest.json declares id {data.get('id')!r}, not {run_id!r}",
                "the manifest's id must match its directory under runs/",
                exit_code=1,
            )
        return data

    def licence_identifiers(self) -> list[str]:
        """Return sorted unique leading licence identifiers present across all public entries."""
        ids: set[str] = set()
        for rid in self.manifest_ids():
            m = self.manifest(rid)
            for entry in m.get("files", ()):
                if entry.get("visibility") == "public" and entry.get("licence"):
                    ids.add(leading_licence_id(entry["licence"]))
        return sorted(ids)

    def runs(
        self,
        *,
        kind: str | None = None,
        source: str | None = None,
        licence: str | None = None,
    ) -> list[dict[str, Any]]:
        """List run and collection summaries, optionally filtered by kind, source prefix or leading licence id."""
        if kind is not None and kind not in ("run", "collection"):
            raise RndDataError(
                "BAD_KIND",
                f"unknown kind {kind!r}",
                "pass --kind run or --kind collection",
                exit_code=2,
            )

        rows: list[dict[str, Any]] = []
        for rid in self.manifest_ids():
            m = self.manifest(rid)
            mkind = m.get("kind")
            msource = m.get("source", "")
            files = m.get("files", ())
            public_entries = [f for f in files if f.get("visibility") == "public"]
            listed_private = sum(1 for f in files if f.get("visibility") == "private")
            counted_private = sum(int(v) for v in m.get("private_files", {}).values())

            full_licences = sorted({f["licence"] for f in public_entries if f.get("licence")})
            lead_ids = sorted({leading_licence_id(f["licence"]) for f in public_entries if f.get("licence")})
            public_bytes = sum(int(f["bytes"]) for f in public_entries)

            if kind is not None and mkind != kind:
                continue
            if source is not None:
                norm_prefix = source.rstrip("/")
                if not (
                    msource == source
                    or msource == norm_prefix
                    or msource.startswith(norm_prefix + "/")
                    or msource.startswith(source)
                ):
                    continue
            if licence is not None and licence not in lead_ids:
                continue

            rows.append(
                {
                    "id": rid,
                    "kind": mkind,
                    "kind_label": mkind if mkind is not None else "(no kind)",
                    "source": msource,
                    "public_files": len(public_entries),
                    "private_files": listed_private + counted_private,
                    "bytes": public_bytes,
                    "licences": full_licences,
                    "licence_ids": lead_ids,
                }
            )
        return rows

    def where(self, query: str) -> list[dict[str, Any]]:
        """Locate every name and declared copy of a public file by SHA-256 (8+ hex) or path.

        Reads manifests only; never walks, stats or opens `blobs/`. Private entries are never matched.
        """
        key = query.strip() if isinstance(query, str) else ""
        if not key:
            raise RndDataError(
                "USAGE",
                "where requires a SHA-256 or path argument",
                "pass a SHA-256 (8+ hex characters) or a file path inside a manifest",
                exit_code=2,
            )

        is_hash_query = 8 <= len(key) <= 64 and bool(_HEX_RE.match(key.lower()))
        hash_prefix = key.lower()

        by_sha: dict[str, dict[str, Any]] = {}
        matched_shas: set[str] = set()

        for rid in self.manifest_ids():
            m = self.manifest(rid)
            public_shas_in_manifest: set[str] = set()
            for entry in m.get("files", ()):
                if entry.get("visibility") != "public":
                    continue
                sha = entry.get("sha256")
                if not isinstance(sha, str) or not _SHA256_RE.match(sha):
                    continue
                public_shas_in_manifest.add(sha)
                path = entry["path"]
                rec = by_sha.setdefault(
                    sha,
                    {
                        "sha256": sha,
                        "bytes": int(entry["bytes"]),
                        "tier": entry["tier"],
                        "licence": entry["licence"],
                        "_licences": set(),
                        "_names": set(),
                        "_copies": set(),
                    },
                )
                rec["_licences"].add(entry["licence"])
                rec["_names"].add((rid, path, entry["licence"]))

                if is_hash_query:
                    if sha.startswith(hash_prefix):
                        matched_shas.add(sha)
                else:
                    if (
                        path == key
                        or path.endswith("/" + key)
                        or f"runs/{rid}/files/{path}" == key
                        or f"{rid}:{path}" == key
                    ):
                        matched_shas.add(sha)

            for copy in m.get("copies", ()):
                csha = copy.get("sha256")
                cstore = copy.get("store")
                cloc = copy.get("location")
                if (
                    csha in public_shas_in_manifest
                    and csha in by_sha
                    and isinstance(cstore, str)
                    and cstore != "rnd-data-private"
                    and isinstance(cloc, str)
                ):
                    resolved_loc = cloc if cstore == "rnd-data" else blob_rel(csha)
                    by_sha[csha]["_copies"].add((cstore, resolved_loc))

        if not matched_shas:
            return []

        results: list[dict[str, Any]] = []
        for sha in sorted(matched_shas):
            rec = by_sha[sha]
            licences = sorted(rec["_licences"])
            names = [
                {"manifest_id": m_id, "path": p, "licence": lic}
                for m_id, p, lic in sorted(rec["_names"])
            ]
            copies = [
                {"store": st, "location": loc}
                for st, loc in sorted(rec["_copies"])
            ]
            results.append(
                {
                    "sha256": sha,
                    "bytes": rec["bytes"],
                    "tier": rec["tier"],
                    "licence": "; ".join(licences),
                    "licences": licences,
                    "blob": blob_rel(sha),
                    "names": names,
                    "copies": copies,
                }
            )
        return results

    @staticmethod
    def schema(
        name: str | None = None,
        *,
        check: str | Path | dict[str, Any] | None = None,
    ) -> dict[str, Any] | list[str]:
        """Return the bundled JSON Schemas, or validate `check` when given."""
        if check is not None:
            if isinstance(check, dict):
                return validate_document(check)
            _, problems = validate_file(check)
            return problems

        schemas = load_schemas()
        if name is None:
            return schemas
        if name in ("run", RUN_SCHEMA):
            return schemas[RUN_SCHEMA]
        if name in ("store", STORE_SCHEMA):
            return schemas[STORE_SCHEMA]
        raise RndDataError(
            "UNKNOWN_SCHEMA",
            f"unknown schema {name!r}",
            f"choose {RUN_SCHEMA!r} or {STORE_SCHEMA!r}",
            exit_code=2,
        )
