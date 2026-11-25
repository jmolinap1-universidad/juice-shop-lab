"""Valida un modelo de Threat Dragon v2 contra el esquema oficial (v2.6.2) y reglas de coherencia propias.

Uso: python -I validar_modelo_td.py <esquema.json> <modelo.json> <salida.md> [modelo-de-control.json]
Requiere jsonschema (versión fijada por quien ejecuta). Sale con código 1 si hay fallos.
El modelo de control (opcional) es la demo oficial de Threat Dragon: prueba que el validador acepta un modelo real.
"""
import json
import re
import sys

import jsonschema
from importlib.metadata import version

ESQUEMA, MODELO, SALIDA = sys.argv[1:4]
CONTROL = sys.argv[4] if len(sys.argv) > 4 else None
esquema = json.load(open(ESQUEMA, encoding="utf-8"))
Validador = jsonschema.validators.validator_for(esquema, default=jsonschema.Draft7Validator)


def errores_esquema(doc):
    return [f"{'/'.join(map(str, e.absolute_path))}: {e.message}" for e in Validador(esquema).iter_errors(doc)]


modelo = json.load(open(MODELO, encoding="utf-8"))
filas = []


def chk(nombre, ok, detalle=""):
    filas.append((nombre, "OK" if ok else "**FALLO**", detalle))


err = errores_esquema(modelo)
chk(f"Esquema oficial threat-dragon-v2 ({Validador.__name__})", not err, "; ".join(err[:5]) or "0 errores")

TIPOS = {"Spoofing", "Tampering", "Repudiation", "Information disclosure", "Denial of service", "Elevation of privilege"}
ids, numeros, amenazas, letras, problemas = [], [], set(), set(), []
for d in modelo["detail"]["diagrams"]:
    celdas = {c["id"]: c for c in d["cells"]}
    ids += list(celdas)
    for c in d["cells"]:
        data = c.get("data", {})
        th = data.get("threats", [])
        if data.get("hasOpenThreats") != any(t["status"] == "Open" for t in th):
            problemas.append(f"hasOpenThreats incoherente en {data.get('name')!r}")
        for t in th:
            numeros.append(t["number"])
            if t["type"] not in TIPOS or t["status"] not in ("Open", "Mitigated", "NA") or t["severity"] not in ("Low", "Medium", "High"):
                problemas.append(f"valores no admitidos en la amenaza {t['title']!r}")
            m = re.match(r"(TC?\d\d) ", t["title"])
            if m:
                amenazas.add(m.group(1))
            letras.add(t["type"])
        if c["shape"] == "flow":
            for extremo in ("source", "target"):
                ref = celdas.get(c[extremo].get("cell"))
                if not ref or ref["shape"] not in ("actor", "process", "store"):
                    problemas.append(f"flujo {data.get('name')!r}: {extremo} no es un elemento del diagrama")
chk("Identificadores de celda únicos", len(ids) == len(set(ids)), f"{len(ids)} celdas")
chk("Flujos conectados a actores, procesos o almacenes del mismo diagrama", not [p for p in problemas if p.startswith("flujo")],
    "; ".join(p for p in problemas if p.startswith("flujo")))
chk("Tipos STRIDE, estados y severidades admitidos por Threat Dragon", not [p for p in problemas if "valores" in p])
chk("hasOpenThreats coherente con el estado de las amenazas", not [p for p in problemas if "hasOpen" in p])
n = modelo["detail"]["threatTop"]
chk("Números de amenaza únicos 1..threatTop", sorted(numeros) == list(range(1, n + 1)), f"threatTop={n}")
esperadas = {f"T{i:02d}" for i in range(1, 21)} | {f"TC{i:02d}" for i in range(1, 11)}
chk("Amenazas T01-T20 y TC01-TC10 presentes", amenazas == esperadas, f"faltan: {sorted(esperadas - amenazas)}" if amenazas != esperadas else "30/30")
chk("Cobertura STRIDE 6/6", letras == TIPOS, f"{len(letras)}/6")
abiertas = sum(t["status"] == "Open" for d in modelo["detail"]["diagrams"] for c in d["cells"] for t in c.get("data", {}).get("threats", []))
control = ""
if CONTROL:
    ec = errores_esquema(json.load(open(CONTROL, encoding="utf-8")))
    control = (f"\nControl del validador — demo oficial de Threat Dragon (`v2-threat-model.json`, v2.6.2): "
               f"{len(ec)} errores de esquema" + (f" (p. ej. `{ec[0]}`)" if ec else "") + ".\n")

fallos = sum(f[1] != "OK" for f in filas)
with open(SALIDA, "w", encoding="utf-8") as f:
    f.write(f"# Validación del modelo de Threat Dragon\n\nModelo: `{MODELO}` · esquema: `{ESQUEMA}` · jsonschema {version('jsonschema')}\n\n"
            f"| Comprobación | Resultado | Detalle |\n|---|---|---|\n")
    for x in filas:
        f.write(f"| {x[0]} | {x[1]} | {x[2]} |\n")
    f.write(f"\n**Resultado: {len(filas) - fallos} OK · {fallos} fallos.** Amenazas: {n} ({abiertas} abiertas, {n - abiertas} mitigadas).\n{control}")
print(f"Threat Dragon: {len(filas) - fallos} OK · {fallos} fallos · {n} amenazas ({abiertas} abiertas)")
sys.exit(1 if fallos else 0)
