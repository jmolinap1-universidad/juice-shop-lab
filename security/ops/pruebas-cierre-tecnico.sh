#!/usr/bin/env bash
# Pruebas defensivas del cierre técnico (2026-11-23), SOLO contra instancias propias del laboratorio.
# Cubre lo que quedaba sin medir: NoSQL (lectura de reseñas, pedidos, actualización masiva), reseña ajena, SSRF,
# CSRF por cookie, XXE, fuga de mensajes internos en 5xx y autorización de Complaints/Recycles.
# Cada caso comprueba el EFECTO REAL, no solo el código HTTP. Sin efecto verificable → NO CONCLUYENTE.
# SSRF y XXE dejan una MARCA única que el ejecutor comprueba después en los logs del WAF y de la app (salida: marcas.env).
# Uso: pruebas-cierre-tecnico.sh <url-base> <carpeta-salida>      (PAUSA=13 si hay WAF con límite de logins)
set -u
B="$1"; D="$2"; mkdir -p "$D"; OUT="$D/resultados.md"
case "$(printf '%s' "$B" | sed -E 's#https?://##; s#[:/].*##')" in
  127.0.0.1|localhost|juice-hardened|juice-corregida|juice-lab) : ;;
  *) echo "RECHAZADO: objetivo fuera del laboratorio"; exit 2 ;;
esac
TS=$(date +%s); PW='Passw0rd!123'; J='Content-Type: application/json'
v=0; p=0; nc=0
fila() { # id, caso, peticion, http, efecto, veredicto
  local ver="$6"; case "$4" in ''|000) ver='NO CONCLUYENTE';; esac
  case "$ver" in VULNERABLE) v=$((v+1));; PROTEGIDO) p=$((p+1));; *) nc=$((nc+1));; esac
  printf '| %s | %s | `%s` | %s | %s | **%s** |\n' "$1" "$2" "$3" "$4" "$5" "$ver" >> "$OUT"
}
cuenta() {
  local em="ct_${1}_${TS}@juice-sh.op"
  curl -s -o /dev/null --max-time 20 -X POST "$B/api/Users" -H "$J" --data '{"email":"'"$em"'","password":"'"$PW"'","passwordRepeat":"'"$PW"'","securityQuestion":{"id":1},"securityAnswer":"x"}'
  sleep "${PAUSA:-0}"
  curl -s --max-time 20 -X POST "$B/rest/user/login" -H "$J" --data '{"email":"'"$em"'","password":"'"$PW"'"}' | grep -oE '"token":"[^"]*"' | cut -d'"' -f4
}
c() { curl -s -o /dev/null --max-time 20 -w '%{http_code}' "$@"; }
TA=$(cuenta A); TB=$(cuenta B)
[ -n "$TA" ] && [ -n "$TB" ] || { echo "Sin sesiones de prueba (¿límite del WAF? use PAUSA=13)"; exit 1; }
EA="ct_A_${TS}@juice-sh.op"
{
  echo "# Pruebas del cierre técnico — $(date -Iseconds)"
  echo ""
  echo "Objetivo: $B. Cuentas nuevas A y B. Tokens no se registran."
  echo ""
  echo "| ID | Caso | Petición | HTTP | Efecto real | Veredicto |"
  echo "|---|---|---|---|---|---|"
} > "$OUT"

# T1 NoSQL en lectura de reseñas: el id se concatena en un $where
n1=$(curl -s --max-time 20 "$B/rest/products/1/reviews" | grep -o '"_id"' | wc -l)
r=$(curl -s --max-time 20 -w '\t%{http_code}' "$B/rest/products/1%20%7C%7C%20true/reviews"); h="${r##*$'\t'}"; n2=$(printf '%s' "${r%$'\t'*}" | grep -o '"_id"' | wc -l)
fila T1 "NoSQL: reseñas de otros productos" "GET /rest/products/1 || true/reviews" "$h" "reseñas del producto 1: $n1; con la inyección: $n2" "$([ "$n2" -gt "$n1" ] && echo VULNERABLE || echo PROTEGIDO)"

# T2 NoSQL en seguimiento de pedidos
r=$(curl -s --max-time 20 -w '\t%{http_code}' "$B/rest/track-order/x'%7C%7C'1'=='1"); h="${r##*$'\t'}"; n=$(printf '%s' "${r%$'\t'*}" | grep -o '"orderId"' | wc -l)
fila T2 "NoSQL: todos los pedidos" "GET /rest/track-order/x'||'1'=='1" "$h" "pedidos devueltos: $n" "$([ "$n" -gt 1 ] && echo VULNERABLE || echo PROTEGIDO)"

