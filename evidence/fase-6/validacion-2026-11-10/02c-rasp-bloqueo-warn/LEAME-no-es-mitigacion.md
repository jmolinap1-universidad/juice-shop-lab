# 02c — Los "MITIGADO" de A1-A3 en esta corrida NO son bloqueos válidos

Configuración: `AIKIDO_BLOCK=true`, `NODE_OPTIONS=--require @aikidosec/firewall --unhandled-rejections=warn`.
El proceso ya no muere (`RestartCount` 0 -> 0; sonda 106/106 con 200), pero las peticiones bloqueadas **se quedan
sin respuesta**: `http.tsv` registra `000` tras 20,0 s (el timeout del cliente). El arnés lo cuenta como
"MITIGADO" porque no recibe datos. Un timeout no es una respuesta HTTP válida: esta configuración es solo una
**mitigación parcial de disponibilidad** y se descartó en favor de la integración `rasp-guard` (escenario 02d).
