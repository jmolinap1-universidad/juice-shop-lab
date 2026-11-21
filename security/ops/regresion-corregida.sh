#!/usr/bin/env bash
# Regresión funcional y de seguridad de la variante corregida (hito A). Solo contra instancias propias.
# Comprueba que las funciones legítimas siguen funcionando y que las correcciones actúan, con el código HTTP real.
# Uso (desde un contenedor en la red del objetivo, con el repo montado en /work):
#   regresion-corregida.sh <url-base> <salida.md> [token-firmado-con-la-clave-antigua]
# La contraseña del administrador sembrado se lee de app/data/static/users.yml (datos de prueba de Juice Shop).
# Los tokens nunca se escriben en la salida.
set -u
B="$1"; OUT="$2"; OLD_TOKEN="${3:-}"
case "$(printf '%s' "$B" | sed -E 's#https?://##; s#[:/].*##')" in
  127.0.0.1|localhost|juice-hardened|juice-corregida) : ;;
  *) echo "RECHAZADO: objetivo fuera del laboratorio"; exit 2 ;;
esac
TS=$(date +%s); PW='Passw0rd!123'; PW2='Nueva!Clave456'
ok=0; fallas=0
fila() { # prueba, esperado, obtenido, cumple(0/1)
  if [ "$4" = 1 ]; then ok=$((ok+1)); r="OK"; else fallas=$((fallas+1)); r="**FALLA**"; fi
  printf '| %s | %s | %s | %s |\n' "$1" "$2" "$3" "$r" >> "$OUT"
}
code() { curl -s -o /dev/null --max-time 20 -w '%{http_code}' "$@"; }
registrar() { code -X POST "$B/api/Users" -H 'Content-Type: application/json' \
  --data '{"email":"'"$1"'","password":"'"$2"'","passwordRepeat":"'"$2"'","securityQuestion":{"id":1},"securityAnswer":"x"}'; }
# REG_PAUSA (segundos): pausa antes de cada intento de login. Con el WAF delante (5 logins/min, ráfaga 3) evita que el
# control de fuerza bruta (429) se confunda con un fallo funcional. Sin WAF: 0 (por defecto).
pausa() { [ "${REG_PAUSA:-0}" -gt 0 ] && sleep "$REG_PAUSA"; return 0; }
login() { pausa; curl -s --max-time 20 -X POST "$B/rest/user/login" -H 'Content-Type: application/json' --data '{"email":"'"$1"'","password":"'"$2"'"}'; }
tok() { printf '%s' "$1" | grep -oE '"token":"[^"]*"' | sed -E 's/"token":"//; s/"//'; }
bid() { printf '%s' "$1" | grep -oE '"bid":[0-9]+' | sed 's/"bid"://'; }

{
  echo "# Regresión de la variante corregida — $(date -Iseconds)"
  echo ""
  echo "Objetivo: $B. Pausa antes de cada login: ${REG_PAUSA:-0} s. Tokens redactados."
  echo ""
  echo "| Prueba | Esperado | Obtenido | Resultado |"
  echo "|---|---|---|---|"
} > "$OUT"

c=$(code "$B/"); fila "Página principal" "200" "$c" "$([ "$c" = 200 ] && echo 1 || echo 0)"
body=$(curl -s --max-time 20 "$B/rest/products/search?q=apple"); c=$(code "$B/rest/products/search?q=apple")
n=$(printf '%s' "$body" | grep -o '"id":' | wc -l); forma=$(printf '%s' "$body" | grep -q '"data":\[{' && echo lista || echo otra)
fila "Búsqueda legítima q=apple" "200, data = lista de productos" "$c, $n productos, data=$forma" "$([ "$c" = 200 ] && [ "$n" -gt 0 ] && [ "$forma" = lista ] && echo 1 || echo 0)"
c=$(code "$B/rest/products/1/reviews"); fila "Reseñas de un producto" "200" "$c" "$([ "$c" = 200 ] && echo 1 || echo 0)"

U="reg_u_${TS}@juice-sh.op"; V="reg_v_${TS}@juice-sh.op"
c=$(registrar "$U" "$PW"); fila "Registro sin role (usuario U)" "201" "$c" "$([ "$c" = 201 ] && echo 1 || echo 0)"
registrar "$V" "$PW" >/dev/null
r=$(curl -s --max-time 20 -w '\n%{http_code}' -X POST "$B/api/Users" -H 'Content-Type: application/json' --data '{"email":"reg_adm_'"$TS"'@juice-sh.op","password":"'"$PW"'","passwordRepeat":"'"$PW"'","role":"admin"}')
rc=$(printf '%s' "$r" | tail -1); rol=$(printf '%s' "$r" | grep -oE '"role":"[^"]*"' | head -1)
# Mitigado si la app ignora el campo (201 con role customer) o si el WAF rechaza la petición (403 real; nunca 000/5xx).
fila "Registro intentando role=admin (asignación masiva)" "201 con role customer, o 403 del WAF" "$rc, ${rol:-sin role en respuesta}" "$( { [ "$rc" = 201 ] && printf '%s' "$rol" | grep -q customer; } || [ "$rc" = 403 ] && echo 1 || echo 0)"

