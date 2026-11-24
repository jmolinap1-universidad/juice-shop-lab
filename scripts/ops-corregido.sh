#!/usr/bin/env bash
# Stack VIGENTE de la Fase 6: variante corregida + WAF + RASP + SIEM (proyecto juice-corregida-defensa).
# Uso: scripts/ops-corregido.sh up|ps|down        (WAF_PORT=8088 si el 8080 está ocupado)
#  up   : exige las imágenes de scripts/construir-corregida.sh (no reconstruye en silencio una imagen distinta),
#         genera la clave JWT efímera solo si NO existe, rechaza arrancar si el stack histórico está activo,
#         espera a que todo esté healthy y muestra qué variante corre.
#  ps   : estado, salud, reinicios, imagen, variante y puertos publicados.
#  down : detiene y elimina contenedores y redes. NUNCA borra volúmenes (sin -v).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/deploy/hardened"
export WAF_PORT="${WAF_PORT:-8080}"
DC=(docker compose -f docker-compose.yml -f docker-compose.ops.yml -f docker-compose.corregido.yml)

estado() {
  for c in juice-hardened juice-waf siem-loki siem-alloy siem-grafana siem-socket-proxy; do
    docker inspect "$c" --format "{{.Name}} | {{.State.Status}} | salud={{if .State.Health}}{{.State.Health.Status}}{{else}}n/a{{end}} | reinicios={{.RestartCount}} | {{.Config.Image}} | proyecto={{index .Config.Labels \"com.docker.compose.project\"}} | variante={{index .Config.Labels \"siem.variante\"}}" 2>/dev/null \
      | sed 's#^/##' || echo "$c | no existe"
  done
  echo "Puertos publicados (deben ser solo 127.0.0.1):"
  docker ps --filter label=com.docker.compose.project=juice-corregida-defensa --format '  {{.Names}}: {{.Ports}}'
}

docker info >/dev/null 2>&1 || {
  echo "El motor de Docker no responde. Abra Docker Desktop y espere a que 'docker info' responda (tras reiniciar Windows no arranca solo)."
  exit 1
}

case "${1:-}" in
  up)
    if [ -n "$(docker ps -q --filter label=com.docker.compose.project=juice-hardened)" ]; then
      echo "RECHAZADO: el stack HISTÓRICO (make ops-up, imagen oficial vulnerable) está activo. Deténgalo con 'make ops-down'."; exit 1
    fi
    for img in juice-corregida:local juice-corregida-rasp:local; do
      docker image inspect "$img" >/dev/null 2>&1 || { echo "Falta $img: ejecute 'make corregida-build'."; exit 1; }
    done
    [ -f ../corregido/secrets/jwt_private_key.pem ] || bash "$ROOT/security/ops/generar-clave-jwt.sh"
    mkdir -p logs-corregido
    "${DC[@]}" up -d --no-build
    for _ in $(seq 1 60); do
      s="$(docker inspect -f '{{.State.Health.Status}}' juice-hardened juice-waf 2>/dev/null | sort -u | tr '\n' ' ')"
      [ "$s" = "healthy " ] && break; sleep 5
    done
    estado
    echo "WAF (único punto de entrada): http://127.0.0.1:${WAF_PORT}   Grafana: http://127.0.0.1:3001   Loki: http://127.0.0.1:3100"
    ;;
  ps) estado ;;
  down) "${DC[@]}" down ;;
  *) echo "Uso: $0 up|ps|down"; exit 2 ;;
esac
