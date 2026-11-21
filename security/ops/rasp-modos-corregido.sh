#!/usr/bin/env bash
# RASP (Aikido Zen + rasp-guard) en el stack VIGENTE: modo MONITOREO (AIKIDO_BLOCK=false) y modo BLOQUEO (true),
# atacando la app DIRECTAMENTE dentro de la red Docker (sin pasar por el WAF). Solo el contenedor propio juice-hardened.
# Por cada modo: 5 inyecciones en el login + 5 peticiones legítimas, código HTTP y tiempo reales, líneas del RASP,
# estado y reinicios. Al terminar deja el stack en modo bloqueo (configuración vigente).
# Uso: rasp-modos-corregido.sh <carpeta-salida>
set -euo pipefail
OUT="$1"; ROOT="$(cd "$(dirname "$0")/../.." && pwd)"; cd "$ROOT/deploy/hardened"
export MSYS_NO_PATHCONV=1 WAF_PORT="${WAF_PORT:-8088}"
DC=(docker compose -f docker-compose.yml -f docker-compose.ops.yml -f docker-compose.corregido.yml)
mkdir -p "$ROOT/$OUT"
for modo in false true; do
  AIKIDO_BLOCK=$modo "${DC[@]}" up -d --no-build --no-deps --force-recreate juice-shop >/dev/null 2>&1
  for _ in $(seq 1 60); do [ "$(docker inspect -f '{{.State.Health.Status}}' juice-hardened)" = healthy ] && break; sleep 3; done
  INI=$(date -u +%Y-%m-%dT%H:%M:%SZ); F="$ROOT/$OUT/modo-block-$modo.txt"
  {
    echo "# AIKIDO_BLOCK=$modo — $(date -Iseconds) — directo a http://juice-hardened:3000 (sin WAF)"
    docker inspect juice-hardened --format 'antes: RestartCount={{.RestartCount}} salud={{.State.Health.Status}} imagen={{.Config.Image}}'
    docker run --rm --network juice-corregida-defensa_interna lab-tools:local bash -c '
      for i in 1 2 3 4 5; do
        printf "inyeccion %s: " $i; curl -s -o /dev/null --max-time 20 -w "%{http_code} %{time_total}s\n" -X POST http://juice-hardened:3000/rest/user/login -H "Content-Type: application/json" --data "{\"email\":\"'"'"' OR 1=1--\",\"password\":\"x\"}"
        printf "legitima  %s: " $i; curl -s -o /dev/null --max-time 20 -w "%{http_code} %{time_total}s\n" "http://juice-hardened:3000/rest/products/search?q=apple"
      done'
    sleep 3
    docker inspect juice-hardened --format 'después: RestartCount={{.RestartCount}} salud={{.State.Health.Status}}'
    echo "Líneas del RASP desde $INI:"
    docker logs --since "$INI" juice-hardened 2>&1 | grep -E 'Zen has|rasp-guard' | sed -E 's/ip="[^"]*"/ip="<red interna>"/' | sort | uniq -c
  } > "$F"
  cat "$F"
done
