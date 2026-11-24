# 13 — Despliegue cloud (contenedor único WAF + app corregida + RASP)

Plataforma: **Render, capa gratuita** (sin tarjeta; `DECISIONES.md` D-18: DigitalOcean exige método de pago y su único
crédito era de inferencia; Seenode lo descartó el equipo). URL de prueba (acceso restringido):
`https://juice-lab-masi-staging.onrender.com` · servicio `srv-dc2i1buk1f9s7382sgmg` · BD `juice-lab-db` (PostgreSQL 17, free,
sin acceso externo) · región virginia. Imagen: `deploy/cloud/Dockerfile`, construida por Render desde el repositorio.

| Carpeta / archivo | Contenido | Resultado |
|---|---|---|
| `render-0be0b5f/` | **Validación de la versión FINAL desplegada** (commit `0be0b5f`: base WAF 202611190211 + parches Debian + exclusiones) | Puerta 28/28, regresión 15/15, recorrido 35/35, A1-A12/BOLA/T1-T10 sin vulnerables, TLS 1.2/1.3, logs sin secretos |
| `render/` | Primera validación en Render (commit `39487a3`) | Ver tabla «Nube» |
| `release-imagen-cloud/`, `escaneo-imagen-cloud/` | Puerta de release y Trivy de la imagen cloud | BLOQUEADA (75 HIGH + 1 CRITICAL sin corrección del SO base del WAF); antes de corregir: 3/135 y 1 secreto |
| `render/tls.md` | Handshakes TLS reales (OpenSSL 3.5.7) | TLS 1.0/1.1 rechazadas; 1.2 y 1.3 aceptadas; certificado Google Trust Services (`*.onrender.com`); HTTP → 301 HTTPS; HSTS |
| `render/higiene-logs.md` | Búsqueda de secretos en los logs de Render | 0 JWT, 0 cookies de acceso, 0 `Authorization` |
| `render/siem/` | Eventos del WAF cloud cargados en el SIEM local (`entorno="cloud"`) | 7 bloqueos; panel de Grafana con el filtro `cloud` (captura) |
| `arranque-casos.md` | 5 casos de arranque del contenedor | Reproduce el fallo de Render (clave inválida → se detiene) y la solución |
| `local-limites-render/` | Validación local con los límites del plan free (0,1 vCPU, 512 MB) + PostgreSQL 17 | Ver tabla «Local» |
| `local-clave-efimera/` | Puerta y regresión con la clave JWT efímera | 27/27 y 15/15 |
| `build-local.log` | Construcciones locales de la imagen cloud | Fuente = diff auditado (21 archivos); Hadolint 0 |
| `intento1-arnes-rutas-windows/` | Primera validación local: **arnés defectuoso** | Sin cookie de acceso (todo 302). **No mide la imagen** |

## Nube (Render, `security/ops/validar-cloud.sh` contra el host autorizado por el usuario)
| Batería | Resultado |
|---|---|
| Fuente construida por Render | `ok fuente = diff auditado (sha256 8cdc9fbb…), 21 archivos` (log de construcción del despliegue `e00e920`; los despliegues posteriores reutilizan esa capa de la caché, con las mismas entradas) |
| Arranque | `clave JWT: generada en el arranque (efímera…)`; `acceso: 1 usuario(s) autorizado(s): verificador`; `/healthz` 200 |
| Puerta de acceso y cabeceras | 27/28. El único «fallo» es del criterio: se esperaba `Server: waf` y Cloudflare (delante de Render) reescribe la cabecera a `cloudflare`, también sin versión. Criterio corregido después en el script |
| Límite de intentos | 429 al 5.º intento; **con `X-Forwarded-For` falsificado distinto en cada intento, igual 429** (no se salta) |
| Regresión funcional | 15/15 |
| Recorrido de la interfaz | 35/35, 0 falsos positivos del WAF |
| A1-A11 + A12 | 0 vulnerables / 11 mitigados; BOLA A12 mitigado |
| BOLA en 5 tipos de objeto | 0 vulnerables / 10; 7/7 controles positivos |
| T1-T10 | 0 vulnerables; T5 (SSRF a 127.0.0.1) bloqueado por el WAF (931100, 934110) sin petición de la app; T7 (XXE) sin entidad resuelta |

Nota de ejecución: edité `validar-cloud.sh` mientras corría (para el criterio del `Server`); bash leyó un fragmento desplazado
y repitió la línea de resultado de la puerta (aparece dos veces en `render/puerta-acceso.md`) y dio un error inocuo. Las
baterías posteriores corrieron completas (sus archivos lo muestran).

## Local (`local-limites-render/`)
| Batería | Resultado |
|---|---|
| Arranque | `/healthz` 200 en 67-69 s; 164 MiB de 512; sin OOM ni reinicios |
| Puerta de acceso y cabeceras | 25/25 en la primera corrida; **27/27** tras la corrección del 401 (`puerta-tras-correccion-401/`) |
| Regresión / recorrido | 15/15 · 35/35 (`recorrido-intento1-sin-cookie.md` = corrida inválida: el script anulaba la cookie) |
| A1-A12 · BOLA · T1-T10 | 0 vulnerables en todos; T5/T7 protegidos según los logs del contenedor |

## Fallos reales encontrados y corregidos
1. **Omisión de la puerta de acceso (grave):** `add_header Set-Cookie … always` enviaba la cookie válida también en el
   **401**: cualquiera entraba sin credenciales. Detectado en los logs de auditoría locales y confirmado (`GET /` con esa
   cookie → 200). Corregido (`4401dc4`) y añadida la prueba «un 401 no entrega cookie». En Render esa versión nunca llegó a
   servir la app (no arrancó) y los logs de Render no contienen ninguna cookie de acceso (`render/higiene-logs.md`).
2. nginx no arrancaba (`map_hash_bucket_size`); redirecciones absolutas con el puerto interno (`absolute_redirect off`).
3. En Render la app no arrancaba por la clave JWT (falla cerrada correcta) y el contenedor **seguía vivo con 502**: la
   supervisión no detenía nginx (`set -e` heredado; `kill 1`). Corregido (`192018c`): el contenedor se detiene en 9 s.
4. La clave JWT pegada a mano en el panel falló dos veces (variable ausente; luego 72 caracteres de otro valor). Solución
   (`39487a3`, D-21): `JWT_CLAVE_EFIMERA=1`, el contenedor genera su clave al arrancar; nadie manipula la clave.
5. Arnés: rutas `/tmp` con `curl.exe` y cabeceras `Cookie` propias de los scripts que anulaban la cookie de acceso.
