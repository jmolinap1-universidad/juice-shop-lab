# Evidencias de la Fase 2 — Arquitectura cloud y requisitos de seguridad

Índice actualizado el 2026-11-25. **Tipo:** *C* = captura real; *D* = diagrama elaborado desde la documentación y la IaC
(no es una captura); *S* = salida nativa de herramienta o del navegador. **Diseño** (AWS, solo `plan`) y **despliegue real**
(Render) se indican por separado.

| Requisito | Evidencia (ruta) | Tipo | Fecha · entorno · versión | Herramienta | Resultado e interpretación |
|---|---|---|---|---|---|
| Diagrama objetivo (diseño AWS) | `evidence/fase-2/capturas/diagramas/03-aws-objetivo.png` (fuente `docs/arquitectura/diagramas/03-aws-objetivo.mmd`) | D | 2026-11-25 · diseño | Mermaid 10.9.1 | Lo que expresa el Terraform (VPC, ALB TLS 1.3, WAFv2, ECS Fargate, KMS, registros) y lo solo conceptual (CDN, BD administrada) |
| Diagrama real (Render) | `capturas/diagramas/02-render-real.png` | D | 2026-11-25 · Render `768d1da` | Mermaid 10.9.1 | Borde de Render, contenedor único (nginx + ModSecurity + app + RASP), PostgreSQL privado, colector |
| Flujo navegador a PostgreSQL | `capturas/diagramas/04-flujo-bd.png` | D | 2026-11-25 · Render | Mermaid 10.9.1 | Cada paso con su prueba: TLS, puerta, WAF, autorización, consulta parametrizada |
| Terraform validate / plan | `evidence/fase-2/terraform-validate.json`, `terraform-plan.txt` | S | 2026-11-03 · diseño | Terraform 1.16.7 | Válido; `Plan: 45 to add`. Nunca se aplicó (sin recursos facturables) |
| Checkov inicial / final | `evidence/fase-2/checkov-inicial/`, `checkov-final/` | S | 2026-11-03 · diseño | Checkov 3.4.0 | 142 superadas / 7 fallidas, luego 144 / 0 con 5 omisiones justificadas en el código |
| Blueprint de Render (IaC) | `evidence/cierre-brechas-2026-11-24/05-iac-render/validacion.md`, `prueba-negativa.md` | S | 2026-11-24 · `render.yaml` | `security/iac/validar-render.py` (esquema oficial + política) | 15/15; la copia insegura produce 4 fallos detectados |
| PostgreSQL privado y conexión real | `05-iac-render/validacion.md` (`ipAllowList: []`, PostgreSQL 17, misma región); `evidence/cierre-brechas-2026-11-24/10-validacion-render/baterias/regresion.md` y `recorrido.md` | S | 2026-11-25 · Render | curl (arnés propio) | La app opera con la BD administrada: regresión 15/15 y recorrido 35/35 |
| Puerta de entrada (función de API Gateway) | `evidence/fase-2/capturas/render-2026-11-25/01-render-puerta-acceso.png`; `10-validacion-render/baterias/puerta-acceso.md` | C / S | 2026-11-25 · Render | Chromium (Playwright 1.49.1); curl | Sin credenciales: 401 «Authorization Required» (captura real); 28/28 comprobaciones de la puerta |
| TLS 1.3 y certificado HTTPS | `capturas/render-2026-11-25/02-render-tls-navegador.json`; `10-validacion-render/tls.md` | S | 2026-11-24/25 · Render | Chromium; OpenSSL 3.5.7 | El navegador negocia QUIC (HTTP/3, que integra TLS 1.3 por diseño, RFC 9001); certificado `onrender.com` de Google Trust Services (WE1), válido hasta 2027-02-17. OpenSSL: TLS 1.0/1.1 rechazados, 1.2 y 1.3 aceptados (TLS_AES_256_GCM_SHA384) |
| Vista del repositorio | `evidence/fase-2/capturas/repositorio-2026-11-25/` (`01-repositorio-inicio.png`, `02-repositorio-evidencias.png`, `capturas.md`) | C | 2026-11-25 · GitHub (página pública) | Chromium (Playwright 1.49.1), `capturas-evidencia.mjs repositorio` | Página principal y carpeta `evidence/` del repositorio en `main` |
| Sitio publicado en Render | `evidence/fase-2/capturas/sitio-render-2026-11-25/` (`01-sitio-tienda.png`, `02-sitio-busqueda.png`, `03-sitio-login.png`, `capturas.md`) | C | 2026-11-25 · Render `768d1da` | Chromium con la credencial de verificación (archivo ignorado por git, no registrada) | Tras la puerta (200), la tienda, la búsqueda (datos desde PostgreSQL de Render) y el login responden. Los íconos de la interfaz aparecen como texto en la captura (causa no investigada) |
| Proceso de despliegue en Render | `capturas/diagramas/06-despliegue-render.png` (fuente `docs/arquitectura/diagramas/06-despliegue-render.mmd`) | D | 2026-11-25 | Mermaid 10.9.1 | 9 pasos: código en `main`, puerta de release, Blueprint validado, recursos, secretos, Manual Deploy con verificación de la fuente, arranque, verificación y operación |
| Credencial de solo lectura del colector | `evidence/cierre-brechas-2026-11-24/06-siem-render/api-key-render.md`; prueba de 2026-11-25: la consulta de despliegues responde 403 `insufficient_token_scope` (requiere `deploys.read`) | S | 2026-11-24/25 · API de Render | curl | La clave solo lee registros (Monitoring); no despliega ni lee secretos |

**Limitaciones que se mantienen:** sin CDN propia con caché (la cabecera de Cloudflare no prueba caché); TLS hacia la BD sin
verificar el certificado (`sslmode=require`); cifrado AES-256 en reposo **declarado** por Render, no medido; sin capturas del panel
de Render (se usan salidas verificables de la API, del navegador y de las baterías).
