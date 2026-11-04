# Proyecto final – Seguridad en Aplicaciones (MASI, UMG, 2026)

Laboratorio de seguridad sobre **OWASP Juice Shop** (aplicación principal). Sustituye al caso ficticio
Kakaw Store (Magento en AWS) de las Fases 1-3; se reutiliza su **metodología y arquitectura**, nunca sus
datos ni resultados simulados.

Equipo: Molina Pérez Juan Carlos, Sánchez Flores Juan Walter Ernesto, García Gonzalez Leopoldo Emanuel,
Cambara Castillo Vanessa Odeth. Catedrático: Matthew Alexander Seigne Samayoa.

## Reglas obligatorias
1. **Aislamiento:** la versión vulnerable solo escucha en `127.0.0.1` o dentro de la red de Docker / del job
   de CI. Nunca se publica en Internet. La versión endurecida solo por túnel o con acceso restringido.
2. **Alcance autorizado:** solo se atacan instancias propias de este laboratorio. Nunca la demo pública de
   Juice Shop ni sistemas de terceros.
3. **Cero resultados inventados:** todo hallazgo, métrica o riesgo en los documentos debe tener evidencia en
   `evidence/` (JSON/SARIF/HTML, captura, request/response, enlace a una ejecución de GitHub Actions) con su
   hash SHA-256 en `evidence/MANIFEST.sha256` y una entrada en `evidence/bitacora.md`.
4. **Pedir autorización antes de:** instalaciones con privilegios de administrador, cambios del sistema,
   borrar archivos fuera de este proyecto, publicar servicios, crear recursos con costo (AWS) o usar credenciales.
5. **No manejar credenciales:** las claves de AWS, GitHub o tokens las configura el equipo. Nunca se
   escriben en el repositorio (Gitleaks lo verifica).
6. Versiones fijas: Juice Shop en un tag de release concreto; herramientas con versión fija en el Makefile/CI.

## Estructura objetivo
```
app/                 Juice Shop (tag fijo, sin modificar)
app-hardened/        copia con correcciones (una rama/commit por vulnerabilidad)
deploy/lab/          docker-compose vulnerable (127.0.0.1)
deploy/hardened/     compose con WAF (Nginx + ModSecurity + OWASP CRS), cabeceras, logs
infra/terraform/     arquitectura AWS (Fase 2) – validada con Checkov y `terraform plan`
.github/workflows/   SAST, SCA, imagen, IaC, ZAP (DAST contra contenedor efímero del job)
security/            reglas Semgrep propias, casos de ataque automatizados (antes/después)
evidence/fase-N/     reportes, capturas, requests, MANIFEST.sha256, bitacora.md
docs/                entregables Word/PDF y matrices de riesgo
Makefile             lab-up, lab-down, scan, attack, report
```

## Fases y entregables
| Fase | Contenido | Evidencia mínima |
|---|---|---|
| 1 | Inventario CIA, DFD, STRIDE, DREAD, 7 capas | DFD (Threat Dragon), tablas desde el código real |
| 2 | Arquitectura cloud, flujos, IAM mínimo, WAF, API Gateway, cifrado | Terraform + Checkov + plan |
| 3 | DevSecOps: GitHub Actions, SAST (Semgrep/CodeQL), SCA (npm audit/OSV/SBOM), código seguro | Ejecuciones de Actions, SARIF |
| 4 | Black/Gray/White Box, casos de abuso, superficie de ataque | ZAP, Burp (manual, equipo), scripts de ataque |
| 5 | Contenedores (Trivy, Hadolint), hardening, IaC, WAF, monitoreo/SIEM | Trivy antes/después, logs del WAF |
| 6 | Riesgo inherente vs. residual, tratamiento ISO/IEC 27005, informe final | Mismos ataques antes/después |

Metodología heredada de Kakaw (Fase 1): CIA A=3/M=2/B=1, criticidad C+I+D; DREAD 1-10 promedio;
riesgo por capa P×I (1-4); trazabilidad amenaza → requisito → control → evidencia.
Formato de documentos: carátula plantilla T3, Arial 12, justificado, interlineado 1.5, APA 7.

## Estado
- [ ] Etapa 0: confirmar Docker Desktop/WSL2, RAM, Git; crear repo en GitHub
- [ ] Etapa 1: estructura, Juice Shop fijado, compose del laboratorio, primer CI
