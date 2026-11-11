# Instrucciones para sincronizar el documento institucional de la Fase 6

**Para quien ensamble la versión final (equipo / ChatGPT).** El entregable institucional actual
(`docs/fase-6/entregable/Fase6_Operaciones_Monitoreo_Ciberseguridad.docx/.pdf`, commit `98bcb88`, 32 páginas)
contiene cifras y afirmaciones **superadas** por la auditoría de cierre. No se sobrescribió para conservar su
carátula. La versión de referencia del contenido es:

- **Borrador de validación:** `docs/fase-6/entregable/BORRADOR_VALIDACION_Fase6_Operaciones_Monitoreo_Ciberseguridad.docx`
  (y `.pdf`, 37 páginas). Lo genera `docs/fase-6/entregable/build/build.js` en dos pasadas (`toc.js` fija las páginas
  reales del índice). Su carátula es provisional: **no** usarla como carátula institucional.
- **Fuentes técnicas:** `fase6-mitigaciones.md`, `tratamiento-riesgo.md` (generado), `CIERRE_Y_VALIDACION_FASE6.md`.

## 1. Reglas
1. Conservar la carátula oficial y el logo de la UMG del equipo. **No** inventar un logo; si no está disponible, dejar el
   requisito como pendiente.
2. No conservar ninguna cifra de la tabla §3 en su forma anterior.
3. Mantener la diferencia entre *probado*, *inspeccionado*, *diseñado*, *propuesto* y *no efectivo*.
4. Formato: texto principal Arial 12, interlineado 1.5, justificado; tablas Arial 7-9 pt y pies de figura Arial 10 pt
   (ajuste de legibilidad); referencias APA 7 con sangría francesa.

## 2. Nueva estructura (índice del borrador)
Introducción · Objetivos · **1. Estrategia de Mitigación y Ciberseguridad** (1.1 Arquitectura operativa y defensa en
profundidad · 1.2 Controles compensatorios por riesgo · 1.3 WAF: reglas para el OWASP Top 10:2025 · 1.4 RASP: detección
y bloqueo en tiempo de ejecución · **1.5 Monitoreo de APIs: heurística de comportamiento anómalo (nueva)** · 1.6 SIEM:
centralización y correlación de logs · 1.7 Validación integral de los controles) · **2. Tratamiento Formal del Riesgo**
(2.1 Método de valoración · 2.2 Opciones · 2.3 Categorización · 2.4 Matriz de decisiones y plan de tratamiento ·
**2.5 Justificación del riesgo residual (nueva)** · 2.6 Matriz de calor · 2.7 Lectura del riesgo residual) ·
Limitaciones y pendientes · Conclusiones · Referencias · Anexos A-E (**E nuevo**).

## 3. Textos y cifras a reemplazar (citas literales del documento actual)
| Ubicación actual | Texto actual | Reemplazar por |
|---|---|---|
| Figura 12 (pie) | «Defensa completa a través del WAF: A1-A11 mitigados (11/11).» | «Escenario 3 a través del WAF: las once condiciones A1-A11 quedan neutralizadas (403 del WAF en 0,008-0,018 s para la SQLi; 429 en fuerza bruta); el caso A12 (BOLA) sigue vulnerable con HTTP 200.» |
| 1.6, párrafo final | «El SIEM sí lo detecta (API_Enumeracion_Objetos_PosibleBOLA)» | «La alerta API_Enumeracion_Objetos_PosibleBOLA es una heurística con falsos positivos demostrados; no verifica la propiedad del objeto.» |
| Figura 8 (pie) | «seis reglas en firing con su hora de activación» | «cinco reglas en firing vía WAF (la del RASP queda inactiva porque el WAF frenó la inyección) y la regla del RASP en firing cuando la app se ataca sin WAF» |
| Figura 11 (pie) | «seis peticiones legítimas a través de WAF y RASP con respuesta 200/201» | «dos usuarios legítimos: nueve operaciones correctas (siete con 200/201 y dos inicios de sesión con token emitido); la heurística BOLA entra en firing: falso positivo» |
| 1.4 (R22) | Corrección con «--unhandled-rejections=warn» presentada como eliminación verificada | Texto de la sección 1.4 del borrador: causa raíz en Sequelize (`serialize(async …)`), integración `rasp-guard` (403), y `warn` como **no efectivo** (petición colgada 20 s) |
| 1.5 (seguridad del SIEM) | «Alloy lee la salida de los contenedores mediante el socket de Docker en solo lectura» | «Alloy corre como uid 473, sin capacidades y sin el socket; consulta Docker a través de un proxy de solo lectura (escrituras 403). El montaje `:ro` del socket no restringía la API.» |
| Figura 13 (pie) | «8 riesgos críticos y 15 altos» | «8 riesgos críticos y 16 altos» |
| Figura 14 (pie) | «1 crítico (R03), 9 altos, 9 medios y 5 bajos» | «4 críticos (R03, R06, R20, R23), 12 altos, 7 medios y 1 bajo (solo controles probados)» |
| Tabla «Riesgos por nivel» | Inherente 0/1/15/8; residual 5/9/9/1 (Bajo/Medio/Alto/Crítico) | Inherente **0/0/16/8**; residual **1/7/12/4** |
| Conclusiones | «redujo los riesgos críticos de 8 a 1 y los altos de 15 a 9» | «reduce los críticos de 8 a 4 y los altos de 16 a 12» |
| Conclusiones | «activó seis de sus siete reglas durante las pruebas, incluida la detección del BOLA» | «activó cinco de siete reglas a través del WAF, más la del RASP cuando la app se atacó directamente; la alerta BOLA es una heurística» |
| Tabla de controles / Anexo D (R22) | «Node --unhandled-rejections=warn (proceso sin caídas, RestartCount 0) — eliminacion — Verificado» | «Integración rasp-guard: bloqueo → HTTP 403 (eliminación; probado)» y «--unhandled-rejections=warn: no efectivo (petición colgada)» |
| Método (2.1) | Reducción de I por detección; controles «verificados» sin distinguir prueba | Texto de 2.1 del borrador: la detección no reduce el impacto; solo cuentan controles **probados**; ISO/IEC 27005 no prescribe la fórmula |
| Todas las menciones a «A11» como vulnerabilidad | — | A11 = clave **pública**: reducción de superficie, no vulnerabilidad; el hallazgo es la clave privada (R03) |

