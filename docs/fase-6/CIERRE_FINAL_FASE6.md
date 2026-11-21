# Cierre final de la Fase 6 — Operaciones, monitoreo y ciberseguridad (local)

**Fecha:** 2026-11-21. **Rama:** `cierre/fase6-definitiva` (desde `cierre/hito-a-local` = `9173cd9`; `main` = `cc08374`).
**Evidencia:** `evidence/fase-6/cierre-final-2026-11-21/` (índice en su `LEAME.md`). **Alcance:** solo laboratorio local
(127.0.0.1 y redes Docker internas). La seguridad en la nube (Seenode/AWS, BD administrada, CDN) es el **hito C** y no se ha
ejecutado: aquí no se creó ningún servicio público ni recurso facturable.

Etiquetas: **PROBADO** (prueba ejecutada con evidencia) · **INSPECCIONADO** (configurado y revisado, no ejercitado) ·
**DISEÑADO** · **PENDIENTE** · **NO EFECTIVO**.

## 1. Dictamen
La Fase 6 **cumple los puntos 6.1 y 6.2 dentro del alcance local**, con evidencia reproducible. No se declara un 100 % de
seguridad: queda **1 riesgo crítico** (R20, dependencias con CVE) y **11 altos**; el SIEM es de laboratorio (un nodo,
sin notificaciones, Loki y Grafana sin autenticación, solo en 127.0.0.1); y Loki conserva líneas con tokens de cuentas de
prueba anteriores a la redacción, cuya purga requiere autorización porque borra datos.

## 2. Dos configuraciones que no deben confundirse
| | Histórica (Fase 6, 2026-11-10) | **Vigente (cierre, 2026-11-21)** |
|---|---|---|
| Arranque | `make ops-up` (aviso de HISTÓRICO) | **`make ops-corregido-up`** (`WAF_PORT=8088` si el 8080 está ocupado) |
| Aplicación | Imagen oficial v20.3.0 (vulnerable) + RASP | Variante corregida (parches 01-10) + RASP, construida con `make corregida-build` |
| Proyecto Compose / logs del WAF | `juice-hardened` / `deploy/hardened/logs/` | `juice-corregida-defensa` / `deploy/hardened/logs-corregido/` |
| WAF | CRS por defecto | + `ALLOWED_METHODS` con PUT/PATCH/DELETE, exclusión acotada de 932260 en `GET /rest/user/whoami`, latido |
| SIEM | 7 reglas | 9 reglas (+ BOLA de alta confianza, + ingesta ausente), redacción de tokens, descubrimiento cada 5 s |
| Riesgo residual (24) | 4 C / 12 A / 7 M / 1 B (`tratamiento-riesgo.md`) | **1 C / 11 A / 9 M / 3 B** (`riesgo-vigente/tratamiento-riesgo-vigente.md`) |

Los dos scripts se niegan a arrancar si el otro stack está activo (los nombres de contenedor coinciden porque el SIEM los usa).
Fotografía intermedia del hito A (sin el parche 10 ni los ajustes del WAF/SIEM): 2 C / 11 A / 8 M / 3 B
(`docs/auditoria-final-2026-11-20/RIESGO_RESIDUAL_HITO_A.md`).

