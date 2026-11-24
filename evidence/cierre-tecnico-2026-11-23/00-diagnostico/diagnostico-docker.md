# Diagnóstico: motor de Docker no disponible (2026-11-23)

**Síntoma (2026-11-23):** `docker info` → `open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file
specified`. `wsl -l -v`: distribución `docker-desktop` en estado `Stopped`; ningún proceso de Docker Desktop en ejecución.
RAM libre 16,9 de 31,9 GB (no es falta de memoria).

**Línea de tiempo reconstruida (registros de Docker Desktop y del Visor de eventos de Windows):**

| Hora local (UTC−6) | Fuente | Evento |
|---|---|---|
| 2026-11-21 17:03-17:04 | `Docker/log/vm/init.log` | El motor responde con normalidad (consultas del colector Alloy a la API vía proxy cada 5 s). |
| **17:04:19** | Windows `User32` 1074 | **El usuario inicia el apagado del equipo desde el menú Inicio** (Explorer.EXE). |
| 17:04:19 | `init.log` | Último registro de la VM: se corta sin error en ese mismo segundo. |
| 17:04:24 en adelante | `monitor.log` | `docker.proxy.sock: connection refused` (el motor ya no existe). |
| 17:05:20 | Windows `User32` 1073 | Un intento de apagado no se completa. |
| 17:10:01-17:10:18 | Windows `Wininit` 100, `Kernel-Power` 109/577, `Kernel-General` 13 | Apagado completo con reinicio; `Docker Desktop.exe` termina con `0x40010004` (terminación forzada por el apagado). |
| 2026-11-21 17:10 → 2026-11-23 17:12 | `Docker/log/host/` | **Sin actividad**: Docker Desktop no se volvió a abrir tras el reinicio. |
| 2026-11-23 17:12 | `monitor.log` | Docker Desktop iniciado manualmente; motor disponible (`Docker 29.9.2`, 8 CPU, 15,6 GB para la VM). |

**Conclusión:** la caída no la provocaron el RASP, la aplicación ni el SIEM. El motor se detuvo por el apagado del equipo y,
después del reinicio, Docker Desktop no arranca solo, por lo que Grafana y Loki no estaban disponibles.

**Acción recomendada (decisión del equipo, no aplicada):** activar en Docker Desktop *Settings → General → Start Docker
Desktop when you sign in to your computer*, o abrir Docker Desktop y esperar `docker info` antes de cualquier demostración.
`scripts/ops-corregido.sh` comprueba ahora que el motor responda y lo indica con un mensaje claro.

**Observación secundaria:** con `refresh_interval = "5s"` el colector consulta la API de Docker cada 5 s (vía el proxy de solo
lectura). No causó la caída, pero genera mucho registro en la VM (`init.log` rota cada pocos minutos).
