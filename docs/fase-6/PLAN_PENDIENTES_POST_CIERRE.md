# Pendientes reales tras el cierre de la Fase 6 (2026-11-21)

Solo trabajo no hecho o no probado. Responsables por rol (el equipo asigna personas). Prioridad: **A** alta, **M** media,
**B** baja.

## 1. Fase 6 local (laboratorio)
| # | Pendiente | Riesgo | Prioridad | Responsable | Impacto si no se hace | Siguiente paso |
|---|---|---|---|---|---|---|
| L1 | Actualizar dependencias con CVE CRITICAL (crypto-js, decompress, jsonwebtoken ×2, lodash, marsdb, tar) | R20, R04 | A | Desarrollo backend | Único riesgo crítico; sigue aceptado temporalmente | Plan por paquete en `evidence/.../08-trivy/analisis-dependencias.md`; regresión completa tras cada cambio |
| L2 | Purgar de Loki las líneas anteriores a la redacción que contienen tokens de cuentas de prueba (también en el volumen del stack histórico) | R24 | A | Monitoreo | Tokens de prueba visibles en el SIEM local | **Requiere autorización** (borra datos): API de borrado de Loki o recrear el volumen |
| L3 | Auditar BOLA en el resto de objetos (Complaints, PrivacyRequests, Recycles, Memories, historial de pedidos) | R06, R23 | A | Desarrollo backend | Posibles accesos ajenos no detectados | Extender `security/ops/bola-recursos.sh` |
| L4 | Probar XXE, inyección NoSQL en reseñas y SSRF | R10, R08, R11, R23 | A | Operaciones de seguridad | Vías de exposición de datos sin medir | Casos acotados contra el laboratorio |
| L5 | Mensajes internos de la base de datos en respuestas 5xx de la capa REST genérica (finale) | R18 (A10:2025) | M | Desarrollo backend | Divulgación de detalles internos (sin traza de pila) | Manejador de errores en los hitos de finale |
| L6 | Prueba documentada de la familia CRS 932 (RCE) | R09 | M | Operaciones de seguridad | Familia solo observada | Caso acotado con registro del audit log |
| L7 | Sinks del RASP distintos de `sqlite3` (`fs`, `http`, `child_process`, `vm`) | R22, R09 | M | Operaciones de seguridad | Alcance del RASP no demostrado | Escenarios por sink |
| L8 | Notificación a personas (Alertmanager/correo) | R19 | M | Monitoreo | Alertas solo visibles en el panel | Alertmanager local |
| L9 | Hueco residual de ingesta en contenedores efímeros | R19 | B | Monitoreo | Pérdida de líneas en recreaciones muy rápidas | Driver de logs hacia el colector |
| L10 | Parche 05 (eval) y 2FA sin prueba dinámica | R09, R05 | B | Desarrollo backend | Corrección solo inspeccionada | Ejecutar fuera de Docker o con `safetyMode: disabled` |
| L11 | Codificación de salida en el frontend | R13 | M | Desarrollo frontend | XSS depende del WAF | Revisión de plantillas Angular |
| L12 | DFD en Threat Dragon; carátula y maquetación institucional | — | M | Equipo | Brecha documental de la rúbrica | Seguir `INSTRUCCIONES_ACTUALIZAR_INFORME_INSTITUCIONAL.md` |

## 2. Hito C — despliegue cloud (Seenode/AWS), NO iniciado
| # | Requisito previo | Responsable | Nota |
|---|---|---|---|
| C1 | Autorización explícita del equipo y confirmación de cupos, prueba gratuita y costos antes de crear cualquier servicio | Líder del proyecto | Nada se crea sin aprobación |
| C2 | Conexión de la cuenta solo por OAuth (sin escribir credenciales en el repositorio) | Arquitectura cloud | Gitleaks lo verifica |
| C3 | Publicar únicamente un servicio apto (nunca la imagen vulnerable); evaluar L1-L5 antes | Equipo | La variante corregida sigue con R20 crítico |
| C4 | HTTPS efectivo, BD administrada y cifrada, WAF/CDN del proveedor | Arquitectura cloud | Hoy solo en el diseño de Terraform (Fase 2) |
| C5 | SIEM con autenticación, sin acceso anónimo, retención y notificaciones | Monitoreo | Limitaciones aceptadas solo para 127.0.0.1 |