## 3. Punto 6.1 — Estrategia de mitigación y ciberseguridad
| Criterio | Estado | Evidencia | Comando | Resultado | Limitación | Acción pendiente |
|---|---|---|---|---|---|---|
| Controles compensatorios por riesgo | **Cumple** — PROBADO / DISEÑADO por control | `riesgo-vigente/tratamiento-riesgo-vigente.md` §6; `datos/riesgos-vigente.json` | `make risk-vigente` | 24 riesgos con controles, tipo, estado y verificación; 324 comprobaciones, 0 fallas | Varios definitivos siguen propuestos (R08, R10, R11, R15, R20) | Ver `PLAN_PENDIENTES_POST_CIERRE.md` |
| Correcciones definitivas en el código | **Cumple** — PROBADO | `04-escenario-B-corregida/`, `02-bola-recursos/` | `make corregida-build`; `regresion-corregida.sh`; `run.sh`; `bola-recursos.sh` | SQLi, asignación masiva, CORS, clave JWT, MD5, BOLA (5 tipos de objeto) eliminados **sin WAF**; regresión 16/16 | Parche 05 (eval) no ejercitable en Docker; 2FA no ejercitado | Auditar resto de objetos de la API |
| WAF frente a casos del OWASP Top 10 | **Cumple** — PROBADO (SQLi, XSS, LFI, parches virtuales, rutas, rate limit, cabeceras, CORS) | `06-escenario-D-defensa-completa/`, `07-waf/familias-waf.md`, `07-waf/crs-inventario-vigente.txt` | `run.sh` vía 127.0.0.1:8088 | A1-A11: 0 vulnerables; XSS/LFI/SQLi 403 con IDs 941/930/942; 35/35 llamadas legítimas de la interfaz | RCE (932) solo observado en un control negativo; el WAF no resuelve BOLA (lo resuelve el código) | Prueba documentada de la familia 932 |
| Falsos positivos del WAF | **Cumple** — PROBADO | `07-waf/recorrido-frontend-*.md` | `recorrido-frontend.sh` | Configuración histórica: 7 bloqueos de uso legítimo; vigente: 0 | Recorrido de 35 llamadas, no toda la interfaz | Repetir tras cambios de rutas |
| RASP / monitoreo de API | **Cumple** — PROBADO (sink `sqlite3`) | `09-rasp/`, `05-escenario-C-corregida-rasp/` | `security/ops/rasp-modos-corregido.sh` | Monitoreo: 5/5 detectados; bloqueo: 5/5 403 (~0,02 s); legítimas 200; 0 reinicios | `fs`, `http`, `vm`, `child_process` sin probar (INSPECCIONADO por la documentación del agente) | Escenarios por sink |
| SIEM: centralización | **Cumple** — PROBADO | `10-siem/ingesta-por-fuente.txt`, captura de Grafana | Consultas LogQL a `http://127.0.0.1:3100` | Tres fuentes en Loki: `waf_audit`, `waf_access`, `docker/juice-hardened` | Un nodo; Loki sin autenticación | Autenticación y réplica antes de publicar |
| SIEM: correlación y alertas | **Cumple** — PROBADO | `10-siem/reglas-tras-*.txt/.json`, `disparadores.txt`, `alerta-ingesta-ausente.txt` | API del ruler `/prometheus/api/v1/rules` | 9 reglas cargadas; 8 de ataque/anomalía en firing con disparadores representativos; ingesta ausente pending→firing→resuelta | Sin notificación a personas | Alertmanager o correo |
| SIEM: visualización | **Cumple** — PROBADO | `10-siem/capturas/grafana-dashboard-siem-vigente.png` | `http://127.0.0.1:3001` (panel «SIEM - Juice Shop endurecido») | Panel con datos reales de las tres fuentes | Acceso anónimo de solo lectura en 127.0.0.1 | Desactivar el anónimo fuera del laboratorio |
| SIEM: falso positivo BOLA | **Cumple** — PROBADO | `10-siem/reglas-tras-trafico-legitimo.txt` | `trafico-legitimo.sh` y luego intento cruzado | Heurística de enumeración = indicador de investigación (se activa con dos usuarios legítimos); la nueva regla de 403 ajeno queda inactiva con tráfico legítimo y se activa con el intento cruzado | — | — |
| SIEM: seguridad propia | **Parcial** — PROBADO en lo implementado | `10-siem/proxy-socket-docker.txt`, `redaccion-tokens-loki.txt`, `hallazgo-perdida-ingesta.txt` | — | Alloy sin root ni socket (escrituras 403); tokens redactados antes de Loki (0 visibles) | Loki conserva líneas con tokens de prueba anteriores al ajuste; hueco de ingesta residual en contenedores efímeros | Purga autorizada en Loki; driver de logs |

