# Requisitos cloud: diseñado frente a implementado (cierre de brechas, 2026-11-24)

**Diseñado** = arquitectura AWS de la Fase 2 (`infra/terraform/`, validada solo con Checkov y `plan`; nunca aplicada).
**Implementado** = lo que corre hoy en Render (capa gratuita) y se midió. Un requisito solo figura como cumplido si hay
evidencia de ejecución; lo que solo declara el proveedor se marca como «declarado». Prioridad: soluciones gratuitas.

| Requisito | Diseñado (AWS, Fase 2) | Implementado (Render, medido) | Estado | Evidencia |
|---|---|---|---|---|
| **CDN** | CloudFront delante del ALB | El tráfico atraviesa la red de **Cloudflare** que Render pone delante (cabecera `Server: cloudflare`, `x-render-origin-server: waf`), con protección DDoS de la plataforma. **Sin** caché ni reglas propias: el *edge caching* de Render es de pago y un CDN propio exige dominio | **PARCIAL** | `evidence/cierre-tecnico-2026-11-23/13-cloud/render/puerta-acceso.md` (fila Server) |
| **API Gateway** | Amazon API Gateway / ALB con reglas | **Puerta de enlace propia en nginx** dentro del contenedor: punto de entrada único, autenticación previa (`/__acceso`), límite de intentos (5/min, también con `X-Forwarded-For` falsificado), métodos permitidos, tamaño de cuerpo 1 MB, retirada de CORS de la app, WAF (CRS) y cabeceras. No es un producto «API Gateway» | **CUMPLE funcionalmente** (sin producto gestionado) | `13-cloud/render-0be0b5f/puerta-acceso.md` (28/28); `docs/cierre-tecnico/DESPLIEGUE_CLOUD_RENDER.md` |
| **IAM / menor privilegio** | Roles IAM mínimos, KMS | Cuenta de Render del equipo (inicio con GitHub); **API key de solo lectura de Monitoring** (no despliega ni lee secretos); BD **sin acceso externo** (`ipAllowList: []`); secretos `sync:false`; contenedor sin root (uid 101), app sin puerto enrutado; colector sin root, solo lectura y sin capacidades | **CUMPLE** en lo técnico · **SIN VERIFICAR**: MFA de las cuentas de GitHub y Render del equipo | `evidence/cierre-brechas-2026-11-24/06-siem-render/api-key-render.md`; `05-iac-render/validacion.md` |
| **AES-256** | KMS (AES-256) en EBS/RDS | En tránsito: **TLS 1.3 con TLS_AES_256_GCM_SHA384** negociado en el borde (medido). En reposo: Render **declara** AES-256 para PostgreSQL (documentación oficial); no es verificable por el cliente. Conexión app→BD con TLS obligatorio (`DATABASE_SSL`), cifra no medida | **CUMPLE en tránsito (medido)** · **DECLARADO** en reposo | `13-cloud/render-0be0b5f/tls.md`; https://render.com/docs/databases |
| **TLS 1.3** | ALB con política TLS 1.3 | TLS 1.3 **aceptado** y negociado por defecto; TLS 1.0/1.1 **rechazados**; **TLS 1.2 también aceptado** (lo fija Render, no es configurable); HTTP→HTTPS 301; HSTS | **PARCIAL**: 1.3 disponible, no exclusivo | `13-cloud/render-0be0b5f/tls.md` |

## Opciones gratuitas evaluadas para cerrar lo parcial
| Brecha | Opción gratuita | Por qué no se aplicó |
|---|---|---|
| CDN propio / WAF gestionado | Cloudflare Free delante de Render | Exige un **dominio propio** (de pago). Los subdominios gratuitos (p. ej. eu.org) dependen de aprobación externa sin plazo; decisión del equipo |
| Solo TLS 1.3 | Cloudflare Free con «Minimum TLS Version 1.3» | Mismo requisito de dominio propio |
| Acceso Zero Trust en lugar de la puerta propia | Cloudflare Zero Trust / Tunnel (gratuito hasta 50 usuarios) | Mismo requisito de dominio; la puerta propia ya restringe el acceso y está probada |
| MFA verificado | Activar 2FA en GitHub y Render | Configuración de las cuentas personales del equipo: no la puede verificar ni activar el asistente |

## Requisitos que no pueden completarse (y por qué)
1. **CDN con caché y reglas propias, y TLS 1.3 exclusivo:** requieren un dominio propio (costo) o un plan de pago de Render.
   Se mantiene el diseño AWS/CloudFront como referencia y se documenta el riesgo residual en R21.
2. **API Gateway como producto gestionado:** Render no lo ofrece; un gateway externo gratuito también exige dominio. La función
   de gateway la cumple nginx (probado).
3. **Cifrado en reposo verificable:** solo el proveedor puede demostrarlo; queda como «declarado» (responsabilidad compartida).
4. **MFA de las cuentas:** debe confirmarlo el equipo (no hay evidencia técnica accesible).
