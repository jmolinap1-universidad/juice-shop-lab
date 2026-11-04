# Fase 4 – Pruebas de seguridad y superficie de ataque (riesgo inherente)

**Estado:** Implementado y verificado. Todas las pruebas se ejecutaron contra la instancia **propia** del
laboratorio en `http://127.0.0.1:3000` (OWASP Juice Shop v20.3.0). Ninguna prueba se dirigió a la demo pública
ni a terceros (regla de alcance, CLAUDE.md §2).

> Etiquetas: **[V]** implementado y verificado · **[S]** simulado · **[P]** propuesto.
> El resultado de esta fase es el **riesgo inherente**: la aplicación sin controles adicionales.
> En la Fase 6 se repiten exactamente las mismas pruebas (mismo `security/attacks/run.sh` y ZAP) contra el
> entorno endurecido para obtener el **riesgo residual**.

## 1. Metodología y herramientas
Se separan tres enfoques, cada uno con su evidencia y sus límites. **No** se mezcla el conocimiento del código
usado en caja gris/blanca con la prueba de caja negra.

| Enfoque | Herramienta (versión) | Conocimiento previo | Evidencia |
|---|---|---|---|
| Caja negra (DAST automatizado, **pasivo**) | OWASP ZAP 2.17.0, `zap-baseline.py` | Ninguno del código; solo la URL | `evidence/fase-4/zap/` (JSON, HTML) y GitHub Actions job `dast` |
| Caja negra (reconocimiento) | Nmap 7.95 | Ninguno | `evidence/fase-4/nmap-127-3000.txt` |
| Caja gris (con conocimiento del código) | `security/attacks/run.sh` (curl + payloads dirigidos) | Rutas y modelos leídos de `app/` | `evidence/fase-4/antes/` (request/response por caso) |
| Caja blanca (revisión de código) | Semgrep 1.181.1 + revisión manual | Código fuente completo | `evidence/fase-3/sast/`, `docs/fase-1/` |
| Manual (complemento) | Burp Suite Community | — | **[P]** a cargo del equipo; capturas en `evidence/fase-4/burp/` |

**Importante sobre el alcance de ZAP:** el `zap-baseline.py` es un escaneo **pasivo**. Observa respuestas y
cabeceras pero **no** ejecuta inyección activa; por tanto confirma de forma independiente cabeceras (A9) y CORS
(A8), pero **no** demuestra por sí mismo SQLi, IDOR ni asignación masiva. Esos vectores se prueban activamente en
caja gris (`run.sh`). No se atribuye a ZAP una cobertura que no realiza.

## 2. Superficie de ataque (enumerada desde `app/server.ts`)
Conteo **reproducible** (una sola línea, resultado determinista):

```bash
grep -cE "app\.(get|post|put|delete|patch)\(('|\`)/" app/server.ts   # => 109
```

- **109 rutas** declaradas con path literal en `server.ts`: **50 GET + 40 POST + 13 PUT + 5 DELETE + 1 PATCH**
  (el total coincide con la suma: 50+40+13+5+1 = 109). *Corrige el valor "102" de una versión previa, que no
  cuadraba con su propio desglose.*
- **+1 GET adicional** registra dos alias mediante arreglo (`/.well-known/security.txt` y `/security.txt`,
  `server.ts:215`); no se incluye en el conteo de path literal anterior y se documenta aparte para no
  distorsionar el método.
- **~81** rutas bajo `/rest`, `/api`, `/b2b` (medidas con
  `grep -oE "('|\`)/(rest|api|b2b)[^'\`,) ]*" app/server.ts | sort -u | wc -l`); es una cota superior porque
  algunas difieren solo por parámetro de ruta.
- **14 modelos** expuestos como API CRUD automática (`finale.resource`, `server.ts:511-528`):
  User, Product, Feedback, BasketItem, Challenge, Complaint, Recycle, SecurityQuestion, SecurityAnswer,
  Address, PrivacyRequest, Card, Quantity, Hint.
