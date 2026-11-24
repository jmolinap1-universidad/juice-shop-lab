#!/usr/bin/env bash
# Prueba defensiva de autorización a nivel de objeto (BOLA/IDOR) MÁS ALLÁ de las cestas, solo contra instancias propias.
# Dos cuentas nuevas del laboratorio: A (víctima) crea sus objetos; B (atacante autenticado) intenta leerlos, modificarlos
# o borrarlos por id. Además del código HTTP, se comprueba el EFECTO REAL releyendo el objeto con la cuenta A
# (un 200 a B no basta para concluir, ni un 4xx para descartar). Datos de prueba ficticios; tokens nunca se escriben.
# Uso: bola-recursos.sh <url-base> <salida.md>
set -u
B="$1"; OUT="$2"
case "$(printf '%s' "$B" | sed -E 's#https?://##; s#[:/].*##')" in
  127.0.0.1|localhost|juice-hardened|juice-corregida|juice-lab) : ;;
  *) echo "RECHAZADO: objetivo fuera del laboratorio"; exit 2 ;;
esac
TS=$(date +%s); PW='Passw0rd!123'
J='Content-Type: application/json'
req() { # metodo url token [datos] -> imprime "codigo<TAB>cuerpo"
  local m u t d r
  m="$1"; u="$2"; t="$3"; d="${4:-}"
  local args=(-s --max-time 20 -X "$m" -H "Authorization: Bearer $t" -w '\t%{http_code}')
  if [ -n "$d" ]; then args+=(-H "$J" --data "$d"); fi
  # Cuerpo en una sola línea (las páginas HTML del WAF traen saltos de línea y romperían el corte del código HTTP)
  r="$(curl "${args[@]}" "$B$u" | tr '\r\n' '  ')"; printf '%s\t%s' "${r##*$'\t'}" "${r%$'\t'*}"
}
code() { printf '%s' "$1" | cut -f1; }
body() { printf '%s' "$1" | cut -f2-; }
campo() { printf '%s' "$1" | grep -oE "\"$2\":(\"[^\"]*\"|[0-9]+)" | head -1 | sed -E "s/\"$2\"://; s/\"//g"; }
cuenta() {
  local em="bolarec_${1}_${TS}@juice-sh.op"
  curl -s -o /dev/null --max-time 20 -X POST "$B/api/Users" -H "$J" --data '{"email":"'"$em"'","password":"'"$PW"'","passwordRepeat":"'"$PW"'","securityQuestion":{"id":1},"securityAnswer":"x"}'
  sleep "${BOLA_PAUSA:-0}"
  curl -s --max-time 20 -X POST "$B/rest/user/login" -H "$J" --data '{"email":"'"$em"'","password":"'"$PW"'"}'
}
la=$(cuenta A); TA=$(campo "$la" token); BIDA=$(campo "$la" bid)
lb=$(cuenta B); TB=$(campo "$lb" token)
[ -n "$TA" ] && [ -n "$TB" ] || { echo "No se obtuvieron las dos sesiones (¿rate limit del WAF? use BOLA_PAUSA=13)"; exit 1; }
ok=0; vuln=0; nc=0
fila() { # recurso, accion, http_B, efecto, veredicto
  # Salvaguarda: sin id del objeto de A o sin código HTTP real (vacío/000/5xx) NUNCA se concluye nada.
  local v="$5"
  case "$1" in *'#') v='NO CONCLUYENTE';; esac
  case "$3" in ''|000|5??) v='NO CONCLUYENTE';; esac
  set -- "$1" "$2" "$3" "$4" "$v"
  case "$5" in PROTEGIDO) ok=$((ok+1));; VULNERABLE) vuln=$((vuln+1));; *) nc=$((nc+1));; esac
  printf '| %s | %s | %s | %s | **%s** |\n' "$1" "$2" "$3" "$4" "$5" >> "$OUT"
}
{
  echo "# BOLA/IDOR en recursos distintos de la cesta — $(date -Iseconds)"
  echo ""
  echo "Objetivo: $B. Cuentas nuevas A (víctima) y B (atacante). Efecto comprobado releyendo con A. Tokens redactados."
  echo ""
  echo "| Recurso | Acción de B sobre el objeto de A | HTTP a B | Efecto real (relectura con A) | Veredicto |"
  echo "|---|---|---|---|---|"
} > "$OUT"

