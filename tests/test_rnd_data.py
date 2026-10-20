"""Tests for the rnd-data package (phase R1)."""

from __future__ import annotations

import builtins
import copy
import io
import json
import os
import shutil
import subprocess
import sys
import tarfile
import zipfile
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from typing import Any
from unittest import mock

import pytest

import rnd_data
from rnd_data import (
    DEFAULT_COPYRIGHT,
    DEFAULT_CREATOR,
    RUN_SCHEMA,
    STORE_SCHEMA,
    RndDataError,
    Store,
    blob_rel,
    is_legacy_rnd_watch_id,
    leading_licence_id,
    load_schemas,
    resolve_root,
    validate_document,
    validate_file,
)
from rnd_data.cli import main

REPO_ROOT = Path(__file__).resolve().parents[1]

LIC_CC = "CC-BY-4.0"
LIC_MIT = "MIT"
LIC_MIT_LLAMA = "MIT (llama.cpp, commit 620d2225)"
LIC_CC_EXCERPTS = "CC-BY-4.0 (the code excerpts in `context` are MIT, from offrig, aspire-si and role-os)"

SHA_A = "1" * 64
SHA_B = "2" * 64
SHA_C = "3" * 64
SHA_D = "4" * 64


def run_cli(*args: str, env: dict[str, str] | None = None) -> tuple[int, str, str]:
    """Invoke `rnd_data.cli.main` in-process and capture `(exit_code, stdout, stderr)`."""
    out_buf = io.StringIO()
    err_buf = io.StringIO()
    if env is None:
        with redirect_stdout(out_buf), redirect_stderr(err_buf):
            code = main(list(args))
    else:
        with mock.patch.dict(os.environ, env, clear=True), redirect_stdout(out_buf), redirect_stderr(err_buf):
            code = main(list(args))
    return code, out_buf.getvalue(), err_buf.getvalue()


def make_store_json() -> dict[str, Any]:
    return {
        "schema": STORE_SCHEMA,
        "stores": {
            "rnd-data": {
                "about": "public git repository",
                "kind": "git",
            },
            "store-blobs": {
                "about": "content-addressed blob store",
                "kind": "blobs",
                "root_from": ["$RND_DATA_STORE_D", "store.local.json:d"],
            },
        },
        "small_file_limit": 262144,
        "blob_layout": "blobs/<sha256[0:2]>/<sha256>",
        "public_blobs": "a Hugging Face dataset, at P4",
    }


def make_run_manifest(
    run_id: str = "run-a",
    *,
    kind: str | None = "run",
    source: str = "receipts/window-a",
    files: list[dict[str, Any]] | None = None,
    copies: list[dict[str, Any]] | None = None,
    private_files: dict[str, int] | None = None,
) -> dict[str, Any]:
    default_files = [
        {
            "path": "outcome.json",
            "sha256": SHA_A,
            "bytes": 128,
            "tier": "T4",
            "licence": LIC_CC,
            "visibility": "public",
        }
    ]
    default_copies = [
        {
            "sha256": SHA_A,
            "store": "rnd-data",
            "location": f"runs/{run_id}/files/outcome.json",
        }
    ]
    doc: dict[str, Any] = {
        "schema": RUN_SCHEMA,
        "id": run_id,
        "source": source,
        "models": [],
        "licence_note": "generating models not yet recorded for this run",
        "files": default_files if files is None else files,
        "copies": default_copies if copies is None else copies,
        "private_files": {} if private_files is None else private_files,
        "ingested": "2026-10-19",
        "rnd_commit": "6c0ec58768b4114ee81804b04b8b5ec8c39e2b0f",
    }
    if kind is not None:
        doc["kind"] = kind
    return doc