## 4. Punto 6.2 — Tratamiento formal del riesgo
| Criterio | Estado | Evidencia | Resultado | Limitación |
|---|---|---|---|---|
| Matriz con las cinco opciones (principal y complementaria, ejecutada o propuesta) | **Cumple** | `riesgo-vigente/tratamiento-riesgo-vigente.md` §4 | 24 decisiones; las cinco opciones usadas; ninguna transferencia declarada como hecha | Responsables por rol |
| Tipo de riesgo e impactos (reputacional, operacional, financiero, legal) | **Cumple** | idem §3 | 6 tipos; 4 impactos; validados (V14) | — |
| Heatmaps inherente / residual con método y justificación | **Cumple** | `riesgo-vigente/img/*.png`; `datos/riesgos-vigente.json` | 8 C / 16 A → 1 C / 11 A / 9 M / 3 B; cada residual con razón de P e I y evidencia | Aritmética = convención del equipo (ISO/IEC 27005 no la prescribe) |
| Coherencia controles ↔ decisiones ↔ evidencias | **Cumple** | `riesgo-vigente/validacion-consistencia.txt` | 324 comprobaciones, 0 fallas (no hay reducción sin control probado; la detección no reduce el impacto) | — |

**Cambios del residual respecto del hito A** (solo con controles PROBADOS): R06 3×4→2×4 (parche 10), R13 4×4→3×4 (CRS 941
probado con dos vectores), R23 4×5→3×5 (SQLi y BOLA eliminadas en el código). R19 y R24 añaden controles probados sin cambiar
el residual (la detección y la minimización no reducen P ni I). **R20 no se reduce**: las 8 CRITICAL siguen presentes.

## 5. Riesgos críticos y altos abiertos (vigente)
| Riesgo | Residual | Tratamiento |
|---|---|---|
| R20 Dependencias con CVE | **4×5 Crítico** | Aceptación temporal; plan por paquete en `08-trivy/analisis-dependencias.md` |
| R23 Datos personales | 3×5 Alto | Probar XXE, NoSQL y SSRF; transferencia (póliza) solo propuesta |
| R04 Bibliotecas JWT obsoletas | 3×5 Alto | Migrar `express-jwt`/`jsonwebtoken` (ligado a R20) |
| R10 XXE | 3×5 Alto | Parser sin entidades externas (propuesto) |
| R03 Clave JWT | 2×5 Alto | Gestor de secretos/KMS y rotación automática |
| R08, R09, R11, R12, R13, R15, R18 | Alto (12-16) | Ver `PLAN_PENDIENTES_POST_CIERRE.md` |

## 6. Cambios por archivo (este cierre)
| Archivo | Cambio |
|---|---|
| `scripts/construir-corregida.sh`, `app-hardened/aplicar_fase6.py`, `app-hardened/patches/v2/correcciones-fase6.patch` | Construcción verificada desde `app/` fijado; parche 10 (BOLA) |
| `scripts/ops-corregido.sh`, `Makefile` | `corregida-build`, `ops-corregido-up/ps/down` (sin `-v`), `risk-vigente`; `ops-up` marcado como HISTÓRICO |
| `deploy/hardened/docker-compose.corregido.yml`, `waf/rules/98-exclusiones-fase6.conf` | Proyecto y logs propios, `ALLOWED_METHODS`, exclusión acotada, latido |
| `deploy/hardened/siem/config.alloy`, `siem/rules/fake/alertas.yaml` | Redacción de tokens, descubrimiento 5 s; 2 reglas nuevas, heurística BOLA reclasificada |
| `security/ops/bola-recursos.sh`, `recorrido-frontend.sh`, `rasp-modos-corregido.sh`; `security/attacks/run.sh` | Pruebas nuevas; el arnés redacta JWT al guardar |
| `docs/fase-6/datos/riesgo.py`, `generar_md.py`, `construir_riesgos_vigente.py`; `docs/fase-6/riesgo-vigente/` | Registro vigente validado, heatmaps y tabla (salidas históricas intactas) |
