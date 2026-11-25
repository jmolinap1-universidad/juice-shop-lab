# A12 — BOLA/IDOR entre dos cuentas (validar-cloud)

Ejecutado: 2026-11-25T00:06:42-06:00 · Objetivo: https://juice-lab-masi-staging.onrender.com (instancia propia, aislada)

| Campo | Valor |
|---|---|
| Cuenta A (víctima) | bola_a_1795586798@juice-sh.op (basket id 9) |
| Cuenta B (atacante) | bola_b_1795586798@juice-sh.op (basket id 10) |
| Petición cruzada | GET /rest/basket/9 con token de B |
| HTTP cruzado | 403 |
| HTTP propio (control) | 200 |
| Clase / CWE / OWASP | N / CWE-639 / A01 (API1:2023 BOLA) |
| Veredicto | **MITIGADO/NEGATIVO** |
| Detalle | B no obtuvo la cesta de A (cross HTTP 403). Recurso protegido o no explotable en esta ruta. |

Esperado (si fuera seguro): B debe recibir 401/403 o solo su propia cesta.
Observado: ver cross-read.json y own-read.json (respuestas saneadas; datos ficticios de laboratorio).

> Limitación: prueba de lectura de cesta por id. No generaliza a todos los objetos de la app.
