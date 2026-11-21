# Recorrido legítimo de la interfaz — 2026-11-21T14:11:41+00:00

Objetivo: http://waf-config-historica:8080. Llamadas tomadas de `app/frontend/src/app/Services`. «BLOQUEO DEL WAF» = 403 con la página de nginx.

| Paso | Petición | Esperado | HTTP | Resultado |
|---|---|---|---|---|
| Configuración de la app | `GET /rest/admin/application-configuration` | 200 | 200 | OK |
| Versión | `GET /rest/admin/application-version` | 200 | 200 | OK |
| Idiomas | `GET /rest/languages` | 200 | 200 | OK |
| Búsqueda de productos | `GET /rest/products/search?q=juice` | 200 | 200 | OK |
| Detalle de producto | `GET /api/Products/1` | 200 | 200 | OK |
| Existencias | `GET /api/Quantitys/` | 200 401 | 200 | OK |
| Reseñas de producto | `GET /rest/products/1/reviews` | 200 | 200 | OK |
| Preguntas de seguridad | `GET /api/SecurityQuestions/` | 200 | 200 | OK |
| Registro | `POST /api/Users` | 201 | 201 | OK |
| Inicio de sesión | `POST /rest/user/login` | 200 | 200 | OK |
| Sesión actual (whoami) | `GET /rest/user/whoami` | 200 | 403 | **BLOQUEO DEL WAF** |
| Guardar IP de acceso | `GET /rest/saveLoginIp` | 200 | 200 | OK |
| Estado 2FA | `GET /rest/2fa/status` | 200 | 200 | OK |
| Escribir reseña | `PUT /rest/products/1/reviews` | 201 | 403 | **BLOQUEO DEL WAF** |
| Ver cesta propia | `GET /rest/basket/33` | 200 | 200 | OK |
| Añadir a la cesta | `POST /api/BasketItems` | 200 | 200 | OK |
| Cambiar cantidad (PUT) | `PUT /api/BasketItems/19` | 200 | 403 | **BLOQUEO DEL WAF** |
| Quitar de la cesta (DELETE) | `DELETE /api/BasketItems/19` | 200 | 403 | **BLOQUEO DEL WAF** |
| Añadir de nuevo para comprar | `POST /api/BasketItems` | 200 | 500 | distinto de lo esperado |
| Crear dirección | `POST /api/Addresss` | 201 | 201 | OK |
| Listar direcciones | `GET /api/Addresss` | 200 | 200 | OK |
| Editar dirección (PUT) | `PUT /api/Addresss/15` | 200 | 403 | **BLOQUEO DEL WAF** |
| Métodos de entrega | `GET /api/Deliverys` | 200 | 200 | OK |
| Registrar tarjeta (ficticia) | `POST /api/Cards` | 201 | 201 | OK |
| Listar tarjetas | `GET /api/Cards` | 200 | 200 | OK |
| Saldo del monedero | `GET /rest/wallet/balance` | 200 | 200 | OK |
| Comprar (checkout) | `POST /rest/basket/33/checkout` | 200 | 200 | OK |
| Historial de pedidos | `GET /rest/order-history` | 200 | 200 | OK |
| Membresía deluxe | `GET /rest/deluxe-membership` | 200 | 200 | OK |
| Recuerdos (fotos) | `GET /rest/memories` | 200 | 200 | OK |
| Captcha de opinión | `GET /rest/captcha/` | 200 | 200 | OK |
| Enviar opinión | `POST /api/Feedbacks` | 201 | 500 | distinto de lo esperado |
| Ver opiniones | `GET /api/Feedbacks/` | 200 | 200 | OK |
| Borrar tarjeta (DELETE) | `DELETE /api/Cards/15` | 200 | 403 | **BLOQUEO DEL WAF** |
| Borrar dirección (DELETE) | `DELETE /api/Addresss/15` | 200 | 403 | **BLOQUEO DEL WAF** |

**Resultado: 26 OK, 7 BLOQUEOS DEL WAF (falsos positivos), 2 respuestas distintas de lo esperado.**

> Lectura: WAF temporal con la configuración HISTÓRICA (sin ALLOWED_METHODS ni la exclusión de whoami), mismo backend corregido, red interna sin puertos. Los dos 500 son consecuencia de bloqueos previos: el artículo no se pudo quitar (DELETE bloqueado) y volver a añadirlo viola la restricción de unicidad; la opinión se envió con UserId=0 porque whoami estaba bloqueado. Ninguno se cuenta como mitigación. Con la configuración vigente (`recorrido-frontend-con-waf.md`): 35 OK, 0 bloqueos.
