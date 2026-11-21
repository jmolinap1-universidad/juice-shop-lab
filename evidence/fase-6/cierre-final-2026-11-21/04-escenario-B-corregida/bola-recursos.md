# BOLA/IDOR en recursos distintos de la cesta — 2026-11-21T13:58:37+00:00

Objetivo: http://juice-corregida:3000. Cuentas nuevas A (víctima) y B (atacante). Efecto comprobado releyendo con A. Tokens redactados.

| Recurso | Acción de B sobre el objeto de A | HTTP a B | Efecto real (relectura con A) | Veredicto |
|---|---|---|---|---|
| Dirección #7 | GET (leer) | 400 | datos de A en la respuesta: no | **PROTEGIDO** |
| Dirección #7 | PUT (modificar) | 403 | intacta ("streetAddress":"Calle 1") | **PROTEGIDO** |
| Dirección #7 | DELETE (borrar) | 400 | A relee: HTTP 200 | **PROTEGIDO** |
| Tarjeta #7 | GET (leer) | 400 | datos de A en la respuesta: no | **PROTEGIDO** |
| Tarjeta #7 | DELETE (borrar) | 400 | A relee: HTTP 200, tarjeta presente | **PROTEGIDO** |
| Artículo de cesta #9 | GET (leer) | 403 | artículo de la cesta de A en la respuesta: no | **PROTEGIDO** |
| Artículo de cesta #9 | PUT (cantidad 1→3) | 403 | cesta de A: "quantity":1 | **PROTEGIDO** |
| Lista de artículos de cesta | GET /api/BasketItems/ (todas) | 403 | incluye el artículo #9 de A: no | **PROTEGIDO** |
| Artículo de cesta #9 | DELETE (borrar) | 403 | artículos en la cesta de A: 1 | **PROTEGIDO** |
| Opinión #9 | DELETE (borrar) | 403 | opinión de A presente | **PROTEGIDO** |

## Controles positivos (el propietario opera sus objetos)

| Acción de A | HTTP / efecto | Resultado |
|---|---|---|
| A modifica SU dirección | 200, Calle 2 (A) | OK |
| A lee SU artículo de cesta | 200 | OK |
| A cambia la cantidad de SU artículo (1→2) | 200, "quantity":2 | OK |
| A borra SU artículo | 200 | OK |
| A borra SU tarjeta | 200 | OK |
| A borra SU dirección | 200 | OK |
| A borra SU opinión | 200 | OK |

Controles positivos: 7 OK, 0 FALLAS. (Si alguna fila anterior es VULNERABLE, B ya alteró o borró ese objeto y el control positivo falla por esa causa.)

**Resultado: 0 VULNERABLE, 10 PROTEGIDO, 0 NO CONCLUYENTE.** GET /api/Feedbacks es público por diseño (carrusel de opiniones) y no se cuenta como BOLA.
