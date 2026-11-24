# A12 — BOLA/IDOR entre dos cuentas (validar-cloud)

Ejecutado: 2026-11-23T23:16:50-06:00 · Objetivo: http://127.0.0.1:8090 (instancia propia, aislada)

| Campo | Valor |
|---|---|
| Cuenta A (víctima) | bola_a_1795497409@juice-sh.op (basket id ) |
| Cuenta B (atacante) | bola_b_1795497409@juice-sh.op (basket id ) |
| Petición cruzada | GET /rest/basket/ con token de B |
| HTTP cruzado | 302 |
| HTTP propio (control) | 302 |
| Clase / CWE / OWASP | N / CWE-639 / A01 (API1:2023 BOLA) |
| Veredicto | **MITIGADO/NEGATIVO** |
| Detalle | B no obtuvo la cesta de A (cross HTTP 302). Recurso protegido o no explotable en esta ruta. |

Esperado (si fuera seguro): B debe recibir 401/403 o solo su propia cesta.
Observado: ver cross-read.json y own-read.json (respuestas saneadas; datos ficticios de laboratorio).

> Limitación: prueba de lectura de cesta por id. No generaliza a todos los objetos de la app.
