#!/usr/bin/env bash
# Valida el contenedor CLOUD (deploy/cloud: WAF + app corregida + RASP + puerta de acceso), en local o desplegado.
#   1) puerta de acceso: sin cookie → 302 a /__acceso; credenciales ausentes/erróneas → 401; límite de intentos → 429;
#      /healthz sin autenticación; cookie con Secure, HttpOnly y SameSite
#   2) con la cookie (vía CURL_HOME/.curlrc, sin tocar las baterías): regresión 15, recorrido 35, A1-A12, BOLA, T1-T10
# Solo instancias propias: 127.0.0.1/localhost o el host exacto en HOST_CLOUD_AUTORIZADO (lo nombra el usuario).
# Uso: security/ops/validar-cloud.sh <url-base> <archivo usuario:contraseña> <carpeta-salida>
# La contraseña nunca se pasa por la línea de comandos ni se escribe en la salida.
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"; cd "$ROOT"
B="${1%/}"; CRED="$2"; OUT="$3"
HOST="$(printf '%s' "$B" | sed -E 's#^https?://([^/:]+).*#\1#')"
case "$HOST" in
  127.0.0.1|localhost) : ;;
  *) [ -n "${HOST_CLOUD_AUTORIZADO:-}" ] && [ "$HOST" = "$HOST_CLOUD_AUTORIZADO" ] || { echo "FUERA DE ALCANCE: $HOST"; exit 2; } ;;
esac
mkdir -p "$OUT"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
# En Git Bash, curl.exe no entiende /tmp/... si MSYS_NO_PATHCONV=1 (intento 1 de la validación): ruta Windows explícita
command -v cygpath >/dev/null 2>&1 && TMP="$(cygpath -m "$TMP")"
umask 077
printf 'user = "%s"\n' "$(cat "$CRED")" > "$TMP/cred.cfg"
R="$OUT/puerta-acceso.md"
c() { curl -s -o /dev/null -w '%{http_code}' --max-time 30 "$@"; }
ok=0; fallo=0
chk() { # $1 descripción, $2 esperado (regex), $3 obtenido
  if printf '%s' "$3" | grep -qE "^($2)$"; then ok=$((ok+1)); r=OK; else fallo=$((fallo+1)); r=**FALLO**; fi
  printf '| %s | %s | %s | %s |\n' "$1" "$2" "$3" "$r" >> "$R"
}
{
  echo "# Puerta de acceso y cabeceras — $(date -Iseconds)"
  echo "Destino: $B"
  echo ""
  echo "| Comprobación | Esperado | Obtenido | Resultado |"
  echo "|---|---|---|---|"
} > "$R"
chk "GET / sin cookie" 302 "$(c "$B/")"
chk "Redirección de / sin cookie (relativa)" "/__acceso" "$(curl -s -o /dev/null -D - "$B/" | grep -i '^location:' | tr -d '\r' | sed -E 's/^[^:]+: //')"
chk "GET API sin cookie (/rest/products/search)" 302 "$(c "$B/rest/products/search?q=a")"
chk "POST login sin cookie" 302 "$(c -X POST -H 'Content-Type: application/json' -d '{"email":"a","password":"b"}' "$B/rest/user/login")"
chk "Cookie falsificada" 302 "$(c -b 'lab_acceso=0000000000000000000000000000000000000000000000000000000000000000' "$B/")"
chk "/healthz sin autenticación" 200 "$(c "$B/healthz")"
chk "/__acceso sin credenciales" 401 "$(c "$B/__acceso")"
chk "/__acceso con contraseña errónea" 401 "$(c -u 'prueba:incorrecta' "$B/__acceso")"
# Un 401 NO debe entregar la cookie (fallo real hallado: add_header ... always la enviaba también en el 401)
chk "401 sin credenciales no entrega cookie" 0 "$(curl -s -o /dev/null -D - "$B/__acceso" | grep -ci '^set-cookie: lab_acceso')"
chk "401 con contraseña errónea no entrega cookie" 0 "$(curl -s -o /dev/null -D - -u 'prueba:incorrecta' "$B/__acceso" | grep -ci '^set-cookie: lab_acceso')"  # gitleaks:allow (contraseña errónea a propósito)
sleep 65
codigos=""; for i in 1 2 3 4 5 6 7; do codigos="$codigos $(c -u "intruso$i:x" "$B/__acceso")"; done
chk "7 intentos erróneos seguidos (límite 5/min, ráfaga 3)" ".*429.*" "$codigos"
sleep 65
curl -s -D "$TMP/h" -o /dev/null -K "$TMP/cred.cfg" "$B/__acceso"
chk "/__acceso con credenciales válidas" 200 "$(head -1 "$TMP/h" | awk '{print $2}')"
SC="$(grep -i '^set-cookie: lab_acceso=' "$TMP/h" | tr -d '\r')"
chk "Cookie con Secure" 1 "$(printf '%s' "$SC" | grep -c '; Secure')"
chk "Cookie con HttpOnly" 1 "$(printf '%s' "$SC" | grep -c '; HttpOnly')"
chk "Cookie con SameSite" 1 "$(printf '%s' "$SC" | grep -c '; SameSite=Lax')"
V="$(printf '%s' "$SC" | sed -E 's/^[^=]+: lab_acceso=([0-9a-f]+);.*/\1/I')"
chk "Valor de la cookie (64 hex = 256 bits)" 64 "${#V}"
mkdir -p "$TMP/home"; printf 'cookie = "lab_acceso=%s"\n' "$V" > "$TMP/home/.curlrc"
export CURL_HOME="$TMP/home"
# Las pruebas que envían su propio -H "Cookie: token=…" anulan la cookie del .curlrc: la añaden desde LAB_ACCESO
export LAB_ACCESO="$V"
chk "GET / con cookie" 200 "$(c "$B/")"
curl -s -D "$TMP/h2" -o /dev/null "$B/"
for h in Content-Security-Policy Strict-Transport-Security X-Content-Type-Options X-Frame-Options Referrer-Policy X-Robots-Tag; do
  chk "Cabecera $h" 1 "$(grep -ci "^$h:" "$TMP/h2")"
