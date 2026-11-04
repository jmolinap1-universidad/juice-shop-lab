# Casos de ataque Fase 4 — objetivo http://127.0.0.1:3000 (inherente-2026-11-04)

Ejecutado: 2026-11-04T14:01:59-06:00

| ID | Caso | CWE | Veredicto | Detalle |
|---|---|---|---|---|
| A1 | SQLi bypass de login | CWE-89 | **VULNERABLE** | Autenticado sin credenciales;  |
| A2 | SQLi UNION (volcado de Users) | CWE-89 | **VULNERABLE** | Se obtienen email y hash MD5 de usuarios |
| A3 | SQLi enumeración de esquema | CWE-89 | **VULNERABLE** | sqlite_master revela DDL de las tablas |
| A4 | Listado de directorios | CWE-548 | **VULNERABLE** | Navegables: /ftp /encryptionkeys /support/logs |
| A5 | Exposición de documento interno (/ftp) | CWE-538 | **VULNERABLE** | acquisitions.md descargado por acceso directo (HTTP 200); no es traversal |
| A6 | /metrics sin autenticación | CWE-200 | **VULNERABLE** | Métricas Prometheus accesibles (HTTP 200) |
| A7 | Asignación masiva (role=admin) | CWE-915 | **VULNERABLE** | Usuario creado con role=admin |
| A8 | CORS permisivo (configuración) | CWE-942 | **VULNERABLE** | ACAO:* permisivo (config insegura); no demuestra robo de datos autenticados |
| A9 | Cabeceras de seguridad | CWE-693 | **VULNERABLE** | Ausentes: content-security-policy strict-transport-security |
| A10 | Fuerza bruta en login | CWE-307 | **VULNERABLE** | 12 intentos sin 429: 401 401 401 401 401 401 401 401 401 401 401 401 |
| A11 | Clave pública JWT servida | CWE-200 | **VULNERABLE** | jwt.pub (clave PÚBLICA) servida HTTP 200; riesgo real = clave privada embebida en código (SAST) |

**Resultado:** 11 VULNERABLE / 0 MITIGADO de 11 casos (A1-A11). A12 BOLA/IDOR: ver evidence/fase-4/bola/.
