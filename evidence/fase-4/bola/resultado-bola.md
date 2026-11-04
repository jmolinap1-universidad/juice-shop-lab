# A12 — BOLA/IDOR entre dos cuentas (riesgo inherente)

Ejecutado: 2026-11-04T14:02:41-06:00 · Objetivo: http://127.0.0.1:3000 (instancia propia, aislada)

| Campo | Valor |
|---|---|
| Cuenta A (víctima) | bola_a_1793822559@juice-sh.op (basket id 6) |
| Cuenta B (atacante) | bola_b_1793822559@juice-sh.op (basket id 7) |
| Petición cruzada | GET /rest/basket/6 con token de B |
| HTTP cruzado | 200 |
| HTTP propio (control) | 200 |
| CWE / OWASP | CWE-639 / A01 (API1:2023 BOLA) |
| Veredicto | **VULNERABLE** |
| Detalle | Usuario B (bid=7) leyó la cesta de A (bid=6) con su propio token; HTTP 200. BOLA confirmado. |

Esperado (si fuera seguro): B debe recibir 401/403 o solo su propia cesta.
Observado: ver cross-read.json y own-read.json (respuestas saneadas; datos ficticios de laboratorio).

> Limitación: prueba de lectura de cesta por id. No generaliza a todos los objetos de la app.
