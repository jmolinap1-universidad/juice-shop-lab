# JWT: rechazo de algoritmos débiles (parche 11: express-jwt 8.5.1 + jsonwebtoken 9.0.3 + jws 4.0.1, RS256 fijo) — 2026-11-23
Red interna, directo a la app (sin WAF). Los tokens se generan en memoria y no se registran.

| Token | Expectativa | HTTP en GET /api/Users |
|---|---|---|
| Legítimo RS256 (control) | 200 | 200 |
| alg=none, sin firma, role=admin | 401 | 401 |
| HS256 firmado con la clave PÚBLICA como secreto (confusión de algoritmo), role=admin | 401 | 401 |
