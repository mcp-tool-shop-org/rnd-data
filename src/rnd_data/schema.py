"""JSON Schema loader and stdlib validator for rnd-data manifests."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

RUN_SCHEMA = "rnd-data-run/v1"
STORE_SCHEMA = "rnd-data-store/v1"
DEFAULT_CREATOR = "mcp-tool-shop"
DEFAULT_COPYRIGHT = "Copyright (c) 2026 mcp-tool-shop"

SCHEMA_FILES = {
    RUN_SCHEMA: "run-v1.schema.json",
    STORE_SCHEMA: "store-v1.schema.json",
}

_SCHEMAS_DIR = Path(__file__).resolve().parent / "schemas"
_LEGACY_RND_WATCH_RE = re.compile(r"^rnd-watch(?:--.+)?$")


def load_schemas() -> dict[str, dict[str, Any]]:
    """Return both bundled JSON Schemas keyed by their schema identifier."""
    return {
        schema_id: json.loads((_SCHEMAS_DIR / filename).read_text(encoding="utf-8"))
        for schema_id, filename in SCHEMA_FILES.items()
    }


def is_legacy_rnd_watch_id(run_id: object) -> bool:
    """True when `run_id` is one of the 4 early rnd-watch manifests without `kind`."""
    return isinstance(run_id, str) and bool(_LEGACY_RND_WATCH_RE.match(run_id))


def _is_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _matches_type(value: object, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "integer":
        return _is_int(value)
    if expected == "null":
        return value is None
    return False


def _resolve_ref(ref: str, root_schema: dict[str, Any]) -> dict[str, Any]:
    if not ref.startswith("#/"):
        raise ValueError(f"unsupported schema reference: {ref}")
    node: Any = root_schema
    for part in ref[2:].split("/"):
        node = node[part]
    return node


def _validate_node(
    value: Any,
    schema: dict[str, Any],
    root_schema: dict[str, Any],
    where: str,
) -> list[str]:
    """Validate `value` against `schema` using stdlib only, returning redacted problem strings."""
    if "$ref" in schema:
        return _validate_node(value, _resolve_ref(schema["$ref"], root_schema), root_schema, where)

    problems: list[str] = []

    if "type" in schema and not _matches_type(value, schema["type"]):
        if where.endswith(".sha256") and schema["type"] == "null":
            problems.append(f"{where}: private entry must not carry a sha256 value")
        elif where.endswith(".licence") and schema["type"] == "null":
            problems.append(f"{where}: private entry must have null licence")
        else:
            problems.append(f"{where}: expected {schema['type']}")
        return problems

    if "const" in schema and value != schema["const"]:
        problems.append(f"{where}: must be {schema['const']!r}")
        return problems

    if "enum" in schema and value not in schema["enum"]:
        allowed = ", ".join(repr(x) for x in schema["enum"])
        problems.append(f"{where}: must be one of {allowed}")
        return problems

    if "not" in schema and not _validate_node(value, schema["not"], root_schema, where):
        problems.append(f"{where}: value is not allowed")
        return problems

    if isinstance(value, str):
        if "minLength" in schema and len(value) < schema["minLength"]:
            problems.append(f"{where}: must be a non-empty string")
        if "pattern" in schema and not re.match(schema["pattern"], value):
            problems.append(f"{where}: does not match required pattern {schema['pattern']}")

    if _is_int(value):
        if "minimum" in schema and value < schema["minimum"]:
            problems.append(f"{where}: must be >= {schema['minimum']}")

    if isinstance(value, list):
        if "minItems" in schema and len(value) < schema["minItems"]:
            problems.append(f"{where}: must contain at least {schema['minItems']} item(s)")
        if "items" in schema:
            item_schema = schema["items"]
            for idx, item in enumerate(value):
                problems.extend(_validate_node(item, item_schema, root_schema, f"{where}[{idx}]"))

    if isinstance(value, dict):
        if "minProperties" in schema and len(value) < schema["minProperties"]:
            problems.append(f"{where}: must contain at least {schema['minProperties']} property")

        for req in schema.get("required", ()):
            if req not in value:
                problems.append(f"{where}: missing required key {req!r}")

        props = schema.get("properties", {})
        add_props = schema.get("additionalProperties", True)
        prop_names = schema.get("propertyNames")

        for k, v in value.items():
            child_where = f"{where}.{k}" if where != "<root>" else k
            if prop_names is not None:
                problems.extend(_validate_node(k, prop_names, root_schema, f"{child_where} (key)"))
            if k in props:
                problems.extend(_validate_node(v, props[k], root_schema, child_where))
            elif add_props is False:
                problems.append(f"{where}: unknown key {k!r}")
            elif isinstance(add_props, dict):
                problems.extend(_validate_node(v, add_props, root_schema, child_where))

        if "if" in schema and "then" in schema:
            cond_problems = _validate_node(value, schema["if"], root_schema, where)
            if not cond_problems:
                for req in schema["then"].get("required", ()):
                    if req not in value:
                        if req == "kind":
                            problems.append(
                                f"{where}: missing required key 'kind' (only rnd-watch manifests may omit kind)"
                            )
                        else:
                            problems.append(f"{where}: missing required key {req!r}")

        if "oneOf" in schema and not problems:
            vis = value.get("visibility")
            if vis == "public":
                problems.extend(_validate_node(value, schema["oneOf"][0], root_schema, where))
            elif vis == "private":
                problems.extend(_validate_node(value, schema["oneOf"][1], root_schema, where))
            else:
                branch_ok = any(not _validate_node(value, sub, root_schema, where) for sub in schema["oneOf"])
                if not branch_ok:
                    problems.append(f"{where}: does not match any allowed file entry variant")

    return problems


def validate_document(data: Any) -> list[str]:
    """Validate a parsed JSON object against its declared rnd-data schema."""
    if not isinstance(data, dict):
        return ["<root>: manifest must be a JSON object"]

    schema_id = data.get("schema")
    if not isinstance(schema_id, str) or not schema_id:
        return ["schema: missing required 'schema' string"]

    schemas = load_schemas()
    if schema_id not in schemas:
        return [
            f"schema: unknown schema {schema_id!r}; expected {RUN_SCHEMA!r} or {STORE_SCHEMA!r}"
        ]

    schema = schemas[schema_id]
    problems = _validate_node(data, schema, schema, "<root>")

    if schema_id == RUN_SCHEMA and isinstance(data.get("copies"), list):
        for idx, copy in enumerate(data["copies"]):
            if isinstance(copy, dict) and copy.get("store") == "rnd-data-private":
                problems.append(f"copies[{idx}].store: public manifest must not name private store")

    return problems


def validate_file(path: str | Path) -> tuple[str | None, list[str]]:
    """Read a JSON file from `path` and validate it against its declared schema."""
    file_path = Path(path)
    try:
        raw = file_path.read_text(encoding="utf-8")
    except OSError as exc:
        return None, [f"cannot read file ({exc.strerror or type(exc).__name__})"]
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        return None, [f"not valid JSON (line {exc.lineno}, column {exc.colno})"]

    schema_id = data.get("schema") if isinstance(data, dict) else None
    return (schema_id if isinstance(schema_id, str) else None), validate_document(data)
