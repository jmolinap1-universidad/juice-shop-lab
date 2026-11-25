# Estado técnico de cierre — 2026-11-23 (actualizado 2026-11-24: despliegue cloud en Render)

**Rama:** `cierre/tecnico-web-seenode` (desde `cierre/fase6-definitiva` = `e6c4109`; `main` = `cc08374`, sin cambios). Publicada en
GitHub (push autorizado por el equipo; sin PR ni merge).
**Artefacto evaluado:** `juice-corregida-rasp:local` = `sha256:2ab64e96129d…`, variante `corregida-cierre-tecnico` (parches 01-13),
fuente verificada contra `app-hardened/patches/v2/correcciones-cierre-tecnico.patch` (sha256 `8cdc9fbb…`), 21 archivos.
**Entorno:** local (127.0.0.1, redes Docker internas) y **cloud: Render, capa gratuita**, `https://juice-lab-masi-staging.onrender.com`
con acceso restringido (`DESPLIEGUE_CLOUD_RENDER.md`; evidencia en `13-cloud/`).
**Evidencia:** `evidence/cierre-tecnico-2026-11-23/` (índice en su `LEAME.md`).

## 1. Requisitos de las seis fases (HISTÓRICO 2026-11-23)
> **Vigente desde el 2026-11-24:** [`MATRIZ_CUMPLIMIENTO_SEIS_FASES.md`](MATRIZ_CUMPLIMIENTO_SEIS_FASES.md) (cierre de brechas: imagen cloud Alpine APTA, XSS en navegador, IaC de Render, release en CI, SIEM cloud automático). Esta tabla se conserva como estaba.
| Fase | Requisito | Estado | Evidencia / configuración |
|---|---|---|---|
| 1 | Inventario ISO/IEC 27001 (35 activos, campos completos) | CUMPLE (local) · PENDIENTE (activos cloud) | `docs/auditoria-final-2026-11-20/INVENTARIO_ACTIVOS_ISO27001.md`; no existen recursos cloud reales que inventariar |
| 1 | STRIDE (6 categorías) y DREAD por amenaza/caso | CUMPLE | `docs/auditoria-final-2026-11-20/TRAZABILIDAD_STRIDE_DREAD_7_CAPAS.md`; los casos nuevos T1-T10 se vinculan a R06, R08, R10, R11 y R23 |
| 1 | DFD y fronteras de confianza; Threat Dragon | PARCIAL | DFD Mermaid en `docs/fase-1/`; falta el archivo editable de Threat Dragon |
| 1 | Siete capas | CUMPLE (local) | Trazabilidad §4-5; el perímetro cloud solo existe en el diseño |
| 2 | Diagrama de diseño y de despliegue real, separados | PARCIAL | Diseño: `PLAN_DESPLIEGUE_SEENODE.md` §3 y `infra/terraform/`; desplegado: solo el local (`deploy/hardened/`) |
| 2 | Contenedor + BD administrada + CDN (opción B) | CUMPLE contenedor y BD administrada (**desplegados en Render**) · PARCIAL CDN (Cloudflare de Render, sin caché ni gestión propia) | `13-cloud/render/` (regresión 15/15 y recorrido 35/35 en la nube con PostgreSQL 17 free, sin acceso externo); local: `09-postgres/` |
| 2 | API Gateway, IAM, TLS 1.3, AES-256 | PARCIAL | Diseño AWS (Checkov y plan) en `evidence/fase-2/`; local sin TLS (127.0.0.1); Seenode no documenta cifrado en reposo de BD |
| 2 | Simulación de capacidad cloud | CUMPLE | `11-simulacion-seenode/`: 512 MB / 0,25 vCPU, pico 145 MiB, 15/15 y 35/35 |
| 3 | CI/CD con SAST, SCA, SBOM y política de release separada | CUMPLE (local) · PENDIENTE (CI remoto del release) | `scripts/pipeline-release.sh`, `security/release/politica-release.json`, `08-pipeline-release/` (APTA; prueba negativa: BLOQUEADA). El CI de GitHub sigue siendo la política del laboratorio (informa, no bloquea) |
| 3 | Código seguro: SQLi, XSS, JWT, CSRF | CUMPLE · XSS PARCIAL | SQLi (A1-A3), JWT (`04-despues-parches/jwt-algoritmos.md`), CSRF (T6); XSS DOM corregido pero no probado en navegador |
| 3 | Seguridad de dependencias | CUMPLE | Trivy CRITICAL 11→1 y HIGH 33→2 (`08-pipeline-release/trivy.json`; excepciones en `security/release/politica-release.json`) |
| 4 | Caja negra (Nmap/ZAP/validación activa local) | CUMPLE | Histórico en `evidence/fase-4/`; variante final: ZAP 0 FAIL (`12-caja-negra/`) |
| 4 | Caja gris/blanca, autenticación, BOLA/IDOR | CUMPLE | `06-regresion/artefacto-final/` (BOLA 0/10, 7/7 propietario; T1-T10 0 vulnerables) |
| 4 | Casos de abuso modelados y ejecutados | CUMPLE | A1-A12 + T1-T10 + XXE/NoSQL con el modo seguro desactivado (`05-sin-modo-seguro/`) |
| 4 | Perímetro (endpoints, puertos, webhooks, MFA) | CUMPLE (local) · NO APLICA webhooks · PARCIAL MFA | Solo el WAF publica puerto. Juice Shop no tiene webhooks (el de Alertmanager es interno). La 2FA existe pero no se probó |
| 5 | Escaneo de la imagen desplegada | CUMPLE (local) · **NO CUMPLE la política (imagen cloud: puerta BLOQUEADA**, 75 HIGH + 1 CRITICAL del SO base del WAF sin corrección; ver `DESPLIEGUE_CLOUD_RENDER.md` §4 y `13-cloud/release-imagen-cloud/`) | `08-pipeline-release/trivy.json`, `sbom.cdx.json`, `grype.json` |
| 5 | Hadolint / Checkov / IaC | CUMPLE · PENDIENTE IaC de Seenode | Hadolint 0; Checkov AWS histórico; Seenode no ofrece IaC documentada (MCP o panel) |
| 5 | Secretos fuera del código, menor privilegio | CUMPLE | Clave JWT como secreto (falla cerrada); Gitleaks 0; contenedores sin root y con `cap_drop` |
| 6 | Control compensatorio por riesgo; matriz y heatmaps | CUMPLE | `docs/fase-6/riesgo-cierre-tecnico/` (350 comprobaciones, 0 fallas) |
| 6 | WAF y OWASP Top 10 (instalado/observado/probado) | CUMPLE | SQLi, XSS, LFI, RCE, rutas, límite de intentos, cabeceras; falsos positivos 0/35 |
| 6 | RASP o monitoreo de API | CUMPLE (local) · CUMPLE (cloud: el RASP corre en el contenedor desplegado; detecciones a los logs de Render) | `evidence/fase-6/cierre-final-2026-11-21/09-rasp/`; en este cierre, bloqueo de A1 sin WAF (06) y regla BOLA de alta confianza |
| 6 | SIEM: eventos, alertas, notificación, redacción, recuperación | CUMPLE (local) · PARCIAL (cloud: 7 eventos reales cargados con `entorno=cloud` por exportación, no continuo) · CUMPLE purga de tokens (133→0 y 19→0) | `10-siem/` (ciclo de 33 s, `purga-tokens-loki.txt`); `13-cloud/render/siem/` |

