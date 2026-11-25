"""Colector AUTOMÁTICO y AUTENTICADO de eventos de Render hacia el SIEM local (Loki), sin abrir Loki a Internet.

Cada INTERVALO segundos consulta la API oficial de Render (GET https://api.render.com/v1/logs, HTTPS, autenticación Bearer
con una API key de SOLO LECTURA que crea el equipo y se monta como secreto de Docker) y envía las líneas nuevas a Loki con
las mismas etiquetas que las fuentes locales (job waf_audit / waf_access / docker) más entorno="cloud", plataforma, servicio.
Así el panel de Grafana (filtro entorno) y las reglas de alerta funcionan igual para la nube.
- Redacta antes de enviar (igual que Alloy): cabeceras Authorization/Cookie/Set-Cookie, JWT, cookie de acceso y Basic.
- Cursor persistente (último instante + ids ya enviados en ese instante): sin duplicados tras reinicios.
- Sin dependencias: solo la biblioteca estándar de Python. Nunca escribe la clave en logs.
Variables: RENDER_API_KEY_FILE, RENDER_OWNER_ID, RENDER_RESOURCE, RENDER_SERVICIO, LOKI_URL, INTERVALO, ESTADO, VENTANA_INICIAL
"""
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

API = os.environ.get("RENDER_API_URL", "https://api.render.com/v1/logs")  # solo se cambia para la prueba con simulador
CLAVE_ARCHIVO = os.environ.get("RENDER_API_KEY_FILE", "/run/secrets/render_api_key")
OWNER = os.environ["RENDER_OWNER_ID"]
RECURSO = os.environ["RENDER_RESOURCE"]
SERVICIO = os.environ.get("RENDER_SERVICIO", RECURSO)
LOKI = os.environ.get("LOKI_URL", "http://siem-loki:3100") + "/loki/api/v1/push"
INTERVALO = int(os.environ.get("INTERVALO", "60"))
ESTADO = os.environ.get("ESTADO", "/estado/cursor.json")
VENTANA_INICIAL = int(os.environ.get("VENTANA_INICIAL", "3600"))  # segundos hacia atrás en el primer arranque
PAGINAS_POR_CICLO = int(os.environ.get("PAGINAS_POR_CICLO", "10"))  # tope de páginas (100 líneas) por ciclo
PAUSA_PAGINA = float(os.environ.get("PAUSA_PAGINA", "2"))          # segundos entre páginas (límite de la API)
UNA_VEZ = os.environ.get("UNA_VEZ") == "1"

REDACCION = [
    (re.compile(r'"(?i:authorization|cookie|set-cookie)":"([^"]*)"'), '"[REDACTADO]":"[REDACTADO]"'),
    (re.compile(r"eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}"), "[JWT-REDACTADO]"),
    (re.compile(r"lab_acceso=[0-9a-f]{16,}"), "lab_acceso=[REDACTADO]"),
    (re.compile(r"(?i)\bBasic [A-Za-z0-9+/=]{8,}"), "Basic [REDACTADO]"),
]


def log(msg):
    print(f"{datetime.now(timezone.utc).isoformat(timespec='seconds')} colector-render: {msg}", flush=True)


def clave():
    with open(CLAVE_ARCHIVO, encoding="utf-8") as f:
        k = f.read().strip()
    if not k:
        raise SystemExit("FALLO: el archivo de la API key está vacío")
    return k


def leer_estado():
    try:
        with open(ESTADO, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, ValueError):
        desde = datetime.now(timezone.utc) - timedelta(seconds=VENTANA_INICIAL)
        return {"desde": desde.isoformat(), "ids": []}


def guardar_estado(e):
    tmp = ESTADO + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(e, f)
    os.replace(tmp, ESTADO)


def pedir(params, k):
    url = API + "?" + urllib.parse.urlencode(params, doseq=True)
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {k}", "Accept": "application/json",
                                               "User-Agent": "colector-siem-laboratorio/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def clasificar(msg):
    """Devuelve (etiquetas, línea) con el mismo esquema que Alloy en local."""
    m = msg.strip()
    if m.startswith('{"transaction"'):
        et = {"job": "waf_audit", "fuente": "waf"}
        try:
            et["status"] = str(json.loads(m)["transaction"]["response"]["http_code"])
        except (ValueError, KeyError, TypeError):
            pass
        return et, m
    if m.startswith("{") and '"fuente":"waf_access"' in m:
        et = {"job": "waf_access", "fuente": "waf"}
        try:
            j = json.loads(m)
            et.update({k_: str(j[k_]) for k_ in ("status", "method") if j.get(k_)})
        except ValueError:
            pass
        return et, m
    return {"job": "docker", "fuente": "runtime", "container": "juice-cloud"}, m


