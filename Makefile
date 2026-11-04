# Atajos del laboratorio (requiere bash + Docker). En Windows: Git Bash.
LAB := deploy/lab/docker-compose.yml

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

attack:     ## Casos de ataque automatizados (Fase 4) – pendiente
	@echo "Pendiente: security/attacks/ se implementa en la Fase 4"; exit 1

report:     ## Regenera el manifiesto de evidencias
	bash scripts/manifest.sh