def write_fixture_store(base: Path) -> Path:
    """Create a synthetic store under `base` covering all 4 licence forms, mixed, private-only, and no-kind."""
    store_dir = base / "store"
    store_dir.mkdir(parents=True, exist_ok=True)
    (store_dir / "store.json").write_text(json.dumps(make_store_json(), indent=1) + "\n", encoding="utf-8")

    manifests = [
        # 1. Plain CC-BY-4.0 and parenthetical CC-BY-4.0 (mentions MIT in parenthetical, must NOT match MIT)
        make_run_manifest(
            "run-cc-excerpts",
            kind="run",
            source="receipts/window-cc",
            files=[
                {
                    "path": "outcome.json",
                    "sha256": SHA_A,
                    "bytes": 100,
                    "tier": "T4",
                    "licence": LIC_CC,
                    "visibility": "public",
                },
                {
                    "path": "notes.txt",
                    "sha256": SHA_B,
                    "bytes": 200,
                    "tier": "T4",
                    "licence": LIC_CC_EXCERPTS,
                    "visibility": "public",
                },
            ],
            copies=[
                {"sha256": SHA_A, "store": "rnd-data", "location": "runs/run-cc-excerpts/files/outcome.json"},
                {"sha256": SHA_B, "store": "rnd-data", "location": "runs/run-cc-excerpts/files/notes.txt"},
            ],
        ),
        # 2. Mixed manifest: holds both CC-BY-4.0 and MIT (llama.cpp, commit 620d2225), plus a listed private entry
        make_run_manifest(
            "run-mixed",
            kind="run",
            source="receipts/window-mixed",
            files=[
                {
                    "path": "outcome.json",
                    "sha256": SHA_A,
                    "bytes": 100,
                    "tier": "T4",
                    "licence": LIC_CC,
                    "visibility": "public",
                },
                {
                    "path": "upload/server.gz",
                    "sha256": SHA_C,
                    "bytes": 500000,
                    "tier": "T4",
                    "licence": LIC_MIT_LLAMA,
                    "visibility": "public",
                },
                {
                    "path": "window.log",
                    "sha256": None,
                    "bytes": 450,
                    "tier": "T4",
                    "licence": None,
                    "visibility": "private",
                    "private_why": "identity",
                },
            ],
            copies=[
                {"sha256": SHA_A, "store": "rnd-data", "location": "runs/run-mixed/files/outcome.json"},
                {"sha256": SHA_C, "store": "d", "location": blob_rel(SHA_C)},
            ],
            private_files={"unapproved": 2},
        ),
        # 3. Collection with plain MIT
        make_run_manifest(
            "collection-mit",
            kind="collection",
            source="receipts/scripts",
            files=[
                {
                    "path": "runner.py",
                    "sha256": SHA_D,
                    "bytes": 320,
                    "tier": "T4",
                    "licence": LIC_MIT,
                    "visibility": "public",
                }
            ],
            copies=[
                {"sha256": SHA_D, "store": "rnd-data", "location": "runs/collection-mit/files/runner.py"},
            ],
        ),
        # 4. Manifest with NO public files (only listed private + counted private)
        make_run_manifest(
            "collection-private-only",
            kind="collection",
            source="receipts/private-only",
            files=[
                {
                    "path": "job.log",
                    "sha256": None,
                    "bytes": 800,
                    "tier": "T4",
                    "licence": None,
                    "visibility": "private",
                    "private_why": "identity",
                }
            ],
            copies=[],
            private_files={"unapproved": 3},
        ),
        # 5. Legacy rnd-watch manifest without `kind`
        make_run_manifest(
            "rnd-watch",
            kind=None,
            source="rnd-watch",
            files=[
                {
                    "path": "summary.json",
                    "sha256": SHA_B,
                    "bytes": 200,
                    "tier": "T4",
                    "licence": LIC_CC,
                    "visibility": "public",
                }
            ],
            copies=[
                {"sha256": SHA_B, "store": "rnd-data", "location": "runs/rnd-watch/files/summary.json"},
            ],
        ),
    ]

    for m in manifests:
        mdir = store_dir / "runs" / m["id"]
        mdir.mkdir(parents=True, exist_ok=True)
        (mdir / "manifest.json").write_text(json.dumps(m, indent=1) + "\n", encoding="utf-8")

    return store_dir


# ----------------------------------------------------------------------
# 1. Live repo schema & counts
# ----------------------------------------------------------------------


def test_live_repo_manifests_and_store_validate() -> None:
    """Every real runs/*/manifest.json and store.json in the checkout passes the schema validator."""
    schema_id, problems = validate_file(REPO_ROOT / "store.json")
    assert schema_id == STORE_SCHEMA
    assert problems == []

    manifest_paths = sorted((REPO_ROOT / "runs").glob("*/manifest.json"))
    assert len(manifest_paths) == 100
    for mp in manifest_paths:
        s_id, probs = validate_file(mp)
        assert s_id == RUN_SCHEMA, f"{mp}: unexpected schema {s_id}"
        assert probs == [], f"{mp}: validation failed: {probs}"


