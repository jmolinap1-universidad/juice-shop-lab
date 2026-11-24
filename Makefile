# Atajos del laboratorio (requiere bash + Docker). En Windows: Git Bash.
LAB := deploy/lab/docker-compose.yml
LAB_URL := http://127.0.0.1:3000

HARD := deploy/hardened/docker-compose.yml

.PHONY: lab-up lab-down hard-up hard-down scan attack report ops-up ops-down risk risk-vigente risk-cierre-tecnico ops-validar corregida-build ops-corregido-up ops-corregido-ps ops-corregido-down release validar-artefacto

lab-up:     ## Laboratorio vulnerable solo en 127.0.0.1:3000
	docker compose -f $(LAB) up -d

lab-down:
	docker compose -f $(LAB) down

hard-up:    ## Entorno endurecido (app read-only + WAF) en 127.0.0.1:8080
	docker compose -f $(HARD) up -d --build

hard-down:
	docker compose -f $(HARD) down -v

scan:       ## SAST, secretos, SCA, contenedores e IaC → evidence/
	bash scripts/scan.sh all

attack:     ## Casos de ataque automatizados (Fase 4) contra el lab local; cada corrida en carpeta propia
	@curl -s -o /dev/null --max-time 5 $(LAB_URL) \
		|| { echo "El laboratorio no responde en $(LAB_URL). Ejecuta 'make lab-up' primero."; exit 1; }
	ATTACK_TAG=run-$$(date +%Y%m%d-%H%M%S) bash security/attacks/run.sh $(LAB_URL)

report:     ## Regenera el manifiesto de evidencias
	bash scripts/manifest.sh

# --- Fase 6 VIGENTE: variante corregida (hito A) + WAF + RASP + SIEM (proyecto juice-corregida-defensa) ---
corregida-build: ## Construye juice-corregida(-rasp):local desde app/ fijado, verificando cada parche contra el diff auditado
	bash scripts/construir-corregida.sh

ops-corregido-up: ## VIGENTE: corregida + WAF + RASP + SIEM. WAF http://127.0.0.1:8080 (o WAF_PORT=8088), Grafana :3001
	WAF_PORT=$(or $(WAF_PORT),8080) bash scripts/ops-corregido.sh up

ops-corregido-ps: ## Estado, salud, reinicios, imagen y variante de cada contenedor
	bash scripts/ops-corregido.sh ps

ops-corregido-down: ## Detiene el stack vigente SIN borrar volúmenes
	bash scripts/ops-corregido.sh down

# --- Fase 6 HISTÓRICO (2026-11-10): imagen OFICIAL vulnerable detrás de WAF + RASP + SIEM (residual v2) ---
ops-up:     ## HISTÓRICO: imagen oficial + WAF + RASP + SIEM (no es la configuración vigente). WAF_PORT=8088 si 8080 está ocupado
	@if [ -n "$$(docker ps -q --filter label=com.docker.compose.project=juice-corregida-defensa)" ]; then \
		echo "RECHAZADO: el stack VIGENTE (ops-corregido) está activo; deténgalo con 'make ops-corregido-down'."; exit 1; fi
	@echo "AVISO: stack HISTÓRICO con la imagen OFICIAL vulnerable (residual v2). El vigente es 'make ops-corregido-up'."
	cd deploy/hardened && WAF_PORT=$(or $(WAF_PORT),8080) docker compose -f docker-compose.yml -f docker-compose.ops.yml up -d --build

ops-down:
	cd deploy/hardened && docker compose -f docker-compose.yml -f docker-compose.ops.yml down

risk:       ## Fase 6: valida el registro (falla si hay reducciones sin control probado), heatmaps y tratamiento-riesgo.md
	MSYS_NO_PATHCONV=1 docker run --rm -v "$(CURDIR)":/r python:3.12-slim@sha256:5e2bdb1b0d542d5039cffb8181c65930093949194a65c365dfb1b0fe13a4fa5b \
		sh -c 'pip install -q --no-cache-dir --root-user-action=ignore matplotlib==3.9.2 && python -I /r/docs/fase-6/datos/riesgo.py /r && python -I /r/docs/fase-6/datos/generar_md.py /r'

risk-vigente: ## Fase 6 VIGENTE (cierre): registro de la variante corregida + defensa; valida, heatmaps y tabla en docs/fase-6/riesgo-vigente/
	MSYS_NO_PATHCONV=1 docker run --rm -v "$(CURDIR)":/r python:3.12-slim@sha256:5e2bdb1b0d542d5039cffb8181c65930093949194a65c365dfb1b0fe13a4fa5b \
		sh -c 'pip install -q --no-cache-dir --root-user-action=ignore matplotlib==3.9.2 && python -I /r/docs/fase-6/datos/construir_riesgos_vigente.py /r && python -I /r/docs/fase-6/datos/riesgo.py /r docs/fase-6/datos/riesgos-vigente.json docs/fase-6/riesgo-vigente && python -I /r/docs/fase-6/datos/generar_md.py /r docs/fase-6/riesgo-vigente/riesgos-calculados.json docs/fase-6/riesgo-vigente/tratamiento-riesgo-vigente.md "Fase 6 – Tratamiento formal del riesgo (configuración VIGENTE: variante corregida + defensa, cierre 2026-11-21)"'

# --- Cierre técnico (2026-11-23) ---
release:    ## Pipeline de RELEASE con puerta (Gitleaks, Hadolint, Semgrep propias, Trivy, SBOM Syft, Grype); falla si no cumple la política
	bash scripts/pipeline-release.sh juice-corregida-rasp:local evidence/release-$$(date +%Y%m%d-%H%M%S)

validar-artefacto: ## Regresión funcional y de seguridad del artefacto en ejecución, sin WAF y con WAF (requiere ops-corregido-up)
	WAF_PORT=$(or $(WAF_PORT),8088) bash scripts/validar-artefacto.sh evidence/validacion-$$(date +%Y%m%d-%H%M%S)

risk-cierre-tecnico: ## Registro de riesgos del cierre técnico (delta sobre el vigente); valida, heatmaps y tabla en docs/fase-6/riesgo-cierre-tecnico/
	MSYS_NO_PATHCONV=1 docker run --rm -v "$(CURDIR)":/r python:3.12-slim@sha256:5e2bdb1b0d542d5039cffb8181c65930093949194a65c365dfb1b0fe13a4fa5b \
		sh -c 'pip install -q --no-cache-dir --root-user-action=ignore matplotlib==3.9.2 && python -I /r/docs/fase-6/datos/construir_riesgos_cierre_tecnico.py /r && python -I /r/docs/fase-6/datos/riesgo.py /r docs/fase-6/datos/riesgos-cierre-tecnico.json docs/fase-6/riesgo-cierre-tecnico && python -I /r/docs/fase-6/datos/generar_md.py /r docs/fase-6/riesgo-cierre-tecnico/riesgos-calculados.json docs/fase-6/riesgo-cierre-tecnico/tratamiento-riesgo-cierre-tecnico.md "Tratamiento formal del riesgo — cierre técnico (2026-11-23): variante corregida-cierre-tecnico + defensa local"'

ops-validar: ## Fase 6: escenarios del RASP sin WAF (R22) con registro HTTP y disponibilidad (requiere make ops-up)
	bash security/ops/escenario-rasp.sh "$(CURDIR)/evidence/fase-6/validacion-$$(date +%F)/rasp-monitoreo" false
	bash security/ops/escenario-rasp.sh "$(CURDIR)/evidence/fase-6/validacion-$$(date +%F)/rasp-bloqueo-integrado" true