# T3 Actualización masiva de reseñas con un operador en el id (solo afecta a la BD del laboratorio, que se re-siembra)
r=$(curl -s --max-time 20 -w '\t%{http_code}' -X PATCH "$B/rest/products/reviews" -H "$J" -H "Authorization: Bearer $TB" --data '{"id":{"$ne":-1},"message":"prueba-nosql-'"$TS"'"}'); h="${r##*$'\t'}"
m=$(printf '%s' "${r%$'\t'*}" | grep -oE '"modified":[0-9]+' | cut -d: -f2)
fila T3 "NoSQL: modificar todas las reseñas" "PATCH /rest/products/reviews {id:{\$ne:-1}}" "$h" "reseñas modificadas: ${m:-0}" "$([ "${m:-0}" -gt 1 ] && echo VULNERABLE || echo PROTEGIDO)"

# T4 Reseña ajena: A escribe una reseña; B intenta cambiar su texto con el _id
curl -s -o /dev/null --max-time 20 -X PUT "$B/rest/products/2/reviews" -H "$J" -H "Authorization: Bearer $TA" --data '{"message":"resena de A '"$TS"'","author":"'"$EA"'"}'
RID=$(curl -s --max-time 20 "$B/rest/products/2/reviews" | grep -oE '"message":"resena de A '"$TS"'"[^}]*"_id":"[^"]*"|"_id":"[^"]*"[^}]*"message":"resena de A '"$TS"'"' | grep -oE '"_id":"[^"]*"' | cut -d'"' -f4 | head -1)
if [ -n "$RID" ]; then
  h=$(c -X PATCH "$B/rest/products/reviews" -H "$J" -H "Authorization: Bearer $TB" --data '{"id":"'"$RID"'","message":"alterada por B '"$TS"'"}')
  alt=$(curl -s --max-time 20 "$B/rest/products/2/reviews" | grep -c "alterada por B $TS")
  fila T4 "Reseña de otra cuenta" "PATCH /rest/products/reviews {id:<reseña de A>} (B)" "$h" "texto alterado: $([ "$alt" -gt 0 ] && echo sí || echo no)" "$([ "$alt" -gt 0 ] && echo VULNERABLE || echo PROTEGIDO)"
else
  fila T4 "Reseña de otra cuenta" "PUT /rest/products/2/reviews (A)" "-" "no se pudo crear la reseña de prueba" "NO CONCLUYENTE"
fi

# T5 SSRF: la app descarga la imagen de perfil desde una URL interna (marca única en el log del WAF)
MARCA_SSRF="ssrf-sonda-$TS"
h=$(c -X POST "$B/profile/image/url" -H "Cookie: token=$TA" -H 'Content-Type: application/x-www-form-urlencoded' --data "imageUrl=http://juice-waf:8080/$MARCA_SSRF.png")
fila T5 "SSRF hacia un servicio interno" "POST /profile/image/url imageUrl=http://juice-waf:8080/…" "$h" "ver marca $MARCA_SSRF en el log de acceso del WAF (lo comprueba el ejecutor)" "PENDIENTE DE LOG"

# T6 CSRF: cambio del nombre de usuario con la cookie y un Origin ajeno (como haría un formulario de otro sitio)
# (whoami no devuelve el nombre de usuario: se lee el usuario por la API con el token de A)
UIDA=$(curl -s --max-time 20 -H "Cookie: token=$TA" "$B/rest/user/whoami" | grep -oE '"id":[0-9]+' | head -1 | cut -d: -f2)
nombre() { curl -s --max-time 20 -H "Authorization: Bearer $TA" "$B/api/Users/${UIDA:-0}" | grep -oE '"username":"[^"]*"' | cut -d'"' -f4; }
h=$(c -X POST "$B/profile" -H "Cookie: token=$TA" -H 'Origin: https://atacante.example' -H 'Content-Type: application/x-www-form-urlencoded' --data "username=csrf$TS")
u=$(nombre | grep -c "csrf$TS")
fila T6 "CSRF: perfil con Origin ajeno" "POST /profile (cookie, Origin: https://atacante.example)" "$h" "nombre cambiado: $([ "$u" -gt 0 ] && echo sí || echo no)" "$([ "$u" -gt 0 ] && echo VULNERABLE || echo PROTEGIDO)"
h=$(c -X POST "$B/profile" -H "Cookie: token=$TA" -H 'Content-Type: application/x-www-form-urlencoded' --data "username=legit$TS")
u=$(nombre | grep -c "legit$TS")
fila T6b "Control: perfil sin Origin ajeno (uso legítimo)" "POST /profile (cookie)" "$h" "nombre cambiado: $([ "$u" -gt 0 ] && echo sí || echo no)" "$([ "$u" -gt 0 ] && echo PROTEGIDO || echo 'NO CONCLUYENTE')"

