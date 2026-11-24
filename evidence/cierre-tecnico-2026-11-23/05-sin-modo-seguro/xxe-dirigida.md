# XXE con el modo seguro DESACTIVADO (prueba dirigida, 2026-11-23)

Red Docker interna temporal `prueba-xxe` (sin puertos). Ambas instancias con `NODE_CONFIG={"challenges":{"safetyMode":"disabled"}}`,
para medir el código sin la protección que Juice Shop activa al detectar Docker. Documento enviado:
`<!DOCTYPE d [<!ENTITY x SYSTEM "file:///etc/hostname">]><d>XXE-INICIO &x; XXE-FIN</d>` a `POST /file-upload`.

| Instancia | HTTP | Lo que devuelve la respuesta | Línea del log de la app | Veredicto |
|---|---|---|---|---|
| Imagen oficial v20.3.0 | 410 | `XXE-INICIO 5519c206c2ba XXE-FIN` (= hostname real del contenedor) | `XXE-INICIO 5519c206c2ba XXE-FIN` | **VULNERABLE** (lectura de archivo local) |
| Variante corregida (parche 12) | 410 | mensaje genérico, sin contenido | `XXE-INICIO &x; XXE-FIN` (entidad sin resolver) | **PROTEGIDO** |

**Corrección de un veredicto propio:** en `oficial/resultados.md` y `corregida/resultados.md` la fila T7 se marcó «PROTEGIDO»
porque la comprobación buscaba el texto de `package.json`, que el mensaje de error trunca a 400 caracteres y escapa. Ese
criterio no detectaba la resolución. Esta prueba dirigida (con `/etc/hostname`, de longitud corta y valor verificable) sustituye
a T7 para el modo seguro desactivado. Con el modo seguro activo, la ruta responde 410 «deprecated» sin analizar el XML.
