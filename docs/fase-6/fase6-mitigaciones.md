# Fase 6 – Operaciones, monitoreo y ciberseguridad

**Estado (cierre 2026-11-10):** implementado y validado en local, solo en `127.0.0.1` y redes Docker internas.
Tratamiento formal del riesgo: [`tratamiento-riesgo.md`](tratamiento-riesgo.md) (generado y validado).
Diagnóstico y cierre: [`AUDITORIA_CUMPLIMIENTO_FASE6.md`](AUDITORIA_CUMPLIMIENTO_FASE6.md),
[`CIERRE_Y_VALIDACION_FASE6.md`](CIERRE_Y_VALIDACION_FASE6.md). Matriz de la primera iteración (histórica):
[`matriz-riesgo.md`](matriz-riesgo.md).

> **Niveles de verificación usados en todo el documento.** *Probado*: una prueba representativa con evidencia
> demostró el efecto. *Inspeccionado*: configuración comprobada (p. ej. `docker inspect`, regla cargada), efecto no
> ejercitado. *Diseñado*: corrección validada como diff (`git apply --check`), no desplegada. *Propuesto*: aún no
> implementado. *No efectivo*: probado y no protege. Un pipeline o un panel "en verde" no implica ausencia de
> vulnerabilidades. Las "11 condiciones" del arnés `run.sh` (A1-A11) **no son 11 explotaciones**: 4 son
> explotación demostrada y 7 son exposiciones, configuraciones inseguras o ausencia de controles (Fase 4).

## 1. Arquitectura operativa (defensa en profundidad)
```
Cliente ─▶ 127.0.0.1:${WAF_PORT:-8080} ─▶ WAF: Nginx 1.30.6 + ModSecurity 3.0.17 + OWASP CRS 4.25.2 (PL1, bloqueo)
                                          │ access log JSON + audit log JSON (volumen ./logs, no versionado)
                                          ▼
                     red "interna" ─▶ Juice Shop 20.3.0 + RASP Aikido Zen 1.8.46 + integración rasp-guard
                                       (runtime de la Fase 5: FS solo lectura, cap_drop ALL, usuario 65532)
red "siem":         Alloy v1.10.2 (uid 473, sin socket) ─▶ Loki 3.5.5 (reglas) ─▶ Grafana 12.1.1 (127.0.0.1:3001)
red "socketproxy" (internal):  Alloy ─▶ docker-socket-proxy v0.4.1 (API de solo lectura) ─▶ docker.sock
```
- Arranque: `make ops-up` (override `deploy/hardened/docker-compose.ops.yml`; no altera la configuración de la
  Fase 5). En esta validación el WAF se publicó en `127.0.0.1:8088` (`WAF_PORT=8088`) porque el 8080 lo ocupaba un
  proceso Java del equipo, que no se interrumpió.
- Puertos publicados verificados en la configuración resuelta de Compose: solo `127.0.0.1:8088`, `127.0.0.1:3001`
  y `127.0.0.1:3100`; el proxy del socket y Alloy no publican puertos.
- Telemetría externa desactivada por configuración (RASP sin `AIKIDO_TOKEN`, que registra *"No token provided,
  disabling reporting"*; Loki `analytics.reporting_enabled: false`; Alloy `--disable-reporting`; Grafana sin
  informes ni comprobación de actualizaciones). **No se auditó el tráfico de red saliente**: es una verificación por
  configuración, no por captura de red.

## 2. Escenarios de validación (evidencia nueva)
Índice completo: `evidence/fase-6/validacion-2026-11-10/LEAME.md`. El arnés registra el **código HTTP real**
de cada petición (`ATTACK_HTTPLOG`); `000` significa sin respuesta y **nunca** se cuenta como bloqueo.

| # | Escenario | A1-A3 (SQLi) | Resto | Disponibilidad / reinicios | Carpeta |
|---|---|---|---|---|---|
| 1 | Línea base vulnerable (lab) | HTTP 200 (ataque con éxito) | 11/11 condiciones + BOLA | — | `01-linea-base-vulnerable/` |
| 2a | RASP sin WAF, monitoreo | HTTP 200; 3 SQLi **detectadas** | sin cambio | 41/41 sondeos; RestartCount 0→0 | `02a-rasp-monitoreo/` |
| 2b | RASP sin WAF, bloqueo por defecto | **000** (proceso terminado) | 000 | **1/6 sondeos; RestartCount 0→1** | `02b-…-sin-integracion/` |
| 2c | Bloqueo + `--unhandled-rejections=warn` | **000 a los 20,0 s** (colgada) | sin cambio | 106/106; RestartCount 0→0 | `02c-rasp-bloqueo-warn/` |
| 2d | Bloqueo + integración `rasp-guard` | **403 en 0,04-0,15 s** | sin cambio (fuera del alcance del RASP) | 41/41; RestartCount 0→0 | `02d-rasp-bloqueo-integrado/` |
| 3 | WAF + RASP + SIEM (vía WAF) | 403 del WAF en 0,008-0,018 s | A4-A11 neutralizadas; **A12 BOLA vulnerable** | WAF y app healthy; RestartCount 0 | `03-waf-rasp-siem/` |
| 3b | RASP sin WAF con el SIEM ingiriendo | 403 (RASP) | — | 41/41; RestartCount 0 | `03b-rasp-a-siem/` |
| 4 | Tráfico legítimo (2 usuarios) | — | 9 operaciones correctas | sin falsos positivos de WAF/RASP | `04-falsos-positivos/` |