done
chk "Server sin versión" "Server: waf" "$(grep -i '^server:' "$TMP/h2" | tr -d '\r')"
chk "Ruta sensible /ftp con cookie" 403 "$(c "$B/ftp/")"
chk "/metrics con cookie" 403 "$(c "$B/metrics")"
chk "SQLi en login (WAF)" 403 "$(c -X POST -H 'Content-Type: application/json' -d "{\"email\":\"' OR 1=1--\",\"password\":\"x\"}" "$B/rest/user/login")"
printf '\n**Resultado puerta y cabeceras: %s OK · %s fallos**\n' "$ok" "$fallo" >> "$R"
echo "puerta: $ok OK, $fallo fallos"

[ "${SOLO_PUERTA:-0}" = 1 ] && exit 0
sleep 65
REG_PAUSA=13 bash security/ops/regresion-corregida.sh "$B" "$OUT/regresion.md" >/dev/null
sleep 30
REG_PAUSA=13 bash security/ops/recorrido-frontend.sh "$B" "$OUT/recorrido.md" >/dev/null
sleep 60
mkdir -p "$OUT/ataques"
ATTACK_FASE=6 ATTACK_TAG=validar-cloud ATTACK_OUT="$ROOT/$OUT/ataques" ATTACK_HTTPLOG="$ROOT/$OUT/ataques/http.tsv" A12_DELAY=65 \
  bash security/attacks/run.sh "$B" > "$OUT/ataques.txt" 2>&1
sleep 60
BOLA_PAUSA=13 bash security/ops/bola-recursos.sh "$B" "$OUT/bola-recursos.md" >/dev/null
sleep 60
PAUSA=13 bash security/ops/pruebas-cierre-tecnico.sh "$B" "$OUT/pruebas" >/dev/null
r() { grep -hE '^\*\*Resultado|^Controles positivos|^=== ' "$1" 2>/dev/null | head -2 | tr '\n' ' ' | sed 's/\*\*//g' | cut -c1-140; }
{
  echo ""
  echo "| Batería | Resultado |"
  echo "|---|---|"
  echo "| Puerta de acceso y cabeceras | $ok OK · $fallo fallos |"
  echo "| Regresión funcional | $(r "$OUT/regresion.md") |"
  echo "| Recorrido de la interfaz | $(r "$OUT/recorrido.md") |"
  echo "| A1-A12 | $(r "$OUT/ataques.txt") |"
  echo "| BOLA | $(r "$OUT/bola-recursos.md") |"
  echo "| T1-T10 | $(r "$OUT/pruebas/resultados.md") |"
  echo ""
  echo "Códigos HTTP del arnés: $(cut -f3 "$OUT/ataques/http.tsv" 2>/dev/null | sort | uniq -c | tr -s ' ' | tr '\n' ' ')"
} >> "$R"
tail -12 "$R"
