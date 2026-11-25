# Pruebas del cierre técnico — 2026-11-24T23:39:23-06:00

Objetivo: http://127.0.0.1:8090. Cuentas nuevas A y B. Tokens no se registran.

| ID | Caso | Petición | HTTP | Efecto real | Veredicto |
|---|---|---|---|---|---|
| T1 | NoSQL: reseñas de otros productos | `GET /rest/products/1 || true/reviews` | 200 | reseñas del producto 1: 3; con la inyección: 0 | **PROTEGIDO** |
| T2 | NoSQL: todos los pedidos | `GET /rest/track-order/x'||'1'=='1` | 200 | pedidos devueltos: 1 | **PROTEGIDO** |
| T3 | NoSQL: modificar todas las reseñas | `PATCH /rest/products/reviews {id:{$ne:-1}}` | 403 | reseñas modificadas: 0 | **PROTEGIDO** |
| T4 | Reseña de otra cuenta | `PATCH /rest/products/reviews {id:<reseña de A>} (B)` | 403 | texto alterado: no | **PROTEGIDO** |
| T5 | SSRF hacia un servicio interno | `POST /profile/image/url imageUrl=http://juice-waf:8080/…` | 400 | ver marca ssrf-sonda-1795585133 en el log de acceso del WAF (lo comprueba el ejecutor) | **PENDIENTE DE LOG** |
| T6 | CSRF: perfil con Origin ajeno | `POST /profile (cookie, Origin: https://atacante.example)` | 403 | nombre cambiado: no | **PROTEGIDO** |
| T6b | Control: perfil sin Origin ajeno (uso legítimo) | `POST /profile (cookie)` | 302 | nombre cambiado: sí | **PROTEGIDO** |
| T7 | XXE: entidad externa con archivo local | `POST /file-upload (xxe.xml)` | 410 | entidad resuelta en la respuesta: no; en el servidor: ver la línea con xxe-sonda-1795585133 en el log de la app ("&x;" = no resuelta) | **PENDIENTE DE LOG** |
| T8 | 5xx con mensaje interno de la BD | `POST /api/Feedbacks (UserId inexistente)` | 500 | cuerpo: {"status":"error","message":"Internal server error"} | **PROTEGIDO** |
| T9 | Quejas de otras cuentas | `GET /api/Complaints (B)` | 403 | queja de A visible: no | **PROTEGIDO** |
| T10 | Reciclajes sin sesión y en lote | `GET /api/Recycles/[1..10] (sin token)` | 403 | registros devueltos: 0 | **PROTEGIDO** |

**Resultado parcial: 0 VULNERABLE, 9 PROTEGIDO, 2 pendientes de log o no concluyentes.**

## Comprobación en logs del contenedor (2026-11-24T23:39:40-06:00)
- T5 SSRF: 0 → **PROTEGIDO**
- T7 XXE: 0 → **PROTEGIDO**
