"""Simulador LOCAL de la API de logs de Render y del push de Loki, para probar colector-render.py sin credenciales.

GET /v1/logs → dos páginas (hasMore) con líneas de la misma forma que las reales (auditoría del WAF, acceso, app) que
incluyen un JWT, una cookie de acceso y una cabecera Authorization FALSOS, para comprobar la redacción.
Exige «Authorization: Bearer clave-de-prueba» (valor ficticio): con otra clave responde 401.
POST /loki/api/v1/push → guarda cada carga recibida en /salida/push-N.json.
"""
import http.server
import itertools
import json

JWT = "eyJ" + "a" * 20 + "." + "b" * 20 + "." + "c" * 20
P1 = [
    {"id": "l1", "timestamp": "2026-11-24T06:39:52Z", "labels": [],
     "message": '{"transaction":{"client_ip":"127.0.0.1","request":{"method":"POST","uri":"/rest/user/login","headers":{"Authorization":"Bearer '
                + JWT + '"}},"response":{"http_code":403},"messages":[{"message":"SQL Injection Attack Detected via libinjection","details":{"ruleId":"942100"}}]}}'},
    {"id": "l2", "timestamp": "2026-11-24T06:39:53Z", "labels": [],
     "message": '{"time":"2026-11-24T06:39:53+00:00","method":"GET","uri":"/","status":"302","args":"lab_acceso=' + "f" * 64
                + '","fuente":"waf_access","entorno":"cloud"}'},
]
P2 = [{"id": "l3", "timestamp": "2026-11-24T06:40:00Z", "labels": [],
       "message": "AIKIDO: Zen has blocked an SQL injection (token " + JWT + ")"}]
contador = itertools.count(1)


class Manejador(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.headers.get("Authorization", "") != "Bearer clave-de-prueba":
            self.send_response(401)
            self.end_headers()
            return
        pagina2 = "pagina2" in self.path
        cuerpo = {"hasMore": not pagina2, "nextStartTime": "pagina2", "nextEndTime": "pagina2", "logs": P2 if pagina2 else P1}
        b = json.dumps(cuerpo).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b)

    def do_POST(self):
        b = self.rfile.read(int(self.headers["Content-Length"]))
        with open(f"/salida/push-{next(contador)}.json", "wb") as f:
            f.write(b)
        self.send_response(204)
        self.end_headers()

    def log_message(self, *a):
        pass


http.server.HTTPServer(("0.0.0.0", 8000), Manejador).serve_forever()
