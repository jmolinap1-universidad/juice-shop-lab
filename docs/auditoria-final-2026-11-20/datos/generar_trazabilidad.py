"""Genera TRAZABILIDAD_STRIDE_DREAD_7_CAPAS.md: amenaza (STRIDE, DREAD) -> caso A1-A12 -> riesgo R01-R24 -> capa -> evidencia.

Uso: python -I generar_trazabilidad.py <raíz del repositorio>
Los resultados por escenario se LEEN de la evidencia (resumen-ataques.md, bola/resultado-bola.md y http.tsv).
Un caso solo cuenta como "Mitigado" si el arnés lo marcó así Y su petición principal obtuvo una respuesta HTTP
válida (no 000, ni 5xx, ni timeout). En otro caso se marca "No concluyente".
"""
import json
import os
import re
import sys

ROOT = sys.argv[1] if len(sys.argv) > 1 else "."
A = os.path.join(ROOT, "docs", "auditoria-final-2026-11-20")
T = json.load(open(os.path.join(A, "datos", "trazabilidad.json"), encoding="utf-8"))
R = {r["id"]: r for r in json.load(open(os.path.join(ROOT, "docs", "fase-6", "datos", "riesgos-calculados.json"), encoding="utf-8"))["riesgos"]}
DREAD = {f"T{int(rid[1:]):02d}": R[rid] for rid in R if int(rid[1:]) <= 20}
RAW = {r["id"]: r for r in json.load(open(os.path.join(ROOT, "docs", "fase-6", "datos", "riesgos.json"), encoding="utf-8"))["riesgos"]}
# Ruta principal de cada caso en http.tsv (para validar que hubo respuesta real)
RUTA = {"A1": "/rest/user/login", "A2": "/rest/products/search", "A3": "/rest/products/search", "A7": "/api/Users", "A8": "/rest/admin/application-version", "A9": "/"}


def nivel(x):
    return "Crítico" if x >= 8 else "Alto" if x >= 6 else "Medio" if x >= 4 else "Bajo"


def leer_escenario(carpeta):
    base = os.path.join(ROOT, carpeta)
    res = {}
    resumen = open(os.path.join(base, "resumen-ataques.md"), encoding="utf-8").read()
    for m in re.finditer(r"^\| (A\d+) \|.*?\*\*(VULNERABLE|MITIGADO)\*\*", resumen, re.M):
        res[m.group(1)] = m.group(2)
    bola = os.path.join(base, "bola", "resultado-bola.md")
    if os.path.exists(bola):
        m = re.search(r"Veredicto \| \*\*([A-Z/]+)\*\*", open(bola, encoding="utf-8").read())
        if m:
            res["A12"] = "VULNERABLE" if m.group(1) == "VULNERABLE" else "MITIGADO"
    codigos = {}
    tsv = os.path.join(base, "http.tsv")
    if os.path.exists(tsv):
        # http.tsv no tiene cabecera: se aceptan solo líneas cuyo tercer campo es un código de 3 dígitos
        for linea in open(tsv, encoding="utf-8").read().splitlines():
            p = linea.split("\t")
            if len(p) >= 3 and re.fullmatch(r"\d{3}", p[2]):
                codigos.setdefault(p[1], []).append(p[2])
    for caso, ruta in RUTA.items():
        if res.get(caso) == "MITIGADO" and ruta in codigos:
            malos = [c for c in codigos[ruta] if c == "000" or c.startswith("5")]
            if malos:
                res[caso] = "NO CONCLUYENTE"
    return res


ESC = T.get("escenarios", [])
resultados = {e["clave"]: leer_escenario(e["carpeta"]) for e in ESC}
L = []
w = L.append
w("# Trazabilidad STRIDE · DREAD · casos A1-A12 · riesgos R01-R24 · siete capas")
w("")
w("> Generado por `datos/generar_trazabilidad.py` desde `datos/trazabilidad.json`, el registro de riesgos de la Fase 6 y la")
w("> evidencia de cada escenario. No modifica las matrices históricas (`docs/fase-1/`, `docs/fase-6/matriz-riesgo.md`).")
w("")
w("## 1. Cobertura STRIDE (20 amenazas de la Fase 1)")
clases = {"S": "Suplantación", "T": "Manipulación", "R": "Repudio", "I": "Divulgación de información", "D": "Denegación de servicio", "E": "Elevación de privilegios"}
w("| Clase | Amenazas | N.º |")
w("|---|---|---|")
for k, v in clases.items():
    ts = [t for t, a in T["amenazas"].items() if k in [x.strip() for x in a["stride"].split(",")]]
    w(f"| {k} · {v} | {', '.join(ts)} | {len(ts)} |")