# --- Direcciones ---
r=$(req POST /api/Addresss "$TA" '{"country":"GT","fullName":"Prueba A","mobileNum":5550000,"zipCode":"01001","streetAddress":"Calle 1","city":"Guatemala","state":"GT"}')
AID=$(campo "$(body "$r")" id)
r=$(req GET "/api/Addresss/$AID" "$TB"); c=$(code "$r"); vis=$(body "$r" | grep -c 'Calle 1')
fila "Dirección #$AID" "GET (leer)" "$c" "datos de A en la respuesta: $([ "$vis" -gt 0 ] && echo sí || echo no)" "$(if [ "$vis" -gt 0 ]; then echo VULNERABLE; elif [ "${c:0:1}" = 4 ] || [ "$c" = 200 ]; then echo PROTEGIDO; else echo 'NO CONCLUYENTE'; fi)"
r=$(req PUT "/api/Addresss/$AID" "$TB" '{"streetAddress":"Modificada por B"}'); c=$(code "$r")
ra=$(req GET "/api/Addresss/$AID" "$TA"); st=$(body "$ra" | grep -oE '"streetAddress":"[^"]*"' | head -1); ca=$(code "$ra")
if body "$ra" | grep -q 'Modificada por B'; then ef="A ve la dirección alterada por B"; v=VULNERABLE
elif [ "$ca" = 200 ] && body "$ra" | grep -q 'Calle 1'; then ef="intacta (${st})"; v=PROTEGIDO
else ef="A ya no puede leer su dirección (HTTP $ca): B se la apropió o la alteró"; v=VULNERABLE; fi
fila "Dirección #$AID" "PUT (modificar)" "$c" "$ef" "$v"
r=$(req DELETE "/api/Addresss/$AID" "$TB"); c=$(code "$r"); ca=$(code "$(req GET "/api/Addresss/$AID" "$TA")")
fila "Dirección #$AID" "DELETE (borrar)" "$c" "A relee: HTTP $ca" "$([ "$ca" = 200 ] && echo PROTEGIDO || echo 'NO CONCLUYENTE')"

# --- Tarjetas (número ficticio, solo existe dentro del laboratorio) ---
r=$(req POST /api/Cards "$TA" '{"fullName":"Prueba A","cardNum":4000000000000002,"expMonth":12,"expYear":2090}')
CID=$(campo "$(body "$r")" id)
r=$(req GET "/api/Cards/$CID" "$TB"); c=$(code "$r"); vis=$(body "$r" | grep -c 'Prueba A')
fila "Tarjeta #$CID" "GET (leer)" "$c" "datos de A en la respuesta: $([ "$vis" -gt 0 ] && echo sí || echo no)" "$([ "$vis" -gt 0 ] && echo VULNERABLE || echo PROTEGIDO)"
r=$(req DELETE "/api/Cards/$CID" "$TB"); c=$(code "$r"); ra=$(req GET "/api/Cards/$CID" "$TA")
fila "Tarjeta #$CID" "DELETE (borrar)" "$c" "A relee: HTTP $(code "$ra"), $(body "$ra" | grep -q 'Prueba A' && echo 'tarjeta presente' || echo 'tarjeta ausente')" "$(body "$ra" | grep -q 'Prueba A' && echo PROTEGIDO || echo VULNERABLE)"

# --- Artículos de la cesta ---
r=$(req POST /api/BasketItems "$TA" '{"ProductId":1,"BasketId":"'"$BIDA"'","quantity":1}')
IID=$(campo "$(body "$r")" id)
r=$(req GET "/api/BasketItems/$IID" "$TB"); c=$(code "$r"); vis=$(body "$r" | grep -c "\"BasketId\":$BIDA")
fila "Artículo de cesta #$IID" "GET (leer)" "$c" "artículo de la cesta de A en la respuesta: $([ "$vis" -gt 0 ] && echo sí || echo no)" "$([ "$vis" -gt 0 ] && echo VULNERABLE || echo PROTEGIDO)"
r=$(req PUT "/api/BasketItems/$IID" "$TB" '{"quantity":3}'); c=$(code "$r")
q=$(body "$(req GET "/rest/basket/$BIDA" "$TA")" | grep -oE '"quantity":[0-9]+' | head -1)
fila "Artículo de cesta #$IID" "PUT (cantidad 1→3)" "$c" "cesta de A: $q" "$([ "$q" = '"quantity":3' ] && echo VULNERABLE || { [ "$q" = '"quantity":1' ] && echo PROTEGIDO || echo 'NO CONCLUYENTE'; })"
r=$(req GET "/api/BasketItems/" "$TB"); c=$(code "$r"); vis=$(body "$r" | grep -c "\"id\":$IID,")
fila "Lista de artículos de cesta" "GET /api/BasketItems/ (todas)" "$c" "incluye el artículo #$IID de A: $([ "$vis" -gt 0 ] && echo sí || echo no)" "$([ "$vis" -gt 0 ] && echo VULNERABLE || echo PROTEGIDO)"
r=$(req DELETE "/api/BasketItems/$IID" "$TB"); c=$(code "$r")
n=$(body "$(req GET "/rest/basket/$BIDA" "$TA")" | grep -c '"quantity":')
fila "Artículo de cesta #$IID" "DELETE (borrar)" "$c" "artículos en la cesta de A: $n" "$([ "$n" -gt 0 ] && echo PROTEGIDO || echo VULNERABLE)"

