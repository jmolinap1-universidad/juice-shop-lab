# BOLA/IDOR en recursos distintos de la cesta — 2026-11-21T13:49:08+00:00

Objetivo: http://juice-hardened:3000. Cuentas nuevas A (víctima) y B (atacante). Efecto comprobado releyendo con A. Tokens redactados.

| Recurso | Acción de B sobre el objeto de A | HTTP a B | Efecto real (relectura con A) | Veredicto |
|---|---|---|---|---|
| Dirección #8 | GET (leer) | 400 | datos de A en la respuesta: no | **PROTEGIDO** |
| Dirección #8 | PUT (modificar) | 200 | A ya no puede leer su dirección (HTTP 400): B se la apropió o la alteró | **VULNERABLE** |
| Dirección #8 | DELETE (borrar) | 200 | A relee: HTTP 400 | **NO CONCLUYENTE** |
| Tarjeta #8 | GET (leer) | 400 | datos de A en la respuesta: no | **PROTEGIDO** |
| Tarjeta #8 | DELETE (borrar) | 400 | A relee: HTTP 200, tarjeta presente | **PROTEGIDO** |
| Artículo de cesta #10 | GET (leer) | 200 | artículo de la cesta de A en la respuesta: sí | **VULNERABLE** |
| Artículo de cesta #10 | PUT (cantidad 1→3) | 200 | cesta de A: "quantity":3 | **VULNERABLE** |
| Lista de artículos de cesta | GET /api/BasketItems/ (todas) | 200 | incluye el artículo #10 de A: sí | **VULNERABLE** |
| Artículo de cesta #10 | DELETE (borrar) | 200 | artículos en la cesta de A: 0 | **VULNERABLE** |
| Opinión #10 | DELETE (borrar) | 200 | opinión de A eliminada | **VULNERABLE** |

**Resultado: 6 VULNERABLE, 3 PROTEGIDO, 1 NO CONCLUYENTE.** GET /api/Feedbacks es público por diseño (carrusel de opiniones) y no se cuenta como BOLA.

> Nota: `antes-parche10-corregida-rasp-sin-waf.md` se generó con una versión previa de este script (sin controles positivos; opinión creada sin UserId). Sus 6 filas VULNERABLE coinciden con la línea base de la imagen oficial.
