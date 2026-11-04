# Progreso del proyecto

## Etapa actual
Etapa 6 – Fase 6 completada (WAF, mitigaciones, riesgo residual). Proyecto en revisión final.

## Completado
- 2026-11-03 Etapa 0: diagnóstico (`evidence/fase-0/diagnostico.txt`): Win11, i3-10100F, 31.9 GB RAM,
  Docker 29.9.2 + WSL2, Compose v5.6.1, Git 2.56. Sin Node/Python locales → todas las herramientas vía Docker.
- 2026-11-03 Etapa 1: estructura del repo; Juice Shop como submódulo `app/` en v20.3.0 (f189f521);
  laboratorio `deploy/lab` solo en 127.0.0.1:3000 (verificado HTTP 200). Pipeline `.github/workflows/devsecops.yml`.
- 2026-11-03 Fase 1: `docs/fase-1/fase1-modelado-amenazas.md` (16 activos CIA, DFD Mermaid, 20 amenazas STRIDE
  con referencias a código, DREAD, 7 capas, trazabilidad ASVS). DFD en Threat Dragon: pendiente (equipo).
- 2026-11-03 Fase 2: Terraform AWS (VPC, ALB TLS 1.3, WAFv2, ECS Fargate privado, KMS, IAM mínimo, logs).
  validate OK, plan offline 45 recursos; Checkov 142/7 → 144/0 (5 omisiones justificadas).
- 2026-11-03 Fase 3 (local): Semgrep 90 hallazgos; Gitleaks 0; npm audit 40 (7 críticas, 20 altas);
  OSV 62 vulns; SBOM Syft 2745 componentes; Grype 12 críticas/44 altas.
- 2026-11-03 Etapa 1-3: repo publicado; primer run de Actions 7/7 success (run 41778118097).
- 2026-11-03 Fase 5 (antes): Trivy imagen original 11 CRITICAL/32 HIGH, 5 secretos; Hadolint 11 avisos.
- 2026-11-03 Fase 4: 11/11 casos VULNERABLE (security/attacks/run.sh); ZAP baseline PASS 61/WARN 7; docs/fase-4/.
- 2026-11-03 Fase 5: Hadolint 11→0; runtime endurecido (read-only, cap_drop ALL, no-new-privileges, límites) verificado con docker inspect; Trivy CVE sin cambio (se difieren a Fase 6); Checkov 47/0. docs/fase-5/.
- 2026-11-03 Fase 6: entorno endurecido (app read-only + WAF CRS); ataques 11/11 MITIGADO (residual); logs de bloqueo del WAF; 7 parches de código; matriz inherente vs residual e ISO 27005. docs/fase-6/.

- 2026-11-04 Cierre académico Fases 4-5 (plan PLAN_PRIORIZACION_FASES_4_Y_5):
  - **F45-01/02/03/04/05 (P0) reclasificación honesta** en `docs/fase-4/`: taxonomía en 4 clases
    (explotación demostrada / exposición / configuración insegura / ausencia de control). A5 CWE-22→**CWE-538**
    (exposición de archivo, no traversal); A11 CWE-798→**CWE-200** (clave PÚBLICA servida; el riesgo real es la
    clave privada embebida en código, hallazgo SAST aparte); A8 CORS = configuración insegura (no robo de datos
    demostrado); A10 = ausencia de rate limiting (no prueba de contraseña adivinada). Etiquetas corregidas
    también en `security/attacks/run.sh` para futuros runs.
  - **F45-06 (P0) conteo reproducible de rutas**: 50 GET+40 POST+13 PUT+5 DELETE+1 PATCH = **109** (corrige
    "102"); comando determinista documentado.
  - **F45-07 (P1) BOLA/IDOR genuino** con dos cuentas de laboratorio: usuario B leyó la cesta de A
    (`UserId:26` vs `UserId:27`, HTTP 200) → **VULNERABLE confirmado** (CWE-639). Evidencia `evidence/fase-4/bola/`.
  - **F45-08/09 (P1)**: metodología black box (pasiva) separada de gray/white; perímetro con conteo reproducible;
    webhooks = no aplica. Matriz de cobertura OWASP Top 10 honesta (probado/revisado/no probado/no aplica).
  - **F45-10/11/12 (P1) Fase 5**: tabla artefacto **auditado** (`app-hardened/Dockerfile`, Hadolint 11→0, NO
    desplegado) vs **desplegado** (`deploy/hardened/Dockerfile`→`juice-hardened:local`, endurecimiento por
    runtime); CVE de imagen siguen presentes (mitigadas en ejecución, no eliminadas); 5 skips Checkov justificados.
  - Lab levantado solo en `127.0.0.1:3000`, pruebas ejecutadas y lab detenido. Evidencia histórica `antes/`
    preservada sin cambios. MANIFEST (72 archivos) y bitácora actualizados; Gitleaks limpio en rutas commiteadas.

## Problemas / bloqueos
- (Resuelto 2026-11-03) push a GitHub completado tras el inicio de sesión del equipo.

## Pendientes diferidos (NO en esta entrega de Fases 4-5)
- Despliegue cloud AWS (`terraform apply`, EC2/ECS/ALB/WAFv2/RDS/CDN/API Gateway): **pospuesto para evitar
  costos** (solo validación estática Checkov + plan offline). BD administrada (SQLite, no RDS). SIEM/monitoreo
  cloud. Fase 6 (WAF/residual) fuera del alcance de esta entrega parcial.
- Recompilar `app-hardened` con los 7 parches y medir residual sin WAF; actualizar dependencias con CVE.
- Equipo: DFD en Threat Dragon, confirmación IDs ASVS 5.0.0, capturas manuales con Burp, logo UMG en portada.
