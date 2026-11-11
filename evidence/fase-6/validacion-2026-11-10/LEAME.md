# Validación de cierre de la Fase 6 (2026-11-10, hora local; UTC 2026-11-11)

Todas las corridas contra instancias propias: laboratorio en 127.0.0.1:3000, entorno endurecido detrás del WAF
en 127.0.0.1:8088 y la app endurecida por la red interna de Docker. Arnés: `security/attacks/run.sh` con
`ATTACK_HTTPLOG` (código HTTP real por petición; `000` = sin respuesta, nunca un bloqueo).

| Carpeta | Escenario | Qué demuestra |
|---|---|---|
| `01-linea-base-vulnerable/` | Laboratorio vulnerable original | 11/11 condiciones del arnés presentes + BOLA; A1-A3 HTTP 200 |
| `01-linea-base-vulnerable-intento1/` | Intento previo | Resultados válidos sin registro HTTP (fallo del arnés corregido; ver LEAME) |
| `02a-rasp-monitoreo/` | RASP sin WAF, solo detecta | 3 SQLi detectadas; ataques no bloqueados (200); disponibilidad 41/41 |
| `02b-rasp-bloqueo-sin-integracion/` | RASP bloquea, configuración por defecto | **Caída del proceso** (RestartCount 0->1; 000); ver LEAME |
| `02c-rasp-bloqueo-warn/` | RASP bloquea + `--unhandled-rejections=warn` | Sin caída, pero petición **colgada** (000 a los 20 s); ver LEAME |
| `02d-rasp-bloqueo-integrado/` | RASP bloquea + integración `rasp-guard` | **403 en 0,04-0,15 s**, disponibilidad 41/41, RestartCount 0 |
| `03-waf-rasp-siem/` | Defensa completa vía WAF | A1-A11 neutralizadas; **A12 BOLA sigue vulnerable**; 5/7 alertas; logs redactados; panel |
| `03b-rasp-a-siem/` | RASP sin WAF con el SIEM ingiriendo | Eventos del RASP en Loki y alerta `RASP_Ataque_Detectado` en firing |
| `04-falsos-positivos/` | Tráfico legítimo de dos usuarios | WAF/RASP sin falsos positivos; **falso positivo de la heurística BOLA** |
| `05-siem-seguridad/` | Proxy del socket de Docker | Lecturas 200; escrituras (crear, detener, exec, borrar, descargar) 403 |
| `06-cloud-no-desplegado.txt` | Estado de la nube | Sin .tfstate ni credenciales: diseñado, no desplegado |

Incidencia registrada: entre 04:56 y 05:07 UTC el SIEM no ingirió los logs de contenedores (el proxy denegaba
`GET /networks`, que Alloy necesita). Los eventos del RASP de 02a-02d constan en sus `rasp.log` (docker logs);
el recorrido RASP -> SIEM se demostró después en `03b-rasp-a-siem/`.
