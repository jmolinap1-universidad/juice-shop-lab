# Regresión de la variante corregida — 2026-11-24T00:54:43+00:00

Objetivo: http://juice-corregida:3000. Pausa antes de cada login: 0 s. Tokens redactados.

| Prueba | Esperado | Obtenido | Resultado |
|---|---|---|---|
| Página principal | 200 | 200 | OK |
| Búsqueda legítima q=apple | 200, data = lista de productos | 000, 3 productos, data=lista | **FALLA** |
| Reseñas de un producto | 200 | 000 | **FALLA** |
| Registro sin role (usuario U) | 201 | 000 | **FALLA** |
| Registro intentando role=admin (asignación masiva) | 201 con role customer, o 403 del WAF | 000, sin role en respuesta | **FALLA** |
| Login de U con su contraseña | token emitido | sin token | **FALLA** |
| U lee SU cesta (bid ) | 200 | 000 | **FALLA** |
| U lee la cesta de V (bid ) — BOLA | 403 | 000 | **FALLA** |
| Cambio de contraseña de U (con la actual) | 200 | 000 | **FALLA** |
| Login de U con la contraseña NUEVA | token emitido | sin token | **FALLA** |
| Login de U con la contraseña ANTIGUA | 401 | 000 | **FALLA** |
| Login del administrador sembrado (contraseña del archivo de semillas; hash scrypt) | token emitido | sin token | **FALLA** |
| Login del administrador con contraseña incorrecta | 401 | 000 | **FALLA** |
| Ruta autenticada con token de la clave NUEVA | 200 | 000 | **FALLA** |
| Error provocado (JSON malformado): sin traza de pila | 4xx/5xx genérico (JSON de la app o página del WAF), 0 trazas | 000, trazas=0, cuerpo= | **FALLA** |

**Resultado: 1 OK, 14 FALLAS.**
