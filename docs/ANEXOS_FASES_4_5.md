# Anexos — Fases 4 y 5

> Apartado de **Anexos** del documento de Fases 4-5. Todas las evidencias referidas existen en el
> repositorio; su integridad se verifica con los hashes SHA-256 de `evidence/MANIFEST.sha256` y su
> trazabilidad (comando, versión de herramienta, resultado) consta en `evidence/bitacora.md`.
> Laboratorio ejecutado únicamente en `127.0.0.1` / red de Docker; nunca se atacó la demo pública ni terceros.

---

## Anexo A — Índice de figuras (capturas)

Ubicación: `docs/evidencias-fase4-5/img/`.

| Fig. | Archivo | Descripción | Fase |
|---|---|---|---|
| A.1 | `01-app-homepage.jpg` | Página principal de OWASP Juice Shop v20.3.0 en el laboratorio local (`127.0.0.1:3000`). | 4 |
| A.2 | `02-sqli-union-users.jpg` | Inyección SQL UNION en el buscador: volcado de la tabla `Users` (correos y hashes). | 4 |
| A.3 | `03-ftp-directory-listing.jpg` | Listado del directorio interno `/ftp` (exposición de documentos). | 4 |
| A.4 | `04-encryptionkeys-listing.jpg` | Listado de `/encryptionkeys` (clave pública servida). | 4 |
| A.5 | `05-metrics-expuesto.jpg` | Endpoint `/metrics` accesible sin autenticación. | 4 |
| A.6 | `06-zap-reporte-resumen.jpg` | Resumen del reporte de OWASP ZAP baseline (análisis pasivo). | 4 |
| A.7 | `07-zap-alertas.jpg` | Alertas detectadas por ZAP baseline (WARN-NEW). | 4 |
| A.8 | `08-ataques-antes-consola.jpg` | Consola de `security/attacks/run.sh` contra el laboratorio vulnerable. | 4 |
| A.9 | `09-nmap.jpg` | Reconocimiento de red con Nmap sobre el puerto 3000. | 4 |
| A.10 | `10-trivy-imagen.jpg` | Escaneo de la imagen con Trivy (CVE y secretos). | 5 |
| A.11 | `11-grype-sbom.jpg` | Análisis de composición (Grype) y SBOM de dependencias. | 5 / 3 |
| A.12 | `12-hadolint.jpg` | Hadolint sobre el Dockerfile (avisos de higiene de build). | 5 |
| A.13 | `13-checkov.jpg` | Checkov sobre IaC de despliegue (`deploy/`, `app-hardened/`). | 5 |
| A.14 | `14-docker-inspect-hardening.jpg` | `docker inspect` del contenedor endurecido (runtime). | 5 |
| A.15 | `15-bola-idor.png` | Prueba BOLA/IDOR: la cuenta B lee la cesta de la cuenta A (`UserId:26` ≠ `UserId:27`, HTTP 200). | 4 |

---

## Anexo B — Evidencia técnica de la Fase 4 (pruebas de seguridad)

Ubicación raíz: `evidence/fase-4/`.

### B.1 Casos de ataque — estado inherente (laboratorio vulnerable, `127.0.0.1:3000`)
| Archivo | Contenido |
|---|---|
| `antes/resumen-ataques.md` | Tabla resumen de los 11 casos (clase y veredicto). |
| `antes/a1-sqli-login.json`, `antes/a1-req-resp.txt` | SQLi bypass de login (petición/respuesta). |
| `antes/a2-sqli-union-search.json` | SQLi UNION (volcado de `Users`). |
| `antes/a3-sqli-schema.json` | SQLi enumeración de esquema. |
| `antes/a4-directory-listing.txt` | Listado de directorios `/ftp`, `/encryptionkeys`. |
| `antes/a5-acquisitions.md` | Exposición de documento interno (`/ftp/acquisitions.md`). |
| `antes/a6-metrics.txt` | `/metrics` sin autenticación. |
| `antes/a7-mass-assignment.json` | Asignación masiva `role=admin` en el registro. |
| `antes/a8-cors-headers.txt` | CORS permisivo (`Access-Control-Allow-Origin: *`). |
| `antes/a9-security-headers.txt` | Ausencia de cabeceras de seguridad. |
| `antes/a10-bruteforce-login.txt` | Ausencia de límite de intentos (rate limiting). |
| `antes/a11-jwt-key.txt` | Clave JWT / `/encryptionkeys`. |
| `inherente-2026-11-04/resumen-ataques.md` | Reejecución de verificación (2026-11-04). |

