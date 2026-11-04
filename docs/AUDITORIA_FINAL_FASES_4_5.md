# Auditoría final técnica — Fases 4 y 5 (OWASP Juice Shop lab)

**Fecha:** 2026-11-04 · **Alcance:** consolidación técnica de las Fases 4 (pruebas de seguridad) y 5
(contenedores y hardening). **Base:** último commit publicado en `main`.
**Regla rectora:** evidencias reales y verificables; sin resultados inventados; sin modificar los documentos
Word/PDF (su redacción académica la realiza otra persona). Las correcciones tocan **código, scripts, Markdown
técnico y evidencias**, no los `.docx`/`.pdf`.

> Clasificación OWASP utilizada en todo el proyecto: **OWASP Top 10:2025** (`https://owasp.org/Top10/2025/`).

---

## 1. Matriz de requisitos — Fase 4

| # | Requisito | Estado | Evidencia / ubicación |
|---|---|---|---|
| F4-P1 | Clasificación OWASP **2025** correcta y sin mezcla con 2021 | **Cumple** | `docs/fase-4/fase4-pruebas-seguridad.md` §3 (nota de edición), §6 (matriz 2025) |
| F4-P2 | BOLA/IDOR con dos cuentas, tokens propios, control +/−, sin reconstrucciones | **Cumple** | `evidence/fase-4/bola/`, `docs/evidencias-fase4-5/term/bola.txt` (ahora literal) |
| F4-P3 | Al menos una prueba **activa** de caja negra sin conocimiento del código | **Cumple** | `evidence/fase-4/blackbox-2026-11-04/` (sqlmap), `docs/fase-4/...` §3.4 |
| F4-P4 | Reclasificación honesta A1–A12 (E/X/C/N); `run.sh` no etiqueta todo como vulnerable | **Cumple** | `security/attacks/run.sh` (columna Clase), `docs/fase-4/...` §3 |
| F4-P5 | Superficie de ataque reproducible; versiones de herramientas reales | **Cumple** | conteo 109 reproducible; Nmap 7.98 corregido |
| F4 | Diferenciación explícita Black/Gray/White box | **Cumple** | `docs/fase-4/...` §1 |
| F4 | ZAP presentado como baseline **pasivo** (no se le atribuye SQLi/IDOR) | **Cumple** | `docs/fase-4/...` §1, §4; `evidence/fase-4/zap/` |

## 2. Matriz de requisitos — Fase 5

| # | Requisito | Estado | Evidencia / ubicación |
|---|---|---|---|
| F5-1 | Escaneo Trivy de imagen (antes/después) | **Cumple** | `evidence/fase-5/antes|despues/resumen-trivy.md` (11C/32H/71M/11L/1U, idénticos) |
| F5-2 | SCA Grype + OSV + npm audit + SBOM | **Cumple** | `evidence/fase-3/sca/` (grype.json, osv.json, npm-audit.json, sbom …cdx.json) |
| F5-3 | Hadolint (antes/después) | **Cumple** | `evidence/fase-5/antes|despues/resumen-hadolint.md` (11→0) |
| F5-4 | Checkov sobre IaC de despliegue | **Cumple** | `evidence/fase-5/iac/results_cli.txt` (47/0/0) |
| F5-5 | Hardening de runtime verificado (read-only, cap_drop, no-new-priv, límites, no root) | **Cumple** | `evidence/fase-5/despues/runtime-hardening-inspect.txt` (`docker inspect`) |
| F5-6 | Aislamiento de red (solo 127.0.0.1) | **Cumple** | `deploy/lab/docker-compose.yml` (`127.0.0.1:3000:3000`) |
| F5-7 | Distinguir Dockerfile **auditado** vs. contenedor **desplegado** | **Cumple** | `docs/fase-5/...` §2.1 |
| F5-8 | No afirmar eliminación de CVE si solo hay controles de runtime | **Cumple** | `docs/fase-5/...` §1, §2.1 ("mitigadas en ejecución, no eliminadas") |

---

## 3. Problemas detectados y correcciones implementadas

