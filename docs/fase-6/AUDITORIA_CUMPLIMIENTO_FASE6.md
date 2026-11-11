# Auditoría de cumplimiento de la Fase 6 — diagnóstico inicial

**Fecha:** 2026-11-11 · **Base auditada:** `main` = `origin/main` = `98bcb88` (sin cambios locales del equipo;
pipeline DevSecOps de ese commit: `success`, run 42955926926).
**Alcance:** rúbrica de la Fase 6 y `PROMPT_CLAUDE_CIERRE_FASE_6_100.md`. Este documento registra el
diagnóstico **antes** de las correcciones; el resultado final está en
[`CIERRE_Y_VALIDACION_FASE6.md`](CIERRE_Y_VALIDACION_FASE6.md).

## 1. Requisitos de la rúbrica y estado encontrado
| # | Requisito | Estado encontrado | Observación principal |
|---|---|---|---|
| 1.1 | Controles compensatorios por cada riesgo | Cumple parcialmente | Cada riesgo tiene controles, pero no se distingue control **configurado/inspeccionado** de **probado**. |
| 1.2 | WAF con reglas para el OWASP Top 10 | Cumple parcialmente | Inventario real y SQLi probada; la tabla mezcla regla instalada, observada y probada. |
| 1.3 | RASP / monitoreo de API | Cumple parcialmente | Detección y bloqueo de SQLi probados, pero el bloqueo deja la petición **sin respuesta HTTP** (ver D1). La alerta BOLA se presenta como "detección del BOLA" cuando es una heurística. |
| 1.4 | SIEM: centralización y correlación | Cumple parcialmente | Funciona (6/7 reglas en firing), pero Alloy usa el socket de Docker como root; `:ro` **no** limita la API de Docker. |
| 2.1 | Matriz de decisiones (5 opciones) | Cumple parcialmente | Faltan responsable, prioridad, estado del tratamiento y criterio de revisión; decisiones "Eliminar" sin control ejecutado. |
| 2.2 | Categorización por tipo e impacto | Cumple | 24 riesgos con tipo e impactos. |
| 2.3 | Heatmaps inherente/residual | Cumple parcialmente | Figuras correctas respecto a sus datos, pero el método residual **sobrestima la reducción** (ver D2). |

## 2. Hallazgos del diagnóstico
| ID | Prioridad | Hallazgo verificado | Corrección prevista |
|---|---|---|---|
| D1 | P0 | **R22** marcado "Eliminar" y residual Bajo. `--unhandled-rejections=warn` evita la caída, pero la petición bloqueada se queda sin respuesta (la evidencia `03-bloqueo-sin-caida` registra respuestas vacías, no un código HTTP). | Reproducir midiendo código HTTP, tiempo y disponibilidad; integrar el error del RASP para responder 403; reclasificar según el resultado. |
| D2 | P0 | `riesgo.py` reduce **I en 1 por cualquier detección** (SCA/SIEM), reduce P por controles solo **inspeccionados** (CSP en R13, límites en R18) y aplica `P=1` a la evitación sin acotar su alcance (R21). Afecta a R01, R02, R04-R07, R12, R13, R16-R20, R23. | Residual **explícito por riesgo** con razonamiento y evidencia; validaciones que impidan reducciones sin control **probado**; la detección no reduce el impacto. |
| D3 | P1 | La matriz no indica responsable, prioridad, estado de ejecución ni revisión; "Transferir" no se marca como propuesta; aceptaciones R04/R20/R24 sin condiciones. | Campos de plan de tratamiento y reglas de coherencia decisión ↔ estado. |
| D4 | P1 | Textos con "A1-A11 mitigados (11/11)" pueden leerse como 11 explotaciones; A11 (clave **pública**) se presenta como vulnerabilidad mitigada; 920350 propuesta sin prueba. | Redacción: "11 condiciones del arnés neutralizadas"; A11 = reducción de superficie; tabla WAF con 4 columnas de verificación. |
| D5 | P1 | `API_Enumeracion_Objetos_PosibleBOLA` correlaciona por IP de la pasarela Docker, sin identidad: falsos positivos (usuarios legítimos distintos) y negativos (una sola lectura cruzada). | Etiquetar como heurística; prueba benigna de falso positivo; análisis de falsos negativos; propuesta de campos mínimos sanitizados. |
| D6 | P1 | Alloy como root con `docker.sock` montado `:ro`: el montaje de solo lectura no restringe las llamadas a la API (crear o ejecutar contenedores). Loki sin autenticación; Grafana anónimo (solo loopback). | Proxy del socket de Docker que solo permite lecturas (GET) y Alloy sin root ni socket; verificar que las escrituras se rechazan. |
| D7 | P1 | La Fase 6 no reejecutó la línea base vulnerable; las corridas del RASP no registran código HTTP ni disponibilidad por petición. | Cuatro escenarios con evidencia nueva e instrumentación HTTP (`ATTACK_HTTPLOG`). |
| D8 | P2 | PDF: 0 anotaciones de enlace (índice sin hipervínculos), carátula con el texto "[ Logo oficial UMG — insertar ]", fuentes sustitutas en la conversión del contenedor (Liberation Sans por Arial; DejaVu Serif para el texto en Consolas). | Índice con enlaces internos en el generador; borrador de validación con otro nombre; instrucciones de sincronización para el documento institucional. |
| D9 | Info | Confirmado correcto: CI `success`, `sha256sum -c` del manifiesto OK, Gitleaks sin fugas, puertos solo en 127.0.0.1, falsos positivos 6/6 OK, BOLA reportado como vulnerable. | Mantener. |

## 3. Orden de trabajo
1. P0: R22 (manejo real del bloqueo) y método residual.
2. P1: SIEM (socket), monitoreo API (heurística, falsos positivos), WAF (tabla de verificación), matriz formal.
3. Validación en cuatro escenarios con evidencia nueva bajo `evidence/fase-6/validacion-*`.
4. Documentación, sincronización del Word/PDF, integridad y commit local (sin push sin autorización).
