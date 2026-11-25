# Falso positivo socket.io (regla 920420) — después de EX-2 en REQUEST-900 (2026-11-24T22:58:19-06:00)
Imagen local juice-cloud:local sha256:5fc2f4d04b141de7637d4213b090647075ab354979cfc88b1e0f83bf15b52c0b. Antes del cambio las tres primeras daban 403 (intento1-exclusion-tras-crs.md: con la exclusión cargada después del CRS seguía en 403).

| Petición | Esperado | Obtenido |
|---|---|---|
| GET handshake socket.io | 200 | 200 |
| POST text/plain '40' (conexión legítima) | 200 | 200 |
| POST text/plain a /api/Feedbacks (fuera del alcance) | 403 | 403 |
| POST form-urlencoded con SQLi a /socket.io/ (argumentos sí analizados) | 403 | 403 |
| GET /socket.io/ con SQLi en la query | 403 | 403 |
