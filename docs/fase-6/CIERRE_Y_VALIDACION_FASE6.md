# Cierre y validación de la Fase 6 — Operaciones, monitoreo y ciberseguridad

**Fecha:** 2026-11-10 (hora local; UTC 2026-11-11). **Base:** `main` = `origin/main` = `98bcb88` al iniciar la auditoría
(sin cambios del equipo). Diagnóstico previo: [`AUDITORIA_CUMPLIMIENTO_FASE6.md`](AUDITORIA_CUMPLIMIENTO_FASE6.md).
Evidencia nueva: `evidence/fase-6/validacion-2026-11-10/` (índice en su `LEAME.md`).

## 1. Dictamen
La Fase 6 **cumple los requisitos de la rúbrica dentro del alcance declarado**: hay controles compensatorios
definidos para los 24 riesgos, un WAF, un RASP y un monitoreo de API integrados y probados en ejecución, un SIEM que
centraliza y correlaciona tres fuentes, una matriz de decisiones con las cinco opciones, la categorización por tipo e
impacto y matrices de calor regeneradas desde datos validados. **No se declara un 100 %:** quedan abiertos riesgos
críticos que dependen de correcciones de código no desplegadas (BOLA, clave privada JWT, dependencias, datos
personales), familias del WAF configuradas sin prueba, el RASP probado solo en el sink `sqlite3`, un SIEM de laboratorio
(un nodo, sin notificaciones) y la nube sin desplegar. Además, la carátula institucional (logo oficial UMG) sigue pendiente.

## 2. Matriz de cumplimiento (rúbrica)
| Requisito | Estado | Evidencia | Prueba ejecutada | Limitación | Acción correctiva aplicada | Resultado |
|---|---|---|---|---|---|---|
| 1.1 Controles compensatorios por cada riesgo | **Cumple** | `tratamiento-riesgo.md` §6; `datos/riesgos.json` | Validador (`make risk`): 24 riesgos con controles, tipo, implementación, verificación y evidencia existente | Muchos controles definitivos están diseñados o propuestos | Nivel de verificación por control (probado / inspeccionado / sin verificar / no efectivo) | 301 comprobaciones OK |
| 1.2 WAF con reglas para el OWASP Top 10 | **Cumple** (alcance declarado) | `fase6-mitigaciones.md` §3; `evidence/fase-6/waf/crs-inventario.txt`; `validacion-…/03-waf-rasp-siem/` | Arnés vía WAF con código HTTP real; reglas observadas en el audit log | Solo la SQLi está probada; XSS, RCE y LFI configurados sin prueba; BOLA no bloqueable | Tabla instalada / observada / probada / raíz pendiente; A11 reclasificado (clave pública); ruido de 920350 cuantificado | A1-A11 neutralizadas; A12 vulnerable |
| 1.3 RASP / monitoreo de API | **Cumple** (alcance declarado) | `validacion-…/02a`-`02d`, `03b`, `04`; `deploy/hardened/rasp/rasp-guard.js` | Cuatro configuraciones del RASP sin WAF con disponibilidad y reinicios; tráfico legítimo de dos usuarios | Solo el sink `sqlite3` probado; 403 con traza de pila; heurística BOLA con falsos positivos | Integración `rasp-guard` (bloqueo → 403 sin caídas); se retira `warn`; heurística etiquetada y probada | 403 en 0,04-0,15 s; 41/41; RestartCount 0 |
| 1.4 SIEM: centralización y correlación | **Cumple** (laboratorio) | `validacion-…/03-waf-rasp-siem/`, `03b`, `05-siem-seguridad/` | Estado de las reglas, LogQL y panel en la misma ventana; prueba de la API de Docker a través del proxy | Un nodo, Loki sin autenticación, sin notificaciones; ingesta interrumpida ~11 min (corregida) | Proxy de solo lectura del socket; Alloy sin root ni socket | 5/7 reglas vía WAF + RASP en 3b; escrituras a Docker 403 |
| 2.1 Matriz de decisiones (5 opciones) | **Cumple** | `tratamiento-riesgo.md` §4 | Validador V7-V10 (estado coherente, aceptaciones con condiciones, transferencias propuestas) | Responsables por rol (el equipo asigna personas) | Decisión principal + complementaria con estado real; plan con responsable, revisión y pendiente | 24 decisiones; 5 opciones usadas |
| 2.2 Categorización por tipo e impacto | **Cumple** | `tratamiento-riesgo.md` §3 | Validador V14 | — | — | 6 tipos; 4 categorías de impacto |
| 2.3 Heatmaps inherente / residual | **Cumple** | `docs/fase-6/img/heatmap-*.png`, `niveles-antes-despues.png` | Recuentos que suman 24 (V15); tabla del documento comparada con el JSON | Convención del equipo, no fórmula de ISO | Residual explícito y justificado; detección sin efecto en el impacto | 8C/16A → 4C/12A/7M/1B |
| Documento académico (Word/PDF) | **Parcial** | `entregable/BORRADOR_VALIDACION_*.docx/.pdf`; `INSTRUCCIONES_SINCRONIZACION_DOCUMENTO.md` | Índice con 22 hipervínculos (DOCX y PDF); Anexo A = manifiesto (243/243) | Carátula institucional y maquetación final pendientes del equipo | Borrador con otro nombre; el entregable institucional no se sobrescribió | Listo para sincronizar |

