#!/usr/bin/env bash
# From Git Bash on the rig: read the two scoped tokens at Windows User scope (setx'd after this shell started) by name
# only, hand them to WSL through WSLENV, and run the check there. No value is printed or put on a command line.
set -uo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
user_var() { powershell.exe -NoProfile -Command "[Environment]::GetEnvironmentVariable('$1','User')" | tr -d '\r\n'; }
HF_TOKEN_GGUF_READ="$(user_var HF_TOKEN_GGUF_READ)"; export HF_TOKEN_GGUF_READ
HF_TOKEN_GGUF_WRITE="$(user_var HF_TOKEN_GGUF_WRITE)"; export HF_TOKEN_GGUF_WRITE
export WSLENV="HF_TOKEN_GGUF_READ:HF_TOKEN_GGUF_WRITE:SCOPES_ONLY"
MSYS_NO_PATHCONV=1 wsl -d Ubuntu -e bash -lc \
  'cd /mnt/e/AI/Publisher/receipts/colab/token-scope-check && uv run --no-project --quiet --with huggingface_hub python token_scope_check.py' \
  | tee "$here/result${SCOPES_ONLY:+-scopes}.json"