## 4. Figuras (archivo nuevo → posición en el borrador)
| Fig. | Archivo | Sustituye a |
|---|---|---|
| 1 | `entregable/img/v2-01-arquitectura.png` | `00-arquitectura.png` |
| 2 | `entregable/img/v2-10-stack.png` | `10-stack.png` |
| 3 | `entregable/img/09-crs-inventario.png` (sin cambios) | — |
| 4 | `entregable/img/v2-02-r22-comparativa.png` | nueva |
| 5 | `entregable/img/v2-04-rasp-caida.png` | `04-rasp-caida.png` |
| 6 | `entregable/img/v2-03-rasp-integrado.png` | `05-rasp-bloqueo.png` (era la corrida con `warn`) |
| 7 | `entregable/img/v2-09-falsos-positivos.png` | `01-funcional.png` |
| 8 | `entregable/img/v2-06-siem-reglas.png` | `07-siem-reglas.png` |
| 9 | `evidence/fase-6/validacion-2026-11-10/03-waf-rasp-siem/capturas/grafana-dashboard-siem.png` | `evidence/fase-6/siem/capturas/grafana-dashboard-siem.png` |
| 10 | `entregable/img/v2-07-siem-metricas.png` | `08-siem-metricas.png` |
| 11 | `entregable/img/v2-08-proxy-socket.png` | nueva |
| 12 | `entregable/img/v2-05-defensa-completa.png` | `06-defensa-completa.png` |
| 13-15 | `docs/fase-6/img/heatmap-antes.png`, `heatmap-despues.png`, `niveles-antes-despues.png` (regenerados) | mismos nombres, contenido nuevo |

Las figuras `02-rasp-arranque.png` y `03-rasp-deteccion.png` de la versión anterior siguen siendo válidas como apoyo,
pero el borrador no las usa. Los pies de figura exactos están en el borrador.

## 5. Tablas
Las tablas 1-12 del borrador se generan desde `datos/riesgos-calculados.json` o se transcriben de la evidencia:
1 controles por riesgo · 2 cobertura OWASP (6 columnas: instalada / observada / probada / raíz pendiente) ·
3 configuraciones del RASP · 4 reglas del SIEM (escenarios 3 y 3b) · 5 escenarios de validación · 6 opciones de
tratamiento · 7 registro (tipo e impacto) · 8 matriz de decisiones con estado y prioridad · 9 plan (responsable,
revisión, pendiente) · 10 aceptaciones temporales · 11 justificación del residual · 12 riesgos por nivel. Copiarlas
del borrador; si se editan en Word, conservar los valores.

## 6. Anexos
- **A:** extracto del manifiesto con 243 archivos de la Fase 6 (prefijo de 16 caracteres por espacio; hash completo en
  `evidence/MANIFEST.sha256`). Si se regenera la evidencia, regenerar el borrador para actualizarlo.
- **B:** entradas de la bitácora con fase 6, incluidas las **CORRECCIONES** (02b, 02c, línea base intento 1).
- **C:** reglas LogQL (`deploy/hardened/siem/rules/fake/alertas.yaml`).
- **D:** controles por riesgo con verificación y evidencia.
- **E (nuevo):** validación automática (301 comprobaciones) y prueba negativa del validador.

## 7. Índice con hipervínculos
El borrador tiene un índice estático con **22 hipervínculos internos** a marcadores en cada título (verificado: 22
`w:hyperlink w:anchor` en el DOCX y 22 enlaces con destino interno en el PDF). Si en Word se prefiere un índice
automático, usar *Referencias → Tabla de contenido* con los estilos Título 1 y 2 (los títulos ya los usan) y
actualizarlo antes de exportar a PDF.

## 8. Fuentes en el PDF
El PDF del borrador se exportó con LibreOffice en un contenedor sin Arial: usa **Liberation Sans** (equivalente métrico
de Arial) y Liberation Mono. Al exportar desde Word en Windows se usará Arial; revisar la paginación final.

## 9. Lista de comprobación final
- [ ] Carátula institucional con logo oficial (no el texto provisional del borrador).
- [ ] Ninguna cifra de la columna «Texto actual» de §3 permanece.
- [ ] Figuras 1-15 según §4 y tablas 1-12 según §5.
- [ ] Índice actualizado con páginas correctas e hipervínculos funcionales.
- [ ] Riesgos por nivel: inherente 0/0/16/8, residual 1/7/12/4 (Bajo/Medio/Alto/Crítico), total 24.
- [ ] BOLA (A12/R06) presentado como **vulnerable y crítico**; A11 no presentado como vulnerabilidad.
