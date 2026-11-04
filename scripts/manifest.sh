#!/usr/bin/env bash
# Regenera evidence/MANIFEST.sha256 con el hash de cada archivo de evidencia.
set -euo pipefail
cd "$(dirname "$0")/../evidence"
find . -type f ! -name MANIFEST.sha256 ! -path './*/tmp/*' -print0 | LC_ALL=C sort -z | xargs -0 sha256sum > MANIFEST.sha256
echo "MANIFEST: $(wc -l < MANIFEST.sha256) archivos"
