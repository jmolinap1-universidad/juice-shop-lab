# SIEM: centralización automática y autenticada de eventos de Render — 2026-11-24T23:29:44-06:00

**Diseño:** `deploy/hardened/siem/colector-render.py` (servicio `colector-render`, perfil `nube` de
`docker-compose.corregido.yml`) consulta cada 60 s `GET https://api.render.com/v1/logs` con autenticación Bearer (API key
de **solo lectura** de Monitoring, ver `api-key-render.md`), redacta y escribe en el Loki LOCAL por la red interna del SIEM
con las etiquetas de las fuentes locales más `entorno=cloud`, `plataforma=render`, `servicio`, `fuente_ingesta=api-render`.
Loki **no** se expone a Internet. Gratuito (API incluida en la cuenta; sin servicios de terceros).

## Pruebas
| Prueba | Resultado |
|---|---|
| Simulador local (sin credenciales): paginación, etiquetas, redacción de JWT/cookie/Authorization, sin duplicados, clave errónea → 401 | OK (`prueba-simulador/`) |
| Primer arranque real | Halló dos fallos del colector, corregidos: **429** por paginar sin pausa (ahora: página a página con cursor guardado y respeto de Retry-After) y **permiso** del volumen de estado (servicio de inicialización `colector-estado-init`) |
| Marca 1 (`marcasiem1795581784`, SQLi enviada a Render) | En Loki en **3 flujos** (waf_audit 403, waf_access 403, docker) — llegó tras ponerse al día con el atraso |
| Marca 2 (`marcasiem1795584518`), con el colector al día | En Loki en **48 s**: "job":"docker" "job":"waf_access" "job":"waf_audit" |
| Líneas cloud ingeridas (últimas 3 h, por job) | docker=7006 waf_access=11719 waf_audit=5860  |
| Líneas con JWT, cookie de acceso o cabeceras de autorización en Loki (entorno=cloud) | **0** |

## Hallazgo operativo durante la ingesta
El volumen inicial (~285 líneas/min) eran peticiones `/socket.io/` del navegador de un integrante: el WAF bloqueaba los POST
(regla 920420, `text/plain`) y el navegador reintentaba sin fin. Falso positivo corregido con la exclusión acotada EX-2
(`../07-falso-positivo-socketio/`). Sin la centralización no se habría visto.