lu=$(login "$U" "$PW"); tu=$(tok "$lu"); bu=$(bid "$lu")
fila "Login de U con su contraseña" "token emitido" "$([ -n "$tu" ] && echo 'token emitido [REDACTADO]' || echo 'sin token')" "$([ -n "$tu" ] && echo 1 || echo 0)"
lv=$(login "$V" "$PW"); bv=$(bid "$lv")
c=$(code -H "Authorization: Bearer $tu" "$B/rest/basket/${bu:-0}"); fila "U lee SU cesta (bid $bu)" "200" "$c" "$([ "$c" = 200 ] && echo 1 || echo 0)"
c=$(code -H "Authorization: Bearer $tu" "$B/rest/basket/${bv:-0}"); fila "U lee la cesta de V (bid $bv) — BOLA" "403" "$c" "$([ "$c" = 403 ] && echo 1 || echo 0)"

c=$(code -H "Authorization: Bearer $tu" "$B/rest/user/change-password?current=$(printf '%s' "$PW" | sed 's/!/%21/g')&new=$(printf '%s' "$PW2" | sed 's/!/%21/g')&repeat=$(printf '%s' "$PW2" | sed 's/!/%21/g')")
fila "Cambio de contraseña de U (con la actual)" "200" "$c" "$([ "$c" = 200 ] && echo 1 || echo 0)"
t2=$(tok "$(login "$U" "$PW2")"); fila "Login de U con la contraseña NUEVA" "token emitido" "$([ -n "$t2" ] && echo 'token emitido [REDACTADO]' || echo 'sin token')" "$([ -n "$t2" ] && echo 1 || echo 0)"
pausa; c=$(code -X POST "$B/rest/user/login" -H 'Content-Type: application/json' --data '{"email":"'"$U"'","password":"'"$PW"'"}'); fila "Login de U con la contraseña ANTIGUA" "401" "$c" "$([ "$c" = 401 ] && echo 1 || echo 0)"

ADMPW=$(grep -A3 "email: admin" "$(dirname "$0")/../../app/data/static/users.yml" | grep -m1 'password:' | sed -E "s/.*password: *'?([^']*)'?.*/\1/")
ta=$(tok "$(login "admin@juice-sh.op" "$ADMPW")")
fila "Login del administrador sembrado (contraseña del archivo de semillas; hash scrypt)" "token emitido" "$([ -n "$ta" ] && echo 'token emitido [REDACTADO]' || echo 'sin token')" "$([ -n "$ta" ] && echo 1 || echo 0)"
pausa; c=$(code -X POST "$B/rest/user/login" -H 'Content-Type: application/json' --data '{"email":"admin@juice-sh.op","password":"incorrecta"}'); fila "Login del administrador con contraseña incorrecta" "401" "$c" "$([ "$c" = 401 ] && echo 1 || echo 0)"

c=$(code -H "Authorization: Bearer $tu" "$B/api/Users"); fila "Ruta autenticada con token de la clave NUEVA" "200" "$c" "$([ "$c" = 200 ] && echo 1 || echo 0)"
if [ -n "$OLD_TOKEN" ]; then
  c=$(code -H "Authorization: Bearer $OLD_TOKEN" "$B/api/Users"); fila "Ruta autenticada con token firmado por la clave ANTIGUA (emitido por el laboratorio vulnerable)" "401" "$c" "$([ "$c" = 401 ] && echo 1 || echo 0)"
fi

pausa; e=$(curl -s --max-time 20 -w '\n%{http_code}' -X POST "$B/rest/user/login" -H 'Content-Type: application/json' --data '{"email":')
ec=$(printf '%s' "$e" | tail -1); eb=$(printf '%s' "$e" | head -1)
traza=$(printf '%s' "$eb" | grep -cE '    at |/juice-shop/|node_modules')
fila "Error provocado (JSON malformado): sin traza de pila" "4xx/5xx genérico (JSON de la app o página del WAF), 0 trazas" "$ec, trazas=$traza, cuerpo=$(printf '%s' "$eb" | cut -c1-60)" "$([ "$traza" = 0 ] && [ "$ec" -ge 400 ] && echo 1 || echo 0)"

{ echo ""; echo "**Resultado: $ok OK, $fallas FALLAS.**"; } >> "$OUT"
cat "$OUT"