def fecha(ts):
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def ns(ts):
    return str(int(fecha(ts).timestamp() * 1_000_000_000))


def enviar_loki(flujos):
    carga = {"streams": [{"stream": dict(k_), "values": sorted(v)} for k_, v in flujos.items()]}
    req = urllib.request.Request(LOKI, data=json.dumps(carga).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        if resp.status not in (200, 204):
            raise RuntimeError(f"Loki respondió {resp.status}")


class LimiteAPI(Exception):
    def __init__(self, espera):
        super().__init__(f"límite de la API (429); reintento en {espera} s")
        self.espera = espera


def ciclo(k, estado):
    """Una página cada vez: se envía a Loki y se GUARDA el cursor antes de pedir la siguiente (corrección del primer
    arranque real: con 429 a mitad de la paginación se perdía todo lo leído). Pausa entre páginas y tope por ciclo."""
    ahora = datetime.now(timezone.utc).isoformat()
    params = {"ownerId": OWNER, "resource": RECURSO, "startTime": estado["desde"], "endTime": ahora,
              "direction": "forward", "limit": 100}
    enviados, ultimo, ids_ultimo = 0, estado["desde"], set(estado.get("ids", []))
    vistos = set(estado.get("ids", []))
    for pagina in range(PAGINAS_POR_CICLO):
        if pagina:
            time.sleep(PAUSA_PAGINA)
        try:
            r = pedir(params, k)
        except urllib.error.HTTPError as e:
            if e.code == 429:
                v = e.headers.get("Retry-After") or e.headers.get("RateLimit-Reset") or "120"
                raise LimiteAPI(int(v) if str(v).isdigit() else 120)
            raise
        flujos = {}
        for e in r.get("logs", []):
            if e["id"] in vistos:
                continue
            vistos.add(e["id"])
            msg = e.get("message", "")
            for rx, rep in REDACCION:
                msg = rx.sub(rep, msg)
            et, linea = clasificar(msg)
            et.update({"entorno": "cloud", "plataforma": "render", "servicio": SERVICIO, "fuente_ingesta": "api-render"})
            flujos.setdefault(tuple(sorted(et.items())), []).append([ns(e["timestamp"]), linea])
            # Se comparan FECHAS, no texto: la API y el cursor usan formatos distintos (Z / +00:00, con o sin fracción);
            # la comparación de texto dejaba el cursor quieto y reenviaba líneas (hallado con el simulador)
            if fecha(e["timestamp"]) > fecha(ultimo):
                ultimo, ids_ultimo = e["timestamp"], {e["id"]}
            elif fecha(e["timestamp"]) == fecha(ultimo):
                ids_ultimo.add(e["id"])
            else:
                ids_ultimo.add(e["id"])  # línea anterior al cursor (reloj o paginación): se recuerda para no repetirla
            enviados += 1
        if flujos:
            enviar_loki(flujos)
        guardar_estado({"desde": ultimo, "ids": sorted(ids_ultimo)})
        if not r.get("hasMore"):
            break
        params["startTime"], params["endTime"] = r["nextStartTime"], r["nextEndTime"]
    return enviados, {"desde": ultimo, "ids": sorted(ids_ultimo)}


def main():
    k = clave()
    log(f"inicio: servicio {SERVICIO}, cada {INTERVALO} s, destino {LOKI}")
    while True:
        estado = leer_estado()
        try:
            n, nuevo = ciclo(k, estado)
            guardar_estado(nuevo)
            log(f"ciclo correcto: {n} líneas nuevas enviadas a Loki (hasta {nuevo['desde']})")
        except LimiteAPI as e:
            log(f"AVISO {e} (lo ya leído quedó en Loki y en el cursor)")
            if UNA_VEZ:
                break
            time.sleep(max(e.espera, INTERVALO))
            continue
        except urllib.error.HTTPError as e:
            # 401/403: clave inválida o sin permiso. Nunca se imprime la clave.
            log(f"ERROR API Render: HTTP {e.code} {e.reason}")
            if e.code in (401, 403) and UNA_VEZ:
                sys.exit(2)
        except Exception as e:  # red, Loki caído, etc.: se reintenta en el siguiente ciclo
            log(f"ERROR ciclo: {type(e).__name__}: {str(e)[:160]}")
        if UNA_VEZ:
            break
        time.sleep(INTERVALO)


if __name__ == "__main__":
    main()
