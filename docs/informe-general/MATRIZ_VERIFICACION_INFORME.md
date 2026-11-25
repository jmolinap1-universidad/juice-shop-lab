# Matriz de verificación del Informe General – Opción B (2026-11-25)

Documento revisado: `Informe_General_Opcion_B_UMG.docx` y su PDF equivalente (147 páginas en ambos; índice con 114 entradas
enlazadas). Las páginas corresponden al PDF. **Estado:** *Cubierto* = el criterio está desarrollado con evidencia;
*Parcial* = cubierto con una brecha declarada en el propio informe; *Pendiente* = depende del equipo o del catedrático.
Esta matriz no asigna una nota ni afirma un cumplimiento total.

## 1. Estructura obligatoria y formato
| Criterio | Sección / página | Evidencia | Estado |
|---|---|---|---|
| Orden, numeración y títulos de la estructura obligatoria | Portada (1), Resumen (2), Índice (4), 1-6.6 (8-147) | Marcadores del PDF idénticos a la estructura | Cubierto |
| Portada institucional | p. 1 | Carátula del documento de la Fase 6 conservada; solo cambia el título | Cubierto (los correos conservan el formato de la carátula original) |
| Arial 12, texto negro, interlineado 1.5, justificado, sangría 1,27 cm, márgenes 2,54 cm | Todo el cuerpo | Comprobación automática del PDF: 8655 fragmentos de texto, todos Arial 12 y color negro | Cubierto |
| Índice automático con hipervínculos y tres niveles | pp. 4-7 | Campo TOC `\o "1-3" \h`, 114 hipervínculos | Cubierto |
| Tablas y figuras numeradas, con título y nota de fuente | 57 tablas y 15 figuras | Revisión página por página | Cubierto |
| Referencias APA 7 con sangría francesa | 6.6 (pp. 144-147) | 37 referencias; citas autor-fecha concordantes | Cubierto |
| Paginación coherente con la portada | Portada sin número; el número comienza en la p. 2 | Igual que el documento institucional de la Fase 6 | Cubierto |

## 2. Seis fases de la consigna
| Fase | Sección / página | Evidencia principal | Estado |
|---|---|---|---|
| 1. Inventario CIA, DFD, STRIDE, DREAD, siete capas | 2.1-2.5 (16-40); 5.6 capas (102-103) | Inventario CSV (42 activos), Threat Dragon, trazabilidad.json | Cubierto (revisión del modelo por el equipo pendiente) |
| 2. Arquitectura cloud, IAM, WAF, API Gateway, cifrado | 4.1 (64-71), 4.6 (79-80) | Terraform + Checkov, despliegue en Render, TLS medido | Parcial: CDN propia y TLS 1.3 exclusivo; cifrado en reposo solo declarado |
| 3. DevSecOps: SAST, SCA, SBOM, código seguro | 3.5-3.6 (58-61), 4.3 (74-77), 4.7 (80-84) | Semgrep, CodeQL, npm audit, OSV, Grype, SBOM, puerta de release, CI | Cubierto |
| 4. Caja negra, gris y blanca; abuso; superficie | 3.1-3.3 (41-56) | Nmap, ZAP, sqlmap, A1-A12, BOLA, T1-T10, 2FA | Cubierto (Burp Suite sin evidencia: declarado como pendiente en el Anexo F) |
| 5. Contenedores, hardening, IaC, WAF, monitoreo | 3.7 (61-63), 4.5 (77-79), 5.1-5.5 (85-95) | Trivy, Hadolint, Checkov, docker inspect, WAF, RASP, SIEM | Cubierto (Docker Bench pendiente; SIEM sin 24/7) |
| 6. Riesgo inherente frente a residual, ISO/IEC 27005 | 2.5 (33-40), 5.6 (95-104), 6.1 (105) | Registro validado (382 comprobaciones), mapas de calor | Cubierto |

## 3. Componentes de la rúbrica
| Componente | Sección / página | Evidencia | Estado |
|---|---|---|---|
| Análisis de riesgos y activos | 2 (16-40), 5.6 (95-104), Anexos A-C | Inventario ISO 27001 completo, CIA, STRIDE/DREAD por amenaza y caso, 7 capas con 4 subcapas, heatmaps, cinco decisiones, tipos e impactos | Cubierto |
| Arquitectura cloud y DevSecOps | 4.1, 4.6, 4.7 (64-84) | Diagramas objetivo y real, flujo web a BD administrada, IAM, AES-256/TLS 1.3, SAST/SCA, IaC | Parcial (CDN, TLS 1.3 exclusivo, MFA de cuentas y cifrado en reposo) |
| Implementación de ciberdefensa | 3.1-3.3 (41-56) | Pruebas ejecutadas, BOLA, autenticación, abuso, endpoints, puertos, perímetro local y cloud | Cubierto |
| Implementación de ciberseguridad | 4.2-4.5, 5.1-5.4 (71-95) | Mitigación por hallazgo, 14 parches, WAF, RASP, SIEM, hardening, pruebas antes y después | Cubierto |
| Informe técnico y formato APA | Todo el documento | Formato verificado, referencias APA 7, dictamen y conclusiones fundamentadas | Cubierto |

## 4. Pendientes que el informe declara
| Pendiente | Dónde se declara | Responsable |
|---|---|---|
| Aceptación de Juice Shop como Opción B | 1.1 (8-9), Anexo F | Catedrático |
| MFA de las cuentas de GitHub y Render | 4.1 (70), 6.1, Anexo F | Equipo |
| Revisión del modelo de Threat Dragon | 6.3, Anexo F | Equipo |
| Aprobación formal de excepciones y aceptaciones | 5.6, Anexo F | Dueño del riesgo |
| Base de datos de Render (vence 2026-12-24) y excepción de marsdb (2026-12-31) | 5.5, 6.3 | Operaciones cloud; desarrollo |

## 5. Coincidencia Word/PDF
El PDF se exportó con Microsoft Word desde el mismo `.docx`, después de actualizar el índice y los campos (`build/word-finalizar.ps1`).
Ambos tienen 147 páginas. Las imágenes son las originales del repositorio o diagramas generados desde su documentación (`build/diagramas/`).
