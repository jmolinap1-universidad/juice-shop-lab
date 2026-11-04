# Bitácora de evidencias

Cada línea: fecha, fase, comando, herramienta/versión, resultado. Hashes en `MANIFEST.sha256`.

| Fecha | Fase | Comando | Herramienta / versión | Resultado |
|---|---|---|---|---|
| 2026-11-03T22:43:36-06:00 | 0 | `powershell -File scripts/diagnostico.ps1` | PowerShell 5.1 | Win11 Pro 26300, i3-10100F 4C/8T, 31.9 GB RAM, Docker 29.9.2 (WSL2), Compose v5.6.1, Git 2.56; sin Node/Python locales → herramientas vía Docker. evidence/fase-0/diagnostico.txt |
| 2026-11-03T22:43:36-06:00 | 1 | `git submodule add juice-shop; git checkout v20.3.0` | git 2.56 | app/ fijado en v20.3.0 (commit f189f521, 2026-10-12) |
| 2026-11-03T22:43:37-06:00 | 1 | `docker compose -f deploy/lab/docker-compose.yml up -d; curl /rest/admin/application-version` | Docker 29.9.2, imagen juice-shop:v20.3.0 sha256:cea5a4af… | HTTP 200 {"version":"20.3.0"}; puerto publicado solo en 127.0.0.1:3000 |
