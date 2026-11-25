# Evidencias de la Fase 3 — Desarrollo seguro y automatización DevSecOps

Índice actualizado el 2026-11-25. **Tipo:** *C* = captura real; *S* = salida nativa de herramienta; *E* = extracto literal de un
archivo versionado. **Línea base** = imagen/código oficial vulnerable; **artefacto final** = variante corregida e imagen cloud.

| Requisito | Evidencia (ruta) | Tipo | Fecha · entorno · versión | Herramienta | Resultado e interpretación |
|---|---|---|---|---|---|
| Workflows integrados en CI/CD | `evidence/fase-3/capturas/actions-2026-11-25/01-actions-devsecops-resumen.png`, `02-actions-release-resumen.png`, `03/04-…-historial.png` | C | 2026-11-25 · GitHub Actions (páginas públicas) | Chromium (Playwright 1.49.1) | `devsecops.yml` run 45665962666 (`8b3e422`): 7 jobs en verde (informa, no bloquea). `release.yml` run 45555578891 (`84241b4`): IaC, app y cloud APTA (bloquea si incumple) |
| SAST — Semgrep (línea base) | `evidence/fase-3/sast/semgrep.sarif`, `.json`, `resumen-semgrep.md` | S | 2026-11-03 · local · Semgrep 1.181.1 | Semgrep | 90 hallazgos (26 ERROR, 62 WARNING, 2 MEDIUM) en código original, workflows de Juice Shop y ejemplos de retos |
| SAST — Semgrep (artefacto final) | `evidence/cierre-brechas-2026-11-24/08-puerta-release-local/{app,cloud-alpine}/semgrep.json`, `puerta-release.md` | S | 2026-11-24 · local y CI | Semgrep 1.181.1 (reglas propias `security/semgrep/`) | 12 ERROR cubiertos por 7 excepciones documentadas y 33 WARNING |
| SAST — CodeQL | `evidence/fase-3/codeql-resultados.md` | S | 2026-11-25 · GitHub code scanning | CodeQL (`codeql-action` v3) | 93 alertas abiertas (7 Critical, 72 High, 14 Medium) sobre el código **original** |
| SCA — npm audit, OSV, Syft/SBOM, Grype | `evidence/fase-3/sca/` (`npm-audit.json`, `osv.json`, `sbom-juice-shop-v20.3.0.cdx.json`, `grype.json` y resúmenes) | S | 2026-11-03 · imagen oficial | npm audit, OSV-Scanner v2.7.0, Syft v1.55.0, Grype v0.120.1 | npm audit 40 (7 críticos, 20 altos); OSV 28 paquetes / 62 vulnerabilidades; Grype 129 coincidencias (12 Critical, 44 High); SBOM 2745 componentes |
| SCA — artefacto final | `08-puerta-release-local/{app,cloud-alpine}/trivy.json`, `grype.json`, `sbom.cdx.json` | S | 2026-11-24 | Trivy 0.75.0 (decide), Grype 0.120.1 (informativo) | App: Trivy C1/H2 exceptuadas; cloud: C1 (marsdb, exceptuada) / H0. Grype: app C1/H18, cloud C1/H15 |
| Secretos | `evidence/fase-3/secrets/` y `08-puerta-release-local/*/gitleaks.json` | S | 2026-11-03 y 2026-11-24 | Gitleaks v8.30.1 | 0 secretos en el historial (un falso positivo revisado en `.gitleaksignore`) |
| Código seguro: SQLi, XSS, CSRF, JWT | `evidence/fase-3/codigo-seguro.md` | E | Parche `correcciones-cierre-brechas.patch` (`fc3f765c…`) sobre `f189f5212` | — | Fragmentos antes/después con archivo, línea, parche y prueba asociada |
| Política de release en CI | `evidence/cierre-brechas-2026-11-24/11-ci-release/resultado-ci.md`; `security/release/politica-release.json` | S | 2026-11-24 | `scripts/pipeline-release.sh` | Run 45555578891 en verde; run 45550623082 fallido documentado (imagen Debian BLOQUEADA) |

## Conciliación de cifras de Trivy (no mezclar escaneos)
| Reporte | Fecha | Imagen | CRITICAL | HIGH | Únicas | Motivo de la diferencia |
|---|---|---|---|---|---|---|
| `evidence/fase-5/antes/resumen-trivy.md` | 2026-11-03 | oficial v20.3.0 (`cea5a4af…`) | 11 | **32** | 126 | Base de datos de Trivy de esa fecha |
| `evidence/cierre-2026-11-20/02-escaneos/resumen-trivy.md` | 2026-11-21 | la misma imagen (reescaneo) | 11 | **33** | 150 | Misma imagen, base de datos más reciente: se publicaron nuevas CVE |
| `08-puerta-release-local/app/puerta-release.md` | 2026-11-24 | variante corregida + RASP | 1 | 2 | — | Artefacto final (parches 01-14), ambas exceptuadas con vencimiento |
| `08-puerta-release-local/cloud-alpine/puerta-release.md` | 2026-11-24 | imagen cloud Alpine | 1 | 0 | — | Imagen desplegada en Render; APTA |

Un pipeline `devsecops.yml` en verde **no** aprueba un release: ese workflow escanea la imagen oficial vulnerable y nunca bloquea.
La aprobación la da únicamente `release.yml` con la política `politica-release.json`.