def test_live_repo_ls_counts() -> None:
    """Gate 3 counts on live repo: 100 manifests (74 runs, 22 collections, 4 without kind); 69 MIT, 88 CC-BY-4.0."""
    store = Store(REPO_ROOT)
    all_runs = store.runs()
    assert len(all_runs) == 100
    assert sum(1 for r in all_runs if r["kind"] == "run") == 74
    assert sum(1 for r in all_runs if r["kind"] == "collection") == 22
    no_kind = [r for r in all_runs if r["kind"] is None]
    assert len(no_kind) == 4
    assert all(r["kind_label"] == "(no kind)" for r in no_kind)
    assert [r["id"] for r in no_kind] == [
        "rnd-watch",
        "rnd-watch--argon-gpu-stack",
        "rnd-watch--reports",
        "rnd-watch--runs",
    ]

    mit_runs = store.runs(licence="MIT")
    cc_runs = store.runs(licence="CC-BY-4.0")
    assert len(mit_runs) == 69
    assert len(cc_runs) == 88

    mit_ids = {r["id"] for r in mit_runs}
    cc_ids = {r["id"] for r in cc_runs}
    assert len(mit_ids & cc_ids) == 67
    assert sum(1 for r in all_runs if r["public_files"] == 0) == 10

    assert len(store.runs(kind="run")) == 74
    assert len(store.runs(kind="collection")) == 22
    assert len(store.runs(source="receipts")) == 96
    assert len(store.runs(source="rnd-watch")) == 4

    code, out, err = run_cli("--root", str(REPO_ROOT), "ls")
    assert code == 0
    assert err == ""
    assert "100 manifests: 74 runs, 22 collections and 4 without kind" in out


# ----------------------------------------------------------------------
# 2. Seeded bad manifests & schema rules
# ----------------------------------------------------------------------


