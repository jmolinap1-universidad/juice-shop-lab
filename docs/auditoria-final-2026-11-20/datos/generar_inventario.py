"""Genera el inventario de activos ISO/IEC 27001 (Markdown + CSV) desde inventario.json, con validaciones.

Uso: python -I generar_inventario.py <docs/auditoria-final-2026-11-20>
Falla (exit 1) si falta un campo obligatorio, un valor está fuera de su catálogo o un ID se repite.
"""
import csv
import json
import os
import sys

BASE = sys.argv[1] if len(sys.argv) > 1 else "."
d = json.load(open(os.path.join(BASE, "datos", "inventario.json"), encoding="utf-8"))
TIPOS = {"Información", "Software", "Físico", "Personal", "Servicios", "Empresa"}
UBIC = {"Local", "Cloud", "Local y cloud", "Móvil", "Repositorio"}
CAMPOS = ["id", "f1", "nombre", "tipo", "ubicacion", "estado", "proceso", "descripcion", "C", "I", "D", "just", "prop", "cust", "acceso", "rel"]
V = d["regla_cia"]["valores"]
ROL = d["roles"]
errores = []


def criticidad(t):
    return "Crítica" if t == 9 else "Alta" if t >= 7 else "Media" if t >= 5 else "Baja"


ids = set()
filas = []
for a in d["activos"]:
    for c in CAMPOS:
        if not str(a.get(c, "")).strip():
            errores.append(f"{a.get('id')}: falta el campo {c}")
    if a["id"] in ids:
        errores.append(f"ID repetido {a['id']}")
    ids.add(a["id"])
    if a["tipo"] not in TIPOS:
        errores.append(f"{a['id']}: tipo inválido {a['tipo']}")
    if a["ubicacion"] not in UBIC:
        errores.append(f"{a['id']}: ubicación inválida {a['ubicacion']}")
    for k in ("C", "I", "D"):
        if a[k] not in V:
            errores.append(f"{a['id']}: {k} inválido")
    for k in ("prop", "cust"):
        if a[k] not in ROL:
            errores.append(f"{a['id']}: rol {k} desconocido {a[k]}")
    total = sum(V[a[k]] for k in ("C", "I", "D"))
    filas.append({**a, "total": total, "criticidad": criticidad(total)})
f1 = {a["f1"].split(" ")[0] for a in d["activos"] if a["f1"].startswith("A")}
faltan = [f"A{i:02d}" for i in range(1, 17) if f"A{i:02d}" not in f1]
if faltan:
    errores.append(f"Activos de la Fase 1 sin correspondencia: {faltan}")
if errores:
    print("VALIDACIÓN FALLIDA:\n  " + "\n  ".join(errores))
    sys.exit(1)

with open(os.path.join(BASE, "INVENTARIO_ACTIVOS_ISO27001.csv"), "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(["ID", "ID Fase 1", "Nombre", "Tipo", "Ubicación", "Estado", "Proceso", "Descripción", "C", "I", "D", "Total", "Criticidad",
                "Justificación CIA", "Propietario (rol)", "Custodio (rol)", "Usuarios con acceso", "Relación"])
    for r in filas:
        w.writerow([r["id"], r["f1"], r["nombre"], r["tipo"], r["ubicacion"], r["estado"], r["proceso"], r["descripcion"], r["C"], r["I"], r["D"],
                    r["total"], r["criticidad"], r["just"], ROL[r["prop"]], ROL[r["cust"]], r["acceso"], r["rel"]])

L = []
w = L.append
w("# Inventario de activos (ISO/IEC 27001:2022) — Juice Shop Lab")
w("")
w("> Generado por `datos/generar_inventario.py` desde `datos/inventario.json` (validado). Versión descargable: "
  "[`INVENTARIO_ACTIVOS_ISO27001.csv`](INVENTARIO_ACTIVOS_ISO27001.csv).")
w("")
w(f"**Alcance:** {d['alcance']}")
w("")
w("## 1. Regla de valoración CIA (reproducible)")
w("| Dimensión | Alta (3) | Media (2) | Baja (1) |")
w("|---|---|---|---|")
nombres = {"C": "Confidencialidad", "I": "Integridad", "D": "Disponibilidad"}
for k in ("C", "I", "D"):
    r = d["regla_cia"][k]
    w(f"| {nombres[k]} | {r['A']} | {r['M']} | {r['B']} |")
w(f"\n{d['regla_cia']['criticidad']}.")
w("")
w("## 2. Roles")
for k, v in ROL.items():
    w(f"- **{k}**: {v}")
w(f"\n{d['nota_roles']}")
w("")
w("## 3. Inventario")
w("| ID | Fase 1 | Activo | Tipo | Ubicación | Estado | Proceso | C | I | D | Crit. | Propietario | Custodio |")
w("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
for r in filas:
    w(f"| {r['id']} | {r['f1']} | {r['nombre']} | {r['tipo']} | {r['ubicacion']} | {r['estado']} | {r['proceso']} | {r['C']} | {r['I']} | {r['D']} | "
      f"{r['total']} {r['criticidad']} | {r['prop']} | {r['cust']} |")
w("")
w("## 4. Descripción, justificación CIA, acceso real y relaciones")
for r in filas:
    w(f"### {r['id']} — {r['nombre']}")
    w(f"- **Descripción:** {r['descripcion']}")
    w(f"- **Justificación CIA ({r['C']}/{r['I']}/{r['D']}):** {r['just']}")
    w(f"- **Usuarios con acceso (según configuración):** {r['acceso']}")
    w(f"- **Relación:** {r['rel']}")
    w("")
w("## 5. Resumen")
por_tipo, por_crit = {}, {}
for r in filas:
    por_tipo[r["tipo"]] = por_tipo.get(r["tipo"], 0) + 1
    por_crit[r["criticidad"]] = por_crit.get(r["criticidad"], 0) + 1
w(f"- **{len(filas)} activos** (los 16 de la Fase 1, todos con correspondencia, más los activos de infraestructura, servicio, personal y organización que la Fase 1 no individualizaba).")
w("- **Por tipo:** " + " · ".join(f"{k}: {v}" for k, v in sorted(por_tipo.items(), key=lambda x: -x[1])) + ".")
w("- **Por criticidad:** " + " · ".join(f"{k}: {por_crit.get(k, 0)}" for k in ("Crítica", "Alta", "Media", "Baja")) + ".")
w("- Activo de información frente a activo tecnológico: la información (INF-xx) se valora por sí misma y la columna *Relación* indica "
  "el activo tecnológico que la almacena o procesa (SW-xx, SRV-xx), para no contar dos veces el mismo riesgo.")
w("- La nube (SRV-05) figura como **propuesta, no desplegada**: se valora por el impacto que tendría, pero hoy no existe.")
open(os.path.join(BASE, "INVENTARIO_ACTIVOS_ISO27001.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
print(f"OK: {len(filas)} activos validados · por tipo {por_tipo} · por criticidad {por_crit}")
