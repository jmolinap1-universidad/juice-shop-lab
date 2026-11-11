#!/usr/bin/env bash
# Tráfico LEGÍTIMO (control de falsos positivos) contra la instancia propia del laboratorio.
# Dos usuarios normales: navegan, buscan, se registran SIN 'role', inician sesión y leen SU PROPIA cesta.
# Sirve para: (1) comprobar que WAF/RASP no bloquean uso legítimo; (2) medir la heurística BOLA del SIEM
# (dos usuarios legítimos distintos = dos cestas distintas: si la alerta salta, es un FALSO POSITIVO).
# Uso: trafico-legitimo.sh <url-base> <archivo-salida>     Los tokens se redactan.
set -u
B="$1"; OUT="$2"
case "$(printf '%s' "$B" | sed -E 's#https?://##; s#[:/].*##')" in
  127.0.0.1|localhost|juice-hardened) : ;;
  *) echo "RECHAZADO: objetivo fuera del laboratorio"; exit 2 ;;
esac
TS=$(date +%s); PW='Passw0rd!123'
c() { curl -s -o /dev/null --max-time 15 -w '%{http_code}' "$@"; }
usuario() {
  local em="legit_${1}_${TS}@juice-sh.op" l tk bid
  printf 'POST /api/Users (registro %s, sin role)   -> %s\n' "$1" "$(c -X POST "$B/api/Users" -H 'Content-Type: application/json' \
    --data '{"email":"'"$em"'","password":"'"$PW"'","passwordRepeat":"'"$PW"'","securityQuestion":{"id":1},"securityAnswer":"x"}')"
  l=$(curl -s --max-time 15 -X POST "$B/rest/user/login" -H 'Content-Type: application/json' --data '{"email":"'"$em"'","password":"'"$PW"'"}')
  tk=$(printf '%s' "$l" | grep -oE '"token":"[^"]*"' | sed -E 's/"token":"//; s/"//')
  bid=$(printf '%s' "$l" | grep -oE '"bid":[0-9]+' | sed 's/"bid"://')
  printf 'POST /rest/user/login (%s)                 -> token=%s bid=%s\n' "$1" "$([ -n "$tk" ] && echo 'emitido [REDACTADO]' || echo NO)" "${bid:-?}"
  printf 'GET /rest/basket/%s (cesta PROPIA de %s)    -> %s\n' "${bid:-?}" "$1" "$(c -H "Authorization: Bearer $tk" "$B/rest/basket/${bid:-0}")"
}
{
  echo "# Tráfico legítimo — $(date -Iseconds) — objetivo $B"
  printf 'GET /                                      -> %s\n' "$(c "$B/")"
  printf 'GET /rest/products/search?q=apple          -> %s\n' "$(c "$B/rest/products/search?q=apple")"
  printf 'GET /rest/products/1/reviews               -> %s\n' "$(c "$B/rest/products/1/reviews")"
  usuario A
  usuario B
  echo
  echo "Esperado: 200/201 en todo. Cada usuario lee SOLO su cesta (no hay lectura cruzada)."
} | tee "$OUT"
