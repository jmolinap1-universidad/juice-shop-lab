# Informe ejecutivo — Laboratorio de Seguridad de Aplicaciones (OWASP Juice Shop)

Maestría en Seguridad Informática, UMG, 2026 · Curso: Seguridad en Aplicaciones · Catedrático: Matthew Alexander Seigne Samayoa.
Equipo: Molina Pérez Juan Carlos · Sánchez Flores Juan Walter Ernesto · García Gonzalez Leopoldo Emanuel · Cambara Castillo Vanessa Odeth.

Repositorio: https://github.com/jmolinap1-universidad/juice-shop-lab

## Objetivo
Evaluar y reducir el riesgo de una aplicación web real (OWASP Juice Shop v20.3.0) a lo largo de seis fases,
con evidencia verificable, midiendo el **riesgo inherente** (aplicación vulnerable) frente al **riesgo residual**
(aplicación endurecida), bajo reglas estrictas de aislamiento (solo `127.0.0.1` / CI) y sin resultados inventados.

## Resultados por fase
| Fase | Entregable | Resultado verificado |
|---|---|---|
| 1 | Modelado de amenazas | 16 activos (CIA), DFD, 20 amenazas STRIDE con referencias a código, DREAD, 7 capas, trazabilidad ASVS. `docs/fase-1/` |
| 2 | Arquitectura cloud segura | Terraform AWS (VPC, ALB TLS 1.3, WAFv2, ECS privado, KMS, IAM mínimo): `validate` OK, `plan` 45 recursos, Checkov **144/0** (5 omisiones justificadas). `infra/terraform/` |
| 3 | DevSecOps (SAST/SCA) | Semgrep 90 hallazgos; npm audit 40 (7 críticas); OSV 62; SBOM 2 745 comp.; Grype 12 críticas; Gitleaks limpio. Pipeline GitHub Actions **7/7**. `evidence/fase-3/` |
| 4 | Pruebas de seguridad | 11 observaciones: **4 explotación demostrada** (SQLi ×3 + asignación masiva) + 7 debilidades (listados, exposición, CORS, cabeceras, rate limit); BOLA/IDOR confirmado; SQLi corroborada por prueba activa de caja negra (sqlmap); ZAP baseline pasivo. `docs/fase-4/` |
| 5 | Contenedores y hardening | Hadolint **11→0**; runtime read-only + cap_drop ALL + no-new-privileges + límites (verificado con `docker inspect`); Checkov **47/0**. `docs/fase-5/` |
| 6 | Operaciones, monitoreo y riesgo residual | WAF ModSecurity/CRS 4.25.2 (cobertura OWASP Top 10:2025 diferenciando instalado / observado / probado) + **RASP** Aikido Zen con integración que bloquea con HTTP 403 sin caídas + **SIEM** (Alloy → Loki → Grafana, 7 reglas; proxy de solo lectura del socket de Docker). Vía WAF: las 11 condiciones A1-A11 del arnés quedan neutralizadas; **BOLA (A12) sigue vulnerable** (heurística SIEM con falsos positivos). 24 riesgos con residual justificado y validado: Crítico **8 → 4**, Alto **16 → 12**, Medio **0 → 7**, Bajo **0 → 1**. `docs/fase-6/` |

## Reducción de riesgo (inherente → residual)
- Condiciones del arnés A1-A11 (4 explotación demostrada + 7 debilidades): presentes en la línea base y
  **neutralizadas a través del WAF** (evidence/fase-6/validacion-2026-11-10/03-waf-rasp-siem/). Son 11 condiciones,
  no 11 explotaciones; A11 (clave pública) no es una vulnerabilidad. Sin WAF, la app conserva todas salvo la SQLi,
  que el RASP bloquea con HTTP 403 (escenario 2d).
- **BOLA/IDOR (A12) sigue explotable** a través del WAF y del RASP; la alerta del SIEM es una heurística con falsos
  positivos demostrados. Su eliminación requiere desplegar el parche 08.
- Registro de 24 riesgos (`docs/fase-6/tratamiento-riesgo.md`, 301 validaciones automáticas): Crítico 8 → 4
  (R03 clave privada JWT, R06 BOLA, R20 dependencias, R23 datos personales), Alto 16 → 12, Medio 0 → 7, Bajo 0 → 1.
  Solo los controles **probados** reducen el residual; la detección no reduce el impacto.
- Hallazgo operativo: el bloqueo del RASP hacía caer el proceso (por defecto) o dejaba la petición colgada
  (`warn`); corregido con la integración `rasp-guard` (403, disponibilidad 41/41, sin reinicios).
- Compromiso total como administrador (SQLi y asignación masiva): **bloqueado en el perímetro** (CRS
  942100/949110 y parche virtual 100001); la causa sigue en el código hasta desplegar los parches 01, 02 y 06.
- Pendiente de mayor reducción: dependencias con CVE (requiere actualización que rompe retos de Juice Shop) y
  despliegue cloud/SIEM (requiere recursos y aprobación de costos).

## Garantías metodológicas
- **Aislamiento:** la app vulnerable solo escuchó en `127.0.0.1` o dentro del job efímero de CI; el entorno
  endurecido solo tras el WAF en `127.0.0.1:8080`. Nunca se atacó la demo pública ni terceros.
- **Trazabilidad:** cada hallazgo tiene evidencia en `evidence/fase-N/`, su SHA-256 en `evidence/MANIFEST.sha256`
  y una línea en `evidence/bitacora.md` (comando, versión de herramienta, resultado).
- **Reproducibilidad:** todas las herramientas corren vía Docker con versión fijada, tanto en local como en
  GitHub Actions.
- **Sin secretos:** Gitleaks (con allowlist documentada para datos de prueba de Juice Shop) no reporta
  credenciales reales.

## Trabajo a cargo del equipo / propuesto
- DFD en OWASP Threat Dragon; confirmación de los IDs ASVS 5.0.0; capturas manuales con Burp Suite.
- Ensamblado de los documentos Word con la plantilla T3 (carátula UMG, Arial 12, APA 7) a partir de `docs/`.
- [P] Recompilar `app-hardened` con los parches 01-08 y medir el residual sin WAF; actualizar dependencias;
  SIEM en clúster con notificaciones; desplegar la arquitectura cloud de la Fase 2 (con aprobación de costos).
