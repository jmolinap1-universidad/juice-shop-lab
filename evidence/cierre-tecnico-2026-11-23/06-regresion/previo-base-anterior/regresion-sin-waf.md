# Regresión de la variante corregida — 2026-11-23T23:34:43+00:00

Objetivo: http://juice-hardened:3000. Pausa antes de cada login: 0 s. Tokens redactados.

| Prueba | Esperado | Obtenido | Resultado |
|---|---|---|---|
| Página principal | 200 | 200 | OK |
| Búsqueda legítima q=apple | 200, data = lista de productos | 200, 3 productos, data=lista | OK |
| Reseñas de un producto | 200 | 200 | OK |
| Registro sin role (usuario U) | 201 | 201 | OK |
| Registro intentando role=admin (asignación masiva) | 201 con role customer, o 403 del WAF | 201, "role":"customer" | OK |
| Login de U con su contraseña | token emitido | token emitido [REDACTADO] | OK |
| U lee SU cesta (bid 8) | 200 | 200 | OK |
| U lee la cesta de V (bid 9) — BOLA | 403 | 403 | OK |
| Cambio de contraseña de U (con la actual) | 200 | 200 | OK |
| Login de U con la contraseña NUEVA | token emitido | token emitido [REDACTADO] | OK |
| Login de U con la contraseña ANTIGUA | 401 | 401 | OK |
| Login del administrador sembrado (contraseña del archivo de semillas; hash scrypt) | token emitido | token emitido [REDACTADO] | OK |
| Login del administrador con contraseña incorrecta | 401 | 401 | OK |
| Ruta autenticada con token de la clave NUEVA | 200 | 200 | OK |
| Error provocado (JSON malformado): sin traza de pila | 4xx/5xx genérico (JSON de la app o página del WAF), 0 trazas | 500, trazas=0, cuerpo={"status":"error","message":"Internal server error"} | OK |

**Resultado: 15 OK, 0 FALLAS.**
