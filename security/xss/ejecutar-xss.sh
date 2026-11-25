#!/usr/bin/env bash
# Ejecuta security/xss/xss-navegador.mjs (Chromium real) contra tres instancias LOCALES en una red Docker interna, sin
# puertos publicados (la imagen vulnerable nunca sale de esta red):
#   oficial    bkimminich/juice-shop:v20.3.0 (línea base vulnerable)
#   corregida  juice-corregida-rasp:local, SIN WAF (mide solo el código corregido)
#   cloud      juice-cloud:local = la imagen que se despliega en Render (WAF + CSP + puerta de acceso)
# Uso: bash security/xss/ejecutar-xss.sh <carpeta-salida> [objetivos...]   (por defecto: los cinco)
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"; cd "$ROOT"
export MSYS_NO_PATHCONV=1
hostpath() { if command -v cygpath >/dev/null 2>&1; then cygpath -m "$1"; else printf '%s' "$1"; fi; }
OUT="$1"; shift; OBJ="${*:-oficial corregida oficial-sms corregida-sms cloud}"
W="$(hostpath "$ROOT")"; NET=xss-prueba
PW_IMG=mcr.microsoft.com/playwright@sha256:70e367e0cbf60340a5b5fd562f6247a34eb3196efab9f88a3dd56482d9fe09d2   # v1.49.1-noble
OFICIAL=bkimminich/juice-shop:v20.3.0@sha256:cea5a4af4aacee498c491491af0408934ec81d004035c0a02ef3e54395e3bf27
S=deploy/corregido/secrets
ADMPW=$(grep -A3 "email: admin" app/data/static/users.yml | grep -m1 'password:' | sed -E "s/.*password: *'?([^']*)'?.*/\1/")
mkdir -p "$OUT"
# El paquete npm de Playwright se instala una vez CON red en un volumen de caché; las pruebas corren en la red interna sin salida
docker run --rm -v xss-npm:/work "$PW_IMG" bash -c \
  "cd /work && [ -d node_modules/playwright ] || npm i --silent --no-audit --no-fund playwright@1.49.1" >/dev/null 2>&1 \
  || { echo "FALLO: no se pudo instalar playwright@1.49.1"; exit 1; }
docker network create --internal "$NET" >/dev/null 2>&1
limpiar() { docker rm -f oficial corregida oficial-sms corregida-sms cloud >/dev/null 2>&1; docker network rm "$NET" >/dev/null 2>&1; }
trap limpiar EXIT
listo() { for i in $(seq 1 60); do docker run --rm --network "$NET" "$PW_IMG" curl -s -o /dev/null -w '%{http_code}' --max-time 5 "$1" 2>/dev/null | grep -q 200 && return 0; sleep 5; done; return 1; }
for o in $OBJ; do
  case "$o" in
    oficial)   docker run -d --name oficial --network "$NET" "$OFICIAL" >/dev/null; URL=http://oficial:3000; SALUD=$URL/rest/admin/application-version; CRED="" ;;
    corregida) docker run -d --name corregida --network "$NET" -e NODE_CONFIG='{"challenges":{"safetyMode":"enabled"}}' \
                 -e JWT_PRIVATE_KEY_FILE=/run/secrets/jwt -v "$W/$S/jwt_private_key.pem:/run/secrets/jwt:ro" juice-corregida-rasp:local >/dev/null
               URL=http://corregida:3000; SALUD=$URL/rest/admin/application-version; CRED="" ;;
    # Sin el modo seguro de Juice Shop (que en Docker sanea en el servidor): mide el CÓDIGO frente a los vectores almacenados
    oficial-sms)   docker run -d --name oficial-sms --network "$NET" -e NODE_CONFIG='{"challenges":{"safetyMode":"disabled"}}' "$OFICIAL" >/dev/null
                   URL=http://oficial-sms:3000; SALUD=$URL/rest/admin/application-version; CRED="" ;;
    corregida-sms) docker run -d --name corregida-sms --network "$NET" -e NODE_CONFIG='{"challenges":{"safetyMode":"disabled"}}' \
                     -e JWT_PRIVATE_KEY_FILE=/run/secrets/jwt -v "$W/$S/jwt_private_key.pem:/run/secrets/jwt:ro" juice-corregida-rasp:local >/dev/null
                   URL=http://corregida-sms:3000; SALUD=$URL/rest/admin/application-version; CRED="" ;;
    cloud)     docker run -d --name cloud --network "$NET" -e JWT_CLAVE_EFIMERA=1 \
                 -e BASIC_AUTH_HTPASSWD="$(grep '^BASIC_AUTH_HTPASSWD=' $S/cloud-prueba.env | cut -d= -f2-)" juice-cloud:local >/dev/null
               URL=http://cloud:8080; SALUD=$URL/healthz; CRED=/s/cloud-prueba.cred ;;
    *) echo "objetivo desconocido: $o"; continue ;;
  esac
  echo "== $o: esperando $SALUD"; listo "$SALUD" || { echo "  no arrancó"; docker logs "$o" 2>&1 | tail -5; continue; }
  docker run --rm --network "$NET" --ipc=host -e ADMIN_PW="$ADMPW" -v "$W/security/xss:/src:ro" -v "$W/$S:/s:ro" \
    -v "$W/$OUT:/out" -v xss-npm:/work "$PW_IMG" bash -c \
    "cd /work && cp /src/xss-navegador.mjs . && node xss-navegador.mjs $URL /out/$o $CRED"
done
