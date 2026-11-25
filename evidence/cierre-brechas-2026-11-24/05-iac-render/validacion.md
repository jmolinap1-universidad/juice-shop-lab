# Validación IaC de Render (render.yaml)

Esquema: `render.yaml.schema.json` (https://render.com/schema/render.yaml.json), jsonschema Draft 2020-12.

| Comprobación | Resultado | Detalle | Motivo |
|---|---|---|---|
| Esquema oficial de Render (render.yaml.json) | OK | sin errores | Sintaxis y campos válidos para la plataforma |
| Un único servicio web | OK | 1 | Plan gratuito: un servicio |
| Plan gratuito (sin costo) | OK | web=free bd=['free'] | Regla del proyecto: entorno gratuito |
| Construcción Docker desde el Dockerfile cloud verificado | OK | ./deploy/cloud/Dockerfile | La fuente se comprueba contra el diff auditado al construir |
| Despliegue automático desactivado | OK | off | Cada despliegue es una decisión explícita |
| Chequeo de salud real | OK | /healthz | /healthz atraviesa nginx y consulta la app |
| La rama desplegada existe en el repositorio | OK | main → 6f2fa615190b | Evita desplegar una rama inexistente |
| Ningún secreto con valor en el archivo | OK | ninguno | Los secretos van como sync:false (los introduce el equipo) |
| Usuarios de la puerta como secreto (sync: false) | OK |  | Acceso restringido sin credenciales en el repo |
| Clave JWT generada por el contenedor | OK |  | D-21: nadie manipula la clave de firma |
| BD conectada por referencia, no por cadena escrita | OK |  | La cadena con contraseña no está en el repo |
| IP real sin recursión (X-Forwarded-For) | OK |  | Un X-Forwarded-For falsificado no salta el límite de intentos (probado en la nube) |
| BD juice-lab-db: sin acceso externo (ipAllowList vacía) | OK | [] | Solo el servicio por la red privada |
| BD juice-lab-db: PostgreSQL 17 (versión probada) | OK | 17 | Misma versión que la prueba local del parche 13 |
| BD juice-lab-db: misma región que el servicio | OK | virginia / virginia | La red privada de Render es por región |

**Resultado: 15 OK · 0 fallos.**
