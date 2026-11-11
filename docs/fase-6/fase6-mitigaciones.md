# Fase 6 – Operaciones, monitoreo y ciberseguridad

**Estado:** Implementado y verificado en local (2026-11-10). Todo corre solo en `127.0.0.1` / redes Docker internas.
Tratamiento formal del riesgo y matrices de calor: [`tratamiento-riesgo.md`](tratamiento-riesgo.md).
Matriz histórica de la primera iteración (WAF, 2026-11-03): [`matriz-riesgo.md`](matriz-riesgo.md).

> Etiquetas: **[V]** implementado y verificado con evidencia · **[D]** diseñado (diff validado, no desplegado) ·
> **[P]** propuesto. Un pipeline o un panel "en verde" no implica ausencia de vulnerabilidades.

## 1. Arquitectura operativa (defensa en profundidad)
```
Cliente ─▶ 127.0.0.1:${WAF_PORT:-8080} ─▶ WAF (Nginx 1.30.6 + ModSecurity 3.0.17 + OWASP CRS 4.25.2, PL1, bloqueo)
                                          │  log JSON de acceso + audit log JSON
                                          ▼
                               red "interna" ─▶ Juice Shop 20.3.0 + RASP Aikido Zen 1.8.46 (in-process)
                                                 runtime endurecido de la Fase 5 (read-only, cap_drop ALL, no root)
SIEM (red "siem"):  Grafana Alloy v1.10.2 ─▶ Loki 3.5.5 (almacén + reglas de correlación/alerta) ─▶ Grafana 12.1.1
                    fuentes: audit log del WAF, access log del WAF, stdout de app/RASP y WAF
```
- Arranque: `make ops-up` (equivale a `docker compose -f docker-compose.yml -f docker-compose.ops.yml up -d --build`
  en `deploy/hardened/`). La capa de operaciones es un *override*: no altera la configuración auditada en la Fase 5.
- En esta ejecución el WAF se publicó en `127.0.0.1:8088` (`WAF_PORT=8088`) porque el 8080 estaba ocupado por un
  proceso Java del equipo (`javaw`); no se interrumpió ese proceso.
- Sin telemetría externa: RASP sin `AIKIDO_TOKEN` (registra *"No token provided, disabling reporting"*), Loki con
  `analytics.reporting_enabled: false`, Alloy con `--disable-reporting`, Grafana sin informes ni comprobación de
  actualizaciones. Grafana: solo lectura anónima en `127.0.0.1:3001`, formulario de login deshabilitado.

## 2. Estrategia de mitigación: controles compensatorios por riesgo
La definición detallada **riesgo → control (tipo, estado) → evidencia** de los 24 riesgos está en
[`tratamiento-riesgo.md`](tratamiento-riesgo.md) §5. Resumen por capa:

| Capa | Control | Riesgos | Tipo | Estado |
|---|---|---|---|---|
| Perímetro (WAF) | CRS 942 SQLi, 941 XSS, 932/934 inyección de comandos/código, 930/931 LFI/RFI, 920/921 protocolo, 913 escáneres, 95x fuga en respuestas | R01, R02, R05, R13, R23 | Preventivo | [V] SQLi bloqueada; resto configurado |
| Perímetro (WAF) | Parches virtuales 100001 (asignación masiva) y 100002 (`/metrics`) | R07, R17 | Preventivo | [V] |
| Perímetro (nginx) | `deny` de `/ftp`, `/encryptionkeys`, `/support/logs`, `/metrics`; cabeceras CSP/HSTS/XFO/XCTO/COOP/COEP; ocultar ACAO; `limit_req` 5/min en login | R12, R13, R14, R16, R17 | Preventivo | [V] |
| Aplicación (RASP) | Aikido Zen: detección/bloqueo de inyección en los *sinks* (sqlite3, fs, child_process, http, vm) | R01, R02, R05, R23 | Preventivo/detectivo | [V] SQLi; resto no verificado |
| Runtime (Fase 5) | FS de solo lectura, `cap_drop ALL`, no root, `no-new-privileges`, límites de pids/memoria/CPU | R09, R18 | Contención | [V] |
| Monitoreo (SIEM) | 7 reglas de correlación/alerta en Loki + panel en Grafana | R01, R02, R06, R07, R12, R16, R17, R19 | Detectivo | [V] 6/7 dispararon |
| Código | Parches 01-08 (SQLi ×2, bcrypt, clave a secreto, `eval`, asignación masiva, CORS, **BOLA**) | R01-R07, R09, R14 | Eliminación | [D] `git apply --check` OK (04 manual) |

