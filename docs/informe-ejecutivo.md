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
| 6 | Operaciones, monitoreo y riesgo residual | WAF ModSecurity/CRS 4.25.2 mapeado al OWASP Top 10:2025 + **RASP** Aikido Zen + **SIEM** (Alloy → Loki → Grafana, 7 reglas; 6 dispararon en las pruebas). Defensa completa: A1-A11 mitigados, **BOLA residual** (el WAF no lo bloquea; el SIEM lo detecta). 24 riesgos tratados (Aceptar/Eliminar/Evitar/Mitigar/Transferir): Crítico **8 → 1**, Alto **15 → 9**; heatmaps antes/después. `docs/fase-6/` |

## Reducción de riesgo (inherente → residual)
- Observaciones de ataque activas: **11 → 0** (4 explotación demostrada + 7 debilidades, todas bloqueadas por el WAF/endurecimiento).
  **Excepción verificada:** el BOLA/IDOR (A12) sigue explotable a través del WAF; queda detectado por el SIEM y su
  eliminación requiere desplegar el parche 08 (`evidence/fase-6/defensa-completa/bola/`).
- Registro de 24 riesgos (método reproducible, `docs/fase-6/tratamiento-riesgo.md`): Crítico 8 → 1 (R03, clave
  privada JWT embebida), Alto 15 → 9, Medio 1 → 9, Bajo 0 → 5. Solo los controles verificados reducen el residual.
- Hallazgo operativo: el RASP en modo bloqueo por defecto provocaba la caída del proceso Node; corregido y
  verificado (`evidence/fase-6/rasp/`).
- Compromiso total como administrador (SQLi y asignación masiva): **posible → bloqueado** por el WAF (reglas
  CRS 942100/949110 y parches virtuales 100001/100002), con evidencia en `evidence/fase-6/waf-logs/`.
- Riesgo por capas: capas de datos, código y perímetro de aplicación bajan de **Crítico** a **Medio/Bajo**.
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
