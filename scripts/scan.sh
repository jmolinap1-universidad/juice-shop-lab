#!/usr/bin/env bash
# Escaneos locales reproducibles (todas las herramientas vía Docker, versiones fijas).
# Uso: scripts/scan.sh [sast|secrets|sca|container|iac|all]
# Guarda resultados en evidence/fase-N/. No ataca nada: solo análisis estático y de imágenes.
set -uo pipefail
export MSYS_NO_PATHCONV=1
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
# Ruta para montar volúmenes (Windows/Git Bash o Linux)
if command -v cygpath >/dev/null; then W="$(cygpath -w "$ROOT")"; SEP='\'; else W="$ROOT"; SEP='/'; fi
v() { echo "$W${SEP}${1//\//$SEP}"; }

JUICE_IMAGE="bkimminich/juice-shop:v20.3.0@sha256:cea5a4af4aacee498c491491af0408934ec81d004035c0a02ef3e54395e3bf27"
HARDENED_IMAGE="juice-hardened:local"
SEMGREP=semgrep/semgrep:1.181.1
GITLEAKS=zricethezav/gitleaks:v8.30.1
TRIVY=aquasec/trivy:0.75.0
HADOLINT=hadolint/hadolint:v2.15.1
CHECKOV=bridgecrew/checkov:3.4.0
SYFT=anchore/syft:v1.55.0
GRYPE=anchore/grype:v0.120.1
OSV=ghcr.io/google/osv-scanner:v2.7.0
NODE=node:24.11.0-bookworm-slim
B="bash scripts/bitacora.sh"

sast() {
  local o=evidence/fase-3/sast; mkdir -p $o
  docker run --rm -v "$W:/src" -w /src $SEMGREP semgrep scan \
    --config p/owasp-top-ten --config p/nodejs --config p/typescript --config security/semgrep/ \
    --exclude 'app/frontend/src/assets' --exclude 'app/test' --exclude '**/*.spec.ts' \
    --sarif-output=$o/semgrep.sarif --json-output=$o/semgrep.json --metrics off -q app/ >/dev/null 2>$o/semgrep.stderr.txt
  # Redacta la clave de prueba que Semgrep copia en los fragmentos (evita reexponerla y falsos positivos de Gitleaks)
  sed -i 's/-----BEGIN RSA PRIVATE KEY-----[^"]*-----END RSA PRIVATE KEY-----/[REDACTADO]/g' $o/semgrep.sarif $o/semgrep.json
  local n; n=$(grep -o '"check_id"' $o/semgrep.json | wc -l)
  $B 3 "semgrep scan p/owasp-top-ten p/nodejs p/typescript security/semgrep app/" "Semgrep 1.181.1" "$n hallazgos. $o/semgrep.json"
}

secrets() {
  local o=evidence/fase-3/secrets; mkdir -p $o
  docker run --rm -v "$W:/repo" $GITLEAKS git /repo --redact --report-format json --report-path /repo/$o/gitleaks.json --exit-code 0 2>$o/gitleaks.log.txt
  local n; n=$(grep -o '"RuleID"' $o/gitleaks.json | wc -l)
  $B 3 "gitleaks git (historial del repo del equipo, sin submódulo)" "Gitleaks 8.30.1" "$n secretos. $o/gitleaks.json"
}