### B.2 Casos de ataque — estado residual (entorno endurecido, `127.0.0.1:8080`)
`despues/` contiene los mismos archivos (`a1`–`a11`, `resumen-ataques.md`) tras aplicar WAF + hardening.
Varios `a2`/`a3`/`a5`/`a6`/`a7` comparten el mismo hash (respuesta HTTP 403 del WAF).

### B.3 BOLA / IDOR (dos cuentas de laboratorio)
Ubicación: `evidence/fase-4/bola/`.
| Archivo | Contenido |
|---|---|
| `resultado-bola.md` | Procedimiento y veredicto (CWE-639 / OWASP API1:2023 / A01:2025). |
| `cross-read.json` | Lectura cruzada: cuenta B obtiene la cesta de A → `{"id":6,"UserId":26,...}`. |
| `own-read.json` | Control positivo: cuenta B sobre su propia cesta → `UserId:27`. |

La prueba demuestra el fallo por el `UserId` del objeto devuelto (26 ≠ 27) en respuesta **HTTP 200**, con
control positivo y negativo; la cesta está vacía (`Products:[]`), lo que no invalida el hallazgo.

### B.4 Prueba activa de caja negra — sqlmap
Ubicación: `evidence/fase-4/blackbox-2026-11-04/`.
| Archivo | Contenido |
|---|---|
| `resultado-blackbox.md` | Metodología (sin conocer el código; endpoint hallado desde la UI) y veredicto. |
| `sqlmap-search-q.txt` | Salida literal de sqlmap. |

Resultado: parámetro `q` de `/rest/products/search` **VULNERABLE** (boolean-based + time-based blind, SQLite,
169 peticiones). CWE-89 / A05:2025 Injection. Corrobora de forma independiente A1–A3.

### B.5 DAST pasivo (OWASP ZAP baseline) y reconocimiento (Nmap)
| Archivo | Contenido |
|---|---|
| `zap/resumen-zap.md`, `zap/zap-baseline.html`, `zap/zap-baseline.json`, `zap/zap.yaml` | ZAP baseline **pasivo**: WARN-NEW 7, PASS 61, FAIL 0. |
| `nmap-127-3000.txt` | Nmap 7.98: `3000/tcp open`; el banner HTTP revela `ACAO: *`. |

> **Diferenciación de enfoques.** Caja negra pasiva = ZAP baseline + Nmap (sin autenticar, sin código).
> Caja negra activa = sqlmap (B.4). Caja gris / blanca = `run.sh` y revisión de `server.ts` con acceso al
> código. No se atribuye a ZAP ningún hallazgo obtenido por revisión de código.

---

## Anexo C — Evidencia técnica de la Fase 5 (contenedores y hardening)

Ubicación raíz: `evidence/fase-5/`.

### C.1 Escaneo de imagen (Trivy) — antes vs. después
| Archivo | Contenido |
|---|---|
| `antes/resumen-trivy.md`, `antes/trivy-juice-shop-v20.3.0.json` | Imagen original: 11 CRITICAL / 32 HIGH / 71 MEDIUM / 11 LOW / 1 UNKNOWN; 5 secretos. |
| `despues/resumen-trivy.md`, `despues/trivy-juice-hardened.json` | Imagen endurecida: **idéntica** (11 CRITICAL / 32 HIGH). |

