# Decisiones técnicas

| # | Fecha | Decisión | Motivo |
|---|---|---|---|
| D-01 | 2026-11-03 | OWASP Juice Shop como aplicación principal | E-commerce funcional, código abierto, vulnerabilidades verificables; conserva el enfoque de Kakaw Store. crAPI queda como complemento opcional de APIs; WebGoat se descarta (lecciones, no aplicación). |
| D-02 | 2026-11-03 | Dos entornos: laboratorio vulnerable (127.0.0.1) y entorno endurecido | No publicar una aplicación vulnerable; medir riesgo inherente vs. residual con los mismos ataques. |
| D-03 | 2026-11-03 | Ejecución técnica en Claude Code local; coordinación y documentos en Cowork | Cowork no puede ejecutar comandos en el equipo ni crear sesiones de Claude Code. |
| D-04 | 2026-11-03 | Escaneos automáticos también en GitHub Actions | Evidencia pública y reproducible, independiente del equipo local. |
| D-05 | 2026-11-03 | Despliegue cloud diferido | Requiere aprobación de costos y credenciales del equipo. |