- **Puntos de entrada de archivos:** `/file-upload` (ZIP/XML/YAML), `/profile/image/url` (SSRF), `/rest/memories`.
- **Rutas estáticas con listado:** `/ftp`, `/encryptionkeys`, `/support/logs`, `/.well-known`, `/infrastructure`.
- **Diagnóstico sin autenticación:** `/metrics` (Prometheus).
- **Autenticación:** JWT RS256; sin rate limit en `/rest/user/login`. La clave privada usada para firmar está
  **embebida en el código** (`lib/insecurity.ts`), hallazgo de caja blanca (§3.1), distinto de la clave pública
  servida en `/encryptionkeys` (que por diseño es pública).
- **Webhooks:** **no aplica.** No se identificaron endpoints de webhook entrantes/salientes en `server.ts`.

## 3. Resultados de los casos de ataque — riesgo inherente
Fuente de datos crudos (sin modificar): `evidence/fase-4/antes/` (un archivo request/response por caso, ejecutado
2026-11-03). La tabla siguiente **clasifica honestamente** cada observación en una de cuatro categorías, para no
afirmar más de lo demostrado:

- **Explotación demostrada (E):** la prueba obtuvo un efecto de seguridad real (acceso, datos, privilegios).
- **Exposición observada (X):** un recurso/dato sensible resultó accesible (sin inferir impacto adicional).
- **Configuración insegura (C):** una cabecera/ajuste es permisivo (debilidad, sin explotación demostrada aquí).
- **Ausencia de control (N):** falta un control esperado (sin probar que el ataque haya tenido éxito).

| ID | Caso | Clase | CWE | OWASP 2025 | Qué demuestra la evidencia (y qué NO) | Evidencia |
|---|---|---|---|---|---|---|
| A1 | Bypass de login por SQLi → sesión de admin | **E** | CWE-89 | A05 | Se obtiene JWT con `id:1, role:admin` sin credenciales válidas. Explotación completa. | `a1-req-resp.txt`, `a1-sqli-login.json` |
| A2 | SQLi UNION: volcado de `Users` | **E** | CWE-89 | A05 | Se extraen email + hash MD5 de usuarios (admin `0192023a7bbd7325…`). | `a2-sqli-union-search.json` |
| A3 | SQLi: enumeración de esquema (`sqlite_master`) | **E** | CWE-89 | A05 | Se obtiene el DDL de las tablas. | `a3-sqli-schema.json` |
| A4 | Listado de directorios `/ftp`, `/encryptionkeys`, `/support/logs` | **X** | CWE-548 | A05 | El servidor devuelve índices navegables. Exposición de estructura. | `a4-directory-listing.txt` |
| A5 | Descarga de documento interno `/ftp/acquisitions.md` | **X** | **CWE-538** (exposición de archivo), **no** CWE-22 | A01 | HTTP 200 a un archivo listado. **No** es *path traversal*: es acceso directo a un recurso expuesto por el listado (A4). No se usó `../`. | `a5-acquisitions.md` |
| A6 | `/metrics` Prometheus sin autenticación | **X** | CWE-200 | A05 | Endpoint de diagnóstico accesible sin auth. | `a6-metrics.txt` |
| A7 | Asignación masiva: registro con `role:admin` | **E** | CWE-915 | A01 | Se crea un usuario con rol admin (escalada por parámetro no filtrado). Explotación. | `a7-mass-assignment.json` |
| A8 | CORS permisivo (`Access-Control-Allow-Origin: *`) | **C** | CWE-942 | A05 | La respuesta de un endpoint **público** trae `ACAO: *`. **No** demuestra lectura de datos autenticados de otro origen: con `ACAO: *` el navegador **no** envía credenciales, y el recurso probado no es sensible. Debilidad de configuración. | `a8-cors-headers.txt` |
| A9 | Cabeceras de seguridad ausentes (CSP, HSTS) | **C** | CWE-693 | A05 | Faltan `content-security-policy` y `strict-transport-security`. Confirmado también por ZAP. | `a9-security-headers.txt` |
| A10 | Login sin limitación de intentos | **N** | CWE-307 | A07 | 12 intentos → 12×HTTP 401 sin 429 ni bloqueo. Demuestra **ausencia de rate limiting**. **No** demuestra que se haya adivinado contraseña alguna. | `a10-bruteforce-login.txt` |
| A11 | Clave pública JWT servida en `/encryptionkeys/jwt.pub` | **X** (bajo) | **CWE-200** | A05 | HTTP 200 devuelve una clave **pública** RSA (servirla es, por diseño, aceptable). **No** es CWE-798 por sí sola. El riesgo real es la **clave privada embebida en código** (§3.1), hallazgo de caja blanca. | `a11-jwt-key.txt` |

