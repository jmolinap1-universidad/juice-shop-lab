# 02b — Los "MITIGADO" de esta corrida NO son mitigaciones

Configuración: `AIKIDO_BLOCK=true`, `NODE_OPTIONS=--require @aikidosec/firewall` (sin integración ni `warn`).
El primer bloqueo (A1, `body.email`) terminó el proceso Node: `rasp.log` muestra el rechazo no manejado y
`estado-contenedor.txt` pasa de `RestartCount=0` a `1`. A partir de ahí las peticiones obtuvieron `000`
(conexión rechazada; ver `http.tsv`) y la sonda falló 5 de 6 veces (`disponibilidad.tsv`).

`resumen-ataques.md` y `consola.txt` cuentan "9 MITIGADO" y A12 "MITIGADO/NEGATIVO" porque el arnés no recibe
datos: es un **fallo de disponibilidad**, no un control. Esta corrida es la evidencia del riesgo R22 (inherente).
