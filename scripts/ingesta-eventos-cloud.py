"""Convierte eventos exportados de la nube (NDJSON {"ns": ..., "linea": ...}) en una carga para la API de Loki.

SIEM híbrido sin abrir Loki a Internet: los eventos se exportan del panel de logs de la plataforma (Render) y se cargan en
el Loki LOCAL con etiquetas que los distinguen de los locales: entorno="cloud", plataforma, servicio. El panel de Grafana ya
filtra por `entorno`. Solo se aceptan líneas sin cabeceras de autorización, cookies ni JWT (se verifica antes de cargar).
Uso: python -I ingesta-eventos-cloud.py <archivo.ndjson> <job> <plataforma> <servicio>   → JSON por stdout
"""
import json
import re
import sys

archivo, job, plataforma, servicio = sys.argv[1:5]
SENSIBLE = re.compile(r'eyJ[A-Za-z0-9_-]{8,}\.|"(?:Authorization|Cookie|Set-Cookie)"|lab_acceso=[0-9a-f]{16}', re.I)
valores = []
with open(archivo, encoding="utf-8") as f:
    for n, texto in enumerate(f, 1):
        if not texto.strip():
            continue
        ev = json.loads(texto)
        if SENSIBLE.search(ev["linea"]):
            raise SystemExit(f"FALLO: la línea {n} contiene datos sensibles; no se carga")
        valores.append([ev["ns"], ev["linea"]])
valores.sort(key=lambda v: int(v[0]))
carga = {"streams": [{"stream": {"job": job, "entorno": "cloud", "plataforma": plataforma, "servicio": servicio,
                                 "fuente_ingesta": "exportacion-panel"}, "values": valores}]}
print(json.dumps(carga))
