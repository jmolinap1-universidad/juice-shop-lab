#!/bin/sh
# Arranque del contenedor cloud (un solo contenedor: WAF nginx+ModSecurity+CRS delante de Juice Shop corregido + RASP).
# Corre como el usuario sin privilegios "nginx" (101). Secretos que configura el EQUIPO en la plataforma (nunca en el repo):
#   JWT_PRIVATE_KEY_B64   clave RSA de firma de los JWT en base64 (o JWT_PRIVATE_KEY en PEM); sin ella la app no
#                         arranca (falla cerrada)
#   BASIC_AUTH_HTPASSWD   líneas htpasswd (bcrypt) de quien puede entrar; vacío = nadie entra (falla cerrada)
#   DATABASE_URL          cadena de la BD PostgreSQL administrada (la inyecta App Platform); vacía = SQLite local
#   DATABASE_CA_CERT      CA de la BD para verificar su certificado TLS (la inyecta App Platform)
set -eu

# 1) Puerta de acceso: usuarios autorizados y cookie de sesión aleatoria (256 bits) por arranque
umask 077
if [ -n "${BASIC_AUTH_HTPASSWD:-}" ]; then
  # Varias entradas separadas por saltos de línea o espacios (los formularios de algunas plataformas son de una línea;
  # ni los nombres de usuario ni los hashes bcrypt contienen espacios)
  printf '%s\n' "$BASIC_AUTH_HTPASSWD" | tr ' ' '\n' | grep -v '^$' > /etc/nginx/htpasswd
else
  echo "AVISO acceso: BASIC_AUTH_HTPASSWD vacío; nadie puede entrar (falla cerrada)" >&2
  printf 'sin-usuarios:!\n' > /etc/nginx/htpasswd
fi
unset BASIC_AUTH_HTPASSWD
ACCESO_COOKIE="$(od -An -N32 -tx1 /dev/urandom | tr -d ' \n')"
[ "${#ACCESO_COOKIE}" -eq 64 ] || { echo "FALLO acceso: no se pudo generar la cookie de acceso" >&2; exit 1; }
export ACCESO_COOKIE

# 1b) Clave JWT: también se acepta en base64 (JWT_PRIVATE_KEY_B64), porque algunos paneles no admiten valores multilínea
if [ -n "${JWT_PRIVATE_KEY_B64:-}" ]; then
  printf '%s' "$JWT_PRIVATE_KEY_B64" | base64 -d > /tmp/jwt.pem
  export JWT_PRIVATE_KEY_FILE=/tmp/jwt.pem
fi
unset JWT_PRIVATE_KEY_B64

# 2) CA de la base de datos (TLS verificado hacia PostgreSQL)
if [ -n "${DATABASE_CA_CERT:-}" ]; then
  printf '%s\n' "$DATABASE_CA_CERT" > /tmp/bd-ca.crt
  export NODE_EXTRA_CA_CERTS=/tmp/bd-ca.crt
fi
unset DATABASE_CA_CERT
umask 022

# 3) Aplicación en el puerto 3000, que la plataforma NO enruta: el único puerto con tráfico externo es el del WAF
#    ($PORT = 8080). PORT se fija aquí porque Juice Shop también lee PORT y chocaría con nginx.
#    Si la app termina, se detiene nginx (PID 1) para que la plataforma reinicie el contenedor completo.
(cd /juice-shop && env -u ACCESO_COOKIE PORT=3000 /nodejs/bin/node build/app.js
 echo "FALLO app: Juice Shop terminó (código $?); se detiene el contenedor" >&2; kill -TERM 1) &

# 4) WAF: los secretos de la app no pasan a nginx
unset JWT_PRIVATE_KEY JWT_PRIVATE_KEY_FILE DATABASE_URL NODE_EXTRA_CA_CERTS
exec /docker-entrypoint.sh "$@"
