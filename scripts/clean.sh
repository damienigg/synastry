#!/usr/bin/env bash
# Remove temporary and generated files from the repository.
#
# Usage:
#     bash scripts/clean.sh          # remove caches and reports
#     bash scripts/clean.sh --all    # also remove .jpl_cache.json

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

removed=0

# __pycache__ directories
while IFS= read -r -d '' d; do
    rm -rf "$d"
    echo "  removed $d"
    removed=$((removed + 1))
done < <(find . -type d -name '__pycache__' -not -path './.git/*' -print0)

# .pytest_cache directories
while IFS= read -r -d '' d; do
    rm -rf "$d"
    echo "  removed $d"
    removed=$((removed + 1))
done < <(find . -type d -name '.pytest_cache' -not -path './.git/*' -print0)

# .mypy_cache
if [ -d .mypy_cache ]; then
    rm -rf .mypy_cache
    echo "  removed .mypy_cache"
    removed=$((removed + 1))
fi

# .coverage
if [ -f .coverage ]; then
    rm -f .coverage
    echo "  removed .coverage"
    removed=$((removed + 1))
fi

# Stale .pyc files outside __pycache__
while IFS= read -r -d '' f; do
    rm -f "$f"
    echo "  removed $f"
    removed=$((removed + 1))
done < <(find . -name '*.pyc' -not -path './.git/*' -print0)

# Test reports
if [ -d reports ] && [ -n "$(ls -A reports/ 2>/dev/null)" ]; then
    count=$(find reports -type f | wc -l)
    rm -f reports/*.txt
    echo "  removed $count test report(s) from reports/"
    removed=$((removed + 1))
fi

# Optional: JPL cache (only with --all)
if [[ "${1:-}" == "--all" ]] && [ -f .jpl_cache.json ]; then
    rm -f .jpl_cache.json
    echo "  removed .jpl_cache.json"
    removed=$((removed + 1))
fi

if [ "$removed" -eq 0 ]; then
    echo "Nothing to clean."
else
    echo "Done — cleaned $removed item(s)."
fi
