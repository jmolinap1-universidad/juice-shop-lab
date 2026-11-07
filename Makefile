# Atajos del laboratorio (requiere bash + Docker). En Windows: Git Bash.
LAB := deploy/lab/docker-compose.yml
LAB_URL := http://127.0.0.1:3000

HARD := deploy/hardened/docker-compose.yml

.PHONY: lab-up lab-down hard-up hard-down scan attack report

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