Totales por clase: **Explotación demostrada: 4 (A1, A2, A3, A7)** · **Exposición observada: 4 (A4, A5, A6, A11)** ·
**Configuración insegura: 2 (A8, A9)** · **Ausencia de control: 1 (A10)**. Total: 11 observaciones registradas.

> **Nota de precisión (reemplaza la afirmación previa "11/11 vulnerable"):** las 11 pruebas **sí** registraron
> una debilidad cada una, pero solo **4** constituyen explotación demostrada de una vulnerabilidad. Las otras 7
> son exposiciones, configuraciones inseguras o ausencia de controles. En Fase 6 se mide cuántas de estas 11
> observaciones quedan mitigadas por los controles compensatorios (WAF + endurecimiento), sin afirmar que el
> código de Juice Shop haya quedado libre de vulnerabilidades.

### 3.1 Hallazgo de caja blanca: clave privada embebida (correlación con A11)
La clave **privada** RS256 usada para firmar los JWT está codificada en el código fuente
(`lib/insecurity.ts`; hallazgo SAST `hardcoded-private-key`, CWE-321/798). Conocerla permite **forjar JWT válidos
de cualquier usuario** sin SQLi. Es un hallazgo **distinto** de A11 (que solo sirve la clave pública). No se
automatiza el forjado ni se publica la clave privada en el repositorio (CLAUDE.md §5); se documenta como vector.

### 3.2 BOLA / IDOR entre usuarios (caja gris, dos cuentas)
Prueba específica de autorización a nivel de objeto, con **dos cuentas de laboratorio distintas** y datos
ficticios, para no confundir BOLA con la asignación masiva (A7). Resultado en §3.3 y evidencia en
`evidence/fase-4/bola/`. Se registra tanto el caso **positivo** (acceso indebido confirmado) como, si aplicara,
el **negativo** (recurso correctamente protegido), sin forzar un hallazgo.

### 3.3 Resultado BOLA/IDOR — **VULNERABLE confirmado**
Ejecución 2026-11-04 contra `127.0.0.1:3000` (caso A12 de `run.sh`). Evidencia:
`evidence/fase-4/bola/` (`resultado-bola.md`, `cross-read.json`, `own-read.json`).

| Campo | Valor |
|---|---|
| Cuenta A (víctima) | `bola_a_…@juice-sh.op` → cesta `id 6`, `UserId 26` |
| Cuenta B (atacante) | `bola_b_…@juice-sh.op` → cesta `id 7`, `UserId 27` |
| Petición | `GET /rest/basket/6` con el **token de B** |
| Esperado (si fuera seguro) | 401/403, o solo la cesta propia de B |
| **Observado** | **HTTP 200** devolviendo la cesta de A (`UserId:26`), distinta de la de B (`UserId:27`) |
| Veredicto | **VULNERABLE** — BOLA/IDOR (CWE-639, OWASP API1:2023 / A01) |

**Prueba:** la respuesta que recibió B incluye `"UserId":26` (propietario = A), mientras que su cesta propia es
`"UserId":27`. La aplicación **no verifica la propiedad del objeto** antes de servir `/rest/basket/:id`. Es un
BOLA genuino entre dos cuentas, **distinto** de la asignación masiva (A7). *Limitación:* probado sobre la lectura
de cesta por `id`; no se generaliza a todos los objetos de la API.

## 4. Resultados DAST (caja negra, OWASP ZAP baseline **pasivo**)
Fuente: `evidence/fase-4/zap/resumen-zap.md`. Totales del baseline: **FAIL 0 · WARN-NEW 7 · PASS 61**
(un baseline pasivo no marca FAIL; lista alertas de riesgo observadas pasivamente).

| Alerta ZAP | Riesgo | CWE | Instancias | Coincide con |
|---|---|---|---|---|
| Content Security Policy (CSP) no establecida | Medium | 693 | 5 | A9 |
| Cross-Domain Misconfiguration (CORS) | Medium | 264 | 5 | A8 |
| Cross-Origin-Embedder-Policy ausente | Low | 693 | 5 | A9 |
| Cross-Origin-Opener-Policy ausente | Low | 693 | 5 | A9 |
| Dangerous JS Functions | Low | 749 | 2 | T13 (XSS) |
| Deprecated Feature Policy Header | Low | 16 | 5 | A9 |
| Modern Web Application / contenido cacheable | Info | — | 11 | — |

