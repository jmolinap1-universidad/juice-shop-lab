# Matriz de validación final — Fase 6 (criterios de aceptación)

Evidencia relativa a `evidence/fase-6/cierre-final-2026-11-21/` salvo que se indique otra ruta. **Cumple** = probado con
evidencia; **Parcial** = probado en parte o con una brecha declarada; **Pendiente** = no ejecutado.

## Criterios de aceptación del cierre
| # | Criterio | Estado | Fuente de evidencia |
|---|---|---|---|
| 1 | Procedimiento corto y probado para iniciar la versión corregida + WAF + RASP + SIEM sin publicar la app vulnerable | **Cumple** | `scripts/ops-corregido.sh`, `make ops-corregido-up`; `00-preflight/estado-stack.txt` (solo 127.0.0.1) |
| 2 | Salud, disponibilidad, uso legítimo y bloqueo del WAF con HTTP reales | **Cumple** | `06-escenario-D-defensa-completa/` (regresión 15/15, `http.tsv`: 200/201/400/403), `07-waf/recorrido-frontend-con-waf.md` (35/35) |
| 3 | BOLA en cestas probada sin WAF y con WAF; otros objetos no se dan por corregidos sin prueba | **Cumple** | A12 403 en B, C y D; `02-bola-recursos/` y `bola-recursos.md` de B y D (5 tipos de objeto, 0/10); objetos no auditados listados en el plan de pendientes |
| 4 | RASP: bloqueos controlados sin caída y logs en Loki; alcance real declarado | **Cumple** | `09-rasp/` (403, 0 reinicios), `10-siem/hallazgo-perdida-ingesta.txt` (5/5 en Loki tras el ajuste); alcance: solo `sqlite3` |
| 5 | Grafana con logs reales de las tres fuentes; situación de las alertas comprobada | **Cumple** | `10-siem/capturas/grafana-dashboard-siem-vigente.png`, `ingesta-por-fuente.txt`, `reglas-tras-*.txt` (9 reglas) |
| 6 | 24 decisiones y mapas de calor coherentes con el registro y la configuración | **Cumple** | `docs/fase-6/riesgo-vigente/` (324 comprobaciones, 0 fallas); histórico intacto en `docs/fase-6/` |
| 7 | Riesgos críticos abiertos declarados o justificados con pruebas | **Cumple** | R20 sigue crítico (aceptación temporal); R23 baja a alto solo con controles probados (`CIERRE_FINAL_FASE6.md` §4-5) |
| 8 | Evidencia y guía reproducibles, sin secretos ni capturas fabricadas | **Cumple** | `LEAME.md`; `GUIA_DEMOSTRACION_FASE6.md` (comandos ejecutados el 2026-11-21); Gitleaks; JWT redactados |
| 9 | Dictamen criterio por criterio sin proclamar 100 % | **Cumple** | `CIERRE_FINAL_FASE6.md` §1, §3, §4 |
| 10 | Ningún servicio cloud público ni recurso facturable creado | **Cumple** | No se usaron credenciales ni cuentas externas; solo imágenes públicas de Docker Hub |

## WAF
| Control | Instalado | Observado | Probado | Evidencia |
|---|---|---|---|---|
| CRS 942 SQLi | Sí | Sí | **Sí** (403) | `07-waf/familias-waf.md`, `06-.../http.tsv` |
| CRS 941 XSS | Sí | Sí | **Sí** (2 vectores, 403) | `07-waf/familias-waf.md` |
| CRS 930 LFI | Sí | Sí | **Sí** (403) | `07-waf/familias-waf.md` |
| CRS 932 RCE | Sí | Sí | Parcial (403 en un control negativo, sin registro guardado) | `07-waf/crs-inventario-vigente.txt` |
| Parches virtuales 100001/100002 | Sí | Sí | **Sí** (403) | `10-siem/disparadores.txt` |
| Rutas sensibles, rate limit, cabeceras, CORS | Sí | Sí | **Sí** (A4-A6, A8-A11) | `06-.../resumen-ataques.md` |
| Falsos positivos (uso real de la interfaz) | — | Sí | **Sí** (histórica 7, vigente 0) | `07-waf/recorrido-frontend-*.md` |

## RASP
| Criterio | Estado | Evidencia |
|---|---|---|
| Modo monitoreo (detecta sin bloquear) | **Cumple** | `09-rasp/modo-block-false.txt` (5/5 detectados) |
| Modo bloqueo con respuesta controlada | **Cumple** | `09-rasp/modo-block-true.txt` (5/5 403, legítimas 200, 0 reinicios) |
| Sinks distintos de `sqlite3` | **Pendiente** | — |

## SIEM
| Criterio | Estado | Evidencia |
|---|---|---|
| Tres fuentes en Loki | **Cumple** | `10-siem/ingesta-por-fuente.txt` |
| 9 reglas cargadas; disparo representativo | **Cumple** (8 de ataque/anomalía en firing; ingesta ausente probada aparte) | `10-siem/reglas-tras-disparadores.txt`, `alerta-ingesta-ausente.txt` |
| Falso positivo BOLA tratado | **Cumple** | `10-siem/reglas-tras-trafico-legitimo.txt` |
| Alloy sin root ni socket; proxy de solo lectura | **Cumple** | `10-siem/proxy-socket-docker.txt` |
| Sin datos sensibles en el SIEM | **Parcial** | Nuevos datos redactados (`redaccion-tokens-loki.txt`); líneas previas con tokens de cuentas de prueba siguen en Loki (purga pendiente de autorización) |
| Notificaciones, autenticación, alta disponibilidad | **Pendiente** (limitación de laboratorio) | `PLAN_PENDIENTES_POST_CIERRE.md` |

## Tratamiento del riesgo y heatmaps
| Criterio | Estado | Evidencia |
|---|---|---|
| Cinco opciones con decisión principal/complementaria y estado real | **Cumple** | `docs/fase-6/riesgo-vigente/tratamiento-riesgo-vigente.md` §4 |
| Tipo e impactos | **Cumple** | idem §3 |
| Heatmaps inherente y residual desde datos versionados | **Cumple** | `docs/fase-6/riesgo-vigente/img/` |
| Responsables y aceptaciones con vigencia | **Cumple** (por rol) | idem §4-§5 |
| Dos fotografías separadas | **Cumple** | Histórica `docs/fase-6/tratamiento-riesgo.md` (4C/12A/7M/1B) y vigente (1C/11A/9M/3B) |