> El repaquetado **no elimina** las CVE de dependencias ni los secretos de reto (residen en el código de
> Juice Shop). El contenedor desplegado las **mitiga en ejecución** mediante el runtime (C.3), no las elimina.

### C.2 Dockerfile (Hadolint) — antes vs. después
| Archivo | Contenido |
|---|---|
| `antes/resumen-hadolint.md`, `antes/hadolint-Dockerfile.json` | `app/Dockerfile`: **11 avisos**. |
| `despues/resumen-hadolint.md`, `despues/hadolint-Dockerfile.json` | `app-hardened/Dockerfile`: **0 avisos** (artefacto auditado, no desplegado). |

### C.3 Hardening de runtime (verificado)
| Archivo | Contenido |
|---|---|
| `despues/runtime-hardening-inspect.txt` | `docker inspect`: `ReadonlyRootfs=true`, `CapDrop=[ALL]`, `no-new-privileges`, `PidsLimit=200`, `Memory=1GiB`, `User=65532:0`, `NODE_ENV=production`; escritura en `/` bloqueada (EROFS); app HTTP 200. |

### C.4 IaC de despliegue (Checkov)
| Archivo | Contenido |
|---|---|
| `iac/results_cli.txt`, `iac/results_json.json` | Frameworks `dockerfile` + `yaml` sobre `deploy/` y `app-hardened/`: **47 passed / 0 failed / 0 skipped**. |

### C.5 Relación con el SCA de dependencias (Fase 3)
La enumeración de CVE de dependencias Node y el SBOM (Grype, OSV, npm audit, Syft/CycloneDX) se ejecutaron en
la **Fase 3** (`evidence/fase-3/sca/`). La Fase 5 escanea la **imagen**. Ambos coinciden y no se recuentan.

---

## Anexo D — Comandos ejecutados y versiones de herramientas

Extracto de `evidence/bitacora.md` (fecha, fase, comando, herramienta, resultado).

| Fecha (hora local) | Fase | Comando | Herramienta (versión fija) | Resultado |
|---|---|---|---|---|
| 2026-11-04 00:20 | 4 | `security/attacks/run.sh (http://127.0.0.1:3000, antes)` | curl + código del lab | 11 observaciones detectadas |
| 2026-11-04 00:31 | 4 | `nmap -sV -Pn -p 3000 (red del contenedor)` | Nmap **7.98** (instrumentisto/nmap) | `3000/tcp open`; banner revela `ACAO:*` |
| 2026-11-03 23:29 | 4 | `zap-baseline.py -t http://127.0.0.1:3000` | OWASP ZAP **2.17.0** (zap-stable:20261016) | WARN-NEW 7, PASS 61, FAIL 0 |
| 2026-11-04 17:08 | 4 | `sqlmap -u .../rest/products/search?q= --batch --level=3 --risk=2` | sqlmap **1.10.4** (parrotsec/sqlmap) | `q` VULNERABLE (boolean+time-based, SQLite) |
| 2026-11-03 23:09 | 5 | `trivy image bkimminich/juice-shop:v20.3.0@sha256:cea5a4af…` | Trivy **0.75.0** | 11 CRITICAL / 32 HIGH |
| 2026-11-03 23:42 | 5 | `hadolint app-hardened/Dockerfile` | Hadolint **2.15.1** | 0 avisos (antes 11) |
| 2026-11-03 23:42 | 5 | `docker build … ; docker run --read-only --cap-drop ALL --security-opt no-new-privileges ; docker inspect` | Docker **29.9.2** | HTTP 200; runtime endurecido verificado (EROFS) |
| 2026-11-03 23:42 | 5 | `trivy image juice-hardened:local (después)` | Trivy **0.75.0** | 11 CRITICAL / 32 HIGH (idénticas) |
| 2026-11-03 23:42 | 5 | `checkov -d deploy -d app-hardened --framework dockerfile,yaml` | Checkov **3.4.0** | 47 passed / 0 failed |

