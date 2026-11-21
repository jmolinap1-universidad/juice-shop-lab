# BOLA/IDOR en recursos distintos de la cesta — 2026-11-21T13:56:38+00:00

Objetivo: http://juice-lab:3000. Cuentas nuevas A (víctima) y B (atacante). Efecto comprobado releyendo con A. Tokens redactados.

| Recurso | Acción de B sobre el objeto de A | HTTP a B | Efecto real (relectura con A) | Veredicto |
|---|---|---|---|---|
| Dirección #7 | GET (leer) | 400 | datos de A en la respuesta: no | **PROTEGIDO** |
| Dirección #7 | PUT (modificar) | 200 | A ya no puede leer su dirección (HTTP 400): B se la apropió o la alteró | **VULNERABLE** |
| Dirección #7 | DELETE (borrar) | 200 | A relee: HTTP 400 | **NO CONCLUYENTE** |
| Tarjeta #7 | GET (leer) | 400 | datos de A en la respuesta: no | **PROTEGIDO** |
| Tarjeta #7 | DELETE (borrar) | 400 | A relee: HTTP 200, tarjeta presente | **PROTEGIDO** |
| Artículo de cesta #9 | GET (leer) | 200 | artículo de la cesta de A en la respuesta: sí | **VULNERABLE** |
| Artículo de cesta #9 | PUT (cantidad 1→3) | 200 | cesta de A: "quantity":3 | **VULNERABLE** |
| Lista de artículos de cesta | GET /api/BasketItems/ (todas) | 200 | incluye el artículo #9 de A: sí | **VULNERABLE** |
| Artículo de cesta #9 | DELETE (borrar) | 200 | artículos en la cesta de A: 0 | **VULNERABLE** |
| Opinión #9 | DELETE (borrar) | 200 | opinión de A eliminada | **VULNERABLE** |

## Controles positivos (el propietario opera sus objetos)

| Acción de A | HTTP / efecto | Resultado |
|---|---|---|
| A modifica SU dirección | 404,  | **FALLA** |
| A lee SU artículo de cesta | 404 | **FALLA** |
| A cambia la cantidad de SU artículo (1→2) | 500
  <head>
    <meta charset='utf-8'> 
    <title>Error: No such item found!</title>
    <style>* {
  margin: 0;
  padding: 0;
  outline: 0;
}

body {
  padding: 80px 100px;
  font: 13px "Helvetica Neue", "Lucida Grande", "Arial";
  background: #ECE9E9 -webkit-gradient(linear, 0% 0%, 0% 100%, from(#fff), to(#ECE9E9));
  background: #ECE9E9 -moz-linear-gradient(top, #fff, #ECE9E9);
  background-repeat: no-repeat;
  color: #555;
  -webkit-font-smoothing: antialiased;
}
h1, h2 {
  font-size: 22px;
  color: #343434;
}
h1 em, h2 em {
  padding: 0 5px;
  font-weight: normal;
}
h1 {
  font-size: 60px;
}
h2 {
  margin-top: 10px;
}
ul li {
  list-style: none;
}
#stacktrace {
  margin-left: 60px;
}
</style>
  </head>
  <body>
    <div id="wrapper">
      <h1>OWASP Juice Shop (Express ^4.22.1)</h1>
      <h2><em>500</em> Error: No such item found!</h2>
      <ul id="stacktrace"><li> &nbsp; &nbsp;at /juice-shop/build/routes/basketItems.js:103:27</li></ul>
    </div>
  </body>
</html>,  | **FALLA** |
| A borra SU artículo | 404 | **FALLA** |
| A borra SU tarjeta | 200 | OK |
| A borra SU dirección | 400 | **FALLA** |
| A borra SU opinión | 404 | **FALLA** |

Controles positivos: 1 OK, 6 FALLAS.

**Resultado: 6 VULNERABLE, 3 PROTEGIDO, 1 NO CONCLUYENTE.** GET /api/Feedbacks es público por diseño (carrusel de opiniones) y no se cuenta como BOLA.

> Nota de lectura: en la imagen oficial, B ya se apropió de la dirección y borró el artículo y la opinión de A (filas VULNERABLE), por eso los controles positivos de A fallan: los objetos ya no le pertenecen o no existen. No es un fallo funcional independiente.
