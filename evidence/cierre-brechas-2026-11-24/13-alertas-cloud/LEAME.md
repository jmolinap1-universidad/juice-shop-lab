# Alertas propias de la nube y salud del colector — 2026-11-25T02:34:33-06:00

**Cambios:** `deploy/hardened/siem/rules/fake/alertas.yaml`
- Las 9 reglas locales se acotaron a `entorno="local"`. **Defecto evitado:** con el colector activo, las líneas cloud del job
  `waf_access` habrían mantenido «viva» la regla `Ingesta_WAF_Ausente` aunque cayera el WAF local, y los ataques a la nube
  habrían disparado alertas etiquetadas como locales.
- Grupo nuevo `juice-shop-nube-render` (6 reglas): SQLi bloqueada, credenciales fallidas en la puerta, límite de intentos,
  RASP, fallo de arranque y **salud del colector** (sus logs entran ahora al SIEM: Alloy incluye `siem-colector-render`).
- Reglas cargadas: 15 (`reglas-cargadas.yaml`).

## Prueba extremo a extremo (Render, host autorizado)
| Acción (hora UTC) | Alerta esperada | Notificación recibida |
|---|---|---|
| SQLi a la búsqueda → 403 (08:27:42) | Nube_WAF_InyeccionSQL_Bloqueada | FIRING, desde 08:28:44 (~1 min) |
| 7 credenciales erróneas en /__acceso → 401×4, 429×3 (08:28:47) | Nube_Puerta_FuerzaBruta_RateLimit | FIRING, desde 08:29:44 |
| 5 credenciales erróneas más → 401×4, 429×1 (08:29:53) | Nube_Puerta_CredencialesFallidas (≥5 en 5 min) | FIRING, desde 08:30:44 |
| Colector con una clave INVÁLIDA (HTTP 401 cada 20 s) | Colector_Render_Fallando | FIRING tras 78 s; colector real restaurado y operativo |

Aislamiento: durante la prueba **no** se disparó ninguna regla local (`notificaciones.txt`: solo las cuatro anteriores).
Las reglas Nube_RASP_Ataque_Detectado y Nube_Arranque_Fallido están cargadas pero no se provocaron (el WAF bloquea antes de
que el RASP actúe y no se forzó un arranque fallido en la nube).
