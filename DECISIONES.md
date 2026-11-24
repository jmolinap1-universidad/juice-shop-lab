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
| D-10 | 2026-11-21 | Stack vigente de la Fase 6 separado del histórico (`make ops-corregido-up`, proyecto `juice-corregida-defensa`, logs propios) | El residual 2C/11A… solo vale con el código corregido; ambos compartían proyecto, volúmenes y logs y podían confundirse en la exposición. |
| D-11 | 2026-11-21 | Falsos positivos del WAF se corrigen con exclusiones ACOTADAS (una regla, una ruta, un método) y `ALLOWED_METHODS`, sin bajar el umbral ni la paranoia | El CRS bloqueaba PUT/DELETE legítimos y `/rest/user/whoami`; la autorización de esos métodos la impone el código (parche 10). |
| D-12 | 2026-11-21 | Redactar `Authorization`, cookies y JWT en Alloy antes de Loki | El audit log de ModSecurity guarda las cabeceras de la petición; el SIEM no debe almacenar credenciales de sesión. |
| D-13 | 2026-11-21 | Tres fotografías del riesgo sin mezclar: histórica (v2), hito A y vigente; cada una con su configuración | Evita atribuir a la imagen oficial reducciones que solo existen con el código corregido. |
| D-14 | 2026-11-23 | Política de release separada (puerta que bloquea) de la política del laboratorio (solo informa) | La variante corregida se publica solo si cumple; el laboratorio vulnerable se escanea para estudiarlo, nunca se publica. |
| D-15 | 2026-11-23 | `safetyMode: enabled` explícito y correcciones en el código que no dependen de detectar Docker | En otra plataforma `/.dockerenv` puede no existir y reabrirían XXE y NoSQL (probado con el modo seguro desactivado). |
| D-16 | 2026-11-23 | PostgreSQL opcional por `DATABASE_URL` (parche 13) en lugar de una BD decorativa | La opción B exige BD administrada real; la prueba local demuestra que la app la usa (datos en la BD). |
| D-17 | 2026-11-23 | Seenode: no crear recursos hasta decidir la opción y autorizar la publicación | La prueba dura 7 días desde el primer recurso; la variante no es apta para exposición pública abierta. |