## 2. Cambios ejecutados
- **Parche 11 (dependencias y JWT):** `express-jwt` 8.5.1, `jsonwebtoken` 9.0.3, `jws` 4.0.1, `sanitize-html` 2.18.2;
  `download` y `decompress` eliminados; overrides de `crypto-js` 4.2.0, `tar` 7.5.23 y `minimatch` 3.1.5.
- **Parche 12 (hallazgos medidos):** NoSQL por campo, reseñas solo de la cuenta autora, SSRF con validación de destino,
  CSRF por origen, 5xx genéricos en la capa REST, quejas solo para administración, reciclajes autenticados y por propietario,
  XXE sin entidades externas, búsqueda sin bypass de Angular, `b2bOrder` sin evaluación de código y `chat` sin `$where`.
- **Parche 13 (BD administrada opcional):** PostgreSQL con `DATABASE_URL`; tipos portables; arreglo de una caída por
  `sqlite_master` hallada en la prueba.
- **Imagen:** base distroless actualizada (Node 24.22.3); sin el ejemplo de Terraform ni los `.spec.ts`; `safetyMode: enabled`.
- **WAF:** CSP con `form-action 'self'`. **SIEM:** Alertmanager + receptor local, etiqueta `entorno`, panel actualizado.
- **Scripts:** `construir-corregida.sh` (variantes), `pipeline-release.sh`, `validar-artefacto.sh`,
  `security/ops/pruebas-cierre-tecnico.sh`; nuevos objetivos de `make`.
- **Fallos reales encontrados durante el ciclo (todos corregidos):** reseñas creadas que no se listaban, caída con PostgreSQL,
  tipos no portables, y detecciones propias defectuosas (CSRF, XXE, puerta sin stdin), anotadas en la evidencia.