def test_seeded_bad_manifests_are_refused(tmp_path: Path) -> None:
    """Gate 2: seeded bad manifests are each refused, and private hashes are never echoed."""
    # 1. Private entry with a hash (must fail AND must redact the hash from output)
    secret_sha = "deadbeef" * 8
    m_priv_hash = make_run_manifest(
        "run-bad-hash",
        files=[
            {
                "path": "window.log",
                "sha256": secret_sha,
                "bytes": 10,
                "tier": "T4",
                "licence": None,
                "visibility": "private",
                "private_why": "identity",
            }
        ],
        copies=[],
    )
    probs = validate_document(m_priv_hash)
    assert probs
    assert any("private entry must not carry a sha256 value" in p for p in probs)
    assert secret_sha not in " ".join(probs)

    bad_file = tmp_path / "bad_priv_hash.json"
    bad_file.write_text(json.dumps(m_priv_hash), encoding="utf-8")
    code, out, err = run_cli("schema", "--check", str(bad_file))
    assert code == 1
    assert secret_sha not in out
    assert secret_sha not in err
    assert "error: SCHEMA_INVALID:" in err

    # Also accepted when sha256 is omitted on a private entry
    m_priv_absent_sha = make_run_manifest(
        "run-ok-priv",
        files=[
            {
                "path": "window.log",
                "bytes": 10,
                "tier": "T4",
                "visibility": "private",
                "private_why": "identity",
            }
        ],
        copies=[],
    )
    assert validate_document(m_priv_absent_sha) == []

    # 2. Entry with no `visibility`
    m_no_vis = make_run_manifest(
        "run-no-vis",
        files=[
            {
                "path": "outcome.json",
                "sha256": SHA_A,
                "bytes": 10,
                "tier": "T4",
                "licence": LIC_CC,
            }
        ],
    )
    probs = validate_document(m_no_vis)
    assert any("visibility" in p for p in probs)

    # 3. Entry with `"visibility": "internal"`
    m_bad_vis = make_run_manifest(
        "run-bad-vis",
        files=[
            {
                "path": "outcome.json",
                "sha256": SHA_A,
                "bytes": 10,
                "tier": "T4",
                "licence": LIC_CC,
                "visibility": "internal",
            }
        ],
    )
    probs = validate_document(m_bad_vis)
    assert any("visibility" in p for p in probs)

    # 4. Manifest without `kind` whose id is not rnd-watch
    m_no_kind = make_run_manifest("receipts--window-a", kind=None)
    probs = validate_document(m_no_kind)
    assert any("missing required key 'kind'" in p for p in probs)

    # 5. Manifest without `kind` whose id is `rnd-watch` or `rnd-watch--*` IS allowed
    assert is_legacy_rnd_watch_id("rnd-watch") is True
    assert is_legacy_rnd_watch_id("rnd-watch--sub") is True
    assert is_legacy_rnd_watch_id("rnd-watcher") is False
    assert validate_document(make_run_manifest("rnd-watch", kind=None)) == []
    assert validate_document(make_run_manifest("rnd-watch--reports", kind=None)) == []

    # 6. Private entry with private_why != "identity"
    m_bad_why = make_run_manifest(
        "run-bad-why",
        files=[
            {
                "path": "window.log",
                "sha256": None,
                "bytes": 10,
                "tier": "T4",
                "licence": None,
                "visibility": "private",
                "private_why": "unapproved",
            }
        ],
        copies=[],
    )
    assert any("private_why" in p for p in validate_document(m_bad_why))

    # 7. Public entry with null licence
    m_null_lic = make_run_manifest(
        "run-null-lic",
        files=[
            {
                "path": "outcome.json",
                "sha256": SHA_A,
                "bytes": 10,
                "tier": "T4",
                "licence": None,
                "visibility": "public",
            }
        ],
    )
    assert any("licence" in p for p in validate_document(m_null_lic))

    # 8. Unknown schema version refused
    m_unknown_schema = make_run_manifest("run-a")
    m_unknown_schema["schema"] = "rnd-data-run/v99"
    probs = validate_document(m_unknown_schema)
    assert any("unknown schema" in p for p in probs)

    # 9. Optional R2 attribution fields on file and store are accepted
    assert DEFAULT_CREATOR == "mcp-tool-shop"
    assert DEFAULT_COPYRIGHT == "Copyright (c) 2026 mcp-tool-shop"
    m_attr = make_run_manifest(
        "run-attr",
        files=[
            {
                "path": "outcome.json",
                "sha256": SHA_A,
                "bytes": 100,
                "tier": "T4",
                "licence": LIC_CC,
                "visibility": "public",
                "creator": DEFAULT_CREATOR,
                "copyright": DEFAULT_COPYRIGHT,
                "prior_modifications": ["trimmed trailing whitespace"],
            }
        ],
    )
    assert validate_document(m_attr) == []

    s_attr = make_store_json()
    s_attr["attribution"] = {
        "creator": DEFAULT_CREATOR,
        "copyright": DEFAULT_COPYRIGHT,
        "licence": LIC_CC,
        "licence_uri": "https://creativecommons.org/licenses/by/4.0/",
    }
    assert validate_document(s_attr) == []

    # 10. Copy naming private store is refused
    m_priv_copy = make_run_manifest(
        "run-priv-copy",
        copies=[{"sha256": SHA_A, "store": "rnd-data-private", "location": "runs/run-priv-copy/files/outcome.json"}],
    )
    assert any("private store" in p for p in validate_document(m_priv_copy))


