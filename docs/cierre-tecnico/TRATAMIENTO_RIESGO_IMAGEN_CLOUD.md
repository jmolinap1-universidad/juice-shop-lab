# Tratamiento del incumplimiento de la política de release de la imagen cloud (2026-11-24)

**Política:** `security/release/politica-release.json` (bloquea secretos, avisos de Hadolint, ERROR de Semgrep sin excepción y
CVE CRITICAL/HIGH de Trivy sin excepción vigente). **Herramienta y versión:** Trivy 0.75.0 en `scripts/pipeline-release.sh`.
No se bajó ningún umbral ni se añadió ninguna excepción nueva.

## 1. Evolución medida (Trivy sobre la imagen que se despliega en Render)
| Iteración | CRITICAL | HIGH | Sin corrección publicada (C+H) | Secretos | Veredicto | Evidencia |
|---|---|---|---|---|---|---|
| Debian, primera imagen desplegada (`e00e920`) | 3 | 135 | — | 1 (clave de ejemplo en `terraform/`) | — (sin puerta) | `evidence/cierre-tecnico-2026-11-23/13-cloud/escaneo-imagen-cloud/` |
| Debian 202611190211 + parches de Debian + `.dockerignore` (`0be0b5f`) | 2 | 76 | 76 | 0 | **BLOQUEADA** | `evidence/cierre-tecnico-2026-11-23/13-cloud/release-imagen-cloud/` |
| Debian reducida (sin módulos ni paquetes no usados) + parche 14 | 2 | 61 | 63 | 0 | **BLOQUEADA** | `evidence/cierre-brechas-2026-11-24/08-puerta-release-local/cloud/` |
| **Alpine** (misma versión del WAF: CRS 4.25.2) + parche 14 | **1** (`marsdb`, exceptuada) | **0** | 1 | 0 | **APTA** | `evidence/cierre-brechas-2026-11-24/08-puerta-release-local/cloud-alpine/` |

En la imagen Debian, lo que quedaba sin corrección eran paquetes **esenciales** de Debian (util-linux, login, mount, ncurses,
perl-base, libsystemd) o librerías que **enlaza ModSecurity** (libxml2 —incluida la CRITICAL CVE-2026-6653—, libcurl-gnutls,
libssl). No se podían retirar sin romper el sistema o el WAF.

## 2. Opciones de tratamiento evaluadas (ISO/IEC 27005)
| Opción | Descripción | Resultado |
|---|---|---|
| **Reducir** (elegida y ejecutada) | Cambiar la base del WAF a la variante **Alpine** de la misma versión de CRS y compilar la app para musl (`node:24-alpine`, Node 24.22.3) | **APTA**: 0 HIGH. Probada funcional y de seguridad (ver §3) |
| Aceptar temporalmente | Excepciones fechadas para los 63 CVE sin corrección, con aprobación del dueño del riesgo | No necesaria tras la reducción. No se añadió ninguna excepción |
| Evitar | No publicar la demostración hasta que Debian publique correcciones | No necesaria |
| Transferir | WAF gestionado (p. ej. Cloudflare) en lugar de ModSecurity en el contenedor | Exige dominio propio (costo); ver `REQUISITOS_CLOUD_DISENO_VS_IMPLEMENTADO.md` |

## 3. Riesgo residual tras la reducción (requiere conocimiento del dueño del riesgo)
1. **`marsdb` (GHSA-5mrr-rgp6-x4gr, CRITICAL, sin corrección):** excepción **ya vigente** en la política (aceptación temporal
   de R20 hasta el **2026-12-31**, dueño del riesgo: líder del proyecto). La vía conocida (`$where`) está eliminada del código
   (parche 12). Acción antes del vencimiento: sustituir marsdb o renovar la aceptación de forma expresa.
2. **Grype (informativo, otra base de datos de vulnerabilidades):** sobre la imagen Alpine informa 1 Critical y 15 High
   (dependencias npm de Juice Shop). La política decide con Trivy; la diferencia entre bases de datos se documenta y no se
   oculta. Revisar en cada construcción.
3. **MEDIUM sin corrección** en dependencias npm (`hbs`, `notevil`): por debajo del umbral de la política; quedan en R20.
4. **El WAF del stack LOCAL** usaba la imagen Debian antigua (`4.25.2-nginx-202610180210-lts`): se pasa a la misma base
   Alpine (ver `deploy/hardened/docker-compose.corregido.yml`).

## 4. Decisión que debe registrar el equipo
- **Dueño del riesgo:** líder del proyecto. **Decisión propuesta:** aprobar la reducción ejecutada (Alpine) y mantener la
  aceptación temporal ya vigente de `marsdb` hasta el 2026-12-31. No se pide ninguna aceptación nueva.