## 3. WAF: reglas para el OWASP Top 10:2025 (cobertura honesta)
Inventario real: `evidence/fase-6/waf/crs-inventario.txt` (PL1, umbral entrante 5 / saliente 4, motor `On`).
Reglas observadas en los audit logs (`evidence/fase-6/validacion-2026-11-10/03-waf-rasp-siem/logs-waf/`):
920350 (×43, solo advertencia), 942100 (×3), 942190 (×2), 942270 (×2), 942140 (×1), 949110 (×3), 100001 (×1),
100002 (×1). **Un WAF no "bloquea los diez riesgos"**: varias categorías requieren medidas fuera del perímetro.

| OWASP Top 10:2025 | Control WAF | Regla instalada | Observada en logs | Vector probado y bloqueado | Corrección de raíz pendiente |
|---|---|---|---|---|---|
| A01 Broken Access Control | Deny de rutas internas; VP 100001; CRS 930/931 | Sí (930: 14, 931: 13) | 100001 | Rutas internas y asignación masiva: 403. **BOLA: NO bloqueado** (A12, 200) | Parches 06 y 08; retirar serve-index |
| A02 Security Misconfiguration | Cabeceras, ocultar CORS, deny `/metrics` + VP 100002; CRS 920/921/913 | Sí (920: 68, 921: 26, 913: 9) | 920350, 100002 | Cabeceras presentes, ACAO oculto, `/metrics` 403 | Parche 07; configurar la app |
| A03 Software Supply Chain Failures | — | — | — | No aplica al WAF | Actualizar dependencias (R04, R20) |
| A04 Cryptographic Failures | HSTS; CRS 950-956 (fugas en respuestas) | Sí (125) | No | Solo HSTS presente | Parches 03 y 04 (clave privada) |
| A05 Injection | CRS 942 (SQLi), 941 (XSS), 932 (RCE), 934, 943 | Sí (942: 68, 941: 42, 932: 55, 934: 19, 943: 11) | 942xxx, 949110 | **Solo SQLi** probada y bloqueada; XSS/RCE/LFI **configurado, no probado** | Parches 01, 02 y 05; codificación de salida |
| A06 Insecure Design | — | — | — | No aplica al WAF | Modelado de amenazas y parches |
| A07 Authentication Failures | `limit_req` 5/min, ráfaga 3 | Sí (nginx) | 8 respuestas 429 | Fuerza bruta desde una IP: 429 | Limitación por cuenta |
| A08 Software or Data Integrity Failures | — | — | — | No aplica al WAF | — |
| A09 Security Logging and Alerting Failures | Audit log y access log JSON al SIEM | Sí | Sí (ingestados) | Ver §6 | Notificaciones y alta disponibilidad |
| A10 Mishandling of Exceptional Conditions | CRS 920 (peticiones malformadas) | Sí | 920350 (advertencia) | No probado | Manejo de errores sin traza de pila |

- **A11 (`/encryptionkeys/jwt.pub`) no es una vulnerabilidad:** sirve una clave **pública**. Su bloqueo es reducción de
  superficie, no la corrección de un defecto. El hallazgo real es la clave **privada** embebida en el código (R03),
  que ningún control desplegado mitiga.
- **Ruido de la regla 920350:** se activa en 43 de 43 peticiones auditadas en la ventana del escenario 3 porque el
  laboratorio se accede por IP. Además vuelve "relevante" cada petición para el audit log (`RelevantOnly`). Se
  mantiene como **recomendación** (`SecRuleRemoveById 920350` en el laboratorio, o acceso por nombre de dominio): no
  se cambió para no alterar la configuración medida. Antes de aplicarla habría que repetir los escenarios 3 y 4.

## 4. RASP: detección y bloqueo en tiempo de ejecución (R22)
**Agente:** Aikido Zen 1.8.46 (AGPL-3.0), precargado con `NODE_OPTIONS` sobre la imagen oficial; instrumenta
`sqlite3@5.1.7`, `express`, `node:fs`, `node:child_process`, `node:http(s)` y `node:vm`. Sin token no reporta a
terceros. Modos: `AIKIDO_BLOCK=false` (monitoreo) y `AIKIDO_BLOCK=true` (bloqueo).