def test_seeded_path_and_copy_location_rules(tmp_path: Path) -> None:
    """Seeded path and copy-location tests: unsafe paths refused; duplicate-hash files accepted."""
    bad_paths = [
        "../..",
        "../../etc/passwd",
        "sub/../../outside.txt",
        "C" + ":/folder/file.txt",
        "/ho" + "me/someone/file.txt",
        "sub\\notes.txt",
    ]
    for bad_path in bad_paths:
        # Refused on public_file_entry.path, without echoing the path value
        m_pub = make_run_manifest(
            "run-bad-path",
            files=[
                {
                    "path": bad_path,
                    "sha256": SHA_A,
                    "bytes": 10,
                    "tier": "T4",
                    "licence": LIC_CC,
                    "visibility": "public",
                }
            ],
            copies=[],
        )
        probs = validate_document(m_pub)
        assert probs, f"expected refusal for public path {bad_path!r}"
        assert any("unsafe path" in p for p in probs)
        assert bad_path not in " ".join(probs)

        # Refused on private_file_entry.path, without echoing the path value
        m_priv = make_run_manifest(
            "run-bad-priv-path",
            files=[
                {
                    "path": bad_path,
                    "sha256": None,
                    "bytes": 10,
                    "tier": "T4",
                    "licence": None,
                    "visibility": "private",
                    "private_why": "identity",
                }
            ],
            copies=[],
        )
        probs_priv = validate_document(m_priv)
        assert probs_priv, f"expected refusal for private path {bad_path!r}"
        assert any("unsafe path" in p for p in probs_priv)
        assert bad_path not in " ".join(probs_priv)

        # Refused on copy_entry.location, without echoing the location value
        m_copy = make_run_manifest(
            "run-bad-copy-loc",
            copies=[{"sha256": SHA_A, "store": "rnd-data", "location": bad_path}],
        )
        probs_copy = validate_document(m_copy)
        assert probs_copy, f"expected refusal for copy location {bad_path!r}"
        assert any("unsafe path" in p for p in probs_copy)
        assert bad_path not in " ".join(probs_copy)

    # Refused: a `d` copy whose location hash is not its own sha256
    m_bad_d_copy = make_run_manifest(
        "run-bad-d-copy",
        copies=[{"sha256": SHA_A, "store": "d", "location": blob_rel(SHA_B)}],
    )
    probs_d = validate_document(m_bad_d_copy)
    assert any("store 'd' copy location must be blobs/<sha256[0:2]>/<sha256>" in p for p in probs_d)

    # Refused: an `rnd-data` copy outside its own run (or pointing to a path not holding that sha256)
    m_outside_run = make_run_manifest(
        "run-a",
        copies=[{"sha256": SHA_A, "store": "rnd-data", "location": "runs/run-other/files/outcome.json"}],
    )
    probs_out = validate_document(m_outside_run)
    assert any("store 'rnd-data' copy location must be runs/<id>/files/<path>" in p for p in probs_out)

    # Accepted: one run holding two identical files (same sha256, two different paths and two copies)
    m_dup = make_run_manifest(
        "run-dup-files",
        files=[
            {
                "path": "job.log",
                "sha256": SHA_A,
                "bytes": 128,
                "tier": "T4",
                "licence": LIC_CC,
                "visibility": "public",
            },
            {
                "path": "sub/job-copy.log",
                "sha256": SHA_A,
                "bytes": 128,
                "tier": "T4",
                "licence": LIC_CC,
                "visibility": "public",
            },
        ],
        copies=[
            {"sha256": SHA_A, "store": "rnd-data", "location": "runs/run-dup-files/files/job.log"},
            {"sha256": SHA_A, "store": "rnd-data", "location": "runs/run-dup-files/files/sub/job-copy.log"},
        ],
    )
    assert validate_document(m_dup) == []

    # Verify CLI `schema --check` passes on all 100 real manifests
    for mp in sorted((REPO_ROOT / "runs").glob("*/manifest.json")):
        code, out, err = run_cli("schema", "--check", str(mp))
        assert code == 0, f"{mp}: {err}"


def test_schema_api_and_cli_check(tmp_path: Path) -> None:
    """Test `Store.schema()` and `rnd-data schema [--check <file>]`."""
    all_schemas = Store.schema()
    assert isinstance(all_schemas, dict)
    assert set(all_schemas.keys()) == {RUN_SCHEMA, STORE_SCHEMA}
    assert Store.schema("run") == load_schemas()[RUN_SCHEMA]
    assert Store.schema(RUN_SCHEMA) == load_schemas()[RUN_SCHEMA]
    assert Store.schema("store") == load_schemas()[STORE_SCHEMA]
    assert Store.schema(STORE_SCHEMA) == load_schemas()[STORE_SCHEMA]

    with pytest.raises(RndDataError) as exc_info:
        Store.schema("nope")
    assert exc_info.value.code == "UNKNOWN_SCHEMA"
    assert exc_info.value.exit_code == 2

    valid_path = tmp_path / "manifest.json"
    valid_doc = make_run_manifest("run-valid")
    valid_path.write_text(json.dumps(valid_doc), encoding="utf-8")
    assert Store.schema(check=valid_doc) == []
    assert Store.schema(check=valid_path) == []

    code, out, err = run_cli("schema")
    assert code == 0
    assert json.loads(out)[RUN_SCHEMA]["title"] == "rnd-data run manifest (v1)"

    code, out, err = run_cli("schema", "--check", str(valid_path))
    assert code == 0
    assert "manifest.json: ok (rnd-data-run/v1)" in out

    # Non-JSON and missing file
    bad_json = tmp_path / "broken.json"
    bad_json.write_text("{not json", encoding="utf-8")
    code, _, err = run_cli("schema", "--check", str(bad_json))
    assert code == 1
    assert "not valid JSON" in err

    code, _, err = run_cli("schema", "--check", str(tmp_path / "missing.json"))
    assert code == 1
    assert "cannot read file" in err

    # Non-object JSON and missing schema key
    assert validate_document([1, 2, 3]) == ["<root>: manifest must be a JSON object"]
    assert validate_document({}) == ["schema: missing required 'schema' string"]


