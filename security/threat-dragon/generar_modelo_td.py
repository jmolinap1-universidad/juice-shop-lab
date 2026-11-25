"""Genera el modelo de OWASP Threat Dragon v2 (DFD + STRIDE) del laboratorio a partir de los datos del repositorio.

Fuentes (nada se escribe a mano en el modelo):
  - docs/fase-1/fase1-modelado-amenazas.md  §4 (amenazas T01-T20: descripción, código, OWASP/CWE) y §5 (DREAD)
  - docs/auditoria-final-2026-11-20/datos/trazabilidad.json  (amenazas cloud TC01-TC10 de Render, con DREAD y control)
  - docs/fase-6/riesgo-cierre-brechas/riesgos-calculados.json  (riesgo residual vigente y controles verificados)

Salida: docs/fase-1/threat-dragon/juice-shop-lab.json (se abre en Threat Dragon: «Import» o «Open existing»).
Estado de cada amenaza: Mitigated si su riesgo vinculado tiene residual Bajo/Medio con controles verificados;
Open si el residual es Alto o si el control declara algo SIN VERIFICAR. Una amenaza con varias letras STRIDE se
divide en una amenaza de Threat Dragon por letra (Threat Dragon admite un solo tipo por amenaza).
Identificadores UUID deterministas (uuid5): regenerar produce el mismo archivo.

Uso: python -I generar_modelo_td.py <raiz-del-repositorio>
"""
import json
import re
import sys
import uuid
from pathlib import Path

RAIZ = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
SALIDA = RAIZ / "docs/fase-1/threat-dragon/juice-shop-lab.json"
NS = uuid.UUID("6f2fa615-19b0-4c00-9a6e-6a7569636500")
TIPO = {"S": "Spoofing", "T": "Tampering", "R": "Repudiation", "I": "Information disclosure",
        "D": "Denial of service", "E": "Elevation of privilege"}


def uid(*partes):
    return str(uuid.uuid5(NS, "/".join(partes)))


def tabla(md, encabezado):
    """Filas de la primera tabla markdown después del encabezado indicado."""
    bloque = md.split(encabezado, 1)[1]
    filas = []
    for linea in bloque.splitlines():
        if linea.startswith("## ") and filas:
            break
        if linea.startswith("| T") and not linea.startswith("| ---"):
            filas.append([c.strip() for c in linea.strip().strip("|").split("|")])
    return filas


fase1 = (RAIZ / "docs/fase-1/fase1-modelado-amenazas.md").read_text(encoding="utf-8")
amenazas = {f[0]: {"stride": f[2], "amenaza": f[3], "codigo": f[4], "owasp": f[5]}
            for f in tabla(fase1, "## 4. STRIDE por elemento del DFD") if re.fullmatch(r"T\d\d", f[0])}
for f in tabla(fase1, "## 5. Valoración DREAD"):
    if f[0] in amenazas:
        amenazas[f[0]].update(dread=[int(x) for x in f[2:7]], promedio=f[7], nivel=f[8])
traz = json.loads((RAIZ / "docs/auditoria-final-2026-11-20/datos/trazabilidad.json").read_text(encoding="utf-8"))
cloud = {a["id"]: a for a in traz["amenazas_cloud"]}
riesgos = {r["id"]: r for r in json.loads(
    (RAIZ / "docs/fase-6/riesgo-cierre-brechas/riesgos-calculados.json").read_text(encoding="utf-8"))["riesgos"]}
assert len(amenazas) == 20 and all("dread" in a for a in amenazas.values()), "faltan amenazas o DREAD de la Fase 1"
assert len(cloud) == 10, "faltan amenazas cloud"

SEVERIDAD = {"Crítico": "High", "Alto": "High", "Medio": "Medium", "Bajo": "Low"}
numero = 0


def estado(riesgo, control=""):
    r = riesgos[riesgo]
    if "SIN VERIFICAR" in control:
        return "Open"
    verificados = [c for c in r["controles"] if c["estado"] == "verificado"]
    return "Mitigated" if r["N_res"] in ("Bajo", "Medio") and verificados else "Open"


def mitigacion_riesgo(riesgo):
    r = riesgos[riesgo]
    ver = [c for c in r["controles"] if c["estado"] == "verificado"]
    pro = [c for c in r["controles"] if c["estado"] == "propuesto"]
    texto = "Controles verificados: " + "; ".join(c["control"] for c in ver) + "."
    if pro:
        texto += "\nPropuestos (no implementados): " + "; ".join(c["control"] for c in pro) + "."
    texto += "\nEvidencia: " + ", ".join(sorted({c["evidencia"] for c in ver if c.get("evidencia")}))
    texto += f"\nResidual vigente {riesgo}: {r['P_res']}×{r['I_res']} {r['N_res']} (inherente {r['N_inh']})."
    return texto