> Conteo reproducible de rutas de la superficie de ataque (`app/server.ts`):
> 50 GET + 40 POST + 13 PUT + 5 DELETE + 1 PATCH = **109 rutas declaradas**.

---

## Anexo E — Integridad de la evidencia (hashes SHA-256)

Extracto de `evidence/MANIFEST.sha256` correspondiente a las Fases 4-5. El manifiesto completo cubre todas las
fases y se regenera con `scripts/manifest.sh`.

### E.1 Fase 4
```
b81dcaeda7eef8db32f9fbec530f4fcccdbf8f78e84c9eacee328cc9a048eb89  fase-4/antes/a1-req-resp.txt
be82163c13e8007fb497c12a4ae1c0555127b6caca8b4316eebb8e27ba67bf89  fase-4/antes/a1-sqli-login.json
5aa20fbf043b3d7232e504c003581d857de23fc3721f87e64269a61062371919  fase-4/antes/a2-sqli-union-search.json
9098cfa7a99ad97cc30c8a23e40dd6cef99907b52e07cec3b7b3de9dbd77c3db  fase-4/antes/a3-sqli-schema.json
be86b35a56b7a04a1d9b6725cda48a18247a5be2d89c99fdb4df9fc1f236382e  fase-4/antes/a4-directory-listing.txt
48321ee73b6b6de85cd390e3f395ba794639a268d094201f45c3f973cac441fd  fase-4/antes/a5-acquisitions.md
ace365549d9a8c51c42ea421f68a602e6189a7ced70ebe06c551a67523b42dd1  fase-4/antes/a6-metrics.txt
207dbeb3043aa3c4b6f0d1d970f55f1fffaf67bb6121b41fbfc740c9fbb1799a  fase-4/antes/a7-mass-assignment.json
d3a86fca66c1329f7f41b412d95367cfaf5a7ea8da4326c73b2de27acd33ce56  fase-4/antes/a8-cors-headers.txt
74392a4ac185ee1946808311da4192312b749bcc31c2de4fbe7b560c5f0c49a7  fase-4/antes/a9-security-headers.txt
e414041ef042e8cd1369303fd7f521f2a97bd1134adbe080036682d52376ea65  fase-4/antes/a10-bruteforce-login.txt
89fdb7cbbc50749d7a72fbf3452e5ba537d01e176b8e686b3f8536627c11f338  fase-4/antes/a11-jwt-key.txt
f7b7c2590e562f237eb8bbace406d6a1700b99e4e39530d21485ddbd0b50803f  fase-4/antes/resumen-ataques.md
9580a9c25f978406f577dbae0a725c81fa387628f4ba9f6aeab7325d47bda959  fase-4/bola/cross-read.json
420fe5429467522aac9848925dd01aa08c984194e698111eee931c372e5ecf25  fase-4/bola/own-read.json
db27de6ed707c55bfd4b04343b21f714c4325d578f91482f893724bea0c1e0e0  fase-4/bola/resultado-bola.md
63f8ae4060696214e6ea2dccac11712a86b0704d3fd967a645160157225e3659  fase-4/blackbox-2026-11-04/resultado-blackbox.md
ffbbc81a7ea81f7618dd0d36639ed26b0b2e09a6536aec6e8a0f41e17cdfab6a  fase-4/blackbox-2026-11-04/sqlmap-search-q.txt
ca6b5075c741645af1e3b8884d25f38b03a3cea74ce40878bf867fd444706a8d  fase-4/nmap-127-3000.txt
8dbb4882a07b8f2af1ac266ad4b6ffdde5d09eb334cb366999a94b265050713f  fase-4/zap/resumen-zap.md
e087bfc3e55e53c12e7995e44e2e80f987b8fa1b721398f0cf5a8eb005959370  fase-4/zap/zap-baseline.html
5c23912476b2f22496ed6670be8e8fcbeba61eef1bd25ae77ccc0a595c21b449  fase-4/zap/zap-baseline.json
```

