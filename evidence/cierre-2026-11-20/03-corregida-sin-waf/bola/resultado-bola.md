# A12 — BOLA/IDOR entre dos cuentas (03-corregida-sin-waf)

Ejecutado: 2026-11-21T06:18:37+00:00 · Objetivo: http://juice-corregida:3000 (instancia propia, aislada)

| Campo | Valor |
|---|---|
| Cuenta A (víctima) | bola_a_1795241916@juice-sh.op (basket id 8) |
| Cuenta B (atacante) | bola_b_1795241916@juice-sh.op (basket id 9) |
| Petición cruzada | GET /rest/basket/8 con token de B |
| HTTP cruzado | 403 |
| HTTP propio (control) | 200 |
| Clase / CWE / OWASP | N / CWE-639 / A01 (API1:2023 BOLA) |
| Veredicto | **MITIGADO/NEGATIVO** |
| Detalle | B no obtuvo la cesta de A (cross HTTP 403). Recurso protegido o no explotable en esta ruta. |

Esperado (si fuera seguro): B debe recibir 401/403 o solo su propia cesta.
Observado: ver cross-read.json y own-read.json (respuestas saneadas; datos ficticios de laboratorio).

> Limitación: prueba de lectura de cesta por id. No generaliza a todos los objetos de la app.