def amenazas_fase1(tid):
    global numero
    a, riesgo = amenazas[tid], "R" + tid[1:]
    st = estado(riesgo)
    salida = []
    for letra in [x.strip() for x in a["stride"].split(",")]:
        numero += 1
        salida.append({
            "id": uid("amenaza", tid, letra), "number": numero, "modelType": "STRIDE", "type": TIPO[letra],
            "title": f"{tid} · {a['amenaza'][:90]}",
            "description": f"{a['amenaza']}\nCódigo (v20.3.0 oficial): {a['codigo']}\nOWASP Top 10:2025 / CWE: {a['owasp']}\n"
                           f"STRIDE de la Fase 1: {a['stride']} · riesgo vinculado {riesgo}.",
            "mitigation": mitigacion_riesgo(riesgo),
            "severity": SEVERIDAD[a["nivel"]], "score": f"DREAD {a['promedio']} ({a['nivel']}) · D,R,E,A,Di = {a['dread']}",
            "status": st})
    return salida


def amenazas_cloud(tcid):
    global numero
    a = cloud[tcid]
    prom = sum(a["dread"]) / 5
    nivel = "Crítico" if prom >= 8 else "Alto" if prom >= 6 else "Medio" if prom >= 4 else "Bajo"
    r = riesgos[a["riesgo"]]
    st = estado(a["riesgo"], a["control"])
    salida = []
    for letra in [x.strip() for x in a["stride"].split(",")]:
        numero += 1
        salida.append({
            "id": uid("amenaza", tcid, letra), "number": numero, "modelType": "STRIDE", "type": TIPO[letra],
            "title": f"{tcid} · {a['amenaza'][:90]}",
            "description": f"{a['amenaza']}\nElemento: {a['elemento']} · STRIDE {a['stride']} · riesgo vinculado {a['riesgo']}.",
            "mitigation": f"{a['control']}\nEvidencia: {a['evidencia']}\n"
                          f"Residual vigente {a['riesgo']}: {r['P_res']}×{r['I_res']} {r['N_res']}.",
            "severity": SEVERIDAD[nivel], "score": f"DREAD {prom:.1f} ({nivel}) · D,R,E,A,Di = {a['dread']}",
            "status": st})
    return salida


def estilo(amz, fuera=False):
    abiertas = any(t["status"] == "Open" for t in amz)
    return ("red" if abiertas else "#333333", 2.5 if abiertas else 1.5, "4 3" if fuera else ""), abiertas


def nodo(diag, clave, forma, nombre, x, y, amz=(), z=1, **datos):
    amz = list(amz)
    (color, ancho, guion), abiertas = estilo(amz, datos.get("outOfScope", False))
    tipo = {"actor": "tm.Actor", "process": "tm.Process", "store": "tm.Store"}[forma]
    w, h = (120, 120) if forma == "process" else (170, 80)
    if forma == "store":
        attrs = {"text": {"text": nombre},
                 "topLine": {"stroke": color, "strokeWidth": ancho, "strokeDasharray": guion},
                 "bottomLine": {"stroke": color, "strokeWidth": ancho, "strokeDasharray": guion}}
    else:
        attrs = {"text": {"text": nombre}, "body": {"stroke": color, "strokeWidth": ancho, "strokeDasharray": guion}}
    data = {"name": nombre, "description": datos.pop("descripcion", ""), "type": tipo, "isTrustBoundary": False,
            "outOfScope": False, "reasonOutOfScope": "", "threats": amz, "hasOpenThreats": abiertas}
    if forma == "actor":
        data["providesAuthentication"] = False
    if forma == "process":
        data.update(handlesCardPayment=False, handlesGoodsOrServices=False, isWebApplication=False, privilegeLevel="")
    if forma == "store":
        data.update(isALog=False, storesCredentials=False, isEncrypted=False, isSigned=False, storesInventory=False)
    data.update(datos)
    return {"position": {"x": x, "y": y}, "size": {"width": w, "height": h}, "attrs": attrs, "visible": True,
            "shape": forma, "zIndex": z, "id": uid(diag, clave), "data": data}


