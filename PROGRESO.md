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

## Problemas / bloqueos
- (Resuelto 2026-11-03) push a GitHub completado tras el inicio de sesión del equipo.

## Siguiente tarea
1. Equipo: DFD en Threat Dragon, IDs ASVS 5.0.0, capturas Burp, ensamblar documentos Word con plantilla T3.
2. [P] Recompilar app-hardened, actualizar dependencias con CVE, desplegar SIEM, arquitectura cloud (aprobación de costos).
