"""Receptor LOCAL de notificaciones de Alertmanager (cierre técnico, 2026-11-23).

Escucha solo en la red Docker interna del SIEM (sin puerto publicado). Por cada alerta escribe una línea en stdout con
estado, nombre, severidad, riesgo y hora; nunca el contenido de los eventos (no hay tokens ni datos personales en las
anotaciones de las reglas). Alloy recoge esta salida y la lleva a Loki: la notificación queda auditada en el propio SIEM.
"""
import json
from http.server import BaseHTTPRequestHandler, HTTPServer


class Receptor(BaseHTTPRequestHandler):
    def do_POST(self):  # noqa: N802 (nombre impuesto por http.server)
        largo = min(int(self.headers.get("Content-Length", 0)), 1_000_000)
        try:
            cuerpo = json.loads(self.rfile.read(largo) or b"{}")
        except ValueError:
            self.send_response(400)
            self.end_headers()
            return
        for a in cuerpo.get("alerts", []):
            et = a.get("labels", {})
            print(f"NOTIFICACION estado={a.get('status', '?').upper()} alerta={et.get('alertname', '?')} "
                  f"severidad={et.get('severity', '?')} riesgo={et.get('riesgo', '?')} desde={a.get('startsAt', '?')}", flush=True)
        self.send_response(200)
        self.end_headers()

    def log_message(self, *args):  # silencia el registro por petición de http.server
        pass


if __name__ == "__main__":
    print("notificador: escuchando en :8080 (solo red interna del SIEM)", flush=True)
    HTTPServer(("0.0.0.0", 8080), Receptor).serve_forever()