## 3. WAF: reglas para bloquear el OWASP Top 10:2025
Inventario real del CRS cargado y configuración efectiva: `evidence/fase-6/waf/crs-inventario.txt`
(PL1, `BLOCKING_PARANOIA=1`, umbral de anomalía entrante 5 / saliente 4, `MODSEC_RULE_ENGINE=On`).

| OWASP Top 10:2025 | Control en el WAF | Reglas cargadas | Verificación |
|---|---|---|---|
| A01 Broken Access Control | `deny` de rutas internas; VP 100001 (rol en registro); CRS 930/931 (LFI/RFI) | 930: 14, 931: 13 | [V] rutas y VP (403). **BOLA no es bloqueable por un WAF** (verificado: A12 sigue vulnerable a través del WAF) |
| A02 Security Misconfiguration | Cabeceras de seguridad, ocultar CORS, `deny /metrics` + VP 100002; CRS 920/921 (protocolo), 913 (escáneres) | 920: 68, 921: 26, 913: 9 | [V] cabeceras/CORS/metrics; 920 activo (41 eventos) |
| A03 Software Supply Chain Failures | — (no es función del WAF) | — | Tratado con SCA en CI (Fase 3) |
| A04 Cryptographic Failures | HSTS; CRS 950-956 (fuga de datos/errores en respuestas) | 950-956: 125 | [V] HSTS presente; 95x configurado sin eventos |
| A05 Injection | CRS 942 (SQLi), 941 (XSS), 932 (RCE), 934 (inyección genérica, incl. Node.js), 943 | 942: 68, 941: 42, 932: 55, 934: 19, 943: 11 | [V] 942 bloqueó las 3 SQLi; resto configurado |
| A06 Insecure Design | — (diseño; no corregible en el perímetro) | — | Modelado de amenazas Fase 1 + parches |
| A07 Authentication Failures | `limit_req` 5/min, burst 3 en `/rest/user/login` (HTTP 429) | — | [V] 8 respuestas 429 |
| A08 Software or Data Integrity Failures | — | — | No aplica al WAF (firma/integridad de artefactos) |
| A09 Security Logging and Alerting Failures | Audit log JSON (`RelevantOnly`) + access log JSON → SIEM | — | [V] ingestado en Loki |
| A10 Mishandling of Exceptional Conditions | CRS 920 (peticiones malformadas); alerta `App_Errores_5xx` | 920: 68 | Configurado; la alerta no se activó (sin ráfagas 5xx) |

**Ruido identificado (ajuste fino propuesto):** la regla 920350 ("Host header is a numeric IP address") se activa en
casi todas las peticiones porque el laboratorio se accede por IP (`127.0.0.1`). Es de severidad *warning* y no
bloquea por sí sola, pero consume margen del umbral de anomalía. En producción, con nombre de dominio, desaparece;
en el laboratorio podría excluirse con `SecRuleRemoveById 920350` **[P]**.

## 4. RASP y monitoreo de APIs (detección en tiempo de ejecución)
### 4.1 RASP: Aikido Zen 1.8.46 (open source, AGPL-3.0)
- Se carga sin modificar el código: `deploy/hardened/Dockerfile.rasp` copia el agente a la imagen oficial (digest
  fijo) y `NODE_OPTIONS=--require @aikidosec/firewall`. Instrumenta `sqlite3@5.1.7`, `express@4.22.3`, `node:fs`,
  `node:child_process`, `node:http(s)`, `node:vm` (registro de arranque en `evidence/fase-6/rasp/arranque-agente.log`).