# ----------------------------------------------------------------------
# 3. `ls --licence` four forms, mixed, private-only, and no-match
# ----------------------------------------------------------------------


def test_leading_licence_id_all_four_forms() -> None:
    """`leading_licence_id` extracts text before the first `' ('` with no case folding."""
    assert leading_licence_id(LIC_CC) == "CC-BY-4.0"
    assert leading_licence_id(LIC_MIT_LLAMA) == "MIT"
    assert leading_licence_id(LIC_MIT) == "MIT"
    assert leading_licence_id(LIC_CC_EXCERPTS) == "CC-BY-4.0"
    assert leading_licence_id(LIC_CC_EXCERPTS) != "MIT"


def test_ls_filters_mixed_private_only_and_no_match(tmp_path: Path) -> None:
    """Test `ls --licence` on all 4 forms, mixed manifest, no-public-files manifest, and no-match."""
    store_dir = write_fixture_store(tmp_path)
    store = Store(store_dir)

    # All 5 manifests
    all_rows = store.runs()
    assert [r["id"] for r in all_rows] == [
        "collection-mit",
        "collection-private-only",
        "rnd-watch",
        "run-cc-excerpts",
        "run-mixed",
    ]

    # MIT matches collection-mit (plain MIT) and run-mixed (MIT llama.cpp), NOT run-cc-excerpts or private-only
    mit_rows = store.runs(licence="MIT")
    assert [r["id"] for r in mit_rows] == ["collection-mit", "run-mixed"]

    # CC-BY-4.0 matches rnd-watch, run-cc-excerpts (both plain and parenthetical CC-BY-4.0), and run-mixed
    cc_rows = store.runs(licence="CC-BY-4.0")
    assert [r["id"] for r in cc_rows] == ["rnd-watch", "run-cc-excerpts", "run-mixed"]

    # Case sensitivity: 'mit' matches nothing
    assert store.runs(licence="mit") == []

    # CLI output for `--licence MIT` must show ALL public licences in `run-mixed`, not only MIT
    code, out, err = run_cli("--root", str(store_dir), "ls", "--licence", "MIT")
    assert code == 0
    assert err == ""
    assert "collection-mit" in out
    assert "run-mixed" in out
    assert "run-cc-excerpts" not in out
    assert "collection-private-only" not in out
    # Both public licences of run-mixed appear in its row
    mixed_line = next(line for line in out.splitlines() if "run-mixed" in line)
    assert LIC_CC in mixed_line
    assert LIC_MIT_LLAMA in mixed_line

    # Filter that matches nothing: empty stdout, exit 0, stderr hint listing identifiers present
    code, out, err = run_cli("--root", str(store_dir), "ls", "--licence", "Apache-2.0")
    assert code == 0
    assert out == ""
    assert "hint:" in err
    assert "CC-BY-4.0, MIT" in err

    # `--help` explains the leading licence identifier rule and the 5 CC-BY-4.0 files
    code, out, err = run_cli("ls", "--help")
    assert code == 0
    assert "leading licence identifier" in out
    assert "5 CC-BY-4.0" in out


# ----------------------------------------------------------------------
# 4. `where` and never touching `blobs/` for an undeclared hash
# ----------------------------------------------------------------------