## 3. Pruebas de aceptación del prompt de cierre
| Prueba | Estado | Evidencia / comando |
|---|---|---|
| Se usa el `main` real y no se pierden cambios del equipo | Cumple | `git fetch`; `main` = `origin/main` = `98bcb88`; árbol limpio al iniciar |
| El entorno de operaciones levanta y queda saludable | Cumple | `make ops-up` (`WAF_PORT=8088`); `validacion-…/05-siem-seguridad/stack-docker-ps.txt` (WAF y app healthy) |
| Solo puertos de laboratorio en localhost | Cumple | `docker compose … config`: 127.0.0.1:8088/3001/3100; proxy y Alloy sin puertos |
| 24 riesgos con todos los campos | Cumple | `datos/validacion-consistencia.txt` (V1, V6, V7, V13, V14) |
| Sin reducción automática por detección; juicios razonados | Cumple | Regla V5 y `datos/prueba-negativa-validador.txt` (exit 1) |
| Heatmaps y tablas regenerados; recuentos = 24 = JSON | Cumple | `make risk`; aserciones de `generar_md.py` |
| WAF: inventario, casos probados, BOLA no bloqueado | Cumple | `waf/crs-inventario.txt`; `03-waf-rasp-siem/http.tsv`, `bola/` |
| RASP: detección, bloqueo estable, 000 nunca como éxito | Cumple | `resumen-r22.txt`; `LEAME-no-es-mitigacion.md` en 02b y 02c |
| SIEM: todas las fuentes, reglas, activaciones y panel real | Cumple | `resumen-siem-reglas.txt`; `03-waf-rasp-siem/capturas/`; `03b-rasp-a-siem/loki-rasp.txt` |
| Monitoreo BOLA como heurística | Cumple | `04-falsos-positivos/` (falso positivo demostrado) |
| Controles distinguidos por eficacia y ejecución | Cumple | Campo `verificacion` y estados de tratamiento |
| Tráfico legítimo sin falsos positivos relevantes | Cumple (WAF/RASP) | 9 operaciones correctas (7 con 200/201 y 2 logins con token) en dos corridas |
| Bitácora, versiones, SHA-256 y datos redactados | Cumple | `evidence/bitacora.md`; `MANIFEST.sha256` (`sha256sum -c` OK); `LEAME-redaccion.md`; Gitleaks sin fugas |
| README, PROGRESO, Makefile y docs coherentes | Cumple | `make risk`, `make ops-validar`; análisis vigente señalado en el README |
| Reporte para regenerar el Word/PDF | Cumple | `INSTRUCCIONES_SINCRONIZACION_DOCUMENTO.md` |
| Pendientes declarados con responsable y siguiente paso | Cumple | §6 y `tratamiento-riesgo.md` §4 (plan) |

## 4. Resultados antes / después (pruebas reales)
| Medición | Antes | Después | Evidencia |
|---|---|---|---|
| A1-A3 contra la app | 200, ataque con éxito (línea base) | 403 del WAF en 0,008-0,018 s; 403 del RASP en 0,04-0,15 s si se evade el WAF | `01-linea-base-vulnerable/http.tsv`, `03-…/http.tsv`, `02d-…/http.tsv` |
| Bloqueo del RASP | Caída del proceso (RestartCount 0→1; sonda 1/6) o petición colgada (000 a los 20 s) | 403 controlado; sonda 41/41; RestartCount 0 | `resumen-r22.txt` |
| A12 BOLA | Vulnerable (200) | **Sigue vulnerable** (200) vía WAF y sin WAF | `01-…/bola/`, `03-…/bola/` |
| Alloy frente a la API de Docker | Root + socket (API completa) | Uid 473, sin socket; escrituras 403 vía proxy | `05-siem-seguridad/proxy-socket-api.txt` |
| Riesgo (24) | Inherente: 8 críticos, 16 altos | Residual: 4 críticos, 12 altos, 7 medios, 1 bajo | `datos/riesgos-calculados.json` |

