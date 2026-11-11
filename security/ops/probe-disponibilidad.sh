#!/usr/bin/env bash
# Sonda de disponibilidad (benigna): GET a una ruta de salud cada INTERVALO segundos; registra hora, código
# HTTP y tiempo. 000 = sin respuesta (servicio caído o colgado). Se detiene al existir el archivo de parada.
# Uso: probe-disponibilidad.sh <url> <salida.tsv> <archivo-parada> [intervalo]
set -u
url="$1"; out="$2"; stop="$3"; iv="${4:-1}"
printf 'hora\tcodigo\ttiempo\n' > "$out"
while [ ! -e "$stop" ]; do
  printf '%s\t%s\n' "$(date +%H:%M:%S)" "$(curl -s -o /dev/null --max-time 3 -w '%{http_code}\t%{time_total}s' "$url")" >> "$out"
  sleep "$iv"
done