def test_where_declared_and_undeclared_never_touches_blobs(tmp_path: Path) -> None:
    """`where` finds public files by hash/path and never touches `blobs/` for an undeclared hash."""
    store_dir = write_fixture_store(tmp_path)
    store = Store(store_dir)

    # Declared public hash (prefix and full)
    hits = store.where(SHA_C[:12])
    assert len(hits) == 1
    assert hits[0]["sha256"] == SHA_C
    assert hits[0]["blob"] == blob_rel(SHA_C)
    assert hits[0]["names"] == [{"manifest_id": "run-mixed", "path": "upload/server.gz", "licence": LIC_MIT_LLAMA}]
    assert hits[0]["copies"] == [{"store": "d", "location": blob_rel(SHA_C)}]

    # Lookup by path shared across two manifests
    hits_path = store.where("outcome.json")
    assert len(hits_path) == 1
    assert hits_path[0]["sha256"] == SHA_A
    assert [n["manifest_id"] for n in hits_path[0]["names"]] == ["run-cc-excerpts", "run-mixed"]

    # Private entry path is never matched by `where`
    assert store.where("window.log") == []
    assert store.where("job.log") == []

    # Undeclared hash: patch os.stat, os.path.exists, and builtins.open to assert no `blobs/` path is touched
    undeclared_hash = "f" * 64
    real_stat = os.stat
    real_exists = os.path.exists
    real_open = builtins.open

    def guarded_stat(path: Any, *args: Any, **kwargs: Any) -> Any:
        if "blobs" in str(path).replace("\\", "/").split("/"):
            raise AssertionError(f"os.stat touched blobs/ for undeclared hash: {path}")
        return real_stat(path, *args, **kwargs)

    def guarded_exists(path: Any) -> bool:
        if "blobs" in str(path).replace("\\", "/").split("/"):
            raise AssertionError(f"os.path.exists touched blobs/ for undeclared hash: {path}")
        return real_exists(path)

    def guarded_open(file: Any, *args: Any, **kwargs: Any) -> Any:
        if "blobs" in str(file).replace("\\", "/").split("/"):
            raise AssertionError(f"open touched blobs/ for undeclared hash: {file}")
        return real_open(file, *args, **kwargs)

    with (
        mock.patch("os.stat", side_effect=guarded_stat),
        mock.patch("os.path.exists", side_effect=guarded_exists),
        mock.patch("builtins.open", side_effect=guarded_open),
    ):
        assert store.where(undeclared_hash) == []
        code, out, err = run_cli("--root", str(store_dir), "where", undeclared_hash)

    assert code == 1
    assert out == ""
    assert "error: NOT_DECLARED:" in err
    assert "not declared" in err
    assert "hint:" in err

    # CLI `where` on a declared file
    code, out, err = run_cli("--root", str(store_dir), "where", SHA_C[:10])
    assert code == 0
    assert err == ""
    assert SHA_C in out
    assert "as run-mixed:upload/server.gz" in out
    assert f"copy d: {blob_rel(SHA_C)}" in out


# ----------------------------------------------------------------------
# 5. `show` command and error handling
# ----------------------------------------------------------------------


def test_show_command_and_errors(tmp_path: Path) -> None:
    store_dir = write_fixture_store(tmp_path)

    code, out, err = run_cli("--root", str(store_dir), "show", "run-mixed")
    assert code == 0
    assert err == ""
    assert "run-mixed  (run)" in out
    assert "upload/server.gz  public" in out
    assert "window.log  private (identity)" in out
    assert "private_files (by reason): unapproved: 2" in out

    # No-kind manifest
    code, out, err = run_cli("--root", str(store_dir), "show", "rnd-watch")
    assert code == 0
    assert "rnd-watch  ((no kind))" in out

    # Missing run -> exit 1
    code, out, err = run_cli("--root", str(store_dir), "show", "no-such-run")
    assert code == 1
    assert "error: NO_RUN:" in err
    assert "hint:" in err

    # Path traversal / invalid run id -> exit 2
    code, out, err = run_cli("--root", str(store_dir), "show", "../outside")
    assert code == 2
    assert "error: BAD_RUN_ID:" in err