def flujo(diag, origen, destino, nombre, amz=(), protocolo="", cifrado=False, publica=False, vertices=()):
    amz = list(amz)
    (color, ancho, _), abiertas = estilo(amz)
    return {"shape": "flow", "attrs": {"line": {"stroke": color, "strokeWidth": ancho, "targetMarker": {"name": "block"},
                                                "sourceMarker": {"name": ""}, "strokeDasharray": ""}},
            "width": 200, "height": 100, "zIndex": 10, "connector": "smooth",
            "labels": [{"markup": [{"tagName": "ellipse", "selector": "labelBody"}, {"tagName": "text", "selector": "labelText"}],
                        "attrs": {"labelText": {"text": nombre, "textAnchor": "middle", "textVerticalAnchor": "middle"},
                                  "labelBody": {"ref": "labelText", "refRx": "50%", "refRy": "60%", "fill": "#fff", "strokeWidth": 0}},
                        "position": 0.5}],
            "data": {"type": "tm.Flow", "name": nombre, "description": "", "outOfScope": False, "reasonOutOfScope": "",
                     "hasOpenThreats": abiertas, "isBidirectional": False, "isEncrypted": cifrado, "isPublicNetwork": publica,
                     "protocol": protocolo, "threats": amz, "isTrustBoundary": False},
            "id": uid(diag, "flujo", origen, destino), "source": {"cell": uid(diag, origen)}, "target": {"cell": uid(diag, destino)},
            "vertices": [{"x": vx, "y": vy} for vx, vy in vertices]}


def limite(diag, clave, nombre, x, y, w, h):
    return {"position": {"x": x, "y": y}, "size": {"width": w, "height": h},
            "attrs": {"label": {"text": nombre}, "body": {"stroke": "#333333", "strokeWidth": 3, "strokeDasharray": "10 5"}},
            "visible": True, "shape": "trust-boundary-box", "zIndex": -50, "id": uid(diag, clave),
            "data": {"type": "tm.BoundaryBox", "name": nombre, "description": "", "isTrustBoundary": True, "hasOpenThreats": False}}


def texto(diag, clave, contenido, x, y, w, h):
    return {"position": {"x": x, "y": y}, "size": {"width": w, "height": h}, "attrs": {"text": {"text": contenido}},
            "visible": True, "shape": "td-text-block", "zIndex": 11, "id": uid(diag, clave),
            "data": {"type": "tm.Text", "name": contenido, "hasOpenThreats": False}}


def T(*ids):
    return [t for i in ids for t in amenazas_fase1(i)]


def C(*ids):
    return [t for i in ids for t in amenazas_cloud(i)]


