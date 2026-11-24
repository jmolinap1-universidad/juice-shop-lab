# Pruebas del cierre técnico — 2026-11-24T00:50:56-06:00

Objetivo: https://juice-lab-masi-staging.onrender.com. Cuentas nuevas A y B. Tokens no se registran.

| ID | Caso | Petición | HTTP | Efecto real | Veredicto |
|---|---|---|---|---|---|
| T1 | NoSQL: reseñas de otros productos | `GET /rest/products/1 || true/reviews` | 200 | reseñas del producto 1: 3; con la inyección: 0 | **PROTEGIDO** |
| T2 | NoSQL: todos los pedidos | `GET /rest/track-order/x'||'1'=='1` | 200 | pedidos devueltos: 1 | **PROTEGIDO** |
| T3 | NoSQL: modificar todas las reseñas | `PATCH /rest/products/reviews {id:{$ne:-1}}` | 403 | reseñas modificadas: 0 | **PROTEGIDO** |
| T4 | Reseña de otra cuenta | `PATCH /rest/products/reviews {id:<reseña de A>} (B)` | 403 | texto alterado: no | **PROTEGIDO** |
| T5 | SSRF hacia un servicio interno | `POST /profile/image/url imageUrl=http://127.0.0.1:8080/…` | 403 | ver marca ssrf-sonda-1795503026 en el log de acceso del WAF (lo comprueba el ejecutor) | **PENDIENTE DE LOG** |
| T6 | CSRF: perfil con Origin ajeno | `POST /profile (cookie, Origin: https://atacante.example)` | 403 | nombre cambiado: no | **PROTEGIDO** |
| T6b | Control: perfil sin Origin ajeno (uso legítimo) | `POST /profile (cookie)` | 302 | nombre cambiado: sí | **PROTEGIDO** |
| T7 | XXE: entidad externa con archivo local | `POST /file-upload (xxe.xml)` | 403 | entidad resuelta en la respuesta: no; en el servidor: ver la línea con xxe-sonda-1795503026 en el log de la app ("&x;" = no resuelta) | **PENDIENTE DE LOG** |
| T8 | 5xx con mensaje interno de la BD | `POST /api/Feedbacks (UserId inexistente)` | 500 | cuerpo: {"status":"error","message":"Internal server error"} | **PROTEGIDO** |
| T9 | Quejas de otras cuentas | `GET /api/Complaints (B)` | 403 | queja de A visible: no | **PROTEGIDO** |
| T10 | Reciclajes sin sesión y en lote | `GET /api/Recycles/[1..10] (sin token)` | 403 | registros devueltos: 0 | **PROTEGIDO** |

**Resultado parcial: 0 VULNERABLE, 9 PROTEGIDO, 2 pendientes de log o no concluyentes.**

## Comprobación en los logs de Render (panel de logs del servicio, búsqueda por marca, 2026-11-24T00:52:20-06:00)
- T5 SSRF: la marca ssrf-sonda-1795503026 aparece solo en el registro de auditoría del WAF: POST /profile/image/url → 403 (reglas CRS 931100 RFI por IP y 934110 SSRF; puntuación 10). Ninguna línea de acceso con ua=node: la app no hizo la petición → **PROTEGIDO**
- T7 XXE: búsqueda de xxe-sonda-1795503026 → «No matching logs»: ninguna entidad resuelta en la app (el WAF respondió 403 y el registro de auditoría cloud no guarda cuerpos) → **PROTEGIDO**
