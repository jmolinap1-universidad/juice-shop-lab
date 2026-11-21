# BOLA/IDOR en recursos distintos de la cesta — 2026-11-21T08:05:54-06:00

Objetivo: http://127.0.0.1:8088. Cuentas nuevas A (víctima) y B (atacante). Efecto comprobado releyendo con A. Tokens redactados.

| Recurso | Acción de B sobre el objeto de A | HTTP a B | Efecto real (relectura con A) | Veredicto |
|---|---|---|---|---|
| Dirección #11 | GET (leer) | 400 | datos de A en la respuesta: no | **PROTEGIDO** |
| Dirección #11 | PUT (modificar) | 403
<head><title>403 Forbidden</title></head>
<body>
<center><h1>403 Forbidden</h1></center>
<hr><center>nginx</center>
</body>
</html> | intacta ("streetAddress":"Calle 1") | **PROTEGIDO** |
| Dirección #11 | DELETE (borrar) | 403
<head><title>403 Forbidden</title></head>
<body>
<center><h1>403 Forbidden</h1></center>
<hr><center>nginx</center>
</body>
</html> | A relee: HTTP 200 | **PROTEGIDO** |
| Tarjeta #11 | GET (leer) | 400 | datos de A en la respuesta: no | **PROTEGIDO** |
| Tarjeta #11 | DELETE (borrar) | 403
<head><title>403 Forbidden</title></head>
<body>
<center><h1>403 Forbidden</h1></center>
<hr><center>nginx</center>
</body>
</html> | A relee: HTTP 200, tarjeta presente | **PROTEGIDO** |
| Artículo de cesta #13 | GET (leer) | 403 | artículo de la cesta de A en la respuesta: no | **PROTEGIDO** |
| Artículo de cesta #13 | PUT (cantidad 1→3) | 403
<head><title>403 Forbidden</title></head>
<body>
<center><h1>403 Forbidden</h1></center>
<hr><center>nginx</center>
</body>
</html> | cesta de A: "quantity":1 | **PROTEGIDO** |
| Lista de artículos de cesta | GET /api/BasketItems/ (todas) | 403 | incluye el artículo #13 de A: no | **PROTEGIDO** |
| Artículo de cesta #13 | DELETE (borrar) | 403
<head><title>403 Forbidden</title></head>
<body>
<center><h1>403 Forbidden</h1></center>
<hr><center>nginx</center>
</body>
</html> | artículos en la cesta de A: 1 | **PROTEGIDO** |
| Opinión | crear (A) | 500 | no se pudo crear la opinión de prueba | **NO CONCLUYENTE** |

## Controles positivos (el propietario opera sus objetos)

| Acción de A | HTTP / efecto | Resultado |
|---|---|---|
| A modifica SU dirección | 403
<head><title>403 Forbidden</title></head>
<body>
<center><h1>403 Forbidden</h1></center>
<hr><center>nginx</center>
</body>
</html>,  | **FALLA** |
| A lee SU artículo de cesta | 200 | OK |
| A cambia la cantidad de SU artículo (1→2) | 403
<head><title>403 Forbidden</title></head>
<body>
<center><h1>403 Forbidden</h1></center>
<hr><center>nginx</center>
</body>
</html>, "quantity":1 | **FALLA** |
| A borra SU artículo | 403
<head><title>403 Forbidden</title></head>
<body>
<center><h1>403 Forbidden</h1></center>
<hr><center>nginx</center>
</body>
</html> | **FALLA** |
| A borra SU tarjeta | 403
<head><title>403 Forbidden</title></head>
<body>
<center><h1>403 Forbidden</h1></center>
<hr><center>nginx</center>
</body>
</html> | **FALLA** |
| A borra SU dirección | 403
<head><title>403 Forbidden</title></head>
<body>
<center><h1>403 Forbidden</h1></center>
<hr><center>nginx</center>
</body>
</html> | **FALLA** |

Controles positivos: 1 OK, 5 FALLAS. (Si alguna fila anterior es VULNERABLE, B ya alteró o borró ese objeto y el control positivo falla por esa causa.)

**Resultado: 0 VULNERABLE, 9 PROTEGIDO, 1 NO CONCLUYENTE.** GET /api/Feedbacks es público por diseño (carrusel de opiniones) y no se cuenta como BOLA.
