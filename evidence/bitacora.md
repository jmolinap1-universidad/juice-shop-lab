# Bitácora de evidencias

Cada línea: fecha, fase, comando, herramienta/versión, resultado. Hashes en `MANIFEST.sha256`.

| Fecha | Fase | Comando | Herramienta / versión | Resultado |
|---|---|---|---|---|
| 2026-11-03T22:43:36-06:00 | 0 | `powershell -File scripts/diagnostico.ps1` | PowerShell 5.1 | Win11 Pro 26300, i3-10100F 4C/8T, 31.9 GB RAM, Docker 29.9.2 (WSL2), Compose v5.6.1, Git 2.56; sin Node/Python locales → herramientas vía Docker. evidence/fase-0/diagnostico.txt |
| 2026-11-03T22:43:36-06:00 | 1 | `git submodule add juice-shop; git checkout v20.3.0` | git 2.56 | app/ fijado en v20.3.0 (commit f189f521, 2026-10-12) |
| 2026-11-03T22:43:37-06:00 | 1 | `docker compose -f deploy/lab/docker-compose.yml up -d; curl /rest/admin/application-version` | Docker 29.9.2, imagen juice-shop:v20.3.0 sha256:cea5a4af… | HTTP 200 {"version":"20.3.0"}; puerto publicado solo en 127.0.0.1:3000 |
| 2026-11-03T22:54:40-06:00 | 2 | `terraform init -backend=false; validate; plan -refresh=false (offline_plan=true, sin credenciales)` | Terraform 1.16.7, provider hashicorp/aws ~>6.0 | valid=true; Plan: 45 to add. evidence/fase-2/terraform-plan.txt, terraform-validate.json |
| 2026-11-03T22:54:40-06:00 | 2 | `checkov -d infra/terraform (inicial)` | Checkov 3.4.0 | 142 passed / 7 failed. evidence/fase-2/checkov-inicial/ |
| 2026-11-03T22:54:40-06:00 | 2 | `checkov -d infra/terraform (tras correcciones)` | Checkov 3.4.0 | 144 passed / 0 failed / 5 skipped justificados. evidence/fase-2/checkov-final/ |
| 2026-11-03T23:03:54-06:00 | 3 | `semgrep scan p/owasp-top-ten p/nodejs p/typescript security/semgrep app/` | Semgrep 1.181.1 | 90 hallazgos. evidence/fase-3/sast/semgrep.json |
| 2026-11-03T23:07:21-06:00 | 3 | `npm install --package-lock-only; npm audit --omit=dev` | npm (node 24.11.0) | "vulnerabilities":{"info":0,"low":2,"moderate":11,"high":20,"critical":7,"total":40} |
| 2026-11-03T23:07:22-06:00 | 3 | `osv-scanner scan source -L package-lock.json:<generado>` | OSV-Scanner 2.7.0 | 62 IDs de vulnerabilidad únicos. evidence/fase-3/sca/osv.json |
| 2026-11-03T23:07:22-06:00 | 3 | `syft <imagen> -o cyclonedx-json` | Syft 1.55.0 | 2745 componentes |
| 2026-11-03T23:07:22-06:00 | 3 | `grype sbom:` | Grype 0.120.1 | 24 Critical / 88 High (cuenta incluye entradas relacionadas) |
| 2026-11-03T23:08:37-06:00 | 3 | `gitleaks git (historial del repo del equipo, sin submódulo)` | Gitleaks 8.30.1 | 0 secretos. evidence/fase-3/secrets/gitleaks.json |
| 2026-11-03T23:09:39-06:00 | 5 | `trivy image --scanners vuln,secret,misconfig bkimminich/juice-shop:v20.3.0@sha256:cea5a4af4aacee498c491491af0408934ec81d004035c0a02ef3e54395e3bf27` | Trivy 0.75.0 | 0 CRITICAL / 0 HIGH |
| 2026-11-03T23:09:39-06:00 | 5 | `hadolint app/Dockerfile` | Hadolint 2.15.1 | 11 avisos |
| 2026-11-03T23:14:33-06:00 | 3 | `sed (redacción de PEM en semgrep.sarif/json)` | GNU sed | Fragmento de clave de prueba de Juice Shop redactado en la evidencia SAST; hallazgo hardcoded-private-key se mantiene |
