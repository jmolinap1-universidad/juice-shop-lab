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
#     Se toleran espacios y saltos de línea al pegar, y también un PEM pegado tal cual. El diagnóstico solo informa el
#     tipo (cabecera PEM) y el tamaño, nunca la clave.
if [ -n "${JWT_PRIVATE_KEY_B64:-}" ]; then
  case "$JWT_PRIVATE_KEY_B64" in
    *"PRIVATE KEY"*) printf '%s\n' "$JWT_PRIVATE_KEY_B64" > /tmp/jwt.pem ;;
    *) printf '%s' "$JWT_PRIVATE_KEY_B64" | tr -d ' \r\n\t' | base64 -d > /tmp/jwt.pem 2>/dev/null \
         || { echo "FALLO clave JWT: JWT_PRIVATE_KEY_B64 no es base64 válido (${#JWT_PRIVATE_KEY_B64} caracteres)" >&2; exit 1; } ;;
  esac
  export JWT_PRIVATE_KEY_FILE=/tmp/jwt.pem
  echo "clave JWT: desde JWT_PRIVATE_KEY_B64, $(wc -c < /tmp/jwt.pem) bytes, cabecera: $(head -1 /tmp/jwt.pem | grep -oE '^-----BEGIN [A-Z ]+-----$' || echo 'NO ES PEM')" >&2
elif [ -n "${JWT_PRIVATE_KEY:-}" ]; then
  echo "clave JWT: desde JWT_PRIVATE_KEY (${#JWT_PRIVATE_KEY} caracteres)" >&2
else
  echo "AVISO clave JWT: ni JWT_PRIVATE_KEY_B64 ni JWT_PRIVATE_KEY están definidas; la app no arrancará (falla cerrada)" >&2
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
#    Si la app termina, se detiene nginx para que la plataforma reinicie el contenedor completo. Se usa el PID de ESTE
#    script (nginx lo hereda con exec), no el 1: la plataforma puede tener su propio init. `set +e`: con -e heredado el
#    subshell salía al fallar node sin llegar a detener nginx (hallado en Render: el contenedor quedó vivo con 502).
PRINCIPAL=$$
(set +e; cd /juice-shop || exit 1; env -u ACCESO_COOKIE PORT=3000 /nodejs/bin/node build/app.js; codigo=$?
 echo "FALLO app: Juice Shop terminó (código $codigo); se detiene el contenedor" >&2; kill -TERM "$PRINCIPAL") &

# 4) WAF: los secretos de la app no pasan a nginx
unset JWT_PRIVATE_KEY JWT_PRIVATE_KEY_FILE DATABASE_URL NODE_EXTRA_CA_CERTS
exec /docker-entrypoint.sh "$@"
