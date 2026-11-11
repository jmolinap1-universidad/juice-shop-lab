# Progreso del proyecto

## Etapa actual
Etapa 6 – Fase 6 ampliada (2026-11-10): operaciones, monitoreo (RASP + SIEM) y tratamiento formal del riesgo. Proyecto en revisión final.

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
- 2026-11-03 Fase 4: 11 observaciones (4 explotación demostrada + 7 debilidades) con security/attacks/run.sh;
  ZAP baseline **pasivo**; docs/fase-4/. (La afirmación previa "11/11 VULNERABLE" se corrige en la auditoría del 2026-11-04.)
- 2026-11-03 Fase 5: Hadolint 11→0; runtime endurecido (read-only, cap_drop ALL, no-new-privileges, límites) verificado con docker inspect; Trivy CVE sin cambio (se difieren a Fase 6); Checkov 47/0. docs/fase-5/.
- 2026-11-03 Fase 6: entorno endurecido (app read-only + WAF CRS); ataques 11/11 MITIGADO (residual); logs de bloqueo del WAF; 7 parches de código; matriz inherente vs residual e ISO 27005. docs/fase-6/.

- 2026-11-04 Cierre académico Fases 4-5 (plan PLAN_PRIORIZACION_FASES_4_Y_5):
  - **F45-01/02/03/04/05 (P0) reclasificación honesta** en `docs/fase-4/`: taxonomía en 4 clases
    (explotación demostrada / exposición / configuración insegura / ausencia de control). A5 CWE-22→**CWE-538**
    (exposición de archivo, no traversal); A11 CWE-798→**CWE-200** (clave PÚBLICA servida; el riesgo real es la
    clave privada embebida en código, hallazgo SAST aparte); A8 CORS = configuración insegura (no robo de datos
    demostrado); A10 = ausencia de rate limiting (no prueba de contraseña adivinada). Etiquetas corregidas
    también en `security/attacks/run.sh` para futuros runs.
  - **F45-06 (P0) conteo reproducible de rutas**: 50 GET+40 POST+13 PUT+5 DELETE+1 PATCH = **109** (corrige
    "102"); comando determinista documentado.
  - **F45-07 (P1) BOLA/IDOR genuino** con dos cuentas de laboratorio: usuario B leyó la cesta de A
    (`UserId:26` vs `UserId:27`, HTTP 200) → **VULNERABLE confirmado** (CWE-639). Evidencia `evidence/fase-4/bola/`.
  - **F45-08/09 (P1)**: metodología black box (pasiva) separada de gray/white; perímetro con conteo reproducible;
    webhooks = no aplica. Matriz de cobertura OWASP Top 10 honesta (probado/revisado/no probado/no aplica).
  - **F45-10/11/12 (P1) Fase 5**: tabla artefacto **auditado** (`app-hardened/Dockerfile`, Hadolint 11→0, NO
    desplegado) vs **desplegado** (`deploy/hardened/Dockerfile`→`juice-hardened:local`, endurecimiento por
    runtime); CVE de imagen siguen presentes (mitigadas en ejecución, no eliminadas); 5 skips Checkov justificados.
  - Lab levantado solo en `127.0.0.1:3000`, pruebas ejecutadas y lab detenido. Evidencia histórica `antes/`
    preservada sin cambios. MANIFEST (72 archivos) y bitácora actualizados; Gitleaks limpio en rutas commiteadas.

- 2026-11-04 **Auditoría final técnica Fases 4-5** (`docs/AUDITORIA_FINAL_FASES_4_5.md`; sin tocar Word/PDF):
  - **OWASP Top 10:2025** aplicado de forma coherente (se eliminó la mezcla 2021/2025): A4/A6/A8/A9/A11 → **A02**
    (Security Misconfiguration), SQLi → **A05** (Injection), SSRF fusionado en A01, A10 = Mishandling; §6 reescrita.
  - **Prueba activa de caja negra** añadida: **sqlmap 1.10.4** confirma SQLi en `q` (boolean+time-based, SQLite),
    sin leer el código. Evidencia `evidence/fase-4/blackbox-2026-11-04/`.
  - **BOLA/IDOR:** `term/bola.txt` reescrito como transcripción **literal** del run real (timestamp 1793822559,
    `Products:[]`, JSON idéntico a la evidencia); figura `15-bola-idor.png` re-renderizada; evidencia histórica intacta.
  - **`run.sh`**: columna **Clase** (E/X/C/N) + leyenda; deja de rotular todo como "VULNERABLE".
  - Coherencia: Nmap **7.95→7.98**; rutas **102→109** (Fase 1); A5 **CWE-22→CWE-538** y "11/11 explotables"
    reescrito (Fase 6 / informe ejecutivo). Fase 5 verificada contra evidencia (Trivy/Hadolint/Checkov/runtime);
    §1.1 enlaza el SCA (Grype/OSV/SBOM) de Fase 3.
  - **Dictamen:** Fases 4 y 5 técnicamente listas para la redacción académica final. Cloud **no desplegado**
    (sin costos); Fase 6 ampliada y figuras del `.docx` quedan fuera de esta auditoría.

