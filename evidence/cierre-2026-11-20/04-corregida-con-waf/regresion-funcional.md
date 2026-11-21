# Regresión de la variante corregida — 2026-11-21T00:22:15-06:00

Objetivo: http://127.0.0.1:8088. Pausa antes de cada login: 13 s. Tokens redactados.

| Prueba | Esperado | Obtenido | Resultado |
|---|---|---|---|
| Página principal | 200 | 200 | OK |
| Búsqueda legítima q=apple | 200, data = lista de productos | 200, 3 productos, data=lista | OK |
| Reseñas de un producto | 200 | 200 | OK |
| Registro sin role (usuario U) | 201 | 201 | OK |
| Registro intentando role=admin (asignación masiva) | 201 con role customer, o 403 del WAF | 403, sin role en respuesta | OK |
| Login de U con su contraseña | token emitido | token emitido [REDACTADO] | OK |
| U lee SU cesta (bid 8) | 200 | 200 | OK |
| U lee la cesta de V (bid 9) — BOLA | 403 | 403 | OK |
| Cambio de contraseña de U (con la actual) | 200 | 200 | OK |
| Login de U con la contraseña NUEVA | token emitido | token emitido [REDACTADO] | OK |
| Login de U con la contraseña ANTIGUA | 401 | 401 | OK |
| Login del administrador sembrado (contraseña del archivo de semillas; hash scrypt) | token emitido | token emitido [REDACTADO] | OK |
| Login del administrador con contraseña incorrecta | 401 | 401 | OK |
| Ruta autenticada con token de la clave NUEVA | 200 | 200 | OK |
| Error provocado (JSON malformado): sin traza de pila | 4xx/5xx JSON genérico, 0 trazas | 400, trazas=0, cuerpo=<html> | OK |

**Resultado: 15 OK, 0 FALLAS.**

Nota: la petición con JSON malformado la rechaza ModSecurity (400, página HTML genérica del WAF) antes de llegar a la app; sin WAF la app responde 500 con JSON genérico (ver 03-corregida-sin-waf). En ambos casos, 0 trazas de pila.

`regresion-funcional-sin-pausa.md` es la primera ejecución sin pausa: sus 3 FALLAS son controles del WAF (403 de la regla de asignación masiva y 429 del límite de 5 logins/min), no fallos de la app; se conserva como evidencia.
