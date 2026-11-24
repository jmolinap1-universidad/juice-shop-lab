# 13 — Despliegue cloud (contenedor único WAF + app corregida + RASP)

Plataforma: **Render, capa gratuita** (ver `DECISIONES.md` D-18: DigitalOcean exige método de pago y su único crédito
era de inferencia; Seenode quedó descartado por el equipo). Imagen: `deploy/cloud/Dockerfile`, construida por la plataforma
desde el repositorio; la fuente se verifica contra `app-hardened/patches/v2/correcciones-cierre-tecnico.patch`
(sha256 `8cdc9fbb…`, el mismo del artefacto local).

| Carpeta / archivo | Contenido | Resultado |
|---|---|---|
| `build-local.log` | Construcciones locales de la imagen cloud con la raíz del repo como contexto | Fuente = diff auditado (21 archivos); Hadolint 0. Reconstrucciones por los fallos de abajo |
| `intento1-arnes-rutas-windows/` | Primera validación: **arnés defectuoso** | Sin cookie de acceso (rutas `/tmp` con `curl.exe`): todo 302. **No mide la imagen** |
| `local-limites-render/` | Validación local con los límites del plan free (0,1 vCPU, 512 MB) + PostgreSQL 17 | Ver tabla siguiente |
| `local-limites-render/puerta-tras-correccion-401/` | Puerta tras corregir la omisión de autenticación | 27/27 |

## Validación local (`security/ops/validar-cloud.sh`)
| Batería | Resultado |
|---|---|
| Arranque | `/healthz` 200 en 67-69 s; 164 MiB de 512; sin OOM ni reinicios |
| Puerta de acceso y cabeceras | 25/25 en la primera corrida; **27/27** tras la corrección del 401 |
| Regresión funcional | 15/15 |
| Recorrido de la interfaz | 35/35 (`recorrido.md`); `recorrido-intento1-sin-cookie.md` = corrida inválida (el script anulaba la cookie) |
| A1-A11 + A12 | 0 vulnerables / 11 mitigados; BOLA A12 mitigado |
| BOLA en 5 tipos de objeto | 0 vulnerables / 10; 7/7 controles positivos |
| T1-T10 | 0 vulnerables, 9 protegidos; T5 (SSRF) y T7 (XXE) protegidos según los logs del contenedor |

## Fallos reales encontrados y corregidos
1. **Omisión de la puerta de acceso (grave):** `add_header Set-Cookie … always` enviaba la cookie válida también en el
   **401**: cualquiera entraba sin credenciales. Se detectó al revisar los logs de auditoría (Set-Cookie en respuestas 401)
   y se confirmó (`GET /` con esa cookie → 200). La prueba de la puerta solo comprobaba el código 401. Corregido (commit
   `4401dc4`) y añadida la comprobación «un 401 no entrega cookie».
2. nginx no arrancaba (`map_hash_bucket_size`), redirecciones absolutas con el puerto interno (`absolute_redirect off`).
3. En Render la app no arrancó (clave JWT no válida → falla cerrada correcta) y el contenedor **siguió vivo respondiendo
   502**: la supervisión no detenía nginx (`set -e` heredado; `kill 1`). Corregido (commit `192018c`): ahora el contenedor
   se detiene en 9 s; la clave admite base64 con espacios/CRLF o PEM y el arranque informa tipo y tamaño, nunca el valor.