**Causa raíz del auto-DoS (verificada en el código).** Sequelize ejecuta cada consulta dentro de
`conn.serialize(async () => …)` (`node_modules/sequelize/lib/dialects/sqlite/query.js:183`). Zen bloquea
**lanzando** un error síncrono desde `sqlite3.Database#all`; esa excepción rechaza la promesa de la función `async`,
que `serialize` ignora. La promesa de la consulta nunca se resuelve, la ruta (`.catch(next)`) no recibe el error y:
con la configuración por defecto de Node el proceso **termina** (2b); con `--unhandled-rejections=warn` la petición
queda **colgada** (2c).

**Corrección aplicada: integración `deploy/hardened/rasp/rasp-guard.js`** (cargada después del agente; sin modificar
Juice Shop ni Sequelize). Solo intercepta errores cuyo mensaje empieza por `Zen has blocked`: los entrega por el
callback de `sqlite3` (la vía de error que Sequelize sí propaga) y fija `HTTP 403` en la respuesta de esa petición
(contexto por `AsyncLocalStorage`). Cualquier otro error se relanza: no hay captura genérica. Se retiró
`--unhandled-rejections=warn`, que habría ocultado otros fallos. Resultado (2d y 3b): **403 en 0,04-0,15 s,
disponibilidad 41/41, RestartCount 0**, y cada bloqueo deja `Zen has blocked …` y `rasp-guard: … (HTTP 403)` en stdout.

**Límites honestos:** (1) solo se probó el sink `sqlite3`; los bloqueos en `fs`, `http`, `child_process` y `vm` no se
ejercitaron, por lo que R22 queda **ejecutado parcialmente** (residual Medio); (2) el cuerpo del 403 lo genera el
manejador de errores de Juice Shop, que muestra una **traza de pila** (comportamiento preexistente, A10);
(3) el RASP no cubre exposiciones de configuración, asignación masiva, rate limit, BOLA ni NoSQL sobre MarsDB: sin
WAF, A4-A12 siguen presentes (2d).

## 5. Monitoreo de API: heurística de comportamiento anómalo
- `API_Enumeracion_Objetos_PosibleBOLA` (≥ 2 cestas distintas con HTTP 200 en 5 min) es una **heurística**, no una
  comprobación de propietario ni la prueba del BOLA. La prueba del BOLA es el caso A12 con dos tokens (la cuenta B
  lee la cesta de A con 200).
- **Falso positivo demostrado** (`04-falsos-positivos/`): dos usuarios legítimos, cada uno leyendo **su propia**
  cesta, dispararon la alerta. Causa: la correlación es global (todo el tráfico llega con la IP de la pasarela de
  Docker) y no conoce la identidad del usuario.
- **Falso negativo (análisis, no probado):** un atacante que lea una sola cesta ajena y ninguna otra en 5 min no
  alcanza el umbral de 2.
- **Mejora propuesta (no implementada):** registrar en el access log un identificador **seudónimo** del usuario (p. ej.
  HMAC del `sub` del JWT con una clave del laboratorio, nunca el token) y correlacionar "objetos distintos por
  usuario". Seguiría siendo una heurística; la corrección real es la verificación de propietario (parche 08).
- `Login_FuerzaBruta_RateLimit` se activó (8 respuestas 429). `App_Errores_5xx` está configurada y su consulta se
  ejecuta sin error, pero **no se activó** en ningún escenario (no hubo ráfagas 5xx): no está validada con una ráfaga real.

## 6. SIEM: centralización, correlación y seguridad del propio SIEM
**Fuentes:** audit log de ModSecurity (`job="waf_audit"`), access log JSON del WAF (`job="waf_access"`) y stdout de
`juice-hardened` y `juice-waf` (`job="docker"`, a través del proxy del socket). Retención 30 días, un solo nodo,
evaluación de reglas cada 15 s.

| Regla | Escenario 3 (vía WAF) | Escenario 3b (RASP directo) | Comentario |
|---|---|---|---|
| `WAF_InyeccionSQL_Bloqueada` | firing | firing (ventana) | 3 eventos CRS 942 |
| `WAF_ParcheVirtual_Activado` | firing | firing (ventana) | 100001 y 100002 |
| `Login_FuerzaBruta_RateLimit` | firing | firing (ventana) | 8 respuestas 429 |
| `Acceso_Rutas_Sensibles_Denegado` | firing | firing (ventana) | 403 en rutas internas |
| `API_Enumeracion_Objetos_PosibleBOLA` | firing | firing (ventana) | Heurística con falsos positivos (§5) |
| `RASP_Ataque_Detectado` | **inactive** (correcto: el WAF frenó la SQLi antes de la app) | **firing** | 6 líneas del RASP en Loki |
| `App_Errores_5xx` | inactive | inactive | Configurada, no disparada |

