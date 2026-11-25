# Falso positivo socket.io (regla 920420) — después de EX-2 (2026-11-24T22:56:15-06:00)
Imagen local juice-cloud:local sha256:5bb3c898117c9867af8923f3caaf7a0ae6c8d0015af95295629778b872253eda; antes del cambio las tres primeras daban 403.

| Petición | Esperado | Obtenido |
|---|---|---|
| GET handshake socket.io | 200 | 200 |
| POST text/plain '40' (conexión legítima) | 200 | 403 |
| POST text/plain a /api/Feedbacks (fuera del alcance) | 403 | 403 |
| POST application/x-www-form-urlencoded con SQLi a /socket.io/ (argumentos sí analizados) | 403 | 403 |
| GET /socket.io/ con SQLi en la query | 403 | 403 |