- 2026-11-10 **Fase 6 – Operaciones, monitoreo y ciberseguridad** (`docs/fase-6/`, Word+PDF en `docs/fase-6/entregable/`):
  - Capa de operaciones como override (`deploy/hardened/docker-compose.ops.yml`): **RASP Aikido Zen 1.8.46** in-process y
    **SIEM** Alloy v1.10.2 → Loki 3.5.5 (7 reglas de correlación) → Grafana 12.1.1; todo en 127.0.0.1, sin telemetría externa.
  - WAF mapeado al OWASP Top 10:2025 con inventario real del CRS (`evidence/fase-6/waf/`). Falsos positivos: 6/6 legítimas OK.
  - Defensa completa: A1-A11 mitigados; **BOLA (A12) sigue explotable a través del WAF** → detectado por el SIEM; parche 08 diseñado.
  - RASP: 3 SQLi detectadas (monitoreo) y bloqueadas; **hallazgo**: el bloqueo por defecto hacía caer el proceso Node →
    corregido con `--unhandled-rejections=warn` y verificado (corrida inválida preservada y marcada).
  - SIEM: 6/7 reglas en firing (SQLi, parche virtual, fuerza bruta, rutas sensibles, enumeración BOLA, RASP).
  - Tratamiento formal: 24 riesgos (tipo e impacto), decisiones Aceptar/Eliminar/Evitar/Mitigar/Transferir, método
    reproducible desde el DREAD de la Fase 1; heatmaps: Crítico 8→1, Alto 15→9, Medio 1→9, Bajo 0→5.
    **(Cifras sustituidas por la auditoría de cierre del 2026-11-10: el método anterior reducía el impacto por
    detección y contaba controles no probados. Vigente: Crítico 8→4, Alto 16→12, Medio 0→7, Bajo 0→1.)**

- 2026-11-10 **Auditoría de cierre de la Fase 6** (`docs/fase-6/AUDITORIA_CUMPLIMIENTO_FASE6.md` → `CIERRE_Y_VALIDACION_FASE6.md`):
  - R22: causa raíz en Sequelize (`serialize(async …)`); integración `deploy/hardened/rasp/rasp-guard.js` → bloqueo con
    HTTP 403, disponibilidad 41/41, sin reinicios (antes: caída del proceso o petición colgada 20 s).
  - Riesgo residual explícito y justificado por riesgo; 301 validaciones automáticas (`make risk`) que rechazan
    reducciones sin control probado (prueba negativa incluida). Vigente: Crítico 8→4, Alto 16→12, Medio 0→7, Bajo 0→1.
  - SIEM: Alloy sin root ni socket; proxy de la API de Docker de solo lectura (escrituras 403). Heurística BOLA con
    falso positivo demostrado. Cinco escenarios de validación en `evidence/fase-6/validacion-2026-11-10/`.
  - WAF: tabla instalado / observado / probado; A11 (clave pública) no es vulnerabilidad; 920350 = ruido cuantificado.
  - Documento institucional: instrucciones de sincronización y borrador de validación (no sustituye el entregable).

## Problemas / bloqueos
- (Resuelto 2026-11-03) push a GitHub completado tras el inicio de sesión del equipo.

## Pendientes diferidos (NO en esta entrega de Fases 4-5)
- **Fase 6 (vigentes):** parches 01-08 diseñados sin desplegar (R03, R06, R20 y R23 siguen críticos); bloqueos del RASP
  en sinks distintos de sqlite3 sin probar; reglas CRS de XSS/RCE/LFI sin probar; SIEM sin notificaciones,
  autenticación ni alta disponibilidad; carátula institucional (logo UMG) a cargo del equipo.
- Despliegue cloud AWS (`terraform apply`, EC2/ECS/ALB/WAFv2/RDS/CDN/API Gateway): **pospuesto para evitar
  costos** (solo validación estática Checkov + plan offline). BD administrada (SQLite, no RDS). SIEM/monitoreo
  cloud (el SIEM local de la Fase 6 es de un solo nodo).
- Recompilar `app-hardened` con los 8 parches (incl. 08 BOLA) y medir residual sin WAF; actualizar dependencias con CVE.
- Equipo: DFD en Threat Dragon, confirmación IDs ASVS 5.0.0, capturas manuales con Burp, logo UMG en portada.
