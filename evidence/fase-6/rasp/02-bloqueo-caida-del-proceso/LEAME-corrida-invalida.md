# Corrida NO válida para medir mitigación (fallo de ejecución)

`resumen-ataques.md` de esta carpeta muestra "9 MITIGADO", pero **no son mitigaciones**: tras el primer bloqueo
del RASP (A1, `body.email`), el error lanzado por Aikido Zen dentro de Sequelize/sqlite3 quedó como rechazo de
promesa no manejado y **Node terminó el proceso** (`rasp-caida.log`, `RestartCount=1`). Mientras el contenedor
se reiniciaba, el resto de casos obtuvo `HTTP 000` (conexión rechazada), que `run.sh` interpreta como "sin dato".

Hallazgo operativo: en esta pila, el modo bloqueo por defecto convierte cada intento de SQLi detectado en una
**caída del servicio** (disponibilidad; OWASP A10:2025 Mishandling of Exceptional Conditions, CWE-248/CWE-755).
Tratamiento aplicado y re-prueba: ver `../03-bloqueo-sin-caida/`.