- Modos: `AIKIDO_BLOCK=false` = **monitoreo** (detecta y registra); `AIKIDO_BLOCK=true` = **bloqueo**.
- Prueba diseñada para medir el RASP **aislado del WAF**: el mismo arnés `security/attacks/run.sh` se ejecutó desde la
  red Docker interna directamente contra `juice-hardened:3000` (simula que el WAF fue evadido).

| Corrida | Configuración | Resultado | Evidencia |
|---|---|---|---|
| 1 | Monitoreo (`AIKIDO_BLOCK=false`) | 3 SQLi **detectadas** (`body.email`, `query.q` ×2) en `sqlite3.all(...)`; no bloqueadas (esperado) | `evidence/fase-6/rasp/01-deteccion-sin-bloqueo/` |
| 2 | Bloqueo, configuración por defecto | **Hallazgo:** el primer bloqueo hizo **terminar el proceso Node** (rechazo de promesa no manejado, `RestartCount=1`). Corrida **inválida** para medir mitigación (`HTTP 000`) | `evidence/fase-6/rasp/02-bloqueo-caida-del-proceso/` |
| 3 | Bloqueo + `--unhandled-rejections=warn` | A1-A3 **bloqueadas** en el sink, **sin caídas** (`RestartCount 0`); A4-A12 siguen vulnerables sin WAF (fuera del alcance del RASP) | `evidence/fase-6/rasp/03-bloqueo-sin-caida/` |

- **Hallazgo operativo (R22):** en esta pila, el modo bloqueo por defecto convertía cada SQLi detectada en una
  caída del servicio (auto-DoS; A10:2025, CWE-248/755). Tratamiento **Eliminar** aplicado y verificado
  (`--unhandled-rejections=warn`). Residual: la petición bloqueada queda sin respuesta, pero el servicio sigue
  operativo; la integración definitiva sería capturar el error en la capa de datos y responder 403 **[P]**.
- **Alcance real del RASP (honesto):** cubre la **inyección** en los sinks instrumentados. **No** cubre exposiciones
  por configuración (listados, `/metrics`), asignación masiva, ausencia de rate limit, BOLA (requiere integrar su
  función de protección IDOR en el código) ni NoSQL sobre MarsDB (solo soporta MongoDB). Por eso es una capa
  adicional, no un sustituto del WAF ni de la corrección del código.

### 4.2 Monitoreo de APIs: detección de comportamientos anómalos
Reglas LogQL sobre el access log JSON del WAF (`deploy/hardened/siem/rules/fake/alertas.yaml`):
- **`API_Enumeracion_Objetos_PosibleBOLA`**: ≥2 cestas distintas (`/rest/basket/{id}`) con HTTP 200 en 5 min.
  Es el control **detectivo** para el BOLA que el WAF no puede bloquear. **Disparó** en la prueba de defensa completa.
- **`Login_FuerzaBruta_RateLimit`**: ≥3 respuestas 429 en el login en 5 min.
- **`App_Errores_5xx`**: >5 errores 5xx en 5 min (condiciones excepcionales mal gestionadas).
- Limitación del laboratorio: todo el tráfico llega desde la misma IP de la pasarela Docker, por lo que la
  correlación es global y no por cliente; en producción se agruparía por IP/usuario (sin registrar tokens).

## 5. SIEM: centralización de logs de auditoría
| Fuente | Recolección | Etiquetas en Loki |
|---|---|---|
| Audit log ModSecurity (JSON, una transacción por línea) | `loki.source.file` | `job="waf_audit"`, `status` |
| Access log del WAF (JSON, sin cabeceras de autorización ni cuerpos) | `loki.source.file` | `job="waf_access"`, `status`, `method` |
| stdout de `juice-hardened` (app + RASP) y `juice-waf` | `loki.source.docker` | `job="docker"`, `container` |

Retención 30 días (compactor), un solo nodo. Reglas de correlación/alerta (Loki ruler, evaluación cada 15 s):