Métricas de la ventana del escenario 3 (`03-waf-rasp-siem/consultas-logql.txt`): 403 = 13, 429 = 8, CRS 942 = 3,
949110 = 3, VP 100001 = 1, VP 100002 = 1, 920350 = 34 de 34 transacciones auditadas, eventos del RASP = 0,
cestas distintas = 2, 5xx = 0. El panel de Grafana de la misma ventana (`03-waf-rasp-siem/capturas/`) muestra las
mismas cifras.

**Seguridad del SIEM (riesgo R24):**
- *Antes:* Alloy como root con `docker.sock` montado `:ro`. **El montaje de solo lectura no restringe la API de Docker**:
  quien controlara Alloy podía crear o ejecutar contenedores.
- *Ahora (probado, `05-siem-seguridad/proxy-socket-api.txt`):* Alloy corre como uid 473, sin capacidades y sin el
  socket; consulta Docker a través de `docker-socket-proxy`, que responde 200 a `GET /_ping`, `/version`,
  `/containers/json` y `/networks`, y **403** a `POST /containers/create`, `stop`, `exec`, `DELETE` y
  `POST /images/create`. El proxy está en una red `internal` sin puertos publicados. Sigue montando el socket: es
  el componente de confianza.
- *Aceptado temporalmente (laboratorio):* Loki sin autenticación y Grafana anónimo de solo lectura, ambos solo en
  127.0.0.1; un solo nodo; sin notificación externa. No es una configuración apta para producción.
- *Incidencia observada:* al introducir el proxy, el SIEM dejó de ingerir los logs de contenedores durante unos 11 min
  (el proxy denegaba `GET /networks`, que Alloy necesita). Se corrigió habilitando solo esa lectura. Muestra la
  necesidad de una **alerta por ausencia de datos** de cada fuente (pendiente de R19).

## 7. Controles compensatorios por riesgo
La definición completa **riesgo → control (tipo, implementación, verificación) → evidencia**, con la decisión de
tratamiento, el responsable y la justificación del residual de los 24 riesgos, está en
[`tratamiento-riesgo.md`](tratamiento-riesgo.md) §4-§6. Distribución resultante (solo controles probados):
inherente **8 críticos / 16 altos** → residual **4 críticos / 12 altos / 7 medios / 1 bajo**.

## 8. Hallazgos operativos de la fase
| Hallazgo | Evidencia | Estado |
|---|---|---|
| Bloqueo del RASP → caída del proceso o petición colgada (R22) | `validacion-2026-11-10/02b`, `02c` | Corregido para `sqlite3` con `rasp-guard` (403); otros sinks sin probar |
| Healthcheck del WAF probaba `https://localhost:8443` (no servido) → `unhealthy` | `evidence/fase-6/siem/stack-docker-ps.txt` | Corregido (HTTP 8080/healthz) |
| `docker.sock :ro` no limita la API de Docker | `05-siem-seguridad/proxy-socket-api.txt` | Corregido con proxy de solo lectura |
| Ingesta de contenedores interrumpida ~11 min por la política del proxy | `validacion-2026-11-10/LEAME.md` | Corregido; falta alerta por ausencia de datos |
| Heurística BOLA con falsos positivos | `04-falsos-positivos/` | Documentado; mejora propuesta |
| Registro HTTP del arnés vacío en Git Bash (rutas `/c/…` con `curl.exe`) | `01-linea-base-vulnerable-intento1/LEAME.md` | Corregido (`cygpath -m`) |
| Regla del RASP del SIEM sobrecontaba (primera iteración) | `docs/fase-6/fase6-mitigaciones.md` (historial git) | Corregido (`^Zen has (blocked\|detected)`) |

## 9. Límites y pendientes
- Parches 01-08 **diseñados, no desplegados** (la aplicación no se recompiló): R01-R03, R05-R07, R09, R14 conservan su causa.
- WAF: solo la familia SQLi está probada; XSS, RCE, LFI y fugas en respuestas están configuradas, sin prueba.
- RASP: sinks distintos de `sqlite3` sin probar; respuesta 403 con traza de pila.
- SIEM: un solo nodo, sin autenticación en Loki, sin notificaciones, sin alerta de pérdida de ingesta.
- Nube (Fase 2): diseñada y validada estáticamente, **no desplegada** (`06-cloud-no-desplegado.txt`).
- Carátula institucional y maquetación final del Word/PDF: pendientes del equipo
  ([`INSTRUCCIONES_SINCRONIZACION_DOCUMENTO.md`](INSTRUCCIONES_SINCRONIZACION_DOCUMENTO.md)).
