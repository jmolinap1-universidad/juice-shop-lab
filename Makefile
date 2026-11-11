# Atajos del laboratorio (requiere bash + Docker). En Windows: Git Bash.
LAB := deploy/lab/docker-compose.yml
LAB_URL := http://127.0.0.1:3000

HARD := deploy/hardened/docker-compose.yml

.PHONY: lab-up lab-down hard-up hard-down scan attack report ops-up ops-down risk ops-validar

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

ops-up:     ## Fase 6: endurecido + RASP + SIEM (Grafana 127.0.0.1:3001). Si 8080 está ocupado: make ops-up WAF_PORT=8088
	cd deploy/hardened && WAF_PORT=$(or $(WAF_PORT),8080) docker compose -f docker-compose.yml -f docker-compose.ops.yml up -d --build

ops-down:
	cd deploy/hardened && docker compose -f docker-compose.yml -f docker-compose.ops.yml down

risk:       ## Fase 6: valida el registro (falla si hay reducciones sin control probado), heatmaps y tratamiento-riesgo.md
	MSYS_NO_PATHCONV=1 docker run --rm -v "$(CURDIR)":/r python:3.12-slim@sha256:5e2bdb1b0d542d5039cffb8181c65930093949194a65c365dfb1b0fe13a4fa5b \
		sh -c 'pip install -q --no-cache-dir --root-user-action=ignore matplotlib==3.9.2 && python -I /r/docs/fase-6/datos/riesgo.py /r && python -I /r/docs/fase-6/datos/generar_md.py /r'

ops-validar: ## Fase 6: escenarios del RASP sin WAF (R22) con registro HTTP y disponibilidad (requiere make ops-up)
	bash security/ops/escenario-rasp.sh "$(CURDIR)/evidence/fase-6/validacion-$$(date +%F)/rasp-monitoreo" false
	bash security/ops/escenario-rasp.sh "$(CURDIR)/evidence/fase-6/validacion-$$(date +%F)/rasp-bloqueo-integrado" true