| Regla | Lógica (ventana 5 min) | Riesgo | Estado en la prueba |
|---|---|---|---|
| `WAF_InyeccionSQL_Bloqueada` | eventos CRS `942xxx` > 0 | R01, R02 | **firing** |
| `WAF_ParcheVirtual_Activado` | reglas `10000x` > 0 | R07, R17 | **firing** |
| `Login_FuerzaBruta_RateLimit` | ≥3 respuestas 429 | R16 | **firing** |
| `Acceso_Rutas_Sensibles_Denegado` | 403 en rutas sensibles > 0 | R12, R17 | **firing** |
| `API_Enumeracion_Objetos_PosibleBOLA` | ≥2 cestas distintas con 200 | R06 | **firing** |
| `RASP_Ataque_Detectado` | líneas `^Zen has (blocked\|detected)` > 0 | R01, R02 | **firing** (prueba RASP directa) |
| `App_Errores_5xx` | >5 respuestas 5xx | R18 | inactive (no hubo ráfaga) |

Evidencia: `evidence/fase-6/siem/reglas-estado.json`, `alertas-tras-defensa-completa.json`,
`alertas-tras-prueba-rasp.json`, `consultas-logql.jsonl`, `capturas/grafana-dashboard-siem.png`.
Métricas del periodo de pruebas (LogQL): 13 respuestas 403, 8 respuestas 429, 3 eventos CRS 942, VP 100001 = 1,
VP 100002 = 1, RASP: 3 detecciones y 4 bloqueos, 3 cestas distintas accedidas.
*Ajuste aplicado tras la primera captura:* la expresión del RASP se restringió a `^Zen has (blocked|detected)`
porque la versión inicial contaba también las líneas de *warning* de Node (sobrecontaba 11 en lugar de 7).

## 6. Resultados de la verificación
| Prueba | Resultado | Evidencia |
|---|---|---|
| Falsos positivos: tráfico legítimo vía WAF + RASP | 6/6 peticiones legítimas 200/201 (búsqueda, registro sin `role`, login, cesta propia, reseñas) | `evidence/fase-6/funcional/trafico-legitimo.txt` |
| Defensa completa (WAF + RASP), `run.sh` con `A12_DELAY=65` | **A1-A11 mitigados (11/11)**; **A12 BOLA sigue VULNERABLE** (B leyó la cesta de A, HTTP 200) | `evidence/fase-6/defensa-completa/` |
| RASP aislado (3 corridas) | Ver §4.1 | `evidence/fase-6/rasp/` |
| SIEM | 6/7 reglas en *firing*; panel con métricas reales | `evidence/fase-6/siem/` |
| Logs del WAF de esta fase | Copiados con tokens y credenciales **redactados** (0 JWT) | `evidence/fase-6/waf-logs/fase6-2026-11-10/` |
| Healthcheck del WAF | La imagen probaba `https://localhost:8443/healthz` (no servido) → contenedor `unhealthy` aunque filtraba; corregido a HTTP `8080/healthz` → `healthy` | `evidence/fase-6/siem/stack-docker-ps.txt` |

`A12_DELAY` pausa el arnés antes del caso BOLA para que el rate limit del login (control de A10) no impida obtener
los tokens de las dos cuentas y se confunda con un control de autorización.

## 7. Límites y trabajo propuesto
- Los parches de código (incluido el **08 para BOLA**) están validados como diff pero la aplicación no se recompiló:
  el residual de R03, R06, R08, R10, R11 y R15 sigue Alto/Crítico (ver `tratamiento-riesgo.md` §7) **[D]/[P]**.
- RASP: integración de su protección IDOR y manejo del error de bloqueo en la capa de datos **[P]**.
- SIEM de un solo nodo; el agente usa el socket de Docker en solo lectura (riesgo R24, aceptado en el laboratorio).
  En producción: clúster gestionado, driver de logs y notificación (Alertmanager / correo / chat) **[P]**.
- Cloud (Fase 2) **no desplegado** para evitar costos: diseño en Terraform validado estáticamente (Checkov 144/0).
