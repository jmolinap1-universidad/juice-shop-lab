# Ingesta de eventos cloud (Render) en el SIEM local — 2026-11-24T00:55:28-06:00
Fuente: panel de logs de Render del servicio juice-lab-masi-staging (búsqueda 949110, 06:35-07:00 UTC), exportado con el navegador; sin cabeceras ni cookies (el audit log cloud usa partes A,F,H,Z). Carga: scripts/ingesta-eventos-cloud.py (verifica que no haya JWT, Authorization, Cookie ni la cookie de acceso) → POST /loki/api/v1/push.
Etiquetas: job=waf_audit, entorno=cloud, plataforma=render, servicio=juice-lab-masi-staging, fuente_ingesta=exportacion-panel

- Eventos exportados: 7 (waf-bloqueos-render.ndjson). Carga enviada dos veces por un fallo de mi comando (la primera sin registro de salida); Loki descarta las entradas idénticas (misma marca de tiempo y línea).
- En Loki ahora (entorno=cloud, últimas 2 h): 7 líneas — con reglas 942 (SQLi/NoSQL): 5 — con reglas 930/931 (LFI/RFI): 1
- Eventos locales en la misma ventana (entorno=local), para contraste: 0
- Panel de Grafana «SIEM - Juice Shop endurecido»: variable entorno=cloud (las consultas ya filtran por entorno=~"$entorno")
- Captura: grafana-entorno-cloud.jpg (panel con entorno=cloud, últimas 2 h: SQLi 5; familias 942=5, 932=1, 930/931=1). Los paneles «Peticiones bloqueadas», «Login frenado» y RASP no tienen datos cloud porque solo se exportó la auditoría del WAF (no el log de acceso ni el de la app).
