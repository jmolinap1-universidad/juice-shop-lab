# Casos de ataque Fase 4 — objetivo http://juice-hardened:3000 (03b-rasp-a-siem)

Ejecutado: 2026-11-10T23:16:57-06:00

> **Clase:** E=explotación demostrada · X=exposición observada · C=configuración insegura · N=ausencia de control.
> **Veredicto** VULNERABLE = la condición se detectó (no implica explotación); la clase indica el tipo real del hallazgo.

| ID | Caso | Clase | CWE | Veredicto | Detalle |
|---|---|---|---|---|---|
| A1 | SQLi bypass de login | E | CWE-89 | **MITIGADO** | Sin token (HTTP <html>
  <head>
    <meta charset='utf-8) |
| A2 | SQLi UNION (volcado de Users) | E | CWE-89 | **MITIGADO** | Sin datos de Users en la respuesta |
| A3 | SQLi enumeración de esquema | E | CWE-89 | **MITIGADO** | Sin DDL en la respuesta |
| A4 | Listado de directorios | X | CWE-548 | **VULNERABLE** | Navegables: /ftp /encryptionkeys /support/logs |
| A5 | Exposición de documento interno (/ftp) | X | CWE-538 | **VULNERABLE** | acquisitions.md descargado por acceso directo (HTTP 200); no es traversal |
| A6 | /metrics sin autenticación | X | CWE-200 | **VULNERABLE** | Métricas Prometheus accesibles (HTTP 200) |
| A7 | Asignación masiva (role=admin) | E | CWE-915 | **VULNERABLE** | Usuario creado con role=admin |
| A8 | CORS permisivo (configuración) | C | CWE-942 | **VULNERABLE** | ACAO:* permisivo (config insegura); no demuestra robo de datos autenticados |
| A9 | Cabeceras de seguridad | C | CWE-693 | **VULNERABLE** | Ausentes: content-security-policy strict-transport-security |
| A10 | Fuerza bruta en login | N | CWE-307 | **VULNERABLE** | 12 intentos sin 429: 401 401 401 401 401 401 401 401 401 401 401 401 |
| A11 | Clave pública JWT servida | X | CWE-200 | **VULNERABLE** | jwt.pub (clave PÚBLICA) servida HTTP 200; riesgo real = clave privada embebida en código (SAST) |

**Resultado:** 8 VULNERABLE / 3 MITIGADO de 11 casos (A1-A11). A12 BOLA/IDOR: ver evidence/fase-6/validacion-2026-11-10/03b-rasp-a-siem/bola/.
