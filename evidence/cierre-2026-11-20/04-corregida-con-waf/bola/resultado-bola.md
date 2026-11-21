# A12 — BOLA/IDOR entre dos cuentas (04-corregida-con-waf)

Ejecutado: 2026-11-21T00:26:15-06:00 · Objetivo: http://127.0.0.1:8088 (instancia propia, aislada)

| Campo | Valor |
|---|---|
| Cuenta A (víctima) | bola_a_1795242373@juice-sh.op (basket id 12) |
| Cuenta B (atacante) | bola_b_1795242373@juice-sh.op (basket id 13) |
| Petición cruzada | GET /rest/basket/12 con token de B |
| HTTP cruzado | 403 |
| HTTP propio (control) | 200 |
| Clase / CWE / OWASP | N / CWE-639 / A01 (API1:2023 BOLA) |
| Veredicto | **MITIGADO/NEGATIVO** |
| Detalle | B no obtuvo la cesta de A (cross HTTP 403). Recurso protegido o no explotable en esta ruta. |

Esperado (si fuera seguro): B debe recibir 401/403 o solo su propia cesta.
Observado: ver cross-read.json y own-read.json (respuestas saneadas; datos ficticios de laboratorio).

> Limitación: prueba de lectura de cesta por id. No generaliza a todos los objetos de la app.
