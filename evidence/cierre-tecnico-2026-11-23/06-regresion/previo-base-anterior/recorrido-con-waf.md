# Recorrido legítimo de la interfaz — 2026-11-23T17:37:35-06:00

Objetivo: http://127.0.0.1:8088. Llamadas tomadas de `app/frontend/src/app/Services`. «BLOQUEO DEL WAF» = 403 con la página de nginx.

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
| Sesión actual (whoami) | `GET /rest/user/whoami` | 200 | 200 | OK |
| Guardar IP de acceso | `GET /rest/saveLoginIp` | 200 | 200 | OK |
| Estado 2FA | `GET /rest/2fa/status` | 200 | 200 | OK |
| Escribir reseña | `PUT /rest/products/1/reviews` | 201 | 201 | OK |
| Ver cesta propia | `GET /rest/basket/15` | 200 | 200 | OK |
| Añadir a la cesta | `POST /api/BasketItems` | 200 | 200 | OK |
| Cambiar cantidad (PUT) | `PUT /api/BasketItems/12` | 200 | 200 | OK |
| Quitar de la cesta (DELETE) | `DELETE /api/BasketItems/12` | 200 | 200 | OK |
| Añadir de nuevo para comprar | `POST /api/BasketItems` | 200 | 200 | OK |
| Crear dirección | `POST /api/Addresss` | 201 | 201 | OK |
| Listar direcciones | `GET /api/Addresss` | 200 | 200 | OK |
| Editar dirección (PUT) | `PUT /api/Addresss/9` | 200 | 200 | OK |
| Métodos de entrega | `GET /api/Deliverys` | 200 | 200 | OK |
| Registrar tarjeta (ficticia) | `POST /api/Cards` | 201 | 201 | OK |
| Listar tarjetas | `GET /api/Cards` | 200 | 200 | OK |
| Saldo del monedero | `GET /rest/wallet/balance` | 200 | 200 | OK |
| Comprar (checkout) | `POST /rest/basket/15/checkout` | 200 | 200 | OK |
| Historial de pedidos | `GET /rest/order-history` | 200 | 200 | OK |
| Membresía deluxe | `GET /rest/deluxe-membership` | 200 | 200 | OK |
| Recuerdos (fotos) | `GET /rest/memories` | 200 | 200 | OK |
| Captcha de opinión | `GET /rest/captcha/` | 200 | 200 | OK |
| Enviar opinión | `POST /api/Feedbacks` | 201 | 201 | OK |
| Ver opiniones | `GET /api/Feedbacks/` | 200 | 200 | OK |
| Borrar tarjeta (DELETE) | `DELETE /api/Cards/9` | 200 | 200 | OK |
| Borrar dirección (DELETE) | `DELETE /api/Addresss/9` | 200 | 200 | OK |

**Resultado: 35 OK, 0 BLOQUEOS DEL WAF (falsos positivos), 0 respuestas distintas de lo esperado.**
