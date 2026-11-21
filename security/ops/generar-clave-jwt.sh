#!/usr/bin/env bash
# Genera un par RSA EFÍMERO para firmar los JWT de la variante corregida (parche 04 v2).
# La clave privada se escribe en deploy/corregido/secrets/ (ignorado por git) y se monta como secreto de solo
# lectura; NUNCA se versiona. Ejecutarlo de nuevo rota la clave (los tokens anteriores dejan de ser válidos).
# Uso: security/ops/generar-clave-jwt.sh      (requiere Docker; usa alpine con openssl)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
DEST="$ROOT/deploy/corregido/secrets"
mkdir -p "$DEST"
export MSYS_NO_PATHCONV=1
hostpath() { if command -v cygpath >/dev/null 2>&1; then cygpath -w "$1"; else printf '%s' "$1"; fi; }
docker run --rm -v "$(hostpath "$DEST")":/k alpine:3.20@sha256:d9e853e87e55526f6b2917df91a2115c36dd7c696a35be12163d44e6e2a4b6bc sh -c '
  apk add --no-cache -q openssl >/dev/null
  openssl genrsa -out /k/jwt_private_key.pem 2048 2>/dev/null
  chmod 0444 /k/jwt_private_key.pem'
echo "clave efímera generada (huella de la pública):"
docker run --rm -v "$(hostpath "$DEST")":/k alpine:3.20@sha256:d9e853e87e55526f6b2917df91a2115c36dd7c696a35be12163d44e6e2a4b6bc sh -c '
  apk add --no-cache -q openssl >/dev/null; openssl rsa -in /k/jwt_private_key.pem -pubout 2>/dev/null | openssl sha256 | sed "s/.*= /  sha256(pub)=/"'
