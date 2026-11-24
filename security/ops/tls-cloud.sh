#!/usr/bin/env bash
# Comprueba el TLS REAL del despliegue cloud (handshakes con OpenSSL, no lo que dice la documentación del proveedor):
# versiones aceptadas/rechazadas, cifrado negociado, certificado (emisor, sujeto, vigencia) y redirección HTTP → HTTPS.
# Solo el host exacto en HOST_CLOUD_AUTORIZADO. Uso: security/ops/tls-cloud.sh <host> <salida.md>
set -uo pipefail
H="$1"; OUT="$2"
[ -n "${HOST_CLOUD_AUTORIZADO:-}" ] && [ "$H" = "$HOST_CLOUD_AUTORIZADO" ] || { echo "FUERA DE ALCANCE: $H"; exit 2; }
export MSYS_NO_PATHCONV=1
OSSL=owasp/modsecurity-crs@sha256:d69bfa07bbaeecd15f46188c2b624a4a365aeabf8c70b22e4aba32d72417d2d5   # OpenSSL 3 de Debian 13
o() { docker run --rm --entrypoint sh "$OSSL" -c "$1" 2>&1; }
mkdir -p "$(dirname "$OUT")"
{
  echo "# TLS del despliegue cloud — $(date -Iseconds)"
  echo "Host: \`$H\` · cliente: OpenSSL $(o 'openssl version' | awk '{print $2}') (imagen fijada por digest)"
  echo ""
  echo "| Versión | Resultado | Protocolo/cifrado negociado |"
  echo "|---|---|---|"
  for v in tls1 tls1_1 tls1_2 tls1_3; do
    r="$(o "echo | timeout 20 openssl s_client -connect $H:443 -servername $H -$v -cipher 'DEFAULT:@SECLEVEL=0' 2>&1")"
    if printf '%s' "$r" | grep -qE '^ *Cipher is |New, TLSv'; then
      neg="$(printf '%s' "$r" | grep -E '^New, ' | head -1 | sed 's/^New, //')"
      echo "| $v | ACEPTADA | $neg |"
    else
      echo "| $v | rechazada | $(printf '%s' "$r" | grep -oiE 'alert [a-z ]+|unsupported protocol|no protocols available|wrong version number|handshake failure' | head -1) |"
    fi
  done
  echo ""
  echo "## Certificado"
  echo '```'
  o "echo | timeout 20 openssl s_client -connect $H:443 -servername $H 2>/dev/null | openssl x509 -noout -subject -issuer -dates -ext subjectAltName"
  echo '```'
  echo ""
  echo "## Redirección HTTP → HTTPS"
  echo "- \`http://$H/\` → $(curl -s -o /dev/null -w '%{http_code} %{redirect_url}' --max-time 30 "http://$H/")"
} > "$OUT"
cat "$OUT"
