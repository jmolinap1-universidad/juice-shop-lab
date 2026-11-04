#!/usr/bin/env bash
# Uso: scripts/bitacora.sh <fase> "<comando>" "<herramienta y versión>" "<resultado>"
set -euo pipefail
f="$(dirname "$0")/../evidence/bitacora.md"
printf '| %s | %s | `%s` | %s | %s |\n' "$(date -Iseconds)" "$1" "$2" "$3" "$4" >> "$f"
