"""Corrige la ubicación de los activos que existen a la vez en el laboratorio local y en el despliegue de Render (2026-11-25).

Uso: python -I ubicacion_compartida.py <docs/auditoria-final-2026-11-20>
Criterio: la imagen cloud desplegada (commit 768d1da) contiene la misma variante corregida, WAF y RASP que el stack local, y la
BD PostgreSQL de Render almacena las mismas tablas de la aplicación. SQLite (SW-04), el SIEM, el colector, los registros del SIEM
y las evidencias siguen siendo solo locales; los servicios de Render (SRV-06 a SRV-09) son solo cloud.
Idempotente: si un activo ya tiene la ubicación nueva no lo cambia.
"""
import json
import os
import sys

BASE = sys.argv[1]
RUTA = os.path.join(BASE, "datos", "inventario.json")
COMPARTIDOS = {
    # datos de la aplicación (SQLite en local, PostgreSQL de Render en la nube) y archivos servidos por la misma imagen
    "INF-01", "INF-02", "INF-03", "INF-04", "INF-05", "INF-06", "INF-07", "INF-08", "INF-09", "INF-10", "INF-11", "INF-12",
    # componentes que corren en los dos entornos
    "SW-02", "SW-03", "SW-05", "SW-08", "SW-09", "SW-11",
}
d = json.load(open(RUTA, encoding="utf-8"))
cambiados = []
for a in d["activos"]:
    if a["id"] in COMPARTIDOS and a["ubicacion"] != "Local y cloud":
        if a["ubicacion"] != "Local":
            raise SystemExit(f"{a['id']}: ubicación inesperada {a['ubicacion']}")
        a["ubicacion"] = "Local y cloud"
        cambiados.append(a["id"])
falta = COMPARTIDOS - {a["id"] for a in d["activos"]}
if falta:
    raise SystemExit(f"IDs inexistentes: {sorted(falta)}")
nota = " Ubicación «Local y cloud» (2026-11-25): activos presentes en el laboratorio local y en el despliegue de Render."
if nota.strip() not in d["alcance"]:
    d["alcance"] += nota
json.dump(d, open(RUTA, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
open(RUTA, "a", encoding="utf-8").write("\n")
print("actualizados:", ", ".join(cambiados) or "ninguno")
