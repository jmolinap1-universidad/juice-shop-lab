# CodeQL — resultados en GitHub code scanning (consultados el 2026-11-25)

**Origen:** pestaña *Security › Code scanning* del repositorio, filtro `is:open tool:CodeQL`, consultada con la sesión del equipo
(los resultados de code scanning no son públicos; la consulta se hizo leyendo la página, sin modificar alertas).
**Análisis:** job «SAST – CodeQL» de `.github/workflows/devsecops.yml` (`github/codeql-action` v3, JavaScript/TypeScript) sobre
`app/` = OWASP Juice Shop v20.3.0 **original** (`f189f5212`), rama `main`; última ejecución: run 45665962666 (commit `8b3e422`,
success). El análisis corresponde a la **línea base vulnerable**: la variante corregida se construye fuera del árbol versionado
(`app-hardened/build/`, ignorado) y no la analiza CodeQL. El artefacto `codeql` (SARIF) existe en la ejecución, pero su descarga
exige autenticación y no se versiona.

| Severidad | Alertas abiertas |
|---|---|
| Critical | 7 |
| High | 72 |
| Medium | 14 |
| **Total** | **93** (0 cerradas) |

| Regla CodeQL | Alertas |
|---|---|
| Missing rate limiting | 33 |
| Uncontrolled data used in path expression | 9 |
| Database query built from user-controlled sources | 7 |
| Information exposure through a stack trace | 7 |
| Remote property injection | 5 |
| User-controlled bypass of security check | 4 |
| Clear-text logging of sensitive information | 3 |
| Incomplete string escaping or encoding | 3 |
| Sensitive data read from GET request | 3 |
| Code injection | 2 |
| Type confusion through parameter tampering | 2 |
| Template Object Injection | 2 |
| Incomplete URL substring sanitization (pruebas) | 2 |
| Potential file system race condition | 2 |
| Server-side request forgery, Polynomial regular expression, Insecure randomness, Use of password hash with insufficient computational effort, Missing CSRF middleware, Server-side URL redirect, Prototype-polluting assignment, Log injection, Network data written to file | 1 cada una (9) |

**Relación con el modelo de amenazas:** las alertas coinciden con T01/T02 (consultas construidas con datos del usuario), T09
(*code injection*), T11 (SSRF), T15 (redirección), T16 (falta de limitación de intentos: 33 rutas), T05 (hash débil) y la falta de
CSRF corregida por el parche 12. Son resultados del código **original**; su tratamiento está en los parches 01-14 y en el WAF.