| ID | Problema detectado | Corrección | Archivo |
|---|---|---|---|
| C1 | Columna "OWASP 2025" mezclaba numeración 2021 y 2025: A05 se usaba para SQLi (correcto, Injection=A05:2025) **y** para listados/CORS/cabeceras/metrics/clave pública (incorrecto; esos son A02 Security Misconfiguration) | Remapeo a 2025: A4/A6/A8/A9/A11 → **A02**; SQLi se mantiene en **A05**; A5/A7/A12 → **A01**; A10 → **A07**. Nota de edición explícita | `docs/fase-4/fase4-pruebas-seguridad.md` §3 |
| C2 | §6 "cobertura" usaba numeración 2021 (Injection=A03, A10 SSRF) con etiqueta "2025" | Matriz reescrita a 2025: Injection=A05, Supply Chain=A03, SSRF fusionado en A01, A10=Mishandling of Exceptional Conditions | `docs/fase-4/...` §6 |
| C3 | `term/bola.txt` (fuente de figura) mostraba un *timestamp* de cuenta (`1762286560`) distinto del real y `Products:[...]` inexistentes → reconstrucción no literal | Reescrito como transcripción **literal** del run real: `1793822559`, `Products:[]`, JSON idéntico a `cross-read.json`/`own-read.json`. Figura PNG re-renderizada desde el texto corregido | `docs/evidencias-fase4-5/term/bola.txt`, `img/15-bola-idor.png` |
| C4 | `run.sh` etiquetaba toda observación como "VULNERABLE" (conclusión exagerada) | Añadida columna **Clase** (E/X/C/N) + leyenda; el veredicto VULNERABLE/MITIGADO se conserva solo como indicador de mitigación antes/después (Fase 6) | `security/attacks/run.sh` |
| C5 | Doc decía **Nmap 7.95**; la evidencia real es **7.98** | Corregido a 7.98 (coincide con `nmap-127-3000.txt` y el documento Word, que ya decía 7.98) | `docs/fase-4/...` §1 |
| C6 | Fase 1 decía **102 rutas**; valor real reproducible **109** | Corregido a 109 | `docs/fase-1/fase1-modelado-amenazas.md` |
| C7 | Fase 6 matriz: A5 con **CWE-22** (path traversal) contradecía la reclasificación (CWE-538) | A5 → **CWE-538**; A11 renombrado a "Clave privada JWT embebida (y endpoint /encryptionkeys)" | `docs/fase-6/matriz-riesgo.md` |
| C8 | Informe ejecutivo afirmaba "**11/11 vectores explotables**" | Reescrito: 11 observaciones = 4 explotación demostrada + 7 debilidades | `docs/informe-ejecutivo.md` |
| C9 | Fase 5 no referenciaba dónde viven Grype/OSV/SBOM | Añadido §1.1 que apunta a `evidence/fase-3/sca/` y evita doble conteo | `docs/fase-5/...` §1.1 |

### 3.1 Reclasificación final A1–A12 (OWASP 2025)
| ID | Caso | Clase | CWE | OWASP 2025 |
|---|---|---|---|---|
| A1–A3 | SQLi (login, UNION, esquema) | **E** explotación | CWE-89 | A05 Injection |
| A4 | Listado de directorios | **X** exposición | CWE-548 | A02 Security Misconfiguration |
| A5 | Documento confidencial `/ftp` | **X** exposición | CWE-538 | A01 Broken Access Control |
| A6 | `/metrics` sin auth | **X** exposición | CWE-200 | A02 Security Misconfiguration |
| A7 | Asignación masiva role=admin | **E** explotación | CWE-915 | A01 Broken Access Control |
| A8 | CORS permisivo | **C** config | CWE-942 | A02 Security Misconfiguration |
| A9 | Cabeceras ausentes | **C** config | CWE-693 | A02 Security Misconfiguration |
| A10 | Sin rate limiting en login | **N** ausencia | CWE-307 | A07 Authentication Failures |
| A11 | Clave **pública** JWT servida | **X** exposición (bajo) | CWE-200 | A02 Security Misconfiguration |
| A12 | BOLA/IDOR entre dos cuentas | **E** explotación | CWE-639 | A01 (API1:2023) |
| (blanco) | Clave **privada** embebida | — (white-box) | CWE-798/321 | A04 Cryptographic Failures |

Totales: **4 explotación demostrada** (A1, A2, A3, A7; BOLA A12 añade una 5.ª explotación de acceso) ·
**exposición/config/ausencia** para el resto. No se afirma "11/11 explotables".

---

## 4. Pruebas ejecutadas en esta auditoría (contra el laboratorio propio y aislado)

| Prueba | Herramienta (versión / imagen) | Resultado | Evidencia |
|---|---|---|---|
| SQLi activa de caja negra | sqlmap 1.10.4 — `parrotsec/sqlmap@sha256:aa7836c1…` | Parámetro `q` VULNERABLE (boolean + time-based blind, DBMS SQLite, 169 req) | `evidence/fase-4/blackbox-2026-11-04/` |
| Conteo de rutas reproducible | `grep -cE "app\.(get|post|put|delete|patch)\(…"` | **109** (50 GET+40 POST+13 PUT+5 DELETE+1 PATCH) | verificado en `app/server.ts` |
| Sintaxis de `run.sh` | `bash -n` | OK | — |
| BOLA/IDOR (verificación de evidencia) | revisión de `cross-read.json`/`own-read.json` | UserId 26 ≠ 27, ambos HTTP 200 → BOLA real | `evidence/fase-4/bola/` |

Aislamiento: el laboratorio se levantó solo en `127.0.0.1:3000`; sqlmap accedió al contenedor por la red Docker
interna `juice-lab_default`; el laboratorio se detuvo al terminar. Ninguna prueba se dirigió a Internet ni a
terceros (CLAUDE.md §1/§2).

