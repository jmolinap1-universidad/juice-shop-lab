# Fase 3 – Desarrollo seguro y automatización DevSecOps

**Estado:** implementado y verificado. Índice de evidencias: [`evidence/fase-3/LEAME.md`](../../evidence/fase-3/LEAME.md).

## 1. Pipeline CI/CD (GitHub Actions)
| Workflow | Eventos | Jobs | Efecto |
|---|---|---|---|
| `.github/workflows/devsecops.yml` | push a `main`, pull request, manual | Gitleaks · Semgrep · CodeQL · SCA (npm audit, OSV-Scanner, Syft/SBOM, Grype) · Trivy + Hadolint · Terraform + Checkov · ZAP baseline contra un contenedor efímero | **Informa**: analiza la imagen oficial vulnerable y nunca bloquea |
| `.github/workflows/release.yml` | push a `main` que cambie la variante, WAF, imagen cloud, reglas, política o `render.yaml`; manual | IaC de Render · puerta de release de la imagen de la app · puerta de release de la imagen cloud | **Bloquea**: falla si el artefacto incumple `security/release/politica-release.json` |

Versiones fijadas en el workflow: Semgrep 1.181.1, Gitleaks v8.30.1, Trivy 0.75.0, Hadolint v2.15.1, Checkov 3.4.0, Syft v1.55.0,
Grype v0.120.1, OSV-Scanner v2.7.0, Terraform 1.16.7, ZAP 2.17.0. Ejecuciones de referencia: devsecops 45665962666 (`8b3e422`)
y release 45555578891 (`84241b4`), con capturas en `evidence/fase-3/capturas/actions-2026-11-25/`.

**Política de release** (bloquea si): hay secretos; Hadolint informa avisos; Semgrep (reglas propias de `security/semgrep/`) informa
un ERROR sin excepción; Trivy informa una CVE CRITICAL o HIGH sin excepción vigente; una excepción venció o su paquete ya tiene
versión corregida. Las excepciones registran identificador, motivo, responsable por rol y vencimiento.

## 2. Resultados
| Análisis | Línea base (código/imagen oficial v20.3.0) | Artefacto final |
|---|---|---|
| Semgrep | 90 hallazgos (26 ERROR, 62 WARNING, 2 MEDIUM) | 12 ERROR cubiertos por 7 excepciones, 33 WARNING |
| CodeQL | 93 alertas abiertas (7 Critical, 72 High, 14 Medium) sobre el código original | — (la variante se construye fuera del árbol versionado) |
| npm audit | 40 avisos (7 críticos, 20 altos) | Dependencias directas actualizadas (parche 11) |
| OSV-Scanner | 28 paquetes, 62 vulnerabilidades únicas | — |
| Grype (SBOM, 2745 componentes) | 129 coincidencias (12 Critical, 44 High) | Informativo: app C1/H18, cloud C1/H15 |
| Trivy | 11 CRITICAL / 32 HIGH (2026-11-03) y 11 / 33 (reescaneo 2026-11-21, base más reciente) | App C1/H2 exceptuadas; imagen cloud C1 (marsdb, exceptuada) / H0 → APTA |
| Gitleaks | 0 secretos en el historial | 0 |

## 3. Código seguro
Fragmentos antes/después citados del parche auditado (`app-hardened/patches/v2/correcciones-cierre-brechas.patch`), con la prueba
asociada: [`evidence/fase-3/codigo-seguro.md`](../../evidence/fase-3/codigo-seguro.md).

| Práctica | Archivo (original `f189f5212`) | Parche | Prueba y resultado |
|---|---|---|---|
| Consultas parametrizadas (SQLi) | `routes/login.ts:34`, `routes/search.ts:23` | 01, 02 | A1-A3: vulnerable → 401/sin datos sin WAF; mitigado en Render |
| Codificación de salida (XSS) | `search-result.component.ts:146`, `routes/saveLoginIp.ts` | 12, 14 | XSS en Chromium: 5/6 → 0/6 |
| Validación de origen (CSRF) | `server.ts` (nuevo middleware) | 12 | T6 con origen ajeno: 403; control T6b: cambio aplicado |
| JWT con algoritmo fijo y clave fuera del código | `lib/insecurity.ts:52` | 04, 11 | `alg=none` y HS256: 401; token RS256 legítimo: 200 |

## 4. Diferencia entre pipeline verde y release aprobado
Un `devsecops.yml` en verde no aprueba un release: ese workflow escanea deliberadamente la imagen vulnerable y solo informa.
La aprobación técnica la da `release.yml`. «APTA» significa que el artefacto cumple la política, no que esté libre de vulnerabilidades.