### E.2 Fase 5
```
248b879623bae909377c9c94b81fff0cc93dfefa69d55918a6799dda4eba4d9f  fase-5/antes/resumen-trivy.md
e592988c8d6e09c892923bdfed28496fcf629448ffbb5059e22a9236cd520092  fase-5/antes/trivy-juice-shop-v20.3.0.json
3a11bf9d78832d5f8434c290af409d097b5f18583b9ba6bf9658fabb3bfe8be4  fase-5/antes/hadolint-Dockerfile.json
1a214b79912388d207e7c1414802c6bba726e332484be42c9cf850455135e1a6  fase-5/antes/resumen-hadolint.md
9ee2e5849e2153df982e56100b6a10e1291b2531b07b4ae605c317753addb7cf  fase-5/despues/resumen-trivy.md
3496e9c380067559ddca1e4a31d88564dd31c3bab4a3825548a7bd05204e837f  fase-5/despues/trivy-juice-hardened.json
4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945  fase-5/despues/hadolint-Dockerfile.json
d36ae2c21fb524d4464e1dc07e78d123d4e09f97b3f21d03130f5d1f6c3ff238  fase-5/despues/resumen-hadolint.md
6f28672b9b39a1bbd65c82dd91e45e9011a20813d19df9112b3697de6e1aa387  fase-5/despues/runtime-hardening-inspect.txt
bf4dff6832729badc02f61994585bb3539e0e0042e3fc6178b5675d5c0af8eef  fase-5/iac/results_cli.txt
5015fb691d35fe634839fa0d14739a761ffef4a52b9384a355dffd31d0adbc8c  fase-5/iac/results_json.json
```

> Verificación: `sha256sum -c evidence/MANIFEST.sha256` (ejecutado desde `evidence/`).

---

## Anexo F — Transcripciones de terminal (figuras)

Las capturas de terminal del Anexo A se renderizan a partir de las transcripciones en
`docs/evidencias-fase4-5/term/`:

| Archivo | Figura asociada | Contenido |
|---|---|---|
| `ataques-antes.txt` | A.8 | Salida de `run.sh` contra el laboratorio vulnerable. |
| `nmap.txt` | A.9 | Reconocimiento Nmap. |
| `trivy-antes.txt` | A.10 | Escaneo Trivy de la imagen. |
| `grype.txt` | A.11 | Análisis Grype / SBOM. |
| `hadolint.txt` | A.12 | Avisos Hadolint. |
| `checkov.txt` | A.13 | Resultado Checkov. |
| `docker-inspect.txt` | A.14 | `docker inspect` del runtime endurecido. |
| `bola.txt` | A.15 | Transcripción **literal** del run BOLA/IDOR (dos cuentas). |

---

## Anexo G — Alcance, aislamiento y limitaciones

- **Aislamiento:** la versión vulnerable solo escuchó en `127.0.0.1:3000` / red de Docker; la endurecida en
  `127.0.0.1:8080`. Nunca se publicó a Internet ni se atacó la demo pública de Juice Shop o terceros.
- **Clasificación OWASP:** se aplica **OWASP Top 10:2025** de forma coherente (Injection = A05; Security
  Misconfiguration = A02; SSRF fusionado en A01; A10 = Mishandling of Exceptional Conditions).
- **Artefacto auditado vs. desplegado (Fase 5):** `app-hardened/Dockerfile` (Hadolint 11→0) es propuesto y
  **no se despliega**; el contenedor en ejecución reutiliza la imagen oficial y se endurece por **runtime**,
  por lo que las CVE de la imagen se **mitigan**, no se eliminan.
- **Cloud (Fase 2):** diseñado en Terraform y auditado estáticamente (Checkov); **no desplegado** (sin costos).
- **Pendientes del equipo:** DFD en OWASP Threat Dragon, confirmación de IDs ASVS 5.0.0, capturas manuales con
  Burp Suite y ensamblado final de los documentos Word/PDF (plantilla T3, APA 7).
