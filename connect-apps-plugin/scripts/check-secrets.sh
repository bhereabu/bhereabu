#!/usr/bin/env bash
# Scans modified files for accidentally committed secrets or API keys.
# Runs as a PostToolUse hook after Write/Edit operations.

set -euo pipefail

FILE="${CLAUDE_FILE:-}"
if [ -z "$FILE" ] || [ ! -f "$FILE" ]; then
  exit 0
fi

# Patterns that suggest hardcoded secrets
PATTERNS=(
  'sk-[a-zA-Z0-9]{20,}'
  'AKIA[0-9A-Z]{16}'
  'ghp_[a-zA-Z0-9]{36}'
  'xox[bposa]-[a-zA-Z0-9-]+'
  'eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*'
)

for pattern in "${PATTERNS[@]}"; do
  if grep -qE "$pattern" "$FILE" 2>/dev/null; then
    echo "Warning: Possible secret or API key detected in $FILE"
    echo "Please use environment variables instead of hardcoding credentials."
    exit 0
  fi
done
