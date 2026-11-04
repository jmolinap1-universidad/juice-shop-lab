# Fase 4 – Pruebas de seguridad y superficie de ataque (riesgo inherente)

**Estado:** Implementado y verificado. Todas las pruebas se ejecutaron contra la instancia **propia** del
laboratorio en `http://127.0.0.1:3000` (OWASP Juice Shop v20.3.0). Ninguna prueba se dirigió a la demo pública
ni a terceros (regla de alcance, CLAUDE.md §2).

> Etiquetas: **[V]** implementado y verificado · **[S]** simulado · **[P]** propuesto.
> El resultado de esta fase es el **riesgo inherente**: la aplicación sin controles adicionales.
> En la Fase 6 se repiten exactamente las mismas pruebas (mismo `security/attacks/run.sh` y ZAP) contra el
> entorno endurecido para obtener el **riesgo residual**.

## 1. Metodología y herramientas
| Tipo de prueba | Herramienta (versión) | Evidencia |
|---|---|---|
| Caja negra (DAST automatizado) | OWASP ZAP 2.17.0, `zap-baseline.py` | `evidence/fase-4/zap/` (JSON, HTML) y GitHub Actions |
| Caja gris (con conocimiento del código) | `security/attacks/run.sh` (curl + payloads dirigidos) | `evidence/fase-4/antes/` (request/response por caso) |
| Caja blanca (revisión de código) | Semgrep + revisión manual (Fase 1 y 3) | `evidence/fase-3/sast/`, `docs/fase-1/` |
| Manual (complemento) | Burp Suite Community | **[P]** a cargo del equipo; capturas en `evidence/fase-4/burp/` |

El DAST se ejecuta en dos lugares: localmente (este informe) y en el job `dast` de GitHub Actions contra un
contenedor efímero, como evidencia reproducible e independiente del equipo.

## 2. Superficie de ataque (enumerada desde `app/server.ts`)
- **102** rutas declaradas: 50 GET, 40 POST, 13 PUT, 5 DELETE, 1 PATCH.
- **79** endpoints REST/API únicos bajo `/rest`, `/api`, `/b2b`.
- **14 modelos** expuestos como API CRUD automática (`finale.resource`, `server.ts:511-528`):
  User, Product, Feedback, BasketItem, Challenge, Complaint, Recycle, SecurityQuestion, SecurityAnswer,
  Address, PrivacyRequest, Card, Quantity, Hint.
- **Puntos de entrada de archivos:** `/file-upload` (ZIP/XML/YAML), `/profile/image/url` (SSRF), `/rest/memories`.
- **Rutas estáticas con listado:** `/ftp`, `/encryptionkeys`, `/support/logs`, `/.well-known`, `/infrastructure`.
- **Diagnóstico sin autenticación:** `/metrics` (Prometheus).
- **Autenticación:** JWT RS256 con clave privada embebida; sin rate limit en `/rest/user/login`.

## 3. Resultados de los casos de ataque (caja gris) — riesgo inherente
Fuente: `evidence/fase-4/antes/resumen-ataques.md`. Resultado global: **11 VULNERABLE / 0 MITIGADO de 11**.

| ID | Caso | CWE | OWASP 2025 | Veredicto | Evidencia |
|---|---|---|---|---|---|
| A1 | Bypass de login por SQLi (`' OR 1=1--`) → sesión de admin | CWE-89 | A05 | **VULNERABLE** | JWT con `id:1, role:admin` — `a1-req-resp.txt`, `a1-sqli-login.json` |
| A2 | SQLi UNION: volcado de `Users` (email + hash MD5) | CWE-89 | A05 | **VULNERABLE** | admin→`0192023a7bbd7325…` — `a2-sqli-union-search.json` |
| A3 | SQLi: enumeración de esquema (`sqlite_master`) | CWE-89 | A05 | **VULNERABLE** | DDL de todas las tablas — `a3-sqli-schema.json` |
| A4 | Listado de directorios `/ftp`, `/encryptionkeys`, `/support/logs` | CWE-548 | A02 | **VULNERABLE** | `a4-directory-listing.txt` |
| A5 | Acceso a documento interno `/ftp/acquisitions.md` | CWE-22 | A01 | **VULNERABLE** | `a5-acquisitions.md` (HTTP 200) |
| A6 | `/metrics` Prometheus sin autenticación | CWE-200 | A02 | **VULNERABLE** | `a6-metrics.txt` |
| A7 | Asignación masiva: registro con `role:admin` | CWE-915 | A01 | **VULNERABLE** | `a7-mass-assignment.json` |
| A8 | CORS permisivo (origen arbitrario) | CWE-942 | A02 | **VULNERABLE** | `a8-cors-headers.txt` |
| A9 | Cabeceras de seguridad ausentes (CSP, HSTS) | CWE-693 | A02 | **VULNERABLE** | `a9-security-headers.txt` |
| A10 | Fuerza bruta en login sin bloqueo (12 intentos, sin 429) | CWE-307 | A07 | **VULNERABLE** | `a10-bruteforce-login.txt` |
| A11 | Material criptográfico expuesto (`/encryptionkeys/jwt.pub`) | CWE-798 | A04 | **VULNERABLE** | `a11-jwt-key.txt` |

