#!/usr/bin/env bash
# Regenera evidence/MANIFEST.sha256 con el hash de cada archivo de evidencia.
# Solo incluye archivos versionados o versionables (respeta .gitignore): las corridas locales ignoradas
# (p. ej. evidence/fase-4/run-*/) no deben figurar en el manifiesto del repositorio.
set -euo pipefail
cd "$(dirname "$0")/../evidence"
{ git ls-files -z; git ls-files -z --others --exclude-standard; } \
  | grep -zv -e '^MANIFEST\.sha256$' -e '/tmp/' \
  | LC_ALL=C sort -zu | sed -z 's#^#./#' | xargs -0 sha256sum > MANIFEST.sha256
echo "MANIFEST: $(wc -l < MANIFEST.sha256) archivos"
