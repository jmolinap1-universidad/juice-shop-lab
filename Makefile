# Atajos del laboratorio (requiere bash + Docker). En Windows: Git Bash.
LAB := deploy/lab/docker-compose.yml
LAB_URL := http://127.0.0.1:3000

HARD := deploy/hardened/docker-compose.yml

.PHONY: lab-up lab-down hard-up hard-down scan attack report ops-up ops-down risk

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

risk:       ## Fase 6: recalcula riesgos, heatmaps y docs/fase-6/tratamiento-riesgo.md (Python en Docker)
	MSYS_NO_PATHCONV=1 docker run --rm -v "$(CURDIR)/docs/fase-6":/f6 python:3.12-slim@sha256:5e2bdb1b0d542d5039cffb8181c65930093949194a65c365dfb1b0fe13a4fa5b \
		sh -c 'pip install -q --no-cache-dir --root-user-action=ignore matplotlib==3.9.2 && python -I /f6/datos/riesgo.py /f6 && python -I /f6/datos/generar_md.py /f6'