---

## 5. Resultados verificados (Fase 5)

- **Trivy** imagen oficial vs. `juice-hardened:local`: **11 CRITICAL / 32 HIGH / 71 MEDIUM / 11 LOW / 1 UNKNOWN**,
  idénticos en ambas (la imagen endurecida reutiliza la capa oficial; no recompila). 5 secretos de reto. ✔
- **Hadolint**: `app-hardened/Dockerfile` **11→0**; la imagen desplegada (`deploy/hardened`) se endurece por
  **runtime**, no por recompilación. ✔
- **Runtime** (`docker inspect`): ReadonlyRootfs=true, CapDrop=[ALL], no-new-privileges, PidsLimit=200,
  Memory=1 GiB, User=65532:0, NODE_ENV=production, escritura en `/` bloqueada (EROFS). ✔
- **Checkov** IaC despliegue: **47 passed / 0 failed / 0 skipped**. ✔
- **Honestidad:** las CVE de dependencias **no se eliminan** en Fase 5; se mitigan en ejecución y su eliminación
  es trabajo de Fase 6. Correctamente declarado. ✔

---

## 6. Limitaciones técnicas (declaradas, no ocultas)
- BOLA probado sobre lectura de cesta por `id`; no se generaliza a todos los objetos de la API.
- sqlmap confirmó los puntos de inyección pero **no** se realizó volcado masivo de datos (prueba acotada).
- La cesta del BOLA está vacía (`Products:[]`): la prueba se sostiene por el `UserId` del objeto devuelto, no por
  su contenido.
- ZAP es baseline **pasivo**; la prueba activa de caja negra la cubre sqlmap. Burp manual queda a cargo del equipo.
- El conteo de 109 son **rutas con path literal** en `server.ts`, no el total de endpoints únicos (las APIs CRUD
  de `finale.resource` añaden variantes por método/parámetro; documentado en §2 de Fase 4).

---

## 7. Pendientes de Fases 1–3 (no impiden la entrega de 4–5)
- **Fase 1:** DFD en OWASP Threat Dragon; confirmación de IDs ASVS 5.0.0; campos faltantes del inventario de
  activos. (Académicos; el modelado STRIDE/DREAD y las referencias a código ya existen.)
- **Fase 2:** arquitectura cloud **diseñada y auditada estáticamente** (Terraform + Checkov 144/0), **no desplegada**.
- **Fase 3:** SAST/SCA completos; sin pendientes que afecten a 4–5.
- Capturas manuales con Burp Suite (equipo).

## 8. Actividades diferidas — cloud y Fase 6
Estados de la infraestructura (distinción explícita solicitada):

| Estado | Qué incluye |
|---|---|
| **Local implementada** | `deploy/lab` (vulnerable, 127.0.0.1) y `deploy/hardened` (endurecido + WAF), en ejecución verificada |
| **Cloud diseñada** | `infra/terraform/` (VPC, ALB TLS 1.3, WAFv2, ECS Fargate privado, KMS, IAM mínimo) |
| **Cloud auditada estáticamente** | `terraform validate` OK, `plan` 45 recursos, **Checkov 144/0** (5 omisiones justificadas) |
| **Cloud NO desplegada** | **Sin `terraform apply`, sin EC2/ECS/ALB/RDS reales** — pospuesto para evitar costos |

Diferido también: recompilar `app-hardened` con los 7 parches y medir residual **sin** WAF; actualizar
dependencias con CVE; SIEM/monitoreo (Loki/Promtail o Wazuh). **No se crearon recursos facturables en esta
auditoría.**

---

## 9. Dictamen técnico

Las **Fases 4 y 5 están técnicamente consolidadas y listas para su redacción académica final**, con las
siguientes condiciones cumplidas:

- Clasificación OWASP **2025** coherente y sin mezcla de ediciones.
- Hallazgos clasificados con honestidad (explotación vs. exposición vs. configuración vs. ausencia de control);
  sin la afirmación exagerada "11/11 explotables".
- BOLA/IDOR real y su figura/transcripción ahora **literales** respecto a la evidencia committeada.
- Una prueba **activa** de caja negra (sqlmap) añadida, con evidencia; black/gray/white box diferenciados.
- Fase 5 verificada contra evidencia existente; distinción artefacto auditado vs. desplegado; sin afirmar
  eliminación de CVE.

**Trabajo que NO corresponde a esta auditoría** (y que no bloquea la entrega): ensamblado/estética de los
documentos Word/PDF (APA 7, portada, logo UMG, re-render de figuras en el `.docx`), despliegue cloud y Fase 6
ampliada. La figura `img/15-bola-idor.png` fue re-renderizada en el repositorio; al reconstruir el `.docx` se
tomará la versión corregida automáticamente.

**Trazabilidad:** toda evidencia nueva tiene su hash en `evidence/MANIFEST.sha256` y una línea en
`evidence/bitacora.md`.
