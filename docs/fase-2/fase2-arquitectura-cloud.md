# Fase 2 – Arquitectura cloud y requisitos de seguridad

**Estado:** diseño AWS validado estáticamente (nunca aplicado) y despliegue real en Render (capa gratuita, acceso restringido).
Índice de evidencias: [`evidence/fase-2/LEAME.md`](../../evidence/fase-2/LEAME.md).

| Etiqueta | Significado |
|---|---|
| **Diseño** | Expresado en `infra/terraform/` y validado con `terraform validate`, `terraform plan` y Checkov; sin `apply` ni recursos facturables |
| **Conceptual** | Componente del diseño que **no** está en el Terraform (CDN, API Gateway gestionado, BD administrada en AWS) |
| **Desplegado** | Corre en Render y se midió con pruebas (`render.yaml`, `deploy/cloud/`) |

## 1. Arquitectura objetivo (AWS, diseño)
Fuente: `infra/terraform/` (`network.tf`, `app.tf`, `security.tf`, `variables.tf`, `outputs.tf`, `versions.tf`). Diagrama:
`evidence/fase-2/capturas/diagramas/03-aws-objetivo.png` (fuente `docs/arquitectura/diagramas/03-aws-objetivo.mmd`).

| Componente | Recurso Terraform | Control de seguridad |
|---|---|---|
| Red | `aws_vpc`, subredes públicas y privadas, `aws_nat_gateway`, `aws_flow_log` | App sin IP pública; VPC Flow Logs cifrados |
| Entrada | `aws_lb` + `aws_lb_listener` (HTTPS) | `ELBSecurityPolicy-TLS13-1-3-2021-06` (solo TLS 1.3); protección contra borrado |
| WAF | `aws_wafv2_web_acl` asociada al ALB | Reglas gestionadas Common, SQLi, KnownBadInputs, reputación de IP, IP anónimas y límite de 500 peticiones por IP |
| Cómputo | `aws_ecs_cluster`, `aws_ecs_task_definition` (Fargate 512 CPU / 1024 MB), `aws_ecs_service` | Usuario 65532, sin privilegios, `drop ALL`; solo accesible desde el grupo de seguridad del ALB |
| Identidad | `aws_iam_role` execution, task y flow | Ejecución: solo ECR propio y su grupo de logs; tarea: sin políticas; flow: solo su grupo de logs |
| Cifrado | `aws_kms_key` (rotación), S3 de registros con SSE | Logs de CloudWatch con KMS; registros del ALB con SSE-S3 (AES-256) |
| Conceptual | — | CDN con WAF gestionado y BD administrada privada (no forman parte del plan) |

Validación: `terraform validate` correcto; `terraform plan` = 45 recursos por crear (`evidence/fase-2/terraform-plan.txt`).
Checkov 3.4.0: 142 superadas / 7 fallidas → 144 / 0 con 5 omisiones justificadas en el código (CKV_AWS_336, 145, 18, 144 y
CKV2_AWS_62) (`evidence/fase-2/checkov-inicial/`, `checkov-final/`).

## 2. Arquitectura desplegada (Render)
Detalle operativo: [`docs/cierre-tecnico/DESPLIEGUE_CLOUD_RENDER.md`](../cierre-tecnico/DESPLIEGUE_CLOUD_RENDER.md).
Diagrama: `evidence/fase-2/capturas/diagramas/02-render-real.png`; flujo hasta la BD: `04-flujo-bd.png`.

- **Servicio web** `juice-lab-masi-staging` (Docker, plan free): un contenedor Alpine con nginx + ModSecurity 3.0.17 + CRS 4.25.2
  (puerta `/__acceso`, límite de intentos, cabeceras) y la variante corregida (parches 01-14) con RASP en `127.0.0.1:3000`.
- **PostgreSQL 17** (plan free) sin acceso externo (`ipAllowList: []`), conectado por la red privada con TLS obligatorio.
- **Blueprint** `render.yaml` desde `main`, despliegue manual; secretos `sync: false`; validado con el esquema oficial y una
  política propia: 15/15 y prueba negativa (`evidence/cierre-brechas-2026-11-24/05-iac-render/`).
- Commit desplegado: `768d1da` (2026-11-25). Vistas del sitio publicado: `evidence/fase-2/capturas/sitio-render-2026-11-25/`.

## 3. Requisitos de seguridad: diseñado frente a implementado
Tabla completa: [`docs/cierre-tecnico/REQUISITOS_CLOUD_DISENO_VS_IMPLEMENTADO.md`](../cierre-tecnico/REQUISITOS_CLOUD_DISENO_VS_IMPLEMENTADO.md).

| Requisito | Diseño (AWS) | Desplegado (Render, medido) | Estado |
|---|---|---|---|
| CDN | CloudFront (conceptual) | Borde de Cloudflare gestionado por Render; sin caché propia (la cabecera no prueba caché) | Parcial |
| API Gateway | ALB + WAF (gateway gestionado conceptual) | nginx como punto de entrada único: autenticación previa, límite de intentos, métodos, tamaño, WAF (28/28) | Función equivalente |
| IAM / menor privilegio | Roles execution/task/flow mínimos | Clave de API de solo lectura (despliegues → 403), BD privada, contenedores sin root; MFA de cuentas sin verificar | Cumple en lo técnico |
| AES-256 | KMS / SSE | TLS 1.3 con TLS_AES_256_GCM_SHA384 medido; en reposo **declarado** por Render | En tránsito medido; reposo declarado |
| TLS 1.3 | Política TLS 1.3 del ALB | TLS 1.3 negociado (OpenSSL y navegador HTTP/3); TLS 1.0/1.1 rechazados; 1.2 aceptado por la plataforma | 1.3 disponible, no exclusivo |

## 4. Limitaciones
Sin CDN con caché propia ni WAF gestionado (requieren dominio de pago); TLS hacia la BD sin verificar el certificado
(`sslmode=require`); cifrado en reposo no verificable por el cliente; WAF y app en el mismo contenedor (un solo servicio gratuito);
la BD gratuita vence el 2026-12-24.
