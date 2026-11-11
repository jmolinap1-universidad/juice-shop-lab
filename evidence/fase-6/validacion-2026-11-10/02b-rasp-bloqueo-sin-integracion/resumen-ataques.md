# Casos de ataque Fase 4 — objetivo http://juice-hardened:3000 (02b-rasp-bloqueo-sin-integracion)

Ejecutado: 2026-11-10T22:59:10-06:00

> **Clase:** E=explotación demostrada · X=exposición observada · C=configuración insegura · N=ausencia de control.
> **Veredicto** VULNERABLE = la condición se detectó (no implica explotación); la clase indica el tipo real del hallazgo.

| ID | Caso | Clase | CWE | Veredicto | Detalle |
|---|---|---|---|---|---|
| A1 | SQLi bypass de login | E | CWE-89 | **MITIGADO** | Sin token (HTTP ) |
| A2 | SQLi UNION (volcado de Users) | E | CWE-89 | **MITIGADO** | Sin datos de Users en la respuesta |
| A3 | SQLi enumeración de esquema | E | CWE-89 | **MITIGADO** | Sin DDL en la respuesta |
| A4 | Listado de directorios | X | CWE-548 | **MITIGADO** | Sin listados navegables |
| A5 | Exposición de documento interno (/ftp) | X | CWE-538 | **MITIGADO** | HTTP 000 |
| A6 | /metrics sin autenticación | X | CWE-200 | **MITIGADO** | HTTP 000 |
| A7 | Asignación masiva (role=admin) | E | CWE-915 | **MITIGADO** | role no aceptado () |
| A8 | CORS permisivo (configuración) | C | CWE-942 | **MITIGADO** | Sin ACAO abierto |
| A9 | Cabeceras de seguridad | C | CWE-693 | **VULNERABLE** | Ausentes: content-security-policy strict-transport-security x-content-type-options x-frame-options |
| A10 | Fuerza bruta en login | N | CWE-307 | **VULNERABLE** | 12 intentos sin 429: 000 000 000 000 000 000 000 000 000 000 000 000 |
| A11 | Clave pública JWT servida | X | CWE-200 | **MITIGADO** | HTTP 000 |

**Resultado:** 2 VULNERABLE / 9 MITIGADO de 11 casos (A1-A11). A12 BOLA/IDOR: ver evidence/fase-6/validacion-2026-11-10/02b-rasp-bloqueo-sin-integracion/bola/.
