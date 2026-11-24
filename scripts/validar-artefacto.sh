#!/usr/bin/env bash
# Valida el ARTEFACTO que está corriendo en el stack vigente (make ops-corregido-up): misma batería sin WAF (red interna,
# mide el código) y con WAF (127.0.0.1:$WAF_PORT, mide la configuración completa). Registra imagen, variante, fecha y entorno.
# Solo instancias propias. Uso: scripts/validar-artefacto.sh <carpeta-salida>      (WAF_PORT=8088 por defecto)
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$ROOT"
export MSYS_NO_PATHCONV=1
OUT="$1"; WAF_PORT="${WAF_PORT:-8088}"; B="http://127.0.0.1:$WAF_PORT"; NET=juice-corregida-defensa_interna
mkdir -p "$OUT/sin-waf" "$OUT/con-waf"
hostpath() { if command -v cygpath >/dev/null 2>&1; then cygpath -m "$1"; else printf '%s' "$1"; fi; }
W="$(hostpath "$ROOT")"
lab() { docker run --rm --network "$NET" -v "$W:/work" -w /work lab-tools:local bash -c "$1"; }
logs_ok() { # $1 carpeta con marcas.env, $2 hora de inicio UTC
  . "$1/marcas.env"
  local s x
  s=$(grep "$MARCA_SSRF" deploy/hardened/logs-corregido/access.log 2>/dev/null | grep -c '"ua":"node"')
  x=$(docker logs --since "$2" juice-hardened 2>&1 | grep "$MARCA_XXE" | grep -vc '&x;')
  printf '\n## Comprobación en logs (%s)\n- T5 SSRF (petición de la app a la marca en el log del WAF): %s → %s\n- T7 XXE (entidad resuelta en el log de la app): %s → %s\n' \
    "$(date -Iseconds)" "$s" "$([ "$s" -gt 0 ] && echo '**VULNERABLE**' || echo '**PROTEGIDO**')" "$x" "$([ "$x" -gt 0 ] && echo '**VULNERABLE**' || echo '**PROTEGIDO**')" >> "$1/resultados.md"
}
{
  echo "# Validación del artefacto — $(date -Iseconds)"
  docker inspect juice-hardened --format 'Contenedor juice-hardened · imagen {{.Image}} · {{.Config.Image}} · variante {{index .Config.Labels "masi.variante"}} · salud {{.State.Health.Status}} · reinicios {{.RestartCount}}'
  docker image inspect juice-corregida:local --format 'Base juice-corregida:local {{.Id}} · diff auditado {{index .Config.Labels "masi.fuente.diff.sha256"}} · app {{index .Config.Labels "masi.app.commit"}}'
  echo "Entorno: local (Docker Desktop), stack juice-corregida-defensa, WAF $B"
} > "$OUT/LEAME.md"

echo "== sin WAF (red interna)"
INI=$(date -u +%Y-%m-%dT%H:%M:%SZ)
lab "bash security/ops/regresion-corregida.sh http://juice-hardened:3000 $OUT/sin-waf/regresion.md >/dev/null; bash security/ops/recorrido-frontend.sh http://juice-hardened:3000 $OUT/sin-waf/recorrido.md >/dev/null; bash security/ops/bola-recursos.sh http://juice-hardened:3000 $OUT/sin-waf/bola-recursos.md >/dev/null; bash security/ops/pruebas-cierre-tecnico.sh http://juice-hardened:3000 $OUT/sin-waf/pruebas >/dev/null"
sleep 3; logs_ok "$OUT/sin-waf/pruebas" "$INI"

echo "== con WAF ($B)"
sleep 60
REG_PAUSA=13 bash security/ops/regresion-corregida.sh "$B" "$OUT/con-waf/regresion.md" >/dev/null
sleep 30
REG_PAUSA=13 bash security/ops/recorrido-frontend.sh "$B" "$OUT/con-waf/recorrido.md" >/dev/null
sleep 60
ATTACK_FASE=6 ATTACK_TAG=validar-artefacto ATTACK_OUT="$ROOT/$OUT/con-waf/ataques" ATTACK_HTTPLOG="$ROOT/$OUT/con-waf/ataques/http.tsv" A12_DELAY=65 \
  bash security/attacks/run.sh "$B" > "$OUT/con-waf/ataques.txt" 2>&1
sleep 60
BOLA_PAUSA=13 bash security/ops/bola-recursos.sh "$B" "$OUT/con-waf/bola-recursos.md" >/dev/null
sleep 60
INI=$(date -u +%Y-%m-%dT%H:%M:%SZ)
PAUSA=13 bash security/ops/pruebas-cierre-tecnico.sh "$B" "$OUT/con-waf/pruebas" >/dev/null
sleep 3; logs_ok "$OUT/con-waf/pruebas" "$INI"

{
  echo ""
  echo "| Batería | Sin WAF | Con WAF |"
  echo "|---|---|---|"
  r() { grep -hE '^\*\*Resultado|^Controles positivos|^=== ' "$1" 2>/dev/null | head -2 | tr '\n' ' ' | sed 's/\*\*//g' | cut -c1-120; }
  echo "| Regresión funcional | $(r "$OUT/sin-waf/regresion.md") | $(r "$OUT/con-waf/regresion.md") |"
  echo "| Recorrido de la interfaz (35 llamadas) | $(r "$OUT/sin-waf/recorrido.md") | $(r "$OUT/con-waf/recorrido.md") |"
  echo "| BOLA en 5 tipos de objeto | $(r "$OUT/sin-waf/bola-recursos.md") | $(r "$OUT/con-waf/bola-recursos.md") |"
  echo "| Pruebas T1-T10 | $(r "$OUT/sin-waf/pruebas/resultados.md") | $(r "$OUT/con-waf/pruebas/resultados.md") |"
  echo "| A1-A12 (run.sh) | — | $(r "$OUT/con-waf/ataques.txt") |"
  echo ""
  echo "Códigos HTTP del arnés con WAF: $(cut -f3 "$OUT/con-waf/ataques/http.tsv" 2>/dev/null | sort | uniq -c | tr -s ' ' | tr '\n' ' ')"
  docker inspect juice-hardened --format 'Estado final: salud {{.State.Health.Status}} · reinicios {{.RestartCount}}'
} >> "$OUT/LEAME.md"
cat "$OUT/LEAME.md"
