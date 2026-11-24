# Estado del SIEM y tokens históricos — 2026-11-23T19:33:39-06:00
Loki /ready: ready
Grafana /api/health: "database":"ok"
Alertmanager /-/ready (red interna): HTTP 200

Líneas de auditoría del WAF por día en el Loki del stack vigente (consulta de métrica, paso 1 día):
| Patrón | Resultado (día UTC: líneas) |
|---|---|
| `sum(count_over_time({job="waf_audit"} |~ "Bearer eyJ[A-Za-z0-9_-]{8,}" [1d]))` | 11-22: 128 ·  |
| `sum(count_over_time({job="waf_audit"} |= "REDACTADO" [1d]))` | 11-22: 3244 · 11-24: 93 · 11-25: 129 ·  |

**Lectura:** el día 11-22 (UTC) agrupa las líneas del 21-nov (horario de la región). Las 128 líneas con `Bearer eyJ…` son
anteriores a la redacción en Alloy (21-nov 14:35 local) y contienen tokens de **cuentas de prueba sintéticas**, firmados con la
clave efímera del laboratorio y con validez de 6 h (ya vencidos). Desde la redacción, la auditoría aparece con `[REDACTADO]`.
Loki solo escucha en 127.0.0.1. El volumen del stack histórico (`juice-hardened_loki-data`) puede contener líneas equivalentes.

**Saneamiento propuesto (NO ejecutado; borra datos de registro: requiere autorización):** API de borrado de Loki
(`POST /loki/api/v1/delete` con el selector `{job="waf_audit"} |~ "Bearer eyJ"` y el rango del 21-nov, que exige activar
`deletion_mode` en el compactor), o bien recrear el volumen de Loki tras exportar la evidencia ya guardada en `evidence/`.
