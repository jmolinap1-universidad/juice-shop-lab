#!/usr/bin/env bash
# Pipeline de RELEASE (local, reproducible) de la variante corregida, con puerta de publicación.
# Herramientas y versiones = las fijadas en .github/workflows/devsecops.yml. Política: security/release/politica-release.json.
#   1) Gitleaks (historial del repositorio)   2) Hadolint (Dockerfiles de la variante)
#   3) Semgrep con las reglas propias sobre la FUENTE construida (app-hardened/build/src)
#   4) Trivy (vulnerabilidades y secretos) de la imagen   5) Syft (SBOM CycloneDX) + Grype (informe)
#   6) Puerta: aplica la política y devuelve 0 (APTA) o 1 (BLOQUEADA).
# Uso: scripts/pipeline-release.sh <imagen> <carpeta-salida>
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$ROOT"
export MSYS_NO_PATHCONV=1
IMG="$1"; OUT="$2"; mkdir -p "$OUT"
hostpath() { if command -v cygpath >/dev/null 2>&1; then cygpath -m "$1"; else printf '%s' "$1"; fi; }
W="$(hostpath "$ROOT")"; O="$(hostpath "$ROOT/$OUT")"
PY=python:3.12-slim@sha256:5e2bdb1b0d542d5039cffb8181c65930093949194a65c365dfb1b0fe13a4fa5b
[ -d app-hardened/build/src ] || { echo "Falta app-hardened/build/src: ejecute make corregida-build"; exit 1; }

echo "[1/5] Gitleaks"
docker run --rm -v "$W:/repo" -w /repo zricethezav/gitleaks:v8.30.1 git --config /repo/.gitleaks.toml --redact --no-banner \
  --report-format json --report-path "/repo/$OUT/gitleaks.json" /repo > "$OUT/gitleaks.log" 2>&1; echo "  exit=$?"
echo "[2/5] Hadolint"
: > "$OUT/hadolint.txt"
# La imagen se descarga ANTES y solo stdout de Hadolint cuenta como aviso: en CI (máquina limpia) los mensajes de descarga
# de Docker («Unable to find image…», «Pulling from…») caían en hadolint.txt y bloqueaban la puerta con 8 «avisos»
# inexistentes (hallado en la primera ejecución de release.yml, 2026-11-25).
docker pull -q hadolint/hadolint:v2.15.1 > /dev/null 2>> "$OUT/hadolint-stderr.log"
for f in app-hardened/Dockerfile deploy/hardened/Dockerfile.rasp deploy/cloud/Dockerfile; do
  echo "== $f" >> "$OUT/hadolint.txt"
  docker run --rm -i hadolint/hadolint:v2.15.1 hadolint - < "$f" >> "$OUT/hadolint.txt" 2>> "$OUT/hadolint-stderr.log"
done
echo "[3/5] Semgrep (reglas propias) sobre la fuente construida"
docker run --rm -v "$W/app-hardened/build/src:/src:ro" -v "$W/security/semgrep:/reglas:ro" -v "$O:/out" -w /src semgrep/semgrep:1.181.1 \
  semgrep scan --config /reglas/ --exclude 'frontend/src/assets' --exclude 'test' --exclude '*.spec.ts' \
  --json --output /out/semgrep.json --metrics off --quiet . > /dev/null 2>&1; echo "  exit=$?"
echo "[4/5] Trivy"
docker run --rm -v //var/run/docker.sock:/var/run/docker.sock -v trivy-cache:/root/.cache -v "$O:/out" aquasec/trivy:0.75.0 image \
  --quiet --scanners vuln,secret --format json --output /out/trivy.json "$IMG"; echo "  exit=$?"
echo "[5/5] Syft + Grype"
docker run --rm -v //var/run/docker.sock:/var/run/docker.sock -v "$O:/out" anchore/syft:v1.55.0 "$IMG" -o cyclonedx-json=/out/sbom.cdx.json -q
docker run --rm -v "$O:/out" anchore/grype:v0.120.1 sbom:/out/sbom.cdx.json -o json --file /out/grype.json -q; echo "  exit=$?"

