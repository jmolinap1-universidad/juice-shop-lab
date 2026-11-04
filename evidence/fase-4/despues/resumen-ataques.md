# Casos de ataque Fase 4 — objetivo http://127.0.0.1:8080 (despues)

Ejecutado: 2026-11-03T23:52:03-06:00

| ID | Caso | CWE | Veredicto | Detalle |
|---|---|---|---|---|
| A1 | SQLi bypass de login | CWE-89 | **MITIGADO** | Sin token (HTTP <html>
<head><title>403 Forbidden</titl) |
| A2 | SQLi UNION (volcado de Users) | CWE-89 | **MITIGADO** | Sin datos de Users en la respuesta |
| A3 | SQLi enumeración de esquema | CWE-89 | **MITIGADO** | Sin DDL en la respuesta |
| A4 | Listado de directorios | CWE-548 | **MITIGADO** | Sin listados navegables |
| A5 | Acceso a documento interno (/ftp) | CWE-22 | **MITIGADO** | HTTP 403 |
| A6 | /metrics sin autenticación | CWE-200 | **MITIGADO** | HTTP 403 |
| A7 | Asignación masiva (role=admin) | CWE-915 | **MITIGADO** | role no aceptado () |
| A8 | CORS permisivo | CWE-942 | **MITIGADO** | Sin ACAO abierto |
| A9 | Cabeceras de seguridad | CWE-693 | **MITIGADO** | Presentes las 4 cabeceras clave |
| A10 | Fuerza bruta en login | CWE-307 | **MITIGADO** | Aparece HTTP 429: 401 401 401 401 429 429 429 429 429 429 429 429 |
| A11 | Material criptográfico expuesto | CWE-798 | **MITIGADO** | HTTP 403 |

**Resultado:** 0 VULNERABLE / 11 MITIGADO de 11 casos.
