"""rnd-data: read-only reader and schema validator for the rnd-data research store."""

from .schema import (
    DEFAULT_COPYRIGHT,
    DEFAULT_CREATOR,
    RUN_SCHEMA,
    STORE_SCHEMA,
    is_legacy_rnd_watch_id,
    is_safe_rel_posix_path,
    load_schemas,
    validate_document,
    validate_file,
)
from .store import (
    RndDataError,
    Store,
    blob_rel,
    leading_licence_id,
    resolve_root,
)

__version__ = "0.1.0"

__all__ = [
    "DEFAULT_COPYRIGHT",
    "DEFAULT_CREATOR",
    "RUN_SCHEMA",
    "STORE_SCHEMA",
    "RndDataError",
    "Store",
    "__version__",
    "blob_rel",
    "is_legacy_rnd_watch_id",
    "is_safe_rel_posix_path",
    "leading_licence_id",
    "load_schemas",
    "resolve_root",
    "validate_document",
    "validate_file",
]
