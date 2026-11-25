#!/usr/bin/env bash
# Regenera y valida el modelo de Threat Dragon y lo abre en Threat Dragon v2.6.2 real (sin puertos publicados).
#   1. generar_modelo_td.py  → docs/fase-1/threat-dragon/juice-shop-lab.json
#   2. validar_modelo_td.py  → esquema oficial v2 + coherencia (y la demo oficial como control del validador)
#   3. abrir-en-threat-dragon.mjs → importación por la interfaz, diagramas dibujados e informe (Chromium)
# Playwright comparte la red del contenedor de Threat Dragon y entra por localhost: la CSP de Threat Dragon incluye
# upgrade-insecure-requests, que el navegador solo exime en localhost (con otro nombre forzaría HTTPS y no cargaría).
# Las claves que exige el servidor de Threat Dragon se generan al vuelo, solo viven en el contenedor y no protegen nada.
# Uso: bash security/threat-dragon/ejecutar-threat-dragon.sh <carpeta-salida>
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"; cd "$ROOT"
export MSYS_NO_PATHCONV=1
hostpath() { if command -v cygpath >/dev/null 2>&1; then cygpath -m "$1"; else printf '%s' "$1"; fi; }
OUT="$1"; W="$(hostpath "$ROOT")"; NET=td-prueba; mkdir -p "$OUT"
PY=python:3.12-slim@sha256:5e2bdb1b0d542d5039cffb8181c65930093949194a65c365dfb1b0fe13a4fa5b
TD=owasp/threat-dragon:v2.6.2@sha256:ec26312b472ad364d5b79283d795f946b9aff9639b798e9f76bfdd243810af17
PW_IMG=mcr.microsoft.com/playwright@sha256:70e367e0cbf60340a5b5fd562f6247a34eb3196efab9f88a3dd56482d9fe09d2   # v1.49.1-noble
TDD=security/threat-dragon; MOD=docs/fase-1/threat-dragon/juice-shop-lab.json
CONTROL="$OUT/control-demo-oficial-v2-threat-model.json"
[ -f "$CONTROL" ] || curl -fsSL -o "$CONTROL" https://raw.githubusercontent.com/OWASP/threat-dragon/v2.6.2/td.vue/src/service/demo/v2-threat-model.json

docker run --rm -v "$W":/r -w /tmp "$PY" sh -c "python -I /r/$TDD/generar_modelo_td.py /r && \
  pip install -q --disable-pip-version-check --root-user-action=ignore jsonschema==4.23.0 && \
  python -I /r/$TDD/validar_modelo_td.py /r/$TDD/threat-dragon-v2.schema.json /r/$MOD /r/$OUT/validacion-esquema.md /r/$CONTROL" \
  || { echo "FALLO: el modelo no supera la validación"; exit 1; }
# Prueba negativa: una copia dañada (flujo hacia una celda inexistente, amenaza T05 retirada, estado no admitido y sin
# «reviewer», que el esquema exige) DEBE fallar; si el validador la aceptara, la validación anterior no valdría nada.
docker run --rm -v "$W":/r -w /tmp "$PY" sh -c "pip install -q --disable-pip-version-check --root-user-action=ignore jsonschema==4.23.0 && \
  python -I -c \"
import json
m = json.load(open('/r/$MOD', encoding='utf-8'))
d = m['detail']; del d['reviewer']
celdas = d['diagrams'][0]['cells']
next(c for c in celdas if c['shape'] == 'flow')['target']['cell'] = 'no-existe'
for c in celdas:
    th = c.get('data', {}).get('threats', [])
    c.get('data', {})['threats'] = [t for t in th if not t['title'].startswith('T05 ')]
next(c for c in celdas if c.get('data', {}).get('threats'))['data']['threats'][0]['status'] = 'Cerrada'
json.dump(m, open('/tmp/danado.json', 'w', encoding='utf-8'), ensure_ascii=False)
\" && python -I /r/$TDD/validar_modelo_td.py /r/$TDD/threat-dragon-v2.schema.json /tmp/danado.json /r/$OUT/prueba-negativa.md; \
  test \$? -eq 1" && echo "prueba negativa: el modelo dañado se rechaza" || { echo "FALLO: el validador aceptó un modelo dañado"; exit 1; }

docker run --rm -v xss-npm:/work "$PW_IMG" bash -c \
  "cd /work && [ -d node_modules/playwright ] || npm i --silent --no-audit --no-fund playwright@1.49.1" >/dev/null 2>&1 \
  || { echo "FALLO: no se pudo instalar playwright@1.49.1"; exit 1; }
docker network create --internal "$NET" >/dev/null 2>&1
limpiar() { docker rm -f threat-dragon >/dev/null 2>&1; docker network rm "$NET" >/dev/null 2>&1; }
trap limpiar EXIT
hex() { head -c "$1" /dev/urandom | od -An -tx1 | tr -d ' \n'; }
docker run -d --name threat-dragon --network "$NET" -e NODE_ENV=production -e SERVER_API_PROTOCOL=http -e PORT=3000 \
  -e "ENCRYPTION_KEYS=[{\"isPrimary\": true, \"id\": 0, \"value\": \"$(hex 16)\"}]" \
  -e "ENCRYPTION_JWT_SIGNING_KEY=$(hex 32)" -e "ENCRYPTION_JWT_REFRESH_SIGNING_KEY=$(hex 32)" "$TD" >/dev/null
for i in $(seq 1 30); do docker run --rm --network "$NET" "$PW_IMG" curl -s -o /dev/null -w '%{http_code}' --max-time 5 http://threat-dragon:3000/ 2>/dev/null | grep -q 200 && break; sleep 3; done
docker run --rm --network container:threat-dragon --ipc=host -e ESCALA="${ESCALA:-1}" -v "$W/$TDD:/src:ro" -v "$W/$MOD:/m/juice-shop-lab.json:ro" -v "$W/$OUT:/out" -v xss-npm:/work "$PW_IMG" \
  bash -c "cd /work && cp /src/abrir-en-threat-dragon.mjs . && node abrir-en-threat-dragon.mjs http://localhost:3000 /m/juice-shop-lab.json /out"
