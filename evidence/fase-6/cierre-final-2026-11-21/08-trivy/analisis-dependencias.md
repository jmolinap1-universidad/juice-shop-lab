# Dependencias con CVE CRITICAL en la imagen vigente (juice-corregida-rasp:local) — plan de tratamiento

Fuente: `trivy-juice-corregida-rasp.json` (Trivy 0.75.0) y el árbol de dependencias de `evidence/fase-3/sca/package-lock.generated.json`.
No se actualizó ninguna dependencia en este cierre: cada cambio exige regresión funcional y de retos, y varias son
dependencias transitivas de versiones fijadas por el propio Juice Shop. Estado: **PENDIENTE** (riesgo R20, aceptación temporal vigente).

| Paquete (versión) | Quién lo incorpora | ¿Hay versión corregida? | Tratamiento propuesto | Efecto previsto |
|---|---|---|---|---|
| crypto-js 3.3.0 | `pdfkit` (generación del PDF de pedidos) | Sí (4.x) | `overrides` de npm a crypto-js 4.x y probar la factura PDF | Bajo; requiere prueba del PDF |
| decompress 4.2.1 | `download` (dependencia directa) | No | Retirar `download` si no se usa en tiempo de ejecución, o aislarlo; si no, aceptar con justificación | Medio |
| jsonwebtoken 0.1.0 | `express-jwt` 0.1.3 (dependencia directa, fijada) | Sí (en versiones mayores) | Migrar `express-jwt` y `jsonwebtoken` a versiones mantenidas y adaptar `lib/insecurity.ts` | Alto: cambia la API de autenticación |
| jsonwebtoken 0.4.0 | Dependencia directa, fijada | Sí | Igual que la fila anterior | Alto |
| lodash 2.4.2 | `sanitize-html` (versión antigua fijada) | Sí (en `sanitize-html` moderno) | Actualizar `sanitize-html` y repetir pruebas de entrada de usuario | Medio |
| marsdb 0.6.11 | Dependencia directa (reseñas) | No | Sustituir el almacén de reseñas o aislarlo; si no, aceptar con justificación | Alto |
| tar 6.2.1 | `sqlite3` (herramientas de compilación) | Sí (7.x) | `overrides` de npm a tar 7.x y recompilar `sqlite3` | Medio; solo se usa al instalar |

Lectura: ninguna de estas actualizaciones se puede declarar hecha sin una nueva construcción y la regresión completa
(`make corregida-build`, `regresion-corregida.sh`, `recorrido-frontend.sh`, `run.sh`). Se registran como trabajo pendiente
con responsable de desarrollo y no reducen el riesgo R20 en este cierre.