Comandos principales (Git Bash, desde la raíz): `make ops-up WAF_PORT=8088` (o el `docker compose` equivalente),
`bash security/ops/escenario-rasp.sh <carpeta> <true|false> [NODE_OPTIONS]`,
`A12_DELAY=65 ATTACK_FASE=6 ATTACK_OUT=<carpeta> ATTACK_HTTPLOG=<carpeta>/http.tsv bash security/attacks/run.sh http://127.0.0.1:8088`,
`bash security/ops/trafico-legitimo.sh http://127.0.0.1:8088 <salida>`, `make risk`, `bash scripts/manifest.sh`.
En este equipo no hay `make`: se ejecutaron los comandos equivalentes de cada target.

## 5. Cambios por archivo
| Archivo | Propósito |
|---|---|
| `deploy/hardened/rasp/rasp-guard.js` (nuevo) | Integración del bloqueo del RASP con la capa de datos (403 sin caídas) |
| `deploy/hardened/Dockerfile.rasp` | Copia y precarga `rasp-guard.js` |
| `deploy/hardened/docker-compose.ops.yml` | `NODE_OPTIONS` parametrizable (sin `warn`); proxy del socket; Alloy uid 473 sin socket; red `socketproxy` interna |
| `deploy/hardened/siem/config.alloy` | Docker vía `tcp://socket-proxy:2375` |
| `security/attacks/run.sh` | `ATTACK_HTTPLOG` (código HTTP real), `ATTACK_TIMEOUT`, rutas Windows para `curl.exe` |
| `security/ops/escenario-rasp.sh`, `probe-disponibilidad.sh`, `trafico-legitimo.sh`, `extraer-logs-waf.py` (nuevos) | Escenarios reproducibles, sonda de disponibilidad, tráfico legítimo, extracción redactada de logs |
| `docs/fase-6/datos/riesgos.json` (v2) | Residual explícito y justificado, verificación por control, plan de tratamiento, aceptaciones |
| `docs/fase-6/datos/riesgo.py`, `generar_md.py` | Validaciones (V1-V15), heatmaps, comprobación cruzada documento ↔ JSON |
| `docs/fase-6/tratamiento-riesgo.md`, `img/*.png` | Regenerados |
| `docs/fase-6/fase6-mitigaciones.md` | Reescrito con los resultados verificados |
| `docs/fase-6/AUDITORIA_CUMPLIMIENTO_FASE6.md`, `CIERRE_Y_VALIDACION_FASE6.md`, `INSTRUCCIONES_SINCRONIZACION_DOCUMENTO.md` (nuevos) | Diagnóstico, cierre y sincronización del documento |
| `docs/fase-6/entregable/build/build.js` + `BORRADOR_VALIDACION_*` + `img/v2-*` | Generador actualizado (índice con hipervínculos) y borrador de validación |
| `docs/fase-6/matriz-riesgo.md`, `docs/informe-ejecutivo.md`, `README.md`, `PROGRESO.md`, `Makefile` | Cifras vigentes, notas de vigencia, targets `risk` y `ops-validar` |
| `evidence/fase-6/validacion-2026-11-10/` (nueva), `evidence/bitacora.md`, `evidence/MANIFEST.sha256` | Evidencia, bitácora e integridad |

## 6. Pendientes reales (sin maquillar)
| Pendiente | Riesgos | Responsable (rol) | Siguiente paso |
|---|---|---|---|
| Desplegar los parches 01-08 (la app no se recompiló) | R01-R03, R05-R07, R09, R14 | Desarrollo backend | Compilar `app-hardened` con los parches y repetir el arnés **sin WAF** |
| Cerrar el BOLA | R06, R23 | Desarrollo backend | Aplicar el parche 08 y extender la verificación de propietario a Addresses, Cards y Feedbacks |
| Clave privada JWT embebida | R03 | Desarrollo backend; Arquitectura cloud | Parche 04 manual, rotación de la clave y gestor de secretos |
| Probar las familias del WAF distintas de la SQLi | R13 y otros | Operaciones de seguridad | Casos acotados de XSS, RCE y LFI contra el laboratorio |
| Probar bloqueos del RASP en `fs`, `http`, `child_process` y `vm`; 403 sin traza de pila | R22 | Operaciones de seguridad | Escenario adicional con `escenario-rasp.sh` |
| SIEM: notificaciones, autenticación, alerta por pérdida de ingesta, alta disponibilidad | R19, R24 | Monitoreo | Alertmanager o correo; regla de ausencia de datos por fuente |
| Validar la regla de 5xx con una ráfaga real | R18 | Monitoreo | Prueba controlada de errores |
| Nube no desplegada | R21 | Arquitectura cloud; líder del proyecto | Solo con aprobación de costos y pruebas en ejecución |
| Carátula institucional y maquetación final | — | Equipo | Seguir `INSTRUCCIONES_SINCRONIZACION_DOCUMENTO.md` |
