#!/usr/bin/env bash
# Run the highsignal eval against one or more backends and print each scorecard.
#
# Usage:
#   scripts/score.sh                 # default: codex
#   scripts/score.sh codex anthropic # several backends
#
# Backends and their auth (see tests/eval.py for the full list):
#   codex       codex exec CLI         (no key)
#   anthropic   ANTHROPIC_API_KEY env
#   openrouter  OPENROUTER_API_KEY env + --model
#   fireworks   FIREWORKS_API_KEY env  + --model  (open models)
set -euo pipefail
here="$(cd "$(dirname "$0")/.." && pwd)"
backends=("$@"); [ ${#backends[@]} -eq 0 ] && backends=(codex)
for b in "${backends[@]}"; do
  echo "================ $b ================"
  python3 "$here/tests/eval.py" --backend "$b" || true
done
