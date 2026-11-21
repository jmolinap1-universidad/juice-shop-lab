# Instrucciones para actualizar el informe institucional de la Fase 6 (solo cambios necesarios)

El Word/PDF institucional del equipo **no se modificó**. Estas instrucciones indican qué sección cambiar y con qué dato,
siguiendo la estructura del borrador (`INSTRUCCIONES_SINCRONIZACION_DOCUMENTO.md` §2). Todas las cifras provienen de
archivos versionados; no las redondee ni las combine con las históricas.

## 1. Regla de redacción
Presente **dos configuraciones**: «Fase 6 histórica (imagen oficial + defensa, 2026-11-10)» y «Configuración vigente
(variante corregida + defensa, cierre 2026-11-21)». Las cifras históricas se conservan como antecedente; las conclusiones
usan la vigente.

## 2. Cambios por sección
| Sección | Cambio | Dato nuevo | Fuente |
|---|---|---|---|
| 1.1 Arquitectura operativa | Añadir que el entorno vigente se levanta con `make ops-corregido-up` (proyecto `juice-corregida-defensa`) y que la app ejecuta el código corregido | Parches 01-10; imagen verificada contra el diff auditado | `CIERRE_FINAL_FASE6.md` §2 |
| 1.2 Controles compensatorios | Indicar que las correcciones definitivas ya están PROBADAS sin WAF | Regresión 16/16; A1-A3, A7, A8, A12 mitigados por el código | `evidence/fase-6/cierre-final-2026-11-21/04-escenario-B-corregida/` |
| 1.3 WAF | (a) Familias probadas: SQLi, XSS (2 vectores), LFI, parches virtuales; RCE solo observada. (b) Nuevo párrafo «Falsos positivos medidos»: la configuración histórica bloqueaba 7 de 35 llamadas legítimas de la interfaz (PUT/DELETE por la regla 911100; `/rest/user/whoami` por 932260); la vigente, 0 de 35, gracias a `ALLOWED_METHODS` y a una exclusión acotada | 7/35 → 0/35 | `07-waf/recorrido-frontend-*.md`, `07-waf/familias-waf.md` |
| 1.4 RASP | Sustituir los resultados por los de la variante corregida | Monitoreo 5/5 detectados (app 401); bloqueo 5/5 403 en ~0,02 s; 0 reinicios; alcance: `sqlite3` | `09-rasp/` |
| 1.5 Monitoreo de APIs | (a) La regla de enumeración BOLA pasa a «indicador de investigación» (severidad info). (b) Nueva regla de alta confianza `API_BOLA_AccesoAjenoDenegado`: inactiva con tráfico legítimo, activa con el intento cruzado. (c) BOLA corregido en 5 tipos de objeto (parche 10) | 0 VULNERABLE / 10 PROTEGIDO; 7/7 operaciones legítimas | `02-bola-recursos/`, `10-siem/reglas-tras-*.txt` |
| 1.6 SIEM | (a) 9 reglas (antes 7). (b) Alerta de pérdida de ingesta probada (pending → firing → resuelta). (c) Hallazgo y corrección: tokens `Authorization`/cookies en el audit log enviados a Loki → redacción en Alloy. (d) Descubrimiento de contenedores 60 s → 5 s (detecciones del RASP en Loki tras recrear la app: 0 de 5 antes del ajuste, 5 de 5 después) | Ver columna | `10-siem/` |
| 1.7 Validación integral | Reemplazar la tabla de escenarios por A (vulnerable), B (corregida), C (corregida + RASP sin WAF), D (defensa completa) | A: 11/11 + A12; B y C: 6 abiertos de configuración, A12 403; D: 0 abiertos | `TRAZABILIDAD` y `LEAME.md` de la evidencia |
| 2.4 Matriz de decisiones | Usar la tabla vigente | 24 decisiones; cinco opciones | `riesgo-vigente/tratamiento-riesgo-vigente.md` §4 |
| 2.5 Justificación del residual | Añadir los cambios: R06 3×4→2×4, R13 4×4→3×4, R23 4×5→3×5 (y los del hito A: R01, R02, R03, R05, R07, R14) | Razones literales en el JSON | `datos/riesgos-vigente.json` |
| 2.6 Matriz de calor | Sustituir por las figuras vigentes | Inherente 8 C / 16 A → residual **1 C / 11 A / 9 M / 3 B** | `riesgo-vigente/img/heatmap-comparativo.png` |
| 2.7 Lectura del residual | Único crítico: R20 (dependencias, aceptación temporal). Riesgos altos: tabla de `CIERRE_FINAL_FASE6.md` §5 | — | idem |
| Limitaciones y pendientes | Reemplazar por `PLAN_PENDIENTES_POST_CIERRE.md` (sección local) | — | — |

## 3. Figuras (alta resolución, archivos originales)
| Figura | Archivo |
|---|---|
| Matriz de calor comparativa (vigente) | `docs/fase-6/riesgo-vigente/img/heatmap-comparativo.png` (2160×1120) |
| Niveles antes/después (vigente) | `docs/fase-6/riesgo-vigente/img/niveles-antes-despues.png` |
| Panel del SIEM con datos reales | `evidence/fase-6/cierre-final-2026-11-21/10-siem/capturas/grafana-dashboard-siem-vigente.png` (1700×2100) |

Nota para la figura del SIEM: indicar que se capturó con la ventana posterior a la redacción de tokens
(`ventana-captura.txt`).

## 4. Anexos
- **Anexo A (manifiesto):** regenerar el extracto desde `evidence/MANIFEST.sha256` (sin pegar hashes completos en el cuerpo).
- **Anexo C (reglas LogQL):** sustituir por `deploy/hardened/siem/rules/fake/alertas.yaml` (9 reglas).
- **Anexo E (validación):** 324 comprobaciones, 0 fallas (`riesgo-vigente/validacion-consistencia.txt`).
