# Regresión de la variante corregida — 2026-11-21T06:17:21+00:00

Objetivo: http://juice-corregida:3000 (red Docker interna; sin WAF salvo que se indique). Tokens redactados.

| Prueba | Esperado | Obtenido | Resultado |
|---|---|---|---|
| Página principal | 200 | 200 | OK |
| Búsqueda legítima q=apple | 200, data = lista de productos | 200, 3 productos, data=lista | OK |
| Reseñas de un producto | 200 | 200 | OK |
| Registro sin role (usuario U) | 201 | 201 | OK |
| Registro intentando role=admin (asignación masiva) | role customer | "role":"customer" | OK |
| Login de U con su contraseña | token emitido | token emitido [REDACTADO] | OK |
| U lee SU cesta (bid 6) | 200 | 200 | OK |
| U lee la cesta de V (bid 7) — BOLA | 403 | 403 | OK |
| Cambio de contraseña de U (con la actual) | 200 | 200 | OK |
| Login de U con la contraseña NUEVA | token emitido | token emitido [REDACTADO] | OK |
| Login de U con la contraseña ANTIGUA | 401 | 401 | OK |
| Login del administrador sembrado (contraseña del archivo de semillas; hash scrypt) | token emitido | token emitido [REDACTADO] | OK |
| Login del administrador con contraseña incorrecta | 401 | 401 | OK |
| Ruta autenticada con token de la clave NUEVA | 200 | 200 | OK |
| Ruta autenticada con token firmado por la clave ANTIGUA (emitido por el laboratorio vulnerable) | 401 | 401 | OK |
| Error provocado (JSON malformado): sin traza de pila | 4xx/5xx JSON genérico, 0 trazas | 500, trazas=0, cuerpo={"status":"error","message":"Internal server error"} | OK |

**Resultado: 16 OK, 0 FALLAS.**

## Almacenamiento de contraseñas (copia de solo lectura de la base de datos del contenedor)
Comando: `docker cp juice-corregida:/juice-shop/data/juiceshop.sqlite` → consulta `select password from Users` (Python 3.12, modo `ro`).

```
usuarios=27 scrypt=27 md5_32hex=0 otros=0
formato: scrypt:<sal 16B hex>:<hash 64B hex> (168 caracteres)
```
Los 27 usuarios (sembrados y registrados en esta prueba) se guardan con scrypt y sal aleatoria; ninguno con MD5 sin sal.

## Token antiguo
El token de control se emitió en una instancia temporal de la imagen oficial (`juice-lab-clave-antigua`, solo en la red
interna `juice-corregida_corregida`, sin puertos publicados, detenida al terminar). En esa instancia devolvió 200
(control positivo); en la variante corregida, 401.