## 3. Estado cloud (2026-11-24)
**Desplegado en Render (capa gratuita, US$0):** servicio `juice-lab-masi-staging` (contenedor único WAF + app corregida + RASP,
construido por Render desde el repo con la fuente verificada contra el diff auditado) y PostgreSQL 17 free sin acceso externo.
Verificado en la nube: TLS 1.2/1.3 (1.0/1.1 rechazadas), puerta de acceso 27/28 (el único fallo es del criterio de la cabecera
`Server`, que reescribe Cloudflare), límite de intentos también con `X-Forwarded-For` falsificado, regresión 15/15, recorrido
35/35, A1-A12 / BOLA / T1-T10 sin vulnerables, logs sin secretos. Detalle y límites: `DESPLIEGUE_CLOUD_RENDER.md`.
Seenode y DigitalOcean no se usaron (D-18): el primero lo descartó el equipo; el segundo exige método de pago.

## 4. SIEM
Grafana en `http://127.0.0.1:3001` (lectura anónima, solo local), panel «SIEM - Juice Shop endurecido» con el filtro `entorno`.
Fuentes reales: auditoría y accesos del WAF, app + RASP y notificaciones (todas con `entorno="local"`). 9 reglas cargadas;
ciclo completo probado (petición bloqueada → reglas 942 → Loki → alerta → notificación en 33 s). Salud: app y WAF healthy, Loki
`ready`, Grafana `ok`, Alertmanager listo. **Purga autorizada y hecha (2026-11-23):** líneas con JWT en Loki vigente 133→0 e
histórico 19→0, con borrado filtrado (el resto se conserva; `10-siem/purga-tokens-loki.txt`). **Eventos cloud:** 7 bloqueos
reales del WAF de Render cargados con `entorno="cloud"` (`13-cloud/render/siem/`), por exportación del panel, no continuo.

## 5. Riesgos residuales y bloqueos
Registro `docs/fase-6/riesgo-cierre-tecnico/`: de 8 críticos y 16 altos (inherente) a **0 críticos · 8 altos · 12 medios · 4 bajos**.
Bajan solo con controles probados: R04 (JWT) 1×5, R08 (NoSQL) 1×4, R10 (XXE) 1×5, R11 (SSRF) 2×3, R20 (dependencias) 2×5 con
aceptación temporal de `marsdb` hasta 2026-12-31, R23 (datos personales) 2×5. Siguen altos, entre otros: R03 (sin gestor de
secretos), R09 (eval/vm), R12, R13 (XSS sin prueba en navegador), R15, R18, R20 y R23.

**Bloqueos y acción mínima (actualizado 2026-11-24):**
1. ~~Despliegue cloud~~ **hecho** en Render. Falta que el equipo añada su propio usuario a `BASIC_AUTH_HTPASSWD` (hoy solo
   `verificador`; ver `DESPLIEGUE_CLOUD_RENDER.md` §6). La BD free vence el 2026-12-24.
2. CDN gestionado y API Gateway: Render no los ofrece en el plan gratuito; requieren otro servicio y, para un CDN propio, un dominio.
3. Eventos cloud continuos en el SIEM: requieren un canal autenticado (API key de Render o servicio externo) que cree el equipo.
4. Threat Dragon: dibujar el DFD en la herramienta y versionar el archivo.
5. ~~Purga de tokens antiguos en Loki~~ **hecha**.
5b. **Decisión de tratamiento del riesgo de la imagen base del WAF** (aceptar con excepciones fechadas, reducir con otra base o
   evitar con dos servicios): la puerta de release bloquea la imagen cloud por paquetes de Debian sin corrección.
6. CI remoto del release: la rama ya está en GitHub; falta ejecutar la puerta de release en Actions.

## 6. Comandos
Git Bash, desde la raíz del proyecto (sin `make` en Windows, los scripts equivalentes):
```bash
docker info --format '{{.ServerVersion}}'                       # Docker Desktop encendido
bash scripts/construir-corregida.sh                             # make corregida-build (verifica cada parche)
WAF_PORT=8088 bash scripts/ops-corregido.sh up                  # make ops-corregido-up
bash scripts/ops-corregido.sh ps                                # make ops-corregido-ps
WAF_PORT=8088 bash scripts/validar-artefacto.sh evidence/validacion-$(date +%Y%m%d)   # make validar-artefacto
bash scripts/pipeline-release.sh juice-corregida-rasp:local evidence/release-$(date +%Y%m%d)   # make release
curl -s http://127.0.0.1:3100/ready ; curl -s http://127.0.0.1:3001/api/health            # Loki y Grafana
bash scripts/ops-corregido.sh down                              # make ops-corregido-down (no borra volúmenes)
```
El laboratorio vulnerable histórico sigue en `make lab-up` (127.0.0.1:3000) y nunca se publica.
