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
| 2026-11-03T23:19:56-06:00 | 3 | `GitHub Actions devsecops (push 6ae81ea)` | ubuntu-24.04; versiones fijas en el workflow | 7/7 jobs success (Gitleaks, Semgrep, CodeQL, SCA, Trivy/Hadolint, Terraform/Checkov, ZAP baseline); 7 artefactos. https://github.com/jmolinap1-universidad/juice-shop-lab/actions/runs/41778118097 |
| 2026-11-03T23:25:11-06:00 | 4 | `security/attacks/run.sh (http://127.0.0.1:3000, antes)` | curl + código del laboratorio | 11 VULNERABLE / 0 MITIGADO de 11. /c/Users/CHINO/Desktop/Proyecto Seg Aplicacion/evidence/fase-4/antes/resumen-ataques.md |
| 2026-11-03T23:29:07-06:00 | 4 | `zap-baseline.py -t http://127.0.0.1:3000 (vía host.docker.internal)` | OWASP ZAP 2.17.0 (zap-stable:20261016) | WARN-NEW 7, PASS 61, FAIL 0. evidence/fase-4/zap/ |
| 2026-11-03T23:42:08-06:00 | 5 | `hadolint app-hardened/Dockerfile` | Hadolint 2.15.1 | 0 avisos (antes: 11). evidence/fase-5/despues/hadolint-Dockerfile.json |
| 2026-11-03T23:42:08-06:00 | 5 | `docker build -f deploy/hardened/Dockerfile; docker run --read-only --cap-drop ALL --security-opt no-new-privileges; docker inspect` | Docker 29.9.2 | App HTTP 200; ReadonlyRootfs=true, CapDrop=[ALL], no-new-privileges, pids=200, mem=1g, user 65532, escritura en / BLOQUEADA (EROFS). evidence/fase-5/despues/runtime-hardening-inspect.txt |
| 2026-11-03T23:42:09-06:00 | 5 | `trivy image juice-hardened:local (después)` | Trivy 0.75.0 | 11 CRITICAL/32 HIGH — idénticas a la imagen original: el repaquetado no corrige CVE de dependencias (se tratan en Fase 6) |
| 2026-11-03T23:42:09-06:00 | 5 | `checkov -d deploy -d app-hardened --framework dockerfile,yaml` | Checkov 3.4.0 | 47 passed / 0 failed. evidence/fase-5/iac/ |
| 2026-11-03T23:52:07-06:00 | 4 | `security/attacks/run.sh (http://127.0.0.1:8080, despues)` | curl + código del laboratorio | 0 VULNERABLE / 11 MITIGADO de 11. /c/Users/CHINO/Desktop/Proyecto Seg Aplicacion/evidence/fase-4/despues/resumen-ataques.md |
| 2026-11-03T23:56:54-06:00 | 6 | `docker compose -f deploy/hardened up -d --build (app read-only + WAF CRS)` | ModSecurity 3.0.17, CRS 4.25.2, nginx | App healthy; WAF en 127.0.0.1:8080; 855 reglas cargadas |
| 2026-11-03T23:56:54-06:00 | 6 | `security/attacks/run.sh http://127.0.0.1:8080 (despues)` | curl + WAF | 0 VULNERABLE / 11 MITIGADO de 11 (residual). evidence/fase-4/despues/ |
| 2026-11-03T23:56:54-06:00 | 6 | `recolección de audit log del WAF` | ModSecurity JSON audit | 64 transacciones; CRS 942100/949110 (SQLi) y VP propias 100001/100002. evidence/fase-6/waf-logs/ |
| 2026-11-03T23:56:54-06:00 | 6 | `git apply --check app-hardened/patches/*.patch` | git 2.56 | 6/7 aplican; 04 manual (contiene secreto redactado). app-hardened/patches/ |
| 2026-11-04T00:03:30-06:00 | 6 | `GitHub Actions devsecops (push c8f65c1, Fase 6)` | ubuntu-24.04; versiones fijas | 7/7 jobs success incl. Gitleaks con .gitleaks.toml. https://github.com/jmolinap1-universidad/juice-shop-lab/actions/runs/41782674548 |
| 2026-11-04T00:20:01-06:00 | 4 | `security/attacks/run.sh (http://127.0.0.1:3000, antes)` | curl + código del laboratorio | 11 VULNERABLE / 0 MITIGADO de 11. /c/Users/CHINO/Desktop/Proyecto Seg Aplicacion/evidence/fase-4/antes/resumen-ataques.md |
| 2026-11-04T00:31:59-06:00 | 4 | `nmap -sV -Pn -p 3000 (red del contenedor)` | Nmap 7.98 (instrumentisto/nmap) | 3000/tcp open; banner HTTP revela ACAO:*. evidence/fase-4/nmap-127-3000.txt |
| 2026-11-04T00:31:59-06:00 | 4 | `generación del documento Word+PDF (Fases 4-5, APA 7, 14 capturas)` | docx-js 9.5.1, LibreOffice | docs/evidencias-fase4-5/*.docx y *.pdf (19 páginas) |
| 2026-11-04T14:02:41-06:00 | 4 | `security/attacks/run.sh (http://127.0.0.1:3000, inherente-2026-11-04)` | curl + código del laboratorio | 11 VULNERABLE / 0 MITIGADO de 11. /c/Users/CHINO/Desktop/Proyecto Seg Aplicacion/evidence/fase-4/inherente-2026-11-04/resumen-ataques.md |
| 2026-11-04T17:08:35-06:00 | 4 | `sqlmap -u http://juice-lab:3000/rest/products/search?q= --batch --level=3 --risk=2` | sqlmap 1.10.4 (parrotsec/sqlmap, red del lab) | Parametro q VULNERABLE (boolean+time-based blind, SQLite); evidence/fase-4/blackbox-2026-11-04/ |