# T7 XXE: entidad externa que lee un archivo de la propia app (marca única en el log de la app)
MARCA_XXE="xxe-sonda-$TS"
# Detección: si la entidad se resuelve, entre las marcas aparece el contenido de /etc/hostname en lugar de "&x;"
# (el mensaje de error trunca el XML a 400 caracteres: por eso un archivo corto). En el log: la línea con la marca.
printf '<?xml version="1.0"?>\n<!DOCTYPE d [<!ENTITY x SYSTEM "file:///etc/hostname">]>\n<d>%s &x; FIN</d>\n' "$MARCA_XXE" > "$D/xxe.xml"
r=$(curl -s --max-time 30 -w '\t%{http_code}' -F "file=@$D/xxe.xml;type=text/xml" "$B/file-upload"); h="${r##*$'\t'}"
expuesto=$(printf '%s' "${r%$'\t'*}" | sed 's/<[^>]*>/ /g' | grep -oE "$MARCA_XXE [^ &]+ FIN" | wc -l)
fila T7 "XXE: entidad externa con archivo local" "POST /file-upload (xxe.xml)" "$h" "entidad resuelta en la respuesta: $([ "$expuesto" -gt 0 ] && echo sí || echo no); en el servidor: ver la línea con $MARCA_XXE en el log de la app (\"&x;\" = no resuelta)" "$([ "$expuesto" -gt 0 ] && echo VULNERABLE || echo 'PENDIENTE DE LOG')"
rm -f "$D/xxe.xml"

# T8 5xx con detalles internos (inserción rechazada por la BD: UserId inexistente)
cap=$(curl -s --max-time 20 "$B/rest/captcha/"); cid=$(printf '%s' "$cap" | grep -oE '"captchaId":[0-9]+' | cut -d: -f2); ans=$(printf '%s' "$cap" | grep -oE '"answer":"[^"]*"' | cut -d'"' -f4)
r=$(curl -s --max-time 20 -w '\t%{http_code}' -X POST "$B/api/Feedbacks" -H "$J" --data '{"comment":"prueba 5xx","rating":1,"UserId":999999,"captchaId":'"${cid:-0}"',"captcha":"'"$ans"'"}'); h="${r##*$'\t'}"
fuga=$(printf '%s' "${r%$'\t'*}" | grep -ciE 'SQLITE|constraint|sequelize|at .*\.js')
fila T8 "5xx con mensaje interno de la BD" "POST /api/Feedbacks (UserId inexistente)" "$h" "cuerpo: $(printf '%s' "${r%$'\t'*}" | cut -c1-70 | tr '|' '/')" "$([ "$fuga" -gt 0 ] && echo VULNERABLE || { [ "${h:0:1}" = 5 ] && echo PROTEGIDO || echo 'NO CONCLUYENTE'; })"

# T9 Complaints: B lista las quejas de todos
curl -s -o /dev/null --max-time 20 -X POST "$B/api/Complaints" -H "$J" -H "Authorization: Bearer $TA" --data '{"message":"queja de A '"$TS"'"}'
r=$(curl -s --max-time 20 -w '\t%{http_code}' -H "Authorization: Bearer $TB" "$B/api/Complaints"); h="${r##*$'\t'}"; vis=$(printf '%s' "${r%$'\t'*}" | grep -c "queja de A $TS")
fila T9 "Quejas de otras cuentas" "GET /api/Complaints (B)" "$h" "queja de A visible: $([ "$vis" -gt 0 ] && echo sí || echo no)" "$([ "$vis" -gt 0 ] && echo VULNERABLE || echo PROTEGIDO)"

# T10 Recycles: lectura sin autenticación y con varios ids a la vez (JSON en el parámetro)
curl -s -o /dev/null --max-time 20 -X POST "$B/api/Recycles" -H "$J" -H "Authorization: Bearer $TA" --data '{"quantity":5,"isPickup":false,"date":"2026-12-01","AddressId":1}'
r=$(curl -s --max-time 20 -w '\t%{http_code}' "$B/api/Recycles/%5B1,2,3,4,5,6,7,8,9,10%5D"); h="${r##*$'\t'}"; n=$(printf '%s' "${r%$'\t'*}" | grep -oE '"id":[0-9]+' | wc -l)
fila T10 "Reciclajes sin sesión y en lote" "GET /api/Recycles/[1..10] (sin token)" "$h" "registros devueltos: $n" "$([ "$n" -gt 0 ] && echo VULNERABLE || echo PROTEGIDO)"

{ echo ""; echo "**Resultado parcial: $v VULNERABLE, $p PROTEGIDO, $nc pendientes de log o no concluyentes.**"; } >> "$OUT"
printf 'MARCA_SSRF=%s\nMARCA_XXE=%s\nINICIO=%s\n' "$MARCA_SSRF" "$MARCA_XXE" "$TS" > "$D/marcas.env"
cat "$OUT"
