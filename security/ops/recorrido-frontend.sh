#!/usr/bin/env bash
# Recorrido LEGÍTIMO de un cliente con las mismas llamadas que hace la interfaz de Juice Shop (frontend/src/app/Services):
# catálogo, reseñas, sesión (whoami con cookie), cesta con PUT/DELETE, dirección, tarjeta, compra, pedidos, opinión.
# Objetivo: medir FALSOS POSITIVOS del WAF (403 con la página de nginx) frente a la respuesta de la app sin WAF.
# Solo instancias propias. Datos ficticios. Los tokens nunca se escriben.
# Uso: recorrido-frontend.sh <url-base> <salida.md>     (REG_PAUSA=13 entre logins si hay WAF con límite de tasa)
set -u
B="$1"; OUT="$2"
case "$(printf '%s' "$B" | sed -E 's#https?://##; s#[:/].*##')" in
  127.0.0.1|localhost|juice-hardened|juice-corregida|waf-config-historica) : ;;
  *) echo "RECHAZADO: objetivo fuera del laboratorio"; exit 2 ;;
esac
TS=$(date +%s); PW='Passw0rd!123'; EM="recorrido_${TS}@juice-sh.op"; J='Content-Type: application/json'
ok=0; waf=0; otro=0
paso() { # descripcion metodo ruta esperado [datos]
  local d="${5:-}" args=() r c cuerpo cls
  args=(-s --max-time 20 -X "$2" -w '\t%{http_code}' -H "Authorization: Bearer ${TK:-}" -H "Cookie: token=${TK:-}")
  if [ -n "$d" ]; then args+=(-H "$J" --data "$d"); fi
  r="$(curl "${args[@]}" "$B$3" | tr '\r\n' '  ')"; c="${r##*$'\t'}"; cuerpo="${r%$'\t'*}"
  if printf '%s' "$cuerpo" | grep -q '<center>nginx</center>'; then cls="**BLOQUEO DEL WAF**"; waf=$((waf+1))
  elif printf '%s' "$4" | grep -qw "$c"; then cls="OK"; ok=$((ok+1))
  else cls="distinto de lo esperado"; otro=$((otro+1)); fi
  printf '| %s | `%s %s` | %s | %s | %s |\n' "$1" "$2" "$(printf '%s' "$3" | cut -c1-60)" "$4" "$c" "$cls" >> "$OUT"
  ULTIMO="$cuerpo"
}
campo() { printf '%s' "$1" | grep -oE "\"$2\":(\"[^\"]*\"|[0-9]+)" | head -1 | sed -E "s/\"$2\"://; s/\"//g"; }
{
  echo "# Recorrido legítimo de la interfaz — $(date -Iseconds)"
  echo ""
  echo "Objetivo: $B. Llamadas tomadas de \`app/frontend/src/app/Services\`. «BLOQUEO DEL WAF» = 403 con la página de nginx."
  echo ""
  echo "| Paso | Petición | Esperado | HTTP | Resultado |"
  echo "|---|---|---|---|---|"
} > "$OUT"
TK=""
paso "Configuración de la app" GET /rest/admin/application-configuration 200
paso "Versión" GET /rest/admin/application-version 200
paso "Idiomas" GET /rest/languages 200
paso "Búsqueda de productos" GET "/rest/products/search?q=juice" 200
paso "Detalle de producto" GET /api/Products/1 200
paso "Existencias" GET /api/Quantitys/ "200 401"
paso "Reseñas de producto" GET /rest/products/1/reviews 200
paso "Preguntas de seguridad" GET /api/SecurityQuestions/ 200
paso "Registro" POST /api/Users 201 '{"email":"'"$EM"'","password":"'"$PW"'","passwordRepeat":"'"$PW"'","securityQuestion":{"id":1},"securityAnswer":"x"}'
sleep "${REG_PAUSA:-0}"
paso "Inicio de sesión" POST /rest/user/login 200 '{"email":"'"$EM"'","password":"'"$PW"'"}'
TK=$(campo "$ULTIMO" token); BID=$(campo "$ULTIMO" bid)
paso "Sesión actual (whoami)" GET /rest/user/whoami 200
UID_=$(campo "$ULTIMO" id)
paso "Guardar IP de acceso" GET /rest/saveLoginIp 200
paso "Estado 2FA" GET /rest/2fa/status 200
paso "Escribir reseña" PUT /rest/products/1/reviews 201 '{"message":"Muy bueno (recorrido '"$TS"')","author":"'"$EM"'"}'
paso "Ver cesta propia" GET "/rest/basket/$BID" 200
paso "Añadir a la cesta" POST /api/BasketItems 200 '{"ProductId":1,"BasketId":"'"$BID"'","quantity":1}'
IID=$(campo "$ULTIMO" id)
paso "Cambiar cantidad (PUT)" PUT "/api/BasketItems/$IID" 200 '{"quantity":2}'
paso "Quitar de la cesta (DELETE)" DELETE "/api/BasketItems/$IID" 200
paso "Añadir de nuevo para comprar" POST /api/BasketItems 200 '{"ProductId":1,"BasketId":"'"$BID"'","quantity":1}'
paso "Crear dirección" POST /api/Addresss 201 '{"country":"GT","fullName":"Cliente Prueba","mobileNum":5550000,"zipCode":"01001","streetAddress":"Calle 1","city":"Guatemala","state":"GT"}'
AID=$(campo "$ULTIMO" id)
paso "Listar direcciones" GET /api/Addresss 200
paso "Editar dirección (PUT)" PUT "/api/Addresss/$AID" 200 '{"streetAddress":"Calle 2"}'
paso "Métodos de entrega" GET /api/Deliverys 200
paso "Registrar tarjeta (ficticia)" POST /api/Cards 201 '{"fullName":"Cliente Prueba","cardNum":4000000000000002,"expMonth":12,"expYear":2090}'
CID=$(campo "$ULTIMO" id)
paso "Listar tarjetas" GET /api/Cards 200
paso "Saldo del monedero" GET /rest/wallet/balance 200
paso "Comprar (checkout)" POST "/rest/basket/$BID/checkout" 200 '{"couponData":"","orderDetails":{"paymentId":"'"$CID"'","addressId":"'"$AID"'","deliveryMethodId":"1"}}'
paso "Historial de pedidos" GET /rest/order-history 200
paso "Membresía deluxe" GET /rest/deluxe-membership 200
paso "Recuerdos (fotos)" GET /rest/memories 200
paso "Captcha de opinión" GET /rest/captcha/ 200
cid=$(campo "$ULTIMO" captchaId); ans=$(campo "$ULTIMO" answer)
paso "Enviar opinión" POST /api/Feedbacks 201 '{"comment":"Buen servicio (recorrido '"$TS"')","rating":4,"UserId":'"${UID_:-0}"',"captchaId":'"${cid:-0}"',"captcha":"'"$ans"'"}'
paso "Ver opiniones" GET /api/Feedbacks/ 200
paso "Borrar tarjeta (DELETE)" DELETE "/api/Cards/$CID" 200
paso "Borrar dirección (DELETE)" DELETE "/api/Addresss/$AID" 200
{ echo ""; echo "**Resultado: $ok OK, $waf BLOQUEOS DEL WAF (falsos positivos), $otro respuestas distintas de lo esperado.**"; } >> "$OUT"
cat "$OUT"
