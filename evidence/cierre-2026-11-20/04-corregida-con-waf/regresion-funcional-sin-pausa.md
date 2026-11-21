# Regresión de la variante corregida — 2026-11-21T00:19:21-06:00

Objetivo: http://127.0.0.1:8088 (red Docker interna; sin WAF salvo que se indique). Tokens redactados.

| Prueba | Esperado | Obtenido | Resultado |
|---|---|---|---|
| Página principal | 200 | 200 | OK |
| Búsqueda legítima q=apple | 200, data = lista de productos | 200, 3 productos, data=lista | OK |
| Reseñas de un producto | 200 | 200 | OK |
| Registro sin role (usuario U) | 201 | 201 | OK |
| Registro intentando role=admin (asignación masiva) | role customer | sin role en respuesta | **FALLA** |
| Login de U con su contraseña | token emitido | token emitido [REDACTADO] | OK |
| U lee SU cesta (bid 6) | 200 | 200 | OK |
| U lee la cesta de V (bid 7) — BOLA | 403 | 403 | OK |
| Cambio de contraseña de U (con la actual) | 200 | 200 | OK |
| Login de U con la contraseña NUEVA | token emitido | token emitido [REDACTADO] | OK |
| Login de U con la contraseña ANTIGUA | 401 | 401 | OK |
| Login del administrador sembrado (contraseña del archivo de semillas; hash scrypt) | token emitido | sin token | **FALLA** |
| Login del administrador con contraseña incorrecta | 401 | 429 | **FALLA** |
| Ruta autenticada con token de la clave NUEVA | 200 | 200 | OK |
| Error provocado (JSON malformado): sin traza de pila | 4xx/5xx JSON genérico, 0 trazas | 400, trazas=0, cuerpo=<html> | OK |

**Resultado: 12 OK, 3 FALLAS.**
