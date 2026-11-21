# Regresión de la variante corregida — 2026-11-21T08:00:41-06:00

Objetivo: http://127.0.0.1:8088. Pausa antes de cada login: 13 s. Tokens redactados.

| Prueba | Esperado | Obtenido | Resultado |
|---|---|---|---|
| Página principal | 200 | 200 | OK |
| Búsqueda legítima q=apple | 200, data = lista de productos | 200, 3 productos, data=lista | OK |
| Reseñas de un producto | 200 | 200 | OK |
| Registro sin role (usuario U) | 201 | 201 | OK |
| Registro intentando role=admin (asignación masiva) | 201 con role customer, o 403 del WAF | 403, sin role en respuesta | OK |
| Login de U con su contraseña | token emitido | token emitido [REDACTADO] | OK |
| U lee SU cesta (bid 19) | 200 | 200 | OK |
| U lee la cesta de V (bid 20) — BOLA | 403 | 403 | OK |
| Cambio de contraseña de U (con la actual) | 200 | 200 | OK |
| Login de U con la contraseña NUEVA | token emitido | token emitido [REDACTADO] | OK |
| Login de U con la contraseña ANTIGUA | 401 | 401 | OK |
| Login del administrador sembrado (contraseña del archivo de semillas; hash scrypt) | token emitido | token emitido [REDACTADO] | OK |
| Login del administrador con contraseña incorrecta | 401 | 401 | OK |
| Ruta autenticada con token de la clave NUEVA | 200 | 200 | OK |
| Error provocado (JSON malformado): sin traza de pila | 4xx/5xx genérico (JSON de la app o página del WAF), 0 trazas | 400, trazas=0, cuerpo=<html> | OK |

**Resultado: 15 OK, 0 FALLAS.**