sca() {
  local o=evidence/fase-3/sca; mkdir -p $o "$ROOT/evidence/fase-3/tmp"
  # Lockfile generado en copia temporal (no se modifica app/)
  docker run --rm -v "$(v app/package.json):/w/package.json:ro" -v "$(v evidence/fase-3/tmp):/out" -w /w $NODE sh -c \
    'npm install --package-lock-only --ignore-scripts --no-audit --no-fund --omit=dev >/dev/null 2>&1; cp package-lock.json /out/; npm audit --omit=dev --json > /out/npm-audit.json; true'
  cp evidence/fase-3/tmp/npm-audit.json $o/npm-audit.json
  cp evidence/fase-3/tmp/package-lock.json $o/package-lock.generated.json
  docker run --rm -v "$(v $o):/o" $OSV scan source -L "package-lock.json:/o/package-lock.generated.json" --format json --output-file /o/osv.json >/dev/null 2>&1
  docker run --rm $SYFT "$JUICE_IMAGE" -o cyclonedx-json -q > $o/sbom-juice-shop-v20.3.0.cdx.json
  docker run --rm -v "$(v $o):/o" $GRYPE sbom:/o/sbom-juice-shop-v20.3.0.cdx.json -o json -q > $o/grype.json
  $B 3 "npm install --package-lock-only; npm audit --omit=dev" "npm (node 24.11.0)" "$(tr -d ' \n' < $o/npm-audit.json | grep -o '"vulnerabilities":{"info[^}]*}')"
  $B 3 "osv-scanner scan source -L package-lock.json:<generado>" "OSV-Scanner 2.7.0" "$(tr -d ' \n' < $o/osv.json | grep -oE '"id":"(GHSA|CVE)-[^"]*' | sort -u | wc -l) IDs de vulnerabilidad únicos. $o/osv.json"
  $B 3 "syft <imagen> -o cyclonedx-json" "Syft 1.55.0" "$(grep -o '"bom-ref"' $o/sbom-juice-shop-v20.3.0.cdx.json | wc -l) componentes"
  $B 3 "grype sbom:" "Grype 0.120.1" "$(grep -o '"severity":"Critical"' $o/grype.json | wc -l) Critical / $(grep -o '"severity":"High"' $o/grype.json | wc -l) High (cuenta incluye entradas relacionadas)"
  rm -rf evidence/fase-3/tmp
}

container() {
  local o=evidence/fase-5; mkdir -p $o/antes $o/despues
  docker run --rm -v //var/run/docker.sock:/var/run/docker.sock -v "$(v $o):/o" -v trivy-cache:/root/.cache $TRIVY image \
    --scanners vuln,secret,misconfig --format json --output /o/antes/trivy-juice-shop-v20.3.0.json -q "$JUICE_IMAGE"
  docker run --rm -i $HADOLINT hadolint -f json - < app/Dockerfile > $o/antes/hadolint-Dockerfile.json
  $B 5 "trivy image --scanners vuln,secret,misconfig $JUICE_IMAGE" "Trivy 0.75.0" "$(grep -o '"Severity":"CRITICAL"' $o/antes/trivy-juice-shop-v20.3.0.json | wc -l) CRITICAL / $(grep -o '"Severity":"HIGH"' $o/antes/trivy-juice-shop-v20.3.0.json | wc -l) HIGH"
  $B 5 "hadolint app/Dockerfile" "Hadolint 2.15.1" "$(grep -o '"code"' $o/antes/hadolint-Dockerfile.json | wc -l) avisos"
  if docker image inspect $HARDENED_IMAGE >/dev/null 2>&1; then
    docker run --rm -v //var/run/docker.sock:/var/run/docker.sock -v "$(v $o):/o" -v trivy-cache:/root/.cache $TRIVY image \
      --scanners vuln,secret,misconfig --format json --output /o/despues/trivy-juice-hardened.json -q "$HARDENED_IMAGE"
    docker run --rm -i $HADOLINT hadolint -f json - < app-hardened/Dockerfile > $o/despues/hadolint-Dockerfile.json
    $B 5 "trivy image $HARDENED_IMAGE" "Trivy 0.75.0" "$(grep -o '"Severity":"CRITICAL"' $o/despues/trivy-juice-hardened.json | wc -l) CRITICAL / $(grep -o '"Severity":"HIGH"' $o/despues/trivy-juice-hardened.json | wc -l) HIGH"
    $B 5 "hadolint app-hardened/Dockerfile" "Hadolint 2.15.1" "$(grep -o '"code"' $o/despues/hadolint-Dockerfile.json | wc -l) avisos"
  fi
}

iac() {
  local o=evidence/fase-5/iac; mkdir -p $o
  docker run --rm -v "$W:/src" -w /src $CHECKOV -d deploy -d app-hardened --framework dockerfile,docker_compose,yaml \
    -o cli -o json --output-file-path $o --soft-fail --compact --quiet >/dev/null 2>&1
  $B 5 "checkov -d deploy -d app-hardened (dockerfile/compose)" "Checkov 3.4.0" "$(grep -m1 'Passed checks' $o/results_cli.txt 2>/dev/null)"
}

case "${1:-all}" in
  sast) sast ;; secrets) secrets ;; sca) sca ;; container) container ;; iac) iac ;;
  all) secrets; sast; sca; container; iac ;;
  *) echo "uso: $0 [sast|secrets|sca|container|iac|all]"; exit 1 ;;
esac
bash scripts/manifest.sh
