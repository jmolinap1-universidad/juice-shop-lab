# Recorrido legítimo de la interfaz — 2026-11-23T23:31:05-06:00

Objetivo: http://127.0.0.1:8090. Llamadas tomadas de `app/frontend/src/app/Services`. «BLOQUEO DEL WAF» = 403 con la página de nginx.

| Paso | Petición | Esperado | HTTP | Resultado |
|---|---|---|---|---|
| Configuración de la app | `GET /rest/admin/application-configuration` | 200 | 302 | **BLOQUEO DEL WAF** |
| Versión | `GET /rest/admin/application-version` | 200 | 302 | **BLOQUEO DEL WAF** |
| Idiomas | `GET /rest/languages` | 200 | 302 | **BLOQUEO DEL WAF** |
| Búsqueda de productos | `GET /rest/products/search?q=juice` | 200 | 302 | **BLOQUEO DEL WAF** |
| Detalle de producto | `GET /api/Products/1` | 200 | 302 | **BLOQUEO DEL WAF** |
| Existencias | `GET /api/Quantitys/` | 200 401 | 302 | **BLOQUEO DEL WAF** |
| Reseñas de producto | `GET /rest/products/1/reviews` | 200 | 302 | **BLOQUEO DEL WAF** |
| Preguntas de seguridad | `GET /api/SecurityQuestions/` | 200 | 302 | **BLOQUEO DEL WAF** |
| Registro | `POST /api/Users` | 201 | 302 | **BLOQUEO DEL WAF** |
| Inicio de sesión | `POST /rest/user/login` | 200 | 302 | **BLOQUEO DEL WAF** |
| Sesión actual (whoami) | `GET /rest/user/whoami` | 200 | 302 | **BLOQUEO DEL WAF** |
| Guardar IP de acceso | `GET /rest/saveLoginIp` | 200 | 302 | **BLOQUEO DEL WAF** |
| Estado 2FA | `GET /rest/2fa/status` | 200 | 302 | **BLOQUEO DEL WAF** |
| Escribir reseña | `PUT /rest/products/1/reviews` | 201 | 302 | **BLOQUEO DEL WAF** |
| Ver cesta propia | `GET /rest/basket/` | 200 | 302 | **BLOQUEO DEL WAF** |
| Añadir a la cesta | `POST /api/BasketItems` | 200 | 302 | **BLOQUEO DEL WAF** |
| Cambiar cantidad (PUT) | `PUT /api/BasketItems/` | 200 | 302 | **BLOQUEO DEL WAF** |
| Quitar de la cesta (DELETE) | `DELETE /api/BasketItems/` | 200 | 302 | **BLOQUEO DEL WAF** |
| Añadir de nuevo para comprar | `POST /api/BasketItems` | 200 | 302 | **BLOQUEO DEL WAF** |
| Crear dirección | `POST /api/Addresss` | 201 | 302 | **BLOQUEO DEL WAF** |
| Listar direcciones | `GET /api/Addresss` | 200 | 302 | **BLOQUEO DEL WAF** |
| Editar dirección (PUT) | `PUT /api/Addresss/` | 200 | 302 | **BLOQUEO DEL WAF** |
| Métodos de entrega | `GET /api/Deliverys` | 200 | 302 | **BLOQUEO DEL WAF** |
| Registrar tarjeta (ficticia) | `POST /api/Cards` | 201 | 302 | **BLOQUEO DEL WAF** |
| Listar tarjetas | `GET /api/Cards` | 200 | 302 | **BLOQUEO DEL WAF** |
| Saldo del monedero | `GET /rest/wallet/balance` | 200 | 302 | **BLOQUEO DEL WAF** |
| Comprar (checkout) | `POST /rest/basket//checkout` | 200 | 302 | **BLOQUEO DEL WAF** |
| Historial de pedidos | `GET /rest/order-history` | 200 | 302 | **BLOQUEO DEL WAF** |
| Membresía deluxe | `GET /rest/deluxe-membership` | 200 | 302 | **BLOQUEO DEL WAF** |
| Recuerdos (fotos) | `GET /rest/memories` | 200 | 302 | **BLOQUEO DEL WAF** |
| Captcha de opinión | `GET /rest/captcha/` | 200 | 302 | **BLOQUEO DEL WAF** |
| Enviar opinión | `POST /api/Feedbacks` | 201 | 302 | **BLOQUEO DEL WAF** |
| Ver opiniones | `GET /api/Feedbacks/` | 200 | 302 | **BLOQUEO DEL WAF** |
| Borrar tarjeta (DELETE) | `DELETE /api/Cards/` | 200 | 302 | **BLOQUEO DEL WAF** |
| Borrar dirección (DELETE) | `DELETE /api/Addresss/` | 200 | 302 | **BLOQUEO DEL WAF** |

**Resultado: 0 OK, 35 BLOQUEOS DEL WAF (falsos positivos), 0 respuestas distintas de lo esperado.**
