# Evidencia del cierre técnico — 2026-11-23

Rama `cierre/tecnico-web-seenode`. Todo se ejecutó en 127.0.0.1 o en redes Docker internas (sin puertos publicados para las
instancias temporales). Tokens redactados; sin credenciales. Resumen: `docs/cierre-tecnico/ESTADO_TECNICO_CIERRE.md`.

| Carpeta | Contenido | Resultado clave |
|---|---|---|
| `00-diagnostico/` | Caída de Docker en la exposición | No fue el RASP: apagado de Windows a las 17:04:19 del 21-nov y Docker Desktop no arranca solo |
| `01-entorno/` | Salud inicial del stack | 6 servicios sanos, 3 fuentes con ingesta, 9 reglas |
| `02-antes-parches/` | Pruebas T1-T10 sobre la variante del 21-nov | 7 vulnerables (reseñas, SSRF, CSRF, 5xx, quejas, reciclajes) |
| `03-build/` | Construcción verificada | 21 archivos = diff auditado |
| `04-despues-parches/` | T1-T10 tras los parches 11-12; JWT | 0 vulnerables; `alg=none` y confusión HS256 → 401. `intento1-…`: regresión de reseñas detectada y corregida |
| `05-sin-modo-seguro/` | Mismas pruebas con `safetyMode: disabled` | Imagen oficial vulnerable en NoSQL y XXE; corregida protegida. `xxe-dirigida.md` corrige un veredicto propio |
| `06-regresion/artefacto-final/` | Validación del artefacto final, sin WAF y con WAF | 15/15, 35/35, BOLA 0/10, T1-T10 0, A1-A12 0, sin 000/5xx. Las carpetas `previo-*` son corridas sobre artefactos anteriores |
| `07-escaneos/` | Semgrep propias (fuente original y corregida), Trivy y Grype | Ver `08` para el artefacto final; `previo-base-anterior/` = antes de actualizar la base |
| `08-pipeline-release/` | Puerta de release del artefacto final | APTA; prueba negativa con la imagen oficial: BLOQUEADA |
| `09-postgres/` | Prueba de BD administrada (PostgreSQL 17) | 15/15, 35/35, BOLA 0/10; datos en la BD; `intento1-…`: caída por `sqlite_master`, corregida |
| `10-siem/` | Ciclo de alerta y notificación, panel, tokens históricos | Notificación 33 s después; 128 líneas antiguas con tokens (purga pendiente de autorización) |
| `11-simulacion-seenode/` | Límites del plan Basic (512 MB, 0,25 vCPU) | Pico 145 MiB; 15/15 y 35/35; sin OOM |
| `12-caja-negra/` | ZAP baseline de la variante final | 0 FAIL; tras `form-action`: solo `style-src 'unsafe-inline'` como Medium |

Nota: los artefactos de construcción cambian de ID en cada build (npm resuelve versiones sin `package-lock`); la trazabilidad
se apoya en el diff auditado y en las etiquetas `masi.*` de la imagen.
