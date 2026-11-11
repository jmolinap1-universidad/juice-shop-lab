#!/usr/bin/env bash
# Escenario reproducible del RASP SIN WAF (Fase 6, R22). Ejecutar desde la raíz del repo con el stack de
# operaciones levantado (make ops-up). Solo actúa sobre el contenedor propio juice-hardened (red Docker interna).
#
# Uso: security/ops/escenario-rasp.sh <carpeta-salida> <AIKIDO_BLOCK true|false> [RASP_NODE_OPTIONS]
#   Sin el tercer argumento usa la configuración por defecto del compose (Zen + rasp-guard).
# Salida en <carpeta-salida>: arnés (run.sh), http.tsv (código real por petición), disponibilidad.tsv,
# estado-contenedor.txt (RestartCount antes/después), rasp.log (líneas del agente y de la integración).
set -euo pipefail
OUT="$1"; BLOCK="$2"; NODEOPTS="${3:-}"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
export MSYS_NO_PATHCONV=1
hostpath() { if command -v cygpath >/dev/null 2>&1; then cygpath -w "$1"; else printf '%s' "$1"; fi; }
mkdir -p "$OUT"
COMPOSE=(docker compose -f deploy/hardened/docker-compose.yml -f deploy/hardened/docker-compose.ops.yml)

# 1) Recrear la app con la configuración del escenario y esperar a que esté healthy
EXTRA=()
[ -n "$NODEOPTS" ] && EXTRA=("RASP_NODE_OPTIONS=$NODEOPTS")
env AIKIDO_BLOCK="$BLOCK" "${EXTRA[@]}" WAF_PORT="${WAF_PORT:-8080}" \
  "${COMPOSE[@]}" up -d --no-deps --force-recreate juice-shop >/dev/null 2>&1
for _ in $(seq 1 60); do [ "$(docker inspect -f '{{.State.Health.Status}}' juice-hardened)" = healthy ] && break; sleep 3; done
INICIO=$(date -Iseconds)
{
  echo "# Escenario RASP sin WAF — $(date -Iseconds)"
  echo "AIKIDO_BLOCK=$BLOCK"
  echo "NODE_OPTIONS efectivo: $(docker inspect -f '{{range .Config.Env}}{{println .}}{{end}}' juice-hardened | grep '^NODE_OPTIONS=' | cut -d= -f2-)"
  echo "Antes:   estado=$(docker inspect -f '{{.State.Health.Status}}' juice-hardened) RestartCount=$(docker inspect -f '{{.RestartCount}}' juice-hardened) StartedAt=$(docker inspect -f '{{.State.StartedAt}}' juice-hardened)"
} > "$OUT/estado-contenedor.txt"

# 2) Arnés + sonda de disponibilidad desde la red interna (sin pasar por el WAF)
REL="${OUT#"$ROOT"/}"
docker run --rm --network juice-hardened_interna -e TZ=America/Guatemala \
  -e ATTACK_TAG="$(basename "$OUT")" -e ATTACK_OUT="/work/$REL" -e ATTACK_FASE=6 -e ATTACK_HTTPLOG="/work/$REL/http.tsv" \
  -v "$(hostpath "$ROOT")":/work -w /work \
  alpine:3.20@sha256:d9e853e87e55526f6b2917df91a2115c36dd7c696a35be12163d44e6e2a4b6bc sh -c '
    apk add --no-cache -q bash curl coreutils tzdata grep sed >/dev/null
    printf "metodo\truta\tcodigo\ttiempo\n" > "$ATTACK_HTTPLOG"
    bash security/ops/probe-disponibilidad.sh http://juice-hardened:3000/rest/admin/application-version "$ATTACK_OUT/disponibilidad.tsv" /tmp/parar 1 &
    bash security/attacks/run.sh http://juice-hardened:3000 > "$ATTACK_OUT/consola.txt" 2>&1 || true
    sleep 3; touch /tmp/parar; sleep 2'

# 3) Estado posterior y registros del agente/integración
sleep 5
{
  echo "Después: estado=$(docker inspect -f '{{.State.Health.Status}}' juice-hardened) RestartCount=$(docker inspect -f '{{.RestartCount}}' juice-hardened) StartedAt=$(docker inspect -f '{{.State.StartedAt}}' juice-hardened)"
} >> "$OUT/estado-contenedor.txt"
docker logs --since "$INICIO" juice-hardened 2>&1 | grep -E '^Zen has|^rasp-guard|UnhandledPromiseRejection|triggerUncaughtException|^Error: Zen|^AIKIDO: Starting|^Node\.js' > "$OUT/rasp.log" || true
echo "== $OUT"; cat "$OUT/estado-contenedor.txt"
echo "-- http.tsv (A1-A3 = POST /rest/user/login y GET /rest/products/search):"; head -5 "$OUT/http.tsv"
echo "-- disponibilidad: $(awk -F'\t' 'NR>1{n++; if($2!="200")f++} END{printf "%d sondeos, %d sin 200", n, f+0}' "$OUT/disponibilidad.tsv")"
