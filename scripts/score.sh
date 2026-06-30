#!/usr/bin/env bash
# Print the highsignal eval cases for a manual or agent-driven pass.
# Each dirty case must flag the named tell; each clean case must flag nothing.
# Usage: scripts/score.sh
set -euo pipefail
here="$(cd "$(dirname "$0")/.." && pwd)"
echo "highsignal eval set — load SKILL.md, run each draft in detect mode, compare to 'expect'."
echo
grep -nE '^### |^expect:' "$here/tests/prompts.md"
echo
echo "Dirty cases: $(grep -c '^### [0-9]' "$here/tests/prompts.md") · Clean cases: $(grep -c '^### C' "$here/tests/prompts.md")"