# ---------- Diagrama 0: aplicación (DFD de la Fase 1, variante corregida con su defensa) ----------
d0 = "d0"
celdas0 = [
    limite(d0, "tb0", "TB0 · Internet ↔ contenedores (WAF + Juice Shop corregido)", 200, 0, 760, 810),
    limite(d0, "tb1", "TB1 · proceso ↔ almacenamiento", 1000, 40, 250, 600),
    texto(d0, "nota", "DFD de la Fase 1 actualizado\n(variante corregida, parches 01-14,\ncon WAF, RASP y SIEM).\n"
                      "Amenazas T01-T20; estado según\nel residual vigente.", 1300, 110, 250, 110),
    nodo(d0, "U", "actor", "Cliente / navegador", 0, 40),
    nodo(d0, "ATK", "actor", "Atacante externo", 0, 320, descripcion="Mismos canales que el cliente."),
    nodo(d0, "ADM", "actor", "Administrador", 0, 600, descripcion="Panel /administration."),
    nodo(d0, "WAF", "process", "WAF nginx +\nModSecurity/CRS", 250, 320, isWebApplication=True,
         descripcion="Proxy inverso con OWASP CRS 4.25.2, cabeceras y límites (Fases 5-6)."),
    nodo(d0, "SPA", "process", "Frontend Angular", 470, 40, T("T13"), isWebApplication=True),
    nodo(d0, "API", "process", "API Express\n/rest /api /b2b", 510, 320,
         T("T02", "T06", "T07", "T09", "T14", "T15", "T18", "T20"), isWebApplication=True,
         descripcion="Proceso Node con RASP Aikido Zen; parches 01-14 en la variante corregida."),
    nodo(d0, "AUTH", "process", "Autenticación\nJWT", 760, 140, T("T01", "T03", "T04", "T16")),
    nodo(d0, "UP", "process", "Carga de\narchivos", 760, 450, T("T10")),
    nodo(d0, "STAT", "process", "Estáticos y\nlistados", 470, 620, T("T12")),
    nodo(d0, "MET", "process", "/metrics", 780, 640, T("T17")),
    nodo(d0, "SQL", "store", "SQLite / PostgreSQL\nUsers, Cards…", 1040, 90, T("T05"), storesCredentials=True,
         descripcion="SQLite en local; PostgreSQL 17 administrado en Render (parche 13)."),
    nodo(d0, "NOSQL", "store", "MarsDB\nreseñas, pedidos", 1040, 290, T("T08")),
    nodo(d0, "FS", "store", "Sistema de archivos\nftp/ uploads/", 1040, 500),
    nodo(d0, "EXT", "actor", "URL remota\n(imagen de perfil)", 1330, 420, descripcion="Recurso de terceros (TB2)."),
    nodo(d0, "LOG", "store", "Registros → SIEM\n(Alloy/Loki/Grafana)", 1330, 700, T("T19"), isALog=True),
]
celdas0 += [
    flujo(d0, "U", "WAF", "HTTP(S) JSON/HTML", protocolo="HTTPS", publica=True),
    flujo(d0, "ATK", "WAF", "mismos canales", protocolo="HTTPS", publica=True),
    flujo(d0, "ADM", "WAF", "/administration", protocolo="HTTPS", publica=True),
    flujo(d0, "WAF", "SPA", "/ y /assets", protocolo="HTTP"),
    flujo(d0, "WAF", "API", "/rest /api /b2b", protocolo="HTTP"),
    flujo(d0, "WAF", "STAT", "/ftp /support/logs", protocolo="HTTP"),
    flujo(d0, "WAF", "MET", "/metrics (403 del WAF)", protocolo="HTTP", vertices=[(420, 770)]),
    flujo(d0, "API", "AUTH", "login / token"),
    flujo(d0, "AUTH", "SQL", "consulta de login"),
    flujo(d0, "API", "SQL", "Sequelize", vertices=[(930, 330)]),
    flujo(d0, "API", "NOSQL", "reseñas, pedidos", vertices=[(940, 360)]),
    flujo(d0, "API", "UP", "archivos"),
    flujo(d0, "UP", "FS", "ZIP/XML/YAML"),
    flujo(d0, "UP", "EXT", "descarga por URL (SSRF)", T("T11"), protocolo="HTTP(S)", publica=True, vertices=[(990, 440)]),
    flujo(d0, "STAT", "FS", "lectura", vertices=[(940, 600)]),
    flujo(d0, "WAF", "LOG", "auditoría y accesos", protocolo="Docker logs → Alloy", vertices=[(330, 790), (1280, 790)]),
]