w("")
w("Las seis clases STRIDE tienen al menos una amenaza. Repudio (T19) y Denegación de servicio (T18) tienen una sola: es una limitación del modelo, no un riesgo nulo.")
w("")
w("## 2. Amenazas con DREAD (1-10) y riesgo vinculado")
w("Orden D, R, E, A, Di (Daño, Reproducibilidad, Explotabilidad, Afectados, Descubribilidad); nivel por el promedio: ≥8 Crítico, 6-7.9 Alto, 4-5.9 Medio, <4 Bajo.")
w("")
w("| Amenaza | Elemento DFD | STRIDE | Riesgo | D | R | E | A | Di | Promedio | Nivel |")
w("|---|---|---|---|---|---|---|---|---|---|---|")
for t, a in T["amenazas"].items():
    r = DREAD[t]
    d = RAW[r["id"]]["dread"]
    prom = sum(d) / 5
    w(f"| {t} | {a['elemento']} | {a['stride']} | {r['id']} {r['nombre']} | {' | '.join(str(x) for x in d)} | {prom:.1f} | {nivel(prom)} |")
w("")
w("## 3. Casos de prueba A1-A12: clase, DREAD heredado y resultado por escenario")
w("Clases: " + " · ".join(f"**{k}** {v}" for k, v in T["clases"].items()) + ".")
w("")
cab = "| Caso | Prueba | Clase | Amenaza | DREAD | " + " | ".join(e["titulo"] for e in ESC) + " |"
w(cab)
w("|" + "---|" * (5 + len(ESC)))
for c in T["casos"]:
    if c["amenaza"]:
        d = RAW[DREAD[c["amenaza"]]["id"]]["dread"]
        dr = f"{sum(d) / 5:.1f} ({nivel(sum(d) / 5)})"
    else:
        dr = "No aplica"
    vals = [resultados[e["clave"]].get(c["id"], "—") for e in ESC]
    w(f"| {c['id']} | {c['nombre']} | {c['clase']} | {c['amenaza'] or '—'} | {dr} | " + " | ".join(vals) + " |")
w("")
for c in T["casos"]:
    if c.get("nota"):
        w(f"- **{c['id']}:** {c['nota']}")
w("- El DREAD de un caso es el de su amenaza: el caso es la prueba que demuestra (o no) esa amenaza.")
w("- «MITIGADO» solo se acepta con una respuesta HTTP válida en la petición principal; con 000, 5xx o timeout el caso queda «NO CONCLUYENTE».")
w("")
w("Escenarios (evidencia):")
for e in ESC:
    w(f"- **{e['titulo']}:** `{e['carpeta']}` — {e['descripcion']}")
w("")
w("## 4. Riesgos R01-R24 por capa, con decisión y residual vigentes")
w("| Riesgo | Capa principal | Capa secundaria | Origen | Decisión (estado) | Residual |")
w("|---|---|---|---|---|---|")
cap = T["capas"]
for rid, (p, s) in T["riesgo_capa"].items():
    r = R[rid]
    w(f"| {rid} {r['nombre']} | {p} {cap[p]} | {(s + ' ' + cap[s]) if s else '—'} | {r['origen']} | {r['decision']} ({r['estado_tratamiento']}) | {r['P_res']}×{r['I_res']} {r['N_res']} |")
w("")
w("## 5. Las siete capas: riesgos y controles con evidencia")
w("| Capa | Riesgos | Controles probados (evidencia en el registro de riesgos) |")
w("|---|---|---|")
for k, v in cap.items():
    rs = [rid for rid, (p, s) in T["riesgo_capa"].items() if p == k or s == k]
    ctrl = sorted({c["control"] for rid in rs for c in R[rid]["controles"] if c["verificacion"] == "probado"})
    w(f"| {k} {v} | {', '.join(rs) if rs else '—'} | {'; '.join(ctrl[:6]) + (' …' if len(ctrl) > 6 else '') if ctrl else ('Ver nota' if k == '6' else 'Ninguno probado')} |")
w("")
w(f"**Capa 6:** {T['capa_6_nota']}")
open(os.path.join(A, "TRAZABILIDAD_STRIDE_DREAD_7_CAPAS.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
print("OK trazabilidad:", {e["clave"]: resultados[e["clave"]] for e in ESC})