Correlación con la clave privada embebida (`lib/insecurity.ts:21`, hallazgo SAST `hardcoded-private-key`):
conocer la clave + A11 permite **forjar JWT válidos de cualquier usuario** sin SQLi. Se documenta como vector
pero no se automatiza el forjado para no manejar la clave en el repositorio.

## 4. Resultados DAST (caja negra, OWASP ZAP baseline)
Fuente: `evidence/fase-4/zap/resumen-zap.md`. Totales del baseline: **FAIL 0 · WARN-NEW 7 · PASS 61**
(el baseline pasivo no marca FAIL; las alertas de riesgo se listan abajo).

| Alerta ZAP | Riesgo | CWE | Instancias | Coincide con |
|---|---|---|---|---|
| Content Security Policy (CSP) no establecida | Medium | 693 | 5 | A9 |
| Cross-Domain Misconfiguration (CORS) | Medium | 264 | 5 | A8 |
| Cross-Origin-Embedder-Policy ausente | Low | 693 | 5 | A9 |
| Cross-Origin-Opener-Policy ausente | Low | 693 | 5 | A9 |
| Dangerous JS Functions | Low | 749 | 2 | T13 (XSS) |
| Deprecated Feature Policy Header | Low | 16 | 5 | A9 |
| Modern Web Application / contenido cacheable | Info | — | 11 | — |

El baseline es un escaneo **pasivo**; SQLi, IDOR y mass assignment (A1-A3, A7) requieren pruebas activas y se
cubren con `security/attacks/run.sh` (caja gris). ZAP confirma de forma independiente CSP (A9) y CORS (A8).

## 5. Casos de abuso (abuse cases)
| # | Actor | Caso de abuso | Prueba que lo demuestra |
|---|---|---|---|
| AB1 | Atacante anónimo | Iniciar sesión como administrador sin contraseña | A1 |
| AB2 | Atacante anónimo | Robar credenciales de todos los usuarios y descifrar contraseñas MD5 | A2 + MD5 (T05) |
| AB3 | Atacante anónimo | Escalar privilegios creando una cuenta de administrador | A7 |
| AB4 | Atacante anónimo | Leer documentos internos y claves del servidor | A4, A5, A11 |
| AB5 | Atacante anónimo | Reconocer el sistema vía métricas y esquema de BD | A6, A3 |
| AB6 | Sitio malicioso | Leer datos de la víctima autenticada desde otro origen (CORS) | A8 |
| AB7 | Atacante anónimo | Adivinar contraseñas por fuerza bruta sin ser bloqueado | A10 |

## 6. Conclusión de la fase
El laboratorio confirma **riesgo inherente alto/crítico**: 11/11 vectores explotables, incluido el compromiso
total (admin) por dos vías independientes (SQLi y asignación masiva). Estos resultados alimentan la matriz de la
Fase 6, donde los mismos ataques se reejecutan contra el entorno endurecido (WAF + código corregido + cabeceras)
para medir el riesgo residual y el tratamiento ISO/IEC 27005.

## Nota de aislamiento
Los reportes HTML/JSON de ZAP referencian `host.docker.internal:3000`, que resuelve al `127.0.0.1` del equipo (el contenedor de ZAP accede al laboratorio del host). No hay exposición externa.
