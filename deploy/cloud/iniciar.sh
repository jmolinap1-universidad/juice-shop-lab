#!/bin/sh
# Arranque del contenedor cloud (un solo contenedor: WAF nginx+ModSecurity+CRS delante de Juice Shop corregido + RASP).
# Corre como el usuario sin privilegios "nginx" (101). Secretos que configura el EQUIPO en la plataforma (nunca en el repo):
#   JWT_CLAVE_EFIMERA=1   (no secreta) el contenedor genera su propia clave JWT al arrancar; o bien
#   JWT_PRIVATE_KEY_B64   clave RSA de firma de los JWT en base64 (o JWT_PRIVATE_KEY en PEM); sin ninguna la app no
#                         arranca (falla cerrada)
#   BASIC_AUTH_HTPASSWD   líneas htpasswd (bcrypt) de quien puede entrar; vacío = nadie entra (falla cerrada)
#   DATABASE_URL          cadena de la BD PostgreSQL administrada (la inyecta App Platform); vacía = SQLite local
#   DATABASE_CA_CERT      CA de la BD para verificar su certificado TLS (la inyecta App Platform)
set -eu

# 1) Puerta de acceso: usuarios autorizados y cookie de sesión aleatoria (256 bits) por arranque
umask 077
#    Varias entradas separadas por saltos de línea o espacios (los formularios de algunas plataformas son de una línea;
#    ni los nombres de usuario ni los hashes bcrypt contienen espacios). Solo se aceptan entradas usuario:hash-bcrypt;
#    el diagnóstico informa cuántas y qué USUARIOS, nunca los hashes ni el texto de una entrada no válida.
: > /etc/nginx/htpasswd
validas=0; usuarios=""; n=0
set -f   # sin expansión de comodines al separar las entradas
for entrada in $(printf '%s' "${BASIC_AUTH_HTPASSWD:-}" | tr '\r\n\t' '   '); do
  n=$((n+1))
  if printf '%s' "$entrada" | grep -qE '^[A-Za-z0-9._-]{1,32}:\$2[aby]\$[0-9]{2}\$[./A-Za-z0-9]{53}$'; then
    printf '%s\n' "$entrada" >> /etc/nginx/htpasswd
    validas=$((validas+1)); usuarios="$usuarios ${entrada%%:*}"
  else
    echo "AVISO acceso: la entrada $n de BASIC_AUTH_HTPASSWD no es usuario:hash-bcrypt (${#entrada} caracteres); se ignora" >&2
  fi
done
set +f
if [ "$validas" -eq 0 ]; then
  echo "AVISO acceso: ninguna entrada válida en BASIC_AUTH_HTPASSWD; nadie puede entrar (falla cerrada)" >&2
  printf 'sin-usuarios:!\n' > /etc/nginx/htpasswd
else
  echo "acceso: $validas usuario(s) autorizado(s):$usuarios" >&2
fi
unset BASIC_AUTH_HTPASSWD entrada
ACCESO_COOKIE="$(od -An -N32 -tx1 /dev/urandom | tr -d ' \n')"
[ "${#ACCESO_COOKIE}" -eq 64 ] || { echo "FALLO acceso: no se pudo generar la cookie de acceso" >&2; exit 1; }
export ACCESO_COOKIE

# 1b) Clave JWT. Opción recomendada en la nube: JWT_CLAVE_EFIMERA=1 (variable NO secreta) → el contenedor genera su
#     propia clave RSA 2048 al arrancar; nunca sale del contenedor ni la manipula una persona (evita copiar/pegar secretos,
#     origen del fallo de despliegue del 2026-11-24). Los JWT emitidos dejan de valer al reiniciar (igual que la BD
#     sembrada de Juice Shop). Si no se activa, se exige la clave del equipo (JWT_PRIVATE_KEY_B64 en base64 o PEM pegado,
#     o JWT_PRIVATE_KEY) y sin ella la app no arranca (falla cerrada). El diagnóstico nunca muestra la clave.
# Tipo del bloque PEM sin reproducir su cabecera literal (p. ej. "PRIVATE KEY"); "NO ES PEM" si no lo es
tipo_pem() { head -1 /tmp/jwt.pem | sed -nE 's/^-+BEGIN ([A-Z ]+)-+$/\1/p' | grep . || echo 'NO ES PEM'; }
if [ "${JWT_CLAVE_EFIMERA:-0}" = 1 ]; then
  [ -n "${JWT_PRIVATE_KEY_B64:-}${JWT_PRIVATE_KEY:-}" ] && echo "AVISO clave JWT: JWT_CLAVE_EFIMERA=1; se ignoran JWT_PRIVATE_KEY_B64/JWT_PRIVATE_KEY" >&2
  unset JWT_PRIVATE_KEY
  openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048 -out /tmp/jwt.pem 2>/dev/null \
    || { echo "FALLO clave JWT: no se pudo generar la clave efímera" >&2; exit 1; }
  export JWT_PRIVATE_KEY_FILE=/tmp/jwt.pem
  echo "clave JWT: generada en el arranque (efímera, RSA 2048, $(wc -c < /tmp/jwt.pem) bytes, tipo PEM: $(tipo_pem))" >&2
elif [ -n "${JWT_PRIVATE_KEY_B64:-}" ]; then
  case "$JWT_PRIVATE_KEY_B64" in
    *"PRIVATE KEY"*) printf '%s\n' "$JWT_PRIVATE_KEY_B64" > /tmp/jwt.pem ;;
    *) printf '%s' "$JWT_PRIVATE_KEY_B64" | tr -d ' \r\n\t' | base64 -d > /tmp/jwt.pem 2>/dev/null \
         || { echo "FALLO clave JWT: JWT_PRIVATE_KEY_B64 no es base64 válido (${#JWT_PRIVATE_KEY_B64} caracteres)" >&2; exit 1; } ;;
  esac
  export JWT_PRIVATE_KEY_FILE=/tmp/jwt.pem
  echo "clave JWT: desde JWT_PRIVATE_KEY_B64, $(wc -c < /tmp/jwt.pem) bytes, tipo PEM: $(tipo_pem)" >&2
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
