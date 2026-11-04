# Decisiones técnicas

| # | Fecha | Decisión | Motivo |
|---|---|---|---|
| D-01 | 2026-11-03 | OWASP Juice Shop como aplicación principal | E-commerce funcional, código abierto, vulnerabilidades verificables; conserva el enfoque de Kakaw Store. crAPI queda como complemento opcional de APIs; WebGoat se descarta (lecciones, no aplicación). |
| D-02 | 2026-11-03 | Dos entornos: laboratorio vulnerable (127.0.0.1) y entorno endurecido | No publicar una aplicación vulnerable; medir riesgo inherente vs. residual con los mismos ataques. |
| D-03 | 2026-11-03 | Ejecución técnica en Claude Code local; coordinación y documentos en Cowork | Cowork no puede ejecutar comandos en el equipo ni crear sesiones de Claude Code. |
| D-04 | 2026-11-03 | Escaneos automáticos también en GitHub Actions | Evidencia pública y reproducible, independiente del equipo local. |
| D-05 | 2026-11-03 | Despliegue cloud diferido | Requiere aprobación de costos y credenciales del equipo. |
| D-06 | 2026-11-03 | Juice Shop v20.3.0 como submódulo git (no copia) | Fija versión exacta sin duplicar ~500 MB; trazable al commit oficial. |
| D-07 | 2026-11-03 | Herramientas solo vía Docker con versión fija | No hay Node/Python locales; mismo comportamiento local y en CI. |
| D-08 | 2026-11-03 | Terraform con `offline_plan` (sin credenciales) | Evidencia de `plan` sin manejar claves AWS ni generar costos (D-05). |
| D-09 | 2026-11-03 | Sin API Gateway en Fase 2 | Juice Shop es monolito REST detrás de ALB+WAFv2; API Gateway duplicaría el perímetro sin beneficio. |
