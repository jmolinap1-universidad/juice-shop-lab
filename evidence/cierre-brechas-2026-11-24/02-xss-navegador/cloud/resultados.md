# XSS en navegador — 2026-11-25T04:26:26.270Z
Objetivo: `http://cloud:8080` · Chromium (Playwright 1.49.1) · payload `<iframe src="javascript:alert(`xss`)">`

## Preparación por API
```json
{
 "registro_U": 201,
 "login_U": "ok",
 "V3_post_opinion": 403,
 "V3_comentario_guardado": null,
 "V4_put_producto_sin_token": 403,
 "V4_descripcion_guardada": null,
 "V5_registro": 403,
 "V5_email_guardado": null,
 "V6_saveLoginIp": 200,
 "V6_ip_guardada": "",
 "login_admin": "ok"
}
```

| Vector | Ruta | Página | Diálogos alert | iframes javascript: en el DOM | Avisos CSP | Veredicto |
|---|---|---|---|---|---|---|
| V1 DOM búsqueda | `/#/search?q=%3Ciframe%20src%3D%22javascript%3Aalert(%60xss%6` | cargada | 0 | 0 | 5 | **NO-INYECTADO** |
| V2 reflejado seguimiento | `/#/track-result?id=%3Ciframe%20src%3D%22javascript%3Aalert(%` | cargada | 0 | 0 | 5 | **NO-INYECTADO** |
| V3 almacenado opinión | `/#/about` | cargada | 0 | 0 | 5 | **NO-INYECTADO** |
| V4 almacenado producto | `/#/search` | cargada | 0 | 0 | 5 | **NO-INYECTADO** |
| V5 almacenado correo (admin) | `/#/administration` | cargada | 0 | 0 | 5 | **NO-INYECTADO** |
| V6 almacenado última IP | `/#/privacy-security/last-login-ip` | cargada | 0 | 0 | 5 | **NO-INYECTADO** |

## Avisos CSP (únicos, primeros 3 por vector)
- V1: Refused to execute inline script because it violates the following Content Security Policy directive: "script-src 'self'". Either the 'unsafe-inline' keyword, a hash ('sha256-2ADpmZIga9zdrCfzZ7IWyavas
- V1: Refused to execute inline script because it violates the following Content Security Policy directive: "script-src 'self'". Either the 'unsafe-inline' keyword, a hash ('sha256-LMY6wYoFV9I4wWzxaq1N/dTpl
- V1: Refused to load the font 'https://fonts.gstatic.com/s/vt323/v18/pxiKyp0ihIEF2isQFJXGdg.woff2' because it violates the following Content Security Policy directive: "font-src 'self' data:".

- V2: Refused to execute inline script because it violates the following Content Security Policy directive: "script-src 'self'". Either the 'unsafe-inline' keyword, a hash ('sha256-2ADpmZIga9zdrCfzZ7IWyavas
- V2: Refused to execute inline script because it violates the following Content Security Policy directive: "script-src 'self'". Either the 'unsafe-inline' keyword, a hash ('sha256-LMY6wYoFV9I4wWzxaq1N/dTpl
- V2: Refused to load the font 'https://fonts.gstatic.com/s/vt323/v18/pxiKyp0ihIEF2isQFJXGdg.woff2' because it violates the following Content Security Policy directive: "font-src 'self' data:".

- V3: Refused to execute inline script because it violates the following Content Security Policy directive: "script-src 'self'". Either the 'unsafe-inline' keyword, a hash ('sha256-2ADpmZIga9zdrCfzZ7IWyavas
- V3: Refused to execute inline script because it violates the following Content Security Policy directive: "script-src 'self'". Either the 'unsafe-inline' keyword, a hash ('sha256-LMY6wYoFV9I4wWzxaq1N/dTpl
- V3: Refused to load the font 'https://fonts.gstatic.com/s/vt323/v18/pxiKyp0ihIEF2isQFJXGdg.woff2' because it violates the following Content Security Policy directive: "font-src 'self' data:".

- V4: Refused to execute inline script because it violates the following Content Security Policy directive: "script-src 'self'". Either the 'unsafe-inline' keyword, a hash ('sha256-2ADpmZIga9zdrCfzZ7IWyavas
- V4: Refused to execute inline script because it violates the following Content Security Policy directive: "script-src 'self'". Either the 'unsafe-inline' keyword, a hash ('sha256-LMY6wYoFV9I4wWzxaq1N/dTpl
- V4: Refused to load the font 'https://fonts.gstatic.com/s/vt323/v18/pxiKyp0ihIEF2isQFJXGdg.woff2' because it violates the following Content Security Policy directive: "font-src 'self' data:".

- V5: Refused to execute inline script because it violates the following Content Security Policy directive: "script-src 'self'". Either the 'unsafe-inline' keyword, a hash ('sha256-2ADpmZIga9zdrCfzZ7IWyavas
- V5: Refused to execute inline script because it violates the following Content Security Policy directive: "script-src 'self'". Either the 'unsafe-inline' keyword, a hash ('sha256-LMY6wYoFV9I4wWzxaq1N/dTpl
- V5: Refused to load the font 'https://fonts.gstatic.com/s/vt323/v18/pxiKyp0ihIEF2isQFJXGdg.woff2' because it violates the following Content Security Policy directive: "font-src 'self' data:".

- V6: Refused to execute inline script because it violates the following Content Security Policy directive: "script-src 'self'". Either the 'unsafe-inline' keyword, a hash ('sha256-2ADpmZIga9zdrCfzZ7IWyavas
- V6: Refused to execute inline script because it violates the following Content Security Policy directive: "script-src 'self'". Either the 'unsafe-inline' keyword, a hash ('sha256-LMY6wYoFV9I4wWzxaq1N/dTpl
- V6: Refused to load the font 'https://fonts.gstatic.com/s/vt323/v18/pxiKyp0ihIEF2isQFJXGdg.woff2' because it violates the following Content Security Policy directive: "font-src 'self' data:".


**Resultado: 0 ejecutados, 0 inyectados pero bloqueados, 6 no inyectados.**