docker image inspect "$IMG" --format '{{.Id}} {{index .Config.Labels "masi.variante"}}' > "$OUT/imagen.txt"
docker run --rm -i -v "$W:/r:ro" -v "$O:/o" "$PY" python -I - "$(date +%F)" <<'PYEOF'
import json, sys, collections
hoy = sys.argv[1]
pol = json.load(open('/r/security/release/politica-release.json'))
fallos, notas = [], []
gl = json.load(open('/o/gitleaks.json')) if open('/o/gitleaks.json').read().strip() else []
if len(gl) > pol['secretos_permitidos']: fallos.append(f'Gitleaks: {len(gl)} secretos en el repositorio')
hl = [l for l in open('/o/hadolint.txt') if l.strip() and not l.startswith('==')]
if len(hl) > pol['hadolint_avisos_permitidos']: fallos.append(f'Hadolint: {len(hl)} avisos')
sg = json.load(open('/o/semgrep.json'))
exs = pol['excepciones_semgrep']
for r in sg['results']:
    if r['extra']['severity'] != 'ERROR': continue
    regla, ruta = r['check_id'].split('.')[-1], r['path'].lstrip('./')
    ex = [e for e in exs if e['regla'] == regla and ruta.startswith(e['ruta'])]
    if not ex: fallos.append(f'Semgrep ERROR sin excepción: {regla} {ruta}:{r["start"]["line"]}')
    elif ex[0]['vence'] < hoy: fallos.append(f'Excepción Semgrep vencida: {regla} {ruta}')
for e in exs:
    if e['vence'] < hoy: fallos.append(f'Excepción Semgrep vencida: {e["regla"]} {e["ruta"]}')
tv = json.load(open('/o/trivy.json'))
vista, sec = {}, 0
for res in tv.get('Results', []):
    sec += len(res.get('Secrets') or [])
    for v in res.get('Vulnerabilities') or []:
        vista[(v['VulnerabilityID'], v['PkgName'])] = (v['Severity'], v.get('FixedVersion') or '')
if sec > pol['secretos_permitidos']: fallos.append(f'Trivy: {sec} secretos en la imagen')
exv = {(e['id'], e['paquete']): e for e in pol['excepciones_vulnerabilidades']}
for (vid, pkg), (sev, fix) in sorted(vista.items()):
    if sev not in pol['severidades_bloqueantes']: continue
    e = exv.get((vid, pkg))
    if not e: fallos.append(f'Trivy {sev} sin excepción: {vid} {pkg} (corrección: {fix or "ninguna"})')
    elif e['vence'] < hoy: fallos.append(f'Excepción vencida: {vid} {pkg}')
    elif fix: fallos.append(f'Excepción con versión corregida disponible (actualizar): {vid} {pkg} → {fix}')
    else: notas.append(f'{sev} exceptuada: {vid} {pkg} — {e["motivo"][:80]}… (vence {e["vence"]})')
c = collections.Counter(s for s, _ in vista.values())
gr = json.load(open('/o/grype.json'))
gc = collections.Counter(m['vulnerability']['severity'] for m in gr['matches'])
L = ['# Puerta de release — ' + hoy, '', 'Imagen: `' + open('/o/imagen.txt').read().strip() + '`', '',
     '| Control | Resultado |', '|---|---|',
     f'| Gitleaks (historial) | {len(gl)} hallazgos |', f'| Hadolint | {len(hl)} avisos |',
     f'| Semgrep reglas propias | {sum(1 for r in sg["results"] if r["extra"]["severity"]=="ERROR")} ERROR ({len(exs)} excepciones documentadas), {sum(1 for r in sg["results"] if r["extra"]["severity"]!="ERROR")} WARNING |',
     f'| Trivy | CRITICAL {c["CRITICAL"]} · HIGH {c["HIGH"]} · MEDIUM {c["MEDIUM"]} · LOW {c["LOW"]} · secretos {sec} |',
     f'| Grype (SBOM Syft, informativo) | {dict(gc)} |', '',
     '## Veredicto: ' + ('**BLOQUEADA**' if fallos else '**APTA según la política**'), '']
L += [f'- {f}' for f in fallos] or ['- Sin incumplimientos.']
L += ['', '## Excepciones vigentes aplicadas'] + [f'- {n}' for n in notas]
L += ['', 'APTA significa que el artefacto cumple esta política, no que esté libre de vulnerabilidades ni que pueda publicarse en Internet sin otros controles (ver criterio de publicación).']
open('/o/puerta-release.md', 'w', encoding='utf-8').write('\n'.join(L) + '\n')
print('\n'.join(L))
sys.exit(1 if fallos else 0)
PYEOF
