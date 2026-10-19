#!/usr/bin/env bash
# Check rnd-data against its manifests, with rnd's own checker. rnd-data holds no code: every check is rnd's.
#
#   bash verify.sh          the public check (CI): re-hash every git copy, skip the blob store and the private companion
#   bash verify.sh --full   the full check (the rig, where the blob store is configured)
#
# Exits non-zero on the first failure.
set -euo pipefail

cd "$(dirname "$0")"

case "${1:-}" in
  "")
    RND_DATA="$PWD" rnd raw verify --public-only
    ;;
  --full)
    RND_DATA="$PWD" rnd raw verify
    ;;
  *)
    echo "usage: bash verify.sh [--full]" >&2
    exit 2
    ;;
esac
