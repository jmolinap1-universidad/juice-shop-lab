# Matriz de cumplimiento de las seis fases — cierre de brechas (2026-11-24)

**Referencia:** `main` (desde `6f2fa61`; cierre en este ciclo). **Despliegue:** Render, servicio `juice-lab-masi-staging`,
commit `768d1da` (imagen cloud Alpine, parches 01-14), acceso restringido. **Evidencia:** `evidence/cierre-brechas-2026-11-24/`
(índice en su `LEAME.md`) y ciclos anteriores. **CUMPLE** = probado con evidencia; **PARCIAL** = probado en parte o con brecha
declarada; **NO COMPLETABLE** = imposible sin costo o sin acción de terceros (con justificación). Sustituye a la tabla del
2026-11-23 en `ESTADO_TECNICO_CIERRE.md` §1, que se conserva como histórico.

| Fase | Requisito | Estado | Evidencia |
|---|---|---|---|
| 1 | Inventario de activos ISO/IEC 27001 con la infraestructura real | **CUMPLE** | `docs/auditoria-final-2026-11-20/INVENTARIO_ACTIVOS_ISO27001.md` (42 activos; SRV-06 a SRV-09, INF-16, INF-17, SW-12 de Render/PostgreSQL) |
| 1 | STRIDE y DREAD, incluida la nube real | **CUMPLE** | `TRAZABILIDAD_STRIDE_DREAD_7_CAPAS.md` §1-3 y §6 (10 amenazas cloud TC01-TC10, 6/6 clases STRIDE, DREAD) |
| 1 | Siete capas (perímetro cloud y capa física reales) | **CUMPLE** | Trazabilidad §4-5 y notas de capas 5 y 6 |
| 1 | DFD editable en Threat Dragon | **PARCIAL** | DFD en Mermaid (`docs/fase-1/`); el archivo de Threat Dragon debe dibujarlo el equipo (herramienta gráfica) |
| 2 | Diseño y despliegue real separados | **CUMPLE** | Diseño: `infra/terraform/` + `PLAN_DESPLIEGUE_SEENODE.md` §3; real: `DESPLIEGUE_CLOUD_RENDER.md` §2 |
| 2 | Contenedor + BD administrada | **CUMPLE** | Render web + PostgreSQL 17 (`ipAllowList: []`); `10-validacion-render/` (regresión 15/15, recorrido 35/35) |
| 2 | CDN | **PARCIAL** | Tráfico por Cloudflare de Render; sin caché propia (exige dominio). `REQUISITOS_CLOUD_DISENO_VS_IMPLEMENTADO.md` |
| 2 | API Gateway | **CUMPLE funcionalmente** | Puerta de enlace nginx: autenticación previa, límite de intentos, métodos, tamaño, WAF (`10-validacion-render/baterias/puerta-acceso.md`, 28/28) |
| 2 | IAM / menor privilegio | **CUMPLE** · MFA **SIN VERIFICAR** | API key solo Monitoring:Read; BD privada; contenedores sin root (`06-siem-render/api-key-render.md`) |
| 2 | AES-256 | **CUMPLE en tránsito** · **DECLARADO** en reposo | TLS_AES_256_GCM_SHA384 medido (`10-validacion-render/tls.md`); reposo: declaración de Render |
| 2 | TLS 1.3 | **PARCIAL** | 1.3 aceptado y negociado; 1.0/1.1 rechazados; 1.2 aceptado por la plataforma (no configurable) |
| 3 | CI/CD con SAST, SCA, SBOM | **CUMPLE** | `devsecops.yml` (informe) y `release.yml` (puerta) |
| 3 | Política de release ejecutada en CI sobre el artefacto final | **CUMPLE** | Run 45555578891 (`84241b4`): IaC 15/15, app APTA, cloud APTA (`11-ci-release/resultado-ci.md`) |
| 3 | Código seguro: SQLi, XSS, JWT, CSRF | **CUMPLE** | XSS en navegador: corregida 0/6 con y sin modo seguro, oficial 5/6 (`02-xss-navegador/`); parche 14 |
| 3 | Seguridad de dependencias | **CUMPLE** con aceptación temporal | Trivy app C1/H2 y cloud C1/H0 exceptuados (marsdb hasta 2026-12-31; libssl de la base distroless) |
| 4 | Caja negra / gris / blanca, BOLA, abuso | **CUMPLE** | Local (`09-validacion-imagen-alpine-local/`) y Render (`10-validacion-render/`): A1-A12 0/11, BOLA 0/10, T1-T10 0 |
| 4 | Perímetro (endpoints, puertos, webhooks, MFA) | **CUMPLE** · NO APLICA webhooks · MFA de la app **PARCIAL** | Único puerto enrutado: el del WAF; la 2FA de Juice Shop existe pero no se probó |
| 5 | Escaneo de la imagen DESPLEGADA conforme a la política | **CUMPLE** | Alpine APTA (`08-puerta-release-local/cloud-alpine/` y CI); historial Debian BLOQUEADA conservado (`TRATAMIENTO_RIESGO_IMAGEN_CLOUD.md`) |
| 5 | Hadolint / IaC | **CUMPLE** | Hadolint 0 (3 Dockerfiles); IaC de Render 15/15 + prueba negativa (`05-iac-render/`); Checkov AWS histórico |
| 5 | Secretos fuera del código y del panel | **CUMPLE** | Clave JWT generada en el contenedor; Gitleaks 0 (historial completo, con un falso positivo revisado en `.gitleaksignore`) |
| 5 | WAF endurecido sin falsos positivos | **CUMPLE** | EX-2 socket.io (920420) local y cloud (`07-falso-positivo-socketio/`); recorrido 35/35 sin bloqueos |
| 6 | Matriz de riesgos y heatmaps con la nube real (incl. R21) | **CUMPLE** | `docs/fase-6/riesgo-cierre-brechas/` (378 comprobaciones, 0 fallas; 0C/7A/14M/3B; R21 2×4 sobre el despliegue real) |
| 6 | WAF y OWASP Top 10 | **CUMPLE** | Bloqueos 942/931/934/932 en Render (SIEM) y local |
| 6 | RASP en la nube | **CUMPLE** | Aikido Zen activo en el contenedor de Render (arranque en el SIEM) |
| 6 | SIEM: centralización automática y autenticada de eventos cloud | **CUMPLE** | Colector API de Render → Loki (clave de solo lectura), 48 s extremo a extremo, 0 secretos (`06-siem-render/extremo-a-extremo.md`) |
| 6 | Alertas sobre eventos cloud con umbral propio | **PARCIAL** | Las 9 reglas existentes ven los eventos cloud por etiqueta, pero no hay reglas exclusivas de la nube; el colector depende del equipo local |
| 6 | Tratamiento formal y dueño del riesgo | **CUMPLE** | `tratamiento-riesgo-cierre-brechas.md`; `TRATAMIENTO_RIESGO_IMAGEN_CLOUD.md` (sin aceptaciones nuevas) |

## Requisitos que no pueden completarse en este ciclo
| Requisito | Motivo | Acción mínima |
|---|---|---|
| CDN con caché/WAF gestionado y TLS 1.3 exclusivo | Requieren dominio propio (costo) o plan de pago | Si el equipo adquiere un dominio: Cloudflare Free delante de Render |
| MFA de las cuentas de GitHub y Render | Configuración personal del equipo, no verificable por el asistente | Activar y declarar 2FA en ambas cuentas |
| Cifrado en reposo verificable | Solo el proveedor puede demostrarlo | Mantener como «declarado» (responsabilidad compartida) |
| DFD en Threat Dragon | Herramienta gráfica manual | Dibujarlo y versionar el `.json` |
| Monitoreo cloud 24/7 | El colector corre en el equipo local (gratis); un servicio permanente tendría costo | Mantener el colector activo durante las demostraciones |
