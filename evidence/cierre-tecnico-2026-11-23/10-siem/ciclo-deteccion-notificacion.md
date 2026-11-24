# Ciclo completo de detección y notificación (entorno local) — 2026-11-23T19:19:38-06:00
Partida: regla WAF_InyeccionSQL_Bloqueada en estado inactive (resuelta y notificada como RESOLVED a las 19:18).

1. Petición legítima: GET /rest/products/search?q=apple → HTTP 200
2. Petición de prueba bloqueada: GET /rest/products/search?q=')) UNION SELECT 1-- → HTTP 403
   Regla real (audit log del WAF): 942100 942190 942360 949110 
3. En Loki con entorno=local (últimos 2 min): 1 línea(s) de auditoría con reglas 942
4. Regla en el ruler de Loki: firing
5. Notificación en el receptor local (33 s después de la petición):
   NOTIFICACION estado=FIRING alerta=WAF_InyeccionSQL_Bloqueada severidad=high riesgo=R01,R02 desde=2026-11-24T01:19:42.701Z
6. Notificación auditada en Loki ({entorno="local", container="siem-notificador"}): 2 línea(s)
7. Disponibilidad tras el ciclo: búsqueda legítima → HTTP 200; app healthy reinicios=0