El baseline es **pasivo**: SQLi, IDOR y mass assignment (A1-A3, A7, A12) requieren pruebas activas y se cubren en
caja gris. ZAP confirma de forma independiente CSP (A9) y CORS (A8).

## 5. Casos de abuso (abuse cases)
Redactados de acuerdo con la clase real de cada prueba (§3): un caso de abuso describe la **intención** del
atacante; la columna "demostrado por" indica qué se probó realmente y con qué alcance.

| # | Actor | Caso de abuso | Demostrado por | Alcance real |
|---|---|---|---|---|
| AB1 | Atacante anónimo | Iniciar sesión como administrador sin contraseña | A1 | Explotación completa |
| AB2 | Atacante anónimo | Robar credenciales de todos los usuarios y descifrar hashes MD5 | A2 + MD5 (T05) | Extracción demostrada; descifrado MD5 documentado como viable (hash público conocido) |
| AB3 | Atacante anónimo | Escalar privilegios creando cuenta de administrador | A7 | Explotación completa |
| AB4 | Usuario autenticado | Leer recursos de otro usuario (IDOR) | A12 (§3.3) | Según resultado registrado |
| AB5 | Atacante anónimo | Leer documentos internos y la clave pública del servidor | A4, A5, A11 | Exposición de archivos; la clave es pública |
| AB6 | Atacante anónimo | Reconocer el sistema vía métricas y esquema de BD | A6, A3 | Exposición + enumeración |
| AB7 | Sitio malicioso | Leer datos de la víctima autenticada desde otro origen | A8 | **No demostrado**: solo cabecera permisiva (ver A8) |
| AB8 | Atacante anónimo | Adivinar contraseñas por fuerza bruta sin ser bloqueado | A10 | **No demostrado el acierto**: solo ausencia de rate limiting |

## 6. Cobertura OWASP Web Top 10 — honesta por categoría
Para no atribuir cobertura completa, cada categoría se marca **Probado (explotación) / Revisado (sin
explotación) / No probado / No aplica**.

| OWASP 2025 | Estado | Base |
|---|---|---|
| A01 Broken Access Control | Probado | A5, A7, A12 (IDOR) |
| A02 Cryptographic Failures | Revisado | MD5 (T05), clave privada embebida (§3.1); sin explotación activa de descifrado |
| A03 Injection | Probado | A1, A2, A3 (SQLi) |
| A04 Insecure Design | Revisado | Modelado de amenazas Fase 1 |
| A05 Security Misconfiguration | Probado/Revisado | A4, A6, A8, A9, A11 |
| A06 Vulnerable Components | Revisado | SCA Fase 3 (Trivy/Grype/OSV) |
| A07 Auth Failures | Revisado | A10 (ausencia de rate limit); sin credential stuffing real |
| A08 Integrity Failures | No probado | — |
| A09 Logging/Monitoring Failures | No probado | Se aborda en Fase 6 (logs del WAF) |
| A10 SSRF | No probado | `/profile/image/url` identificado como superficie; no ejecutado |

## 7. Conclusión de la fase
El laboratorio confirma **riesgo inherente alto**: **4 vulnerabilidades explotadas** (compromiso total de admin
por dos vías independientes: SQLi y asignación masiva), más **7 debilidades** adicionales entre exposición de
información, configuración insegura y ausencia de controles. Estos resultados, con su clasificación honesta,
alimentan la matriz de la Fase 6, donde los mismos casos se reejecutan contra el entorno endurecido para medir el
riesgo residual y el tratamiento ISO/IEC 27005. No se afirma cobertura total del OWASP Top 10 ni que el código de
Juice Shop haya quedado corregido en esta fase.

## Nota de aislamiento
Los reportes HTML/JSON de ZAP referencian `host.docker.internal:3000`, que resuelve al `127.0.0.1` del equipo (el
contenedor de ZAP accede al laboratorio del host). No hay exposición externa.
