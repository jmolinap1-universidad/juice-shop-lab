# Regresión de la variante corregida — 2026-11-23T23:12:16-06:00

Objetivo: http://127.0.0.1:8090. Pausa antes de cada login: 13 s. Tokens redactados.

| Prueba | Esperado | Obtenido | Resultado |
|---|---|---|---|
| Página principal | 200 | 302 | **FALLA** |
| Búsqueda legítima q=apple | 200, data = lista de productos | 302, 0 productos, data=otra | **FALLA** |
| Reseñas de un producto | 200 | 302 | **FALLA** |
| Registro sin role (usuario U) | 201 | 302 | **FALLA** |
| Registro intentando role=admin (asignación masiva) | 201 con role customer, o 403 del WAF | 302, sin role en respuesta | **FALLA** |
| Login de U con su contraseña | token emitido | sin token | **FALLA** |
| U lee SU cesta (bid ) | 200 | 302 | **FALLA** |
| U lee la cesta de V (bid ) — BOLA | 403 | 302 | **FALLA** |
| Cambio de contraseña de U (con la actual) | 200 | 302 | **FALLA** |
| Login de U con la contraseña NUEVA | token emitido | sin token | **FALLA** |
| Login de U con la contraseña ANTIGUA | 401 | 302 | **FALLA** |
| Login del administrador sembrado (contraseña del archivo de semillas; hash scrypt) | token emitido | sin token | **FALLA** |
| Login del administrador con contraseña incorrecta | 401 | 302 | **FALLA** |
| Ruta autenticada con token de la clave NUEVA | 200 | 302 | **FALLA** |
| Error provocado (JSON malformado): sin traza de pila | 4xx/5xx genérico (JSON de la app o página del WAF), 0 trazas | 302, trazas=0, cuerpo=<html> | **FALLA** |

**Resultado: 0 OK, 15 FALLAS.**
