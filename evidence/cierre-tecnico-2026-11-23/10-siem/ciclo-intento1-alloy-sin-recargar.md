# Ciclo completo de detección y notificación (entorno local) — 2026-11-23T19:13:40-06:00
1. Petición legítima: GET /rest/products/search?q=apple → HTTP 200
2. Petición de prueba bloqueada: GET /rest/products/search?q=')) UNION SELECT 1-- → HTTP 403
   Regla real en el audit log del WAF: "ruleId":"942100" "ruleId":"942190" "ruleId":"942360" "ruleId":"949110" 
3. En Loki (entorno=local, últimos 2 min):  líneas de auditoría con reglas 942
4. Estado de la regla: firing
5. Notificación recibida (receptor local, 164 s después del ataque):
6. La notificación auditada en Loki:  línea(s)
Disponibilidad tras el ciclo: búsqueda legítima → HTTP 200