# --- Opiniones (Feedbacks): GET público por diseño (carrusel); se prueba el borrado ---
# Como el formulario real (contact.component.ts), la opinión lleva el UserId de la sesión (obtenido de whoami)
# (whoami lee la sesión de la cookie 'token', como en el navegador)
UIDA=$(campo "$(curl -s --max-time 20 -H "Cookie: token=$TA${LAB_ACCESO:+; lab_acceso=$LAB_ACCESO}" "$B/rest/user/whoami")" id)
cap=$(curl -s --max-time 20 "$B/rest/captcha/"); cid=$(campo "$cap" captchaId); ans=$(campo "$cap" answer)
r=$(req POST /api/Feedbacks "$TA" '{"comment":"Opinion de prueba A '"$TS"'","rating":3,"UserId":'"${UIDA:-0}"',"captchaId":'"${cid:-0}"',"captcha":"'"$ans"'"}')
FID=$(campo "$(body "$r")" id)
if [ -n "$FID" ]; then
  r=$(req DELETE "/api/Feedbacks/$FID" "$TB"); c=$(code "$r")
  pres=$(curl -s --max-time 20 "$B/api/Feedbacks/" | grep -c "Opinion de prueba A $TS")
  fila "Opinión #$FID" "DELETE (borrar)" "$c" "opinión de A $([ "$pres" -gt 0 ] && echo presente || echo 'eliminada')" "$([ "$pres" -gt 0 ] && echo PROTEGIDO || echo VULNERABLE)"
else
  fila "Opinión" "crear (A)" "$(code "$r")" "no se pudo crear la opinión de prueba" "NO CONCLUYENTE"
fi
# --- Controles positivos: el PROPIETARIO sigue pudiendo operar sus objetos (un control que bloquea todo no es válido) ---
pos_ok=0; pos_f=0
pos() { if [ "$3" = 1 ]; then pos_ok=$((pos_ok+1)); r=OK; else pos_f=$((pos_f+1)); r="**FALLA**"; fi
        printf '| %s | %s | %s |\n' "$1" "$2" "$r" >> "$POS"; }
POS="$(mktemp)"
r=$(req PUT "/api/Addresss/$AID" "$TA" '{"streetAddress":"Calle 2 (A)"}'); c=$(code "$r")
pos "A modifica SU dirección" "$c, $(body "$(req GET "/api/Addresss/$AID" "$TA")" | grep -o 'Calle 2 (A)' | head -1)" "$([ "$c" = 200 ] && body "$(req GET "/api/Addresss/$AID" "$TA")" | grep -q 'Calle 2 (A)' && echo 1 || echo 0)"
r=$(req GET "/api/BasketItems/$IID" "$TA"); c=$(code "$r"); pos "A lee SU artículo de cesta" "$c" "$([ "$c" = 200 ] && echo 1 || echo 0)"
r=$(req PUT "/api/BasketItems/$IID" "$TA" '{"quantity":2}'); c=$(code "$r")
q=$(body "$(req GET "/rest/basket/$BIDA" "$TA")" | grep -oE '"quantity":[0-9]+' | head -1)
pos "A cambia la cantidad de SU artículo (1→2)" "$c, $q" "$([ "$c" = 200 ] && [ "$q" = '"quantity":2' ] && echo 1 || echo 0)"
r=$(req DELETE "/api/BasketItems/$IID" "$TA"); c=$(code "$r"); pos "A borra SU artículo" "$c" "$([ "$c" = 200 ] && echo 1 || echo 0)"
r=$(req DELETE "/api/Cards/$CID" "$TA"); c=$(code "$r"); pos "A borra SU tarjeta" "$c" "$([ "$c" = 200 ] && echo 1 || echo 0)"
r=$(req DELETE "/api/Addresss/$AID" "$TA"); c=$(code "$r"); pos "A borra SU dirección" "$c" "$([ "$c" = 200 ] && echo 1 || echo 0)"
if [ -n "${FID:-}" ]; then r=$(req DELETE "/api/Feedbacks/$FID" "$TA"); c=$(code "$r"); pos "A borra SU opinión" "$c" "$([ "$c" = 200 ] && echo 1 || echo 0)"; fi
{ echo ""; echo "## Controles positivos (el propietario opera sus objetos)"; echo ""; echo "| Acción de A | HTTP / efecto | Resultado |"; echo "|---|---|---|"; cat "$POS"
  echo ""; echo "Controles positivos: $pos_ok OK, $pos_f FALLAS. (Si alguna fila anterior es VULNERABLE, B ya alteró o borró ese objeto y el control positivo falla por esa causa.)"; } >> "$OUT"; rm -f "$POS"
{ echo ""; echo "**Resultado: $vuln VULNERABLE, $ok PROTEGIDO, $nc NO CONCLUYENTE.** GET /api/Feedbacks es público por diseño (carrusel de opiniones) y no se cuenta como BOLA."; } >> "$OUT"
cat "$OUT"
