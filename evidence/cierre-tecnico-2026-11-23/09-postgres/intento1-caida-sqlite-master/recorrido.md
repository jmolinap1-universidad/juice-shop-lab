# Recorrido legítimo de la interfaz — 2026-11-24T00:55:03+00:00

Objetivo: http://juice-corregida:3000. Llamadas tomadas de `app/frontend/src/app/Services`. «BLOQUEO DEL WAF» = 403 con la página de nginx.

| Paso | Petición | Esperado | HTTP | Resultado |
|---|---|---|---|---|
| Configuración de la app | `GET /rest/admin/application-configuration` | 200 | 000 | distinto de lo esperado |
| Versión | `GET /rest/admin/application-version` | 200 | 000 | distinto de lo esperado |
| Idiomas | `GET /rest/languages` | 200 | 000 | distinto de lo esperado |
| Búsqueda de productos | `GET /rest/products/search?q=juice` | 200 | 000 | distinto de lo esperado |
| Detalle de producto | `GET /api/Products/1` | 200 | 000 | distinto de lo esperado |
| Existencias | `GET /api/Quantitys/` | 200 401 | 000 | distinto de lo esperado |
| Reseñas de producto | `GET /rest/products/1/reviews` | 200 | 000 | distinto de lo esperado |
| Preguntas de seguridad | `GET /api/SecurityQuestions/` | 200 | 000 | distinto de lo esperado |
| Registro | `POST /api/Users` | 201 | 000 | distinto de lo esperado |
| Inicio de sesión | `POST /rest/user/login` | 200 | 000 | distinto de lo esperado |
| Sesión actual (whoami) | `GET /rest/user/whoami` | 200 | 000 | distinto de lo esperado |
| Guardar IP de acceso | `GET /rest/saveLoginIp` | 200 | 000 | distinto de lo esperado |
| Estado 2FA | `GET /rest/2fa/status` | 200 | 000 | distinto de lo esperado |
| Escribir reseña | `PUT /rest/products/1/reviews` | 201 | 000 | distinto de lo esperado |
| Ver cesta propia | `GET /rest/basket/` | 200 | 000 | distinto de lo esperado |
| Añadir a la cesta | `POST /api/BasketItems` | 200 | 000 | distinto de lo esperado |
| Cambiar cantidad (PUT) | `PUT /api/BasketItems/` | 200 | 000 | distinto de lo esperado |
| Quitar de la cesta (DELETE) | `DELETE /api/BasketItems/` | 200 | 000 | distinto de lo esperado |
| Añadir de nuevo para comprar | `POST /api/BasketItems` | 200 | 000 | distinto de lo esperado |
| Crear dirección | `POST /api/Addresss` | 201 | 000 | distinto de lo esperado |
| Listar direcciones | `GET /api/Addresss` | 200 | 000 | distinto de lo esperado |
| Editar dirección (PUT) | `PUT /api/Addresss/` | 200 | 000 | distinto de lo esperado |
| Métodos de entrega | `GET /api/Deliverys` | 200 | 000 | distinto de lo esperado |
| Registrar tarjeta (ficticia) | `POST /api/Cards` | 201 | 000 | distinto de lo esperado |
| Listar tarjetas | `GET /api/Cards` | 200 | 000 | distinto de lo esperado |
| Saldo del monedero | `GET /rest/wallet/balance` | 200 | 000 | distinto de lo esperado |
| Comprar (checkout) | `POST /rest/basket//checkout` | 200 | 000 | distinto de lo esperado |
| Historial de pedidos | `GET /rest/order-history` | 200 | 000 | distinto de lo esperado |
| Membresía deluxe | `GET /rest/deluxe-membership` | 200 | 000 | distinto de lo esperado |
| Recuerdos (fotos) | `GET /rest/memories` | 200 | 000 | distinto de lo esperado |
| Captcha de opinión | `GET /rest/captcha/` | 200 | 000 | distinto de lo esperado |
| Enviar opinión | `POST /api/Feedbacks` | 201 | 000 | distinto de lo esperado |
| Ver opiniones | `GET /api/Feedbacks/` | 200 | 000 | distinto de lo esperado |
| Borrar tarjeta (DELETE) | `DELETE /api/Cards/` | 200 | 000 | distinto de lo esperado |
| Borrar dirección (DELETE) | `DELETE /api/Addresss/` | 200 | 000 | distinto de lo esperado |

**Resultado: 0 OK, 0 BLOQUEOS DEL WAF (falsos positivos), 35 respuestas distintas de lo esperado.**