# ---------- Diagrama 1: despliegue real en Render (capa gratuita) ----------
d1 = "d1"
celdas1 = [
    limite(d1, "svc", "Servicio web Render · contenedor único Alpine (512 MB)", 480, 50, 560, 320),
    limite(d1, "priv", "Red privada de Render", 1100, 50, 260, 240),
    limite(d1, "local", "Equipo del laboratorio (127.0.0.1)", 1100, 420, 300, 380),
    texto(d1, "nota", "Despliegue real verificado: commit 768d1da,\nacceso restringido (puerta /__acceso).\n"
                      "Amenazas TC01-TC10 (trazabilidad §6).", 0, 420, 300, 70),
    nodo(d1, "USR", "actor", "Usuario autorizado\n(navegador)", 0, 40),
    nodo(d1, "ATK", "actor", "Atacante en Internet", 0, 260),
    nodo(d1, "EQ", "actor", "Equipo del laboratorio", 0, 600, providesAuthentication=False),
    nodo(d1, "EDGE", "process", "Borde de Render\n(Cloudflare + LB)", 260, 150, outOfScope=True,
         reasonOutOfScope="Gestionado por Render (TLS 1.2/1.3, DDoS de la plataforma); no configurable en el plan free."),
    nodo(d1, "WAF", "process", "nginx + ModSecurity\npuerta /__acceso", 580, 150, C("TC01"), isWebApplication=True),
    nodo(d1, "APP", "process", "Juice Shop corregido\n+ RASP", 880, 150, C("TC08"), isWebApplication=True,
         descripcion="Parches 01-14, clave JWT efímera generada en el contenedor."),
    nodo(d1, "PG", "store", "PostgreSQL 17 (free)\nipAllowList vacía", 1145, 130, storesCredentials=True, isEncrypted=True,
         descripcion="Cifrado en reposo AES-256 declarado por Render (no verificable)."),
    nodo(d1, "RLOG", "store", "Logs de Render\n(7 días)", 760, 470, C("TC05"), isALog=True),
    nodo(d1, "CP", "process", "Plano de control\nRender (panel/API)", 330, 560, C("TC04", "TC10")),
    nodo(d1, "REPO", "store", "GitHub main\nrender.yaml, Dockerfile", 230, 730, C("TC07")),
    nodo(d1, "BUILD", "process", "Construcción de la\nimagen (Render)", 620, 680, C("TC06")),
    nodo(d1, "COL", "process", "colector-render\n(API key solo lectura)", 1190, 460),
    nodo(d1, "LOKI", "store", "SIEM local\nLoki / Grafana", 1165, 680, isALog=True),
]
celdas1 += [
    flujo(d1, "USR", "EDGE", "HTTPS TLS 1.2/1.3", protocolo="HTTPS", cifrado=True, publica=True),
    flujo(d1, "ATK", "EDGE", "HTTPS", protocolo="HTTPS", cifrado=True, publica=True),
    flujo(d1, "EDGE", "WAF", "HTTP + X-Forwarded-For", C("TC02"), protocolo="HTTP"),
    flujo(d1, "WAF", "APP", "127.0.0.1:3000", protocolo="HTTP"),
    flujo(d1, "APP", "PG", "SQL (sslmode=require)", C("TC03"), protocolo="PostgreSQL/TLS", cifrado=True),
    flujo(d1, "WAF", "RLOG", "auditoría JSON (stdout)", protocolo="stdout"),
    flujo(d1, "APP", "RLOG", "stdout de la app y del RASP", protocolo="stdout"),
    flujo(d1, "RLOG", "COL", "GET /v1/logs cada 60 s", C("TC09"), protocolo="HTTPS", cifrado=True, publica=True),
    flujo(d1, "COL", "LOKI", "push entorno=cloud", protocolo="HTTP (red Docker interna)"),
    flujo(d1, "EQ", "CP", "login (GitHub)", protocolo="HTTPS", cifrado=True, publica=True),
    flujo(d1, "EQ", "REPO", "git push", protocolo="HTTPS/SSH", cifrado=True, publica=True),
    flujo(d1, "REPO", "BUILD", "Blueprint (sincronización manual)", protocolo="HTTPS", cifrado=True),
    flujo(d1, "CP", "BUILD", "Manual Deploy", protocolo="interno"),
    flujo(d1, "BUILD", "APP", "imagen desplegada", protocolo="interno", vertices=[(1050, 620)]),
]

modelo = {
    "version": "2.6.2",
    "summary": {"title": "Laboratorio AppSec — OWASP Juice Shop (MASI-UMG 2026)", "owner": "Equipo del proyecto",
                "description": "DFD y amenazas STRIDE del laboratorio: aplicación (Fase 1, variante corregida con defensa) y "
                               "despliegue real en Render. Generado por security/threat-dragon/generar_modelo_td.py desde los "
                               "datos versionados; no editar a mano sin regenerar.", "id": 0},
    "detail": {
        "contributors": [{"name": n} for n in ("Molina Pérez Juan Carlos", "Sánchez Flores Juan Walter Ernesto",
                                               "García Gonzalez Leopoldo Emanuel", "Cambara Castillo Vanessa Odeth")],
        "diagrams": [
            {"version": "2.6.2", "title": "Aplicación — DFD de la Fase 1 (variante corregida)", "description":
             "Límites TB0 (Internet ↔ contenedores), TB1 (proceso ↔ almacenamiento) y TB2 (recurso remoto).",
             "thumbnail": "./public/content/images/thumbnail.stride.jpg", "diagramType": "STRIDE", "id": 0, "cells": celdas0},
            {"version": "2.6.2", "title": "Despliegue real — Render + PostgreSQL", "description":
             "Servicio web gratuito con acceso restringido, BD administrada privada y colector SIEM local.",
             "thumbnail": "./public/content/images/thumbnail.stride.jpg", "diagramType": "STRIDE", "id": 1, "cells": celdas1},
        ],
        "diagramTop": 2, "reviewer": "Pendiente de revisión por el equipo", "threatTop": numero,
    },
}
SALIDA.parent.mkdir(parents=True, exist_ok=True)
SALIDA.write_text(json.dumps(modelo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
print(f"modelo: {SALIDA.relative_to(RAIZ)} · {numero} amenazas STRIDE en 2 diagramas")
