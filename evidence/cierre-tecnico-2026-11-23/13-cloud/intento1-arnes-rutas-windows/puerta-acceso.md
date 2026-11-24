# Puerta de acceso y cabeceras — 2026-11-23T23:08:57-06:00
Destino: http://127.0.0.1:8090

| Comprobación | Esperado | Obtenido | Resultado |
|---|---|---|---|
| GET / sin cookie | 302 | 302 | OK |
| Redirección de / sin cookie | /__acceso |  | **FALLO** |
| GET API sin cookie (/rest/products/search) | 302 | 302 | OK |
| POST login sin cookie | 302 | 302 | OK |
| Cookie falsificada | 302 | 302 | OK |
| /healthz sin autenticación | 200 | 200 | OK |
| /__acceso sin credenciales | 401 | 401 | OK |
| /__acceso con contraseña errónea | 401 | 401 | OK |
| 7 intentos erróneos seguidos (límite 5/min, ráfaga 3) | .*429.* |  401 401 401 401 429 429 429 | OK |
| /__acceso con credenciales válidas | 200 |  | **FALLO** |
| Cookie con Secure | 1 | 0 | **FALLO** |
| Cookie con HttpOnly | 1 | 0 | **FALLO** |
| Cookie con SameSite | 1 | 0 | **FALLO** |
| Valor de la cookie (64 hex = 256 bits) | 64 | 0 | **FALLO** |
| GET / con cookie | 200 | 302 | **FALLO** |
| Cabecera Content-Security-Policy | 1 |  | **FALLO** |
| Cabecera Strict-Transport-Security | 1 |  | **FALLO** |
| Cabecera X-Content-Type-Options | 1 |  | **FALLO** |
| Cabecera X-Frame-Options | 1 |  | **FALLO** |
| Cabecera Referrer-Policy | 1 |  | **FALLO** |
| Cabecera X-Robots-Tag | 1 |  | **FALLO** |
| Server sin versión | Server: waf |  | **FALLO** |
| Ruta sensible /ftp con cookie | 403 | 302 | **FALLO** |
| /metrics con cookie | 403 | 302 | **FALLO** |
| SQLi en login (WAF) | 403 | 302 | **FALLO** |

**Resultado puerta y cabeceras: 8 OK · 17 fallos**

| Batería | Resultado |
|---|---|
| Puerta de acceso y cabeceras | 8 OK · 17 fallos |
| Regresión funcional | Resultado: 0 OK, 15 FALLAS.  |
| Recorrido de la interfaz | Resultado: 0 OK, 35 BLOQUEOS DEL WAF (falsos positivos), 0 respuestas distintas de lo esperado.  |
| A1-A12 | === 1 VULNERABLE / 10 MITIGADO de 11 casos (validar-cloud) ===  |
| BOLA |  |
| T1-T10 |  |

Códigos HTTP del arnés:  14 302 
