"""CLI for rnd-data (phase R1: ls, show, where, schema)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, NoReturn

from . import __version__
from .schema import validate_file
from .store import RndDataError, Store


def fail(code: str, message: str, hint: str = "", exit_code: int = 2) -> int:
    """Print an error in the studio shape (code, message and hint) to stderr and return `exit_code`."""
    print(f"error: {code}: {message}", file=sys.stderr)
    if hint:
        print(f"  hint: {hint}", file=sys.stderr)
    return exit_code


class _StudioArgumentParser(argparse.ArgumentParser):
    """ArgumentParser that formats usage errors in the studio shape with exit code 2."""

    def error(self, message: str) -> NoReturn:
        fail("USAGE", message, f"run `{self.prog} --help` for usage", exit_code=2)
        raise SystemExit(2)


def _open_store(args: argparse.Namespace) -> Store:
    return Store(args.root)


def cmd_ls(args: argparse.Namespace) -> int:
    store = _open_store(args)
    rows = store.runs(kind=args.kind, source=args.source, licence=args.licence)
    if not rows:
        present = store.licence_identifiers()
        present_str = ", ".join(present) if present else "none"
        print(
            f"hint: no manifests matched; leading licence identifiers present: {present_str}",
            file=sys.stderr,
        )
        return 0

    for r in rows:
        lic_text = "; ".join(r["licences"]) if r["licences"] else "(no public files)"
        print(
            f"{r['id']:<56}  {r['kind_label']:<10}  "
            f"{r['public_files']:>3} public, {r['private_files']:>3} private  "
            f"{r['bytes']:>12,} B  {lic_text}"
        )

    n_runs = sum(1 for r in rows if r["kind"] == "run")
    n_cols = sum(1 for r in rows if r["kind"] == "collection")
    n_none = sum(1 for r in rows if r["kind"] is None)
    print(f"{len(rows)} manifests: {n_runs} runs, {n_cols} collections and {n_none} without kind")
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    store = _open_store(args)
    m = store.manifest(args.run)
    kind_label = m.get("kind") or "(no kind)"
    files = m.get("files", ())
    public_entries = [f for f in files if f.get("visibility") == "public"]
    private_entries = [f for f in files if f.get("visibility") == "private"]
    private_counts: dict[str, Any] = m.get("private_files", {})
    copies = m.get("copies", ())

    print(f"{m['id']}  ({kind_label})")
    print(f"  schema:       {m['schema']}")
    print(f"  source:       {m['source']}")
    print(f"  ingested:     {m['ingested']}  rnd_commit: {m['rnd_commit']}")
    models = ", ".join(m.get("models", ())) if m.get("models") else "(none)"
    print(f"  models:       {models}")
    print(f"  licence_note: {m.get('licence_note', '')}")

    print(f"  files ({len(public_entries)} public, {len(private_entries)} listed private):")
    for f in public_entries:
        print(
            f"    {f['path']}  public  {f['bytes']:,} bytes  tier {f['tier']}  "
            f"sha256 {f['sha256']}  licence {f['licence']}"
        )
    for f in private_entries:
        print(
            f"    {f['path']}  private ({f.get('private_why', 'identity')})  "
            f"{f['bytes']:,} bytes  tier {f['tier']}"
        )

    if private_counts:
        counts_str = ", ".join(f"{k}: {v}" for k, v in sorted(private_counts.items()))
    else:
        counts_str = "none"
    print(f"  private_files (by reason): {counts_str}")

    print(f"  copies ({len(copies)}):")
    for c in copies:
        print(f"    {c['store']}: {c['location']}  ({c['sha256']})")
    return 0


def cmd_where(args: argparse.Namespace) -> int:
    store = _open_store(args)
    matches = store.where(args.target)
    if not matches:
        return fail(
            "NOT_DECLARED",
            f"{args.target!r} is not declared on any public entry",
            "give a SHA-256 (8+ hex characters) or a path declared on a public file entry",
            exit_code=1,
        )
    for item in matches:
        print(
            f"{item['sha256']}  {item['bytes']} bytes  tier {item['tier']}  "
            f"licence {item['licence'] or '-'}"
        )
        for n in item["names"]:
            print(f"  as {n['manifest_id']}:{n['path']}")
        for c in item["copies"]:
            print(f"  copy {c['store']}: {c['location']}")
    return 0


def cmd_schema(args: argparse.Namespace) -> int:
    if args.root is not None:
        _open_store(args)
    if args.check:
        target = Path(args.check)
        schema_id, problems = validate_file(target)
        if problems:
            return fail(
                "SCHEMA_INVALID",
                f"{target.name}: {'; '.join(problems)}",
                "check the manifest against `rnd-data schema` (rnd-data-run/v1 or rnd-data-store/v1)",
                exit_code=1,
            )
        print(f"{target.name}: ok ({schema_id})")
        return 0

    print(json.dumps(Store.schema(), indent=1, ensure_ascii=False))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = _StudioArgumentParser(
        prog="rnd-data",
        description="Read-only reader and schema validator for the rnd-data research store.",
    )
    parser.add_argument(
        "--root",
        metavar="PATH",
        help="the rnd-data store checkout (default: $RND_DATA, else current directory if it holds store.json)",
    )
    parser.add_argument("--version", action="version", version=f"rnd-data {__version__}")

    sub = parser.add_subparsers(dest="cmd", required=True)

    ls_p = sub.add_parser(
        "ls",
        help="list runs and collections with file counts, bytes and public licences",
        description=(
            "List runs and collections in the store. "
            "--licence matches the leading licence identifier (the text before the first ' (', "
            "or the whole value when there is none, compared with no case folding). "
            "A licence named only inside a parenthetical note does not match (for example, the 5 "
            "'CC-BY-4.0 (the code excerpts in `context` are MIT, ...)' files match CC-BY-4.0, not MIT)."
        ),
    )
    ls_p.set_defaults(fn=cmd_ls)
    ls_p.add_argument("--kind", choices=("run", "collection"), help="filter by manifest kind (run or collection)")
    ls_p.add_argument("--source", metavar="PREFIX", help="filter by source prefix (e.g. receipts or rnd-watch)")
    ls_p.add_argument(
        "--licence",
        metavar="ID",
        help=(
            "filter manifests where any public file entry has leading licence identifier ID "
            "(text before the first ' (', exact case; e.g. MIT or CC-BY-4.0; parenthetical mentions such as "
            "the 5 CC-BY-4.0 files with MIT code excerpts do not match MIT)"
        ),
    )

    show_p = sub.add_parser(
        "show",
        help="show one manifest in plain words: files, tiers, licences, private counts and copies",
        description="Show one run or collection manifest in plain words.",
    )
    show_p.set_defaults(fn=cmd_show)
    show_p.add_argument("run", help="the run or collection id under runs/")

    where_p = sub.add_parser(
        "where",
        help="every name and copy a public file has, by SHA-256 or path",
        description=(
            "Find every manifest entry and declared copy for a public file by SHA-256 (8+ hex) or path. "
            "Resolves from manifests only and never walks or probes blobs/."
        ),
    )
    where_p.set_defaults(fn=cmd_where)
    where_p.add_argument("target", metavar="SHA256_OR_PATH", help="SHA-256 (8+ hex chars) or public file path")

    schema_p = sub.add_parser(
        "schema",
        help="print the JSON Schemas for run and store manifests, or validate a file with --check",
        description="Print the bundled JSON Schemas (rnd-data-run/v1 and rnd-data-store/v1), or validate a manifest.",
    )
    schema_p.set_defaults(fn=cmd_schema)
    schema_p.add_argument("--check", metavar="FILE", help="validate a run manifest or store.json file")

    return parser


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code) if isinstance(exc.code, int) else 2

    try:
        return int(args.fn(args) or 0)
    except RndDataError as exc:
        return fail(exc.code, exc.message, exc.hint, exit_code=exc.exit_code)