def test_root_resolution_and_error_shape(tmp_path: Path) -> None:
    store_a = write_fixture_store(tmp_path / "alpha")
    store_b = write_fixture_store(tmp_path / "beta")
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()

    # 1. --root wins over $RND_DATA and cwd
    resolved = resolve_root(store_a, env={"RND_DATA": str(store_b)}, cwd=empty_dir)
    assert resolved == store_a

    # 2. $RND_DATA wins over cwd when --root is None
    resolved = resolve_root(None, env={"RND_DATA": str(store_b)}, cwd=store_a)
    assert resolved == store_b

    # 3. cwd is used when it holds store.json
    resolved = resolve_root(None, env={}, cwd=store_a)
    assert resolved == store_a

    # 4. Neither --root, $RND_DATA, nor cwd with store.json -> exit 2
    with pytest.raises(RndDataError) as exc_info:
        resolve_root(None, env={}, cwd=empty_dir)
    assert exc_info.value.code == "NO_STORE"
    assert exc_info.value.exit_code == 2

    # 5. Bad --root -> exit 2
    code, out, err = run_cli("--root", str(empty_dir), "ls")
    assert code == 2
    assert "error: NOT_A_STORE:" in err
    assert "hint:" in err

    # 6. CLI usage error (no subcommand) -> exit 2 in studio shape
    code, out, err = run_cli()
    assert code == 2
    assert "error: USAGE:" in err
    assert "hint:" in err

    # 7. Invalid Store inputs
    store = Store(store_a)
    assert store.store_manifest()["schema"] == STORE_SCHEMA
    with pytest.raises(RndDataError) as exc_info:
        store.runs(kind="invalid")
    assert exc_info.value.exit_code == 2
    with pytest.raises(RndDataError) as exc_info:
        store.where("   ")
    assert exc_info.value.exit_code == 2
    with pytest.raises(RndDataError) as exc_info:
        blob_rel("not-a-sha")
    assert exc_info.value.exit_code == 2

    # 8. Corrupted store.json or manifest id mismatch
    bad_store_dir = copy.deepcopy(store_a)
    bad_store_copy = tmp_path / "bad-store"
    shutil.copytree(bad_store_dir, bad_store_copy)
    m_mismatch = make_run_manifest("other-id")
    (bad_store_copy / "runs" / "rnd-watch" / "manifest.json").write_text(
        json.dumps(m_mismatch), encoding="utf-8"
    )
    with pytest.raises(RndDataError) as exc_info:
        Store(bad_store_copy).manifest("rnd-watch")
    assert exc_info.value.code == "MANIFEST_ID_MISMATCH"

    (bad_store_copy / "store.json").write_text(json.dumps({"schema": STORE_SCHEMA}), encoding="utf-8")
    with pytest.raises(RndDataError) as exc_info:
        Store(bad_store_copy)
    assert exc_info.value.code == "STORE_INVALID"


# ----------------------------------------------------------------------
# 6. Wheel and sdist ship no data
# ----------------------------------------------------------------------


def test_wheel_and_sdist_ship_no_data(tmp_path: Path) -> None:
    """Build both wheel and sdist and assert no `runs/` file and no `store.json` inside."""
    dist_dir = tmp_path / "dist"
    egg_info = REPO_ROOT / "src" / "rnd_data.egg-info"
    build_dir = REPO_ROOT / "build"
    try:
        res = subprocess.run(
            [sys.executable, "-m", "build", "--no-isolation", "-o", str(dist_dir), str(REPO_ROOT)],
            capture_output=True,
            text=True,
            check=False,
            timeout=120,
        )
        assert res.returncode == 0, f"build failed:\n{res.stdout}\n{res.stderr}"
    finally:
        for artifact_dir in (egg_info, build_dir):
            if artifact_dir.exists():
                shutil.rmtree(artifact_dir, ignore_errors=True)

    wheels = list(dist_dir.glob("*.whl"))
    sdists = list(dist_dir.glob("*.tar.gz"))
    assert len(wheels) == 1
    assert len(sdists) == 1

    with zipfile.ZipFile(wheels[0]) as zf:
        whl_names = zf.namelist()
    assert any(n.startswith("rnd_data/") for n in whl_names)
    assert any(n.endswith("LICENSE-MIT") for n in whl_names)
    assert any(n.endswith("schemas/run-v1.schema.json") for n in whl_names)
    assert any(n.endswith("schemas/store-v1.schema.json") for n in whl_names)
    assert not any("runs/" in n for n in whl_names)
    assert not any(n.endswith("store.json") for n in whl_names)

    with tarfile.open(sdists[0], "r:gz") as tf:
        sdist_names = [m.name for m in tf.getmembers()]
    assert any("src/rnd_data/" in n for n in sdist_names)
    assert any(n.endswith("/LICENSE-MIT") for n in sdist_names)
    assert not any("/runs/" in n or n.endswith("/runs") for n in sdist_names)
    assert not any(n.endswith("/store.json") for n in sdist_names)

    # Module __version__ and python -m rnd_data --version
    assert rnd_data.__version__ == "0.1.0"
    ver_res = subprocess.run(
        [sys.executable, "-m", "rnd_data", "--version"],
        cwd=REPO_ROOT / "src",
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )
    assert ver_res.returncode == 0
    assert "rnd-data 0.1.0" in ver_res.stdout
