# Casos de ataque Fase 4 — objetivo http://127.0.0.1:3000 (antes)

Ejecutado: 2026-11-03T23:24:31-06:00

| ID | Caso | CWE | Veredicto | Detalle |
|---|---|---|---|---|
| A1 | SQLi bypass de login | CWE-89 | **VULNERABLE** | Autenticado sin credenciales;  |
| A2 | SQLi UNION (volcado de Users) | CWE-89 | **VULNERABLE** | Se obtienen email y hash MD5 de usuarios |
| A3 | SQLi enumeración de esquema | CWE-89 | **VULNERABLE** | sqlite_master revela DDL de las tablas |
| A4 | Listado de directorios | CWE-548 | **VULNERABLE** | Navegables: /ftp /encryptionkeys /support/logs |
| A5 | Acceso a documento interno (/ftp) | CWE-22 | **VULNERABLE** | acquisitions.md descargado (HTTP 200) |
| A6 | /metrics sin autenticación | CWE-200 | **VULNERABLE** | Métricas Prometheus accesibles (HTTP 200) |
| A7 | Asignación masiva (role=admin) | CWE-915 | **VULNERABLE** | Usuario creado con role=admin |
| A8 | CORS permisivo | CWE-942 | **VULNERABLE** | ACAO refleja/permite origen arbitrario |
| A9 | Cabeceras de seguridad | CWE-693 | **VULNERABLE** | Ausentes: content-security-policy strict-transport-security |
| A10 | Fuerza bruta en login | CWE-307 | **VULNERABLE** | 12 intentos sin 429: 401 401 401 401 401 401 401 401 401 401 401 401 |
| A11 | Material criptográfico expuesto | CWE-798 | **VULNERABLE** | jwt.pub servido en /encryptionkeys (HTTP 200) |

**Resultado:** 11 VULNERABLE / 0 MITIGADO de 11 casos.
