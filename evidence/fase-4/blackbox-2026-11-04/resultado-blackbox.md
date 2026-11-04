# Prueba activa de caja negra — sqlmap (riesgo inherente)

Ejecutado: 2026-11-04 · Herramienta: **sqlmap 1.10.4#stable** (Docker)
Imagen: `parrotsec/sqlmap@sha256:aa7836c15d5ac7562b611f0cae73920e45c9efcb5a98be60a12aa3ea927082ff`
Objetivo: `http://juice-lab:3000/rest/products/search?q=` — instancia **propia** del laboratorio,
accedida por el nombre del contenedor dentro de la red Docker `juice-lab_default`. El laboratorio solo
publica `127.0.0.1:3000` en el host; sin exposición externa (CLAUDE.md §1/§2).

## Metodología (caja negra pura)
- **No** se usó conocimiento del código fuente. El parámetro `q` se identifica desde el buscador de
  productos de la interfaz pública; sqlmap fingerprinteó el DBMS por sí solo.
- Configuración: `--batch --level=3 --risk=2 --technique=BEUST`. Total: **169 solicitudes HTTP**.

## Resultado — VULNERABLE (inyección SQL confirmada automáticamente)
| Campo | Valor |
|---|---|
| Parámetro | `q` (GET) |
| DBMS detectado (automático) | SQLite |
| Técnica 1 | boolean-based blind (AND … WHERE/HAVING) |
| Técnica 2 | time-based blind (heavy query, SQLite > 2.0) |
| CWE / OWASP | CWE-89 / **A05:2025 Injection** |
| Veredicto | **VULNERABLE** |

Puntos de inyección (del reporte de sqlmap):
- boolean-based: `q=apple%' AND 7245=7245 AND 'TJUl%'='TJUl`
- time-based:    `q=apple%' AND 2145=LIKE(CHAR(65,66,67,68,69,70,71),UPPER(HEX(RANDOMBLOB(500000000/2)))) AND 'qbFw%'='qbFw`

## Interpretación honesta
- Corrobora de forma **independiente** y **sin leer el código** la inyección SQL que los casos de caja
  gris A1-A3 demostraron con payloads dirigidos. Es una prueba de caja negra **activa**, distinta del
  baseline **pasivo** de ZAP (que no ejecuta inyección).
- Alcance: la prueba se detuvo al confirmar los puntos de inyección; **no** se realizó volcado masivo de
  datos. Se registraron 140 respuestas HTTP 500 propias del sondeo a ciegas.

Evidencia cruda: `sqlmap-search-q.txt` (salida literal de sqlmap).
