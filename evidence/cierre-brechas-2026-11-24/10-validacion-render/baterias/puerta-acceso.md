# Puerta de acceso y cabeceras — 2026-11-24T23:56:51-06:00
Destino: https://juice-lab-masi-staging.onrender.com

| Comprobación | Esperado | Obtenido | Resultado |
|---|---|---|---|
| GET / sin cookie | 302 | 302 | OK |
| Redirección de / sin cookie (relativa) | /__acceso | /__acceso | OK |
| GET API sin cookie (/rest/products/search) | 302 | 302 | OK |
| POST login sin cookie | 302 | 302 | OK |
| Cookie falsificada | 302 | 302 | OK |
| /healthz sin autenticación | 200 | 200 | OK |
| /__acceso sin credenciales | 401 | 401 | OK |
| /__acceso con contraseña errónea | 401 | 401 | OK |
| 401 sin credenciales no entrega cookie | 0 | 0 | OK |
| 401 con contraseña errónea no entrega cookie | 0 | 0 | OK |
| 7 intentos erróneos seguidos (límite 5/min, ráfaga 3) | .*429.* |  401 401 401 401 429 429 429 | OK |
| 7 intentos con X-Forwarded-For falsificado distinto (no salta el límite) | .*429.* |  401 401 401 401 429 429 429 | OK |
| /__acceso con credenciales válidas | 200 | 200 | OK |
| Cookie con Secure | 1 | 1 | OK |
| Cookie con HttpOnly | 1 | 1 | OK |
| Cookie con SameSite | 1 | 1 | OK |
| Valor de la cookie (64 hex = 256 bits) | 64 | 64 | OK |
| GET / con cookie | 200 | 200 | OK |
| Cabecera Content-Security-Policy | 1 | 1 | OK |
| Cabecera Strict-Transport-Security | 1 | 1 | OK |
| Cabecera X-Content-Type-Options | 1 | 1 | OK |
| Cabecera X-Frame-Options | 1 | 1 | OK |
| Cabecera Referrer-Policy | 1 | 1 | OK |
| Cabecera X-Robots-Tag | 1 | 1 | OK |
| Server sin versión | [Ss]erver: [A-Za-z-]+ | Server: cloudflare | OK |
| Ruta sensible /ftp con cookie | 403 | 403 | OK |
| /metrics con cookie | 403 | 403 | OK |
| SQLi en login (WAF) | 403 | 403 | OK |

**Resultado puerta y cabeceras: 28 OK · 0 fallos**

| Batería | Resultado |
|---|---|
| Puerta de acceso y cabeceras | 28 OK · 0 fallos |
| Regresión funcional | Resultado: 15 OK, 0 FALLAS.  |
| Recorrido de la interfaz | Resultado: 35 OK, 0 BLOQUEOS DEL WAF (falsos positivos), 0 respuestas distintas de lo esperado.  |
| A1-A12 | === 0 VULNERABLE / 11 MITIGADO de 11 casos (validar-cloud) ===  |
| BOLA | Controles positivos: 7 OK, 0 FALLAS. (Si alguna fila anterior es VULNERABLE, B ya alteró o borró ese objeto y el control positivo falla po |
| T1-T10 | Resultado parcial: 0 VULNERABLE, 9 PROTEGIDO, 2 pendientes de log o no concluyentes.  |

Códigos HTTP del arnés:  4 200  2 201  1 400  7 403 
