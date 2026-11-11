"""Fase 6 - Valoración reproducible del riesgo inherente y residual, validaciones de consistencia y heatmaps.

Uso    : python -I riesgo.py <raíz del repositorio>      (make risk)
Entrada: docs/fase-6/datos/riesgos.json
Salida : docs/fase-6/datos/riesgos-calculados.json, docs/fase-6/datos/validacion-consistencia.txt,
         docs/fase-6/img/heatmap-antes.png, heatmap-despues.png, heatmap-comparativo.png, niveles-antes-despues.png
Método : inherente derivado del DREAD de la Fase 1 (convención del equipo); residual EXPLÍCITO por riesgo con
         razonamiento. Las validaciones rechazan cualquier reducción sin un control 'verificado' y 'probado'.
         ISO/IEC 27005 no prescribe esta aritmética: es una convención documentada en riesgos.json ("metodo").
"""
import json
import math
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402

ROOT = sys.argv[1] if len(sys.argv) > 1 else "."
F6 = os.path.join(ROOT, "docs", "fase-6")
DATA = os.path.join(F6, "datos", "riesgos.json")
OUT_JSON = os.path.join(F6, "datos", "riesgos-calculados.json")
OUT_VAL = os.path.join(F6, "datos", "validacion-consistencia.txt")
IMG = os.path.join(F6, "img")
os.makedirs(IMG, exist_ok=True)

NIVELES = [("Bajo", 1, 4, "#2e9e4f"), ("Medio", 5, 9, "#f2c230"), ("Alto", 10, 16, "#f07f1e"), ("Crítico", 20, 25, "#d7263d")]
PRIORIDAD = {"Crítico": "Muy alta", "Alto": "Alta", "Medio": "Media", "Bajo": "Baja"}
DECISIONES = {"Aceptar", "Eliminar", "Evitar", "Mitigar", "Transferir"}
ESTADOS_TRAT = {"Ejecutado", "Ejecutado parcialmente", "Planificado", "Aceptado temporalmente", "Propuesta"}
TIPOS_RIESGO = {"Seguridad", "Software", "Técnico", "Cloud", "Operacional", "Cumplimiento"}
IMPACTOS = {"Reputacional", "Operacional", "Financiero", "Legal"}
REDUCE_P = {"preventivo", "eliminacion", "evitacion"}
REDUCE_I = {"contencion", "respuesta"}


def nivel(score):
    for nombre, lo, hi, _ in NIVELES:
        if lo <= score <= hi:
            return nombre
    raise ValueError(score)


def color(score):
    return {n: c for n, _, _, c in NIVELES}[nivel(score)]


def inherente(r):
    if "dread" in r:
        d, rep, e, a, di = r["dread"]
        return math.ceil(((rep + e + di) / 3) / 2), math.ceil(((d + a) / 2) / 2), "DREAD Fase 1"
    q = r["pi_cualitativa"]
    return q["P"], q["I"], "Cualitativa"


def probados(r, tipos):
    return [c for c in r["controles"] if c["estado"] == "verificado" and c["verificacion"] == "probado" and c["tipo"] in tipos]


reg = json.load(open(DATA, encoding="utf-8"))
R = reg["riesgos"]
errores, checks = [], []


def check(nombre, ok, detalle=""):
    checks.append(("OK  " if ok else "FALLA") + f" {nombre}" + (f" -> {detalle}" if detalle and not ok else ""))
    if not ok:
        errores.append(f"{nombre}: {detalle}")


ids = [r["id"] for r in R]
check("V1 24 riesgos con ID único R01-R24", ids == [f"R{i:02d}" for i in range(1, 25)], str(ids))
calc = []
for r in R:
    rid = r["id"]
    p, i, fuente = inherente(r)
    pr, ir = r["residual"]["P"], r["residual"]["I"]
    check(f"V2 {rid} P/I en escala 1-5", all(1 <= v <= 5 for v in (p, i, pr, ir)), f"{p},{i},{pr},{ir}")
    check(f"V3 {rid} residual no mayor que inherente", pr <= p and ir <= i, f"P {p}->{pr}, I {i}->{ir}")
    if pr < p:
        check(f"V4 {rid} baja de P respaldada por control preventivo/eliminación/evitación PROBADO", bool(probados(r, REDUCE_P)))
    if ir < i:
        check(f"V5 {rid} baja de I respaldada por contención/respuesta PROBADA (la detección no cuenta)", bool(probados(r, REDUCE_I)))
    check(f"V6 {rid} razonamiento residual de P e I", bool(r["residual"].get("razon_P")) and bool(r["residual"].get("razon_I")))
    check(f"V7 {rid} decisiones válidas", r["decision"] in DECISIONES and (r["decision_sec"] in DECISIONES or r["decision_sec"] == ""))
    check(f"V7 {rid} estado de tratamiento válido", r["estado_tratamiento"] in ESTADOS_TRAT and (r["decision_sec_estado"] in ESTADOS_TRAT or r["decision_sec"] == ""))
    if r["estado_tratamiento"] == "Ejecutado":
        req = {"Eliminar": {"eliminacion"}, "Evitar": {"evitacion"}, "Mitigar": {"preventivo", "contencion"}}.get(r["decision"], set())
        if req:
            check(f"V8 {rid} decisión '{r['decision']}' marcada Ejecutado con control PROBADO de ese tipo", bool(probados(r, req)))
    for d, est in ((r["decision"], r["estado_tratamiento"]), (r["decision_sec"], r["decision_sec_estado"])):
        if d == "Aceptar":
            a = r.get("aceptacion", {})
            check(f"V9 {rid} aceptación temporal documentada (quién, motivo, condiciones, vigencia)",
                  est == "Aceptado temporalmente" and all(a.get(k) for k in ("quien", "motivo", "condiciones", "vigencia")))
        if d == "Transferir":
            ejecutada = any(c["tipo"] == "transferencia" and c["estado"] == "verificado" for c in r["controles"])
            check(f"V10 {rid} transferencia no ejecutada marcada como Propuesta", ejecutada or est == "Propuesta")
    for c in r["controles"]:
        check(f"V11 {rid} evidencia existe: {c['evidencia']}", os.path.exists(os.path.join(ROOT, c["evidencia"])))
        check(f"V12 {rid} coherencia estado/verificación del control", (c["estado"] == "no_efectivo") == (c["verificacion"] == "no_efectivo")
              and not (c["estado"] in ("disenado", "propuesto") and c["verificacion"] in ("probado", "inspeccionado")))
    check(f"V13 {rid} plan: responsable, revisión y pendiente", all(r.get(k) for k in ("responsable", "revision", "pendiente")))
    check(f"V14 {rid} tipo e impactos válidos", r["tipo"] in TIPOS_RIESGO and r["impactos"] and set(r["impactos"]) <= IMPACTOS)
    s_inh, s_res = p * i, pr * ir
    calc.append({**{k: r.get(k, "") for k in ("id", "nombre", "origen", "owasp", "cwe", "tipo", "impactos", "decision", "estado_tratamiento",
                                              "decision_sec", "decision_sec_estado", "responsable", "revision", "pendiente", "nota", "controles")},
                 "aceptacion": r.get("aceptacion"), "justificacion_inherente": r.get("pi_cualitativa", {}).get("justificacion", ""),
                 "fuente_pi": fuente, "P_inh": p, "I_inh": i, "S_inh": s_inh, "N_inh": nivel(s_inh),
                 "P_res": pr, "I_res": ir, "S_res": s_res, "N_res": nivel(s_res), "prioridad": PRIORIDAD[nivel(s_res)],
                 "razon_P": r["residual"]["razon_P"], "razon_I": r["residual"]["razon_I"]})

orden = [n for n, *_ in NIVELES]
antes = [sum(1 for r in calc if r["N_inh"] == n) for n in orden]
despues = [sum(1 for r in calc if r["N_res"] == n) for n in orden]
check("V15 recuento por nivel suma 24 (inherente y residual)", sum(antes) == 24 and sum(despues) == 24, f"{antes} {despues}")

with open(OUT_VAL, "w", encoding="utf-8") as f:
    f.write("# Validación de consistencia del registro de riesgos (generado por riesgo.py)\n")
    f.write(f"# {len(checks)} comprobaciones, {len(errores)} fallas\n")
    f.write("\n".join(checks) + "\n")
if errores:
    print("VALIDACIÓN FALLIDA:\n  " + "\n  ".join(errores))
    sys.exit(1)

json.dump({"version": reg.get("version"), "metodo": reg["metodo"], "riesgos": calc,
           "distribucion": {"niveles": orden, "inherente": antes, "residual": despues}},
          open(OUT_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=2)


def heatmap(ax, clave, titulo):
    pk, ik = ("P_inh", "I_inh") if clave == "inh" else ("P_res", "I_res")
    celdas = {}
    for r in calc:
        celdas.setdefault((r[pk], r[ik]), []).append(r["id"])
    for p in range(1, 6):
        for i in range(1, 6):
            ax.add_patch(plt.Rectangle((i - 0.5, p - 0.5), 1, 1, facecolor=color(p * i), edgecolor="white", linewidth=2, alpha=0.9))
            ax.text(i - 0.42, p + 0.36, str(p * i), fontsize=7, color="white", alpha=0.85, va="top")
            ids_c = celdas.get((p, i), [])
            if ids_c:
                filas = [", ".join(ids_c[k:k + 3]) for k in range(0, len(ids_c), 3)]
                ax.text(i, p - 0.02, "\n".join(filas), ha="center", va="center", fontsize=8.2, fontweight="bold", color="#111111")
    ax.set_xlim(0.5, 5.5)
    ax.set_ylim(0.5, 5.5)
    ax.set_xticks(range(1, 6))
    ax.set_yticks(range(1, 6))
    ax.set_xticklabels(["1\nMuy bajo", "2\nBajo", "3\nModerado", "4\nAlto", "5\nMuy alto"], fontsize=8)
    ax.set_yticklabels(["1 Rara", "2 Improbable", "3 Posible", "4 Probable", "5 Casi segura"], fontsize=8)
    ax.set_xlabel("Impacto", fontsize=10)
    ax.set_ylabel("Probabilidad", fontsize=10)
    ax.set_title(titulo, fontsize=11, fontweight="bold")
    ax.set_aspect("equal")
    for s in ax.spines.values():
        s.set_visible(False)


def leyenda(fig):
    fig.legend(handles=[Patch(color=c, label=f"{n} ({lo}-{hi})") for n, lo, hi, c in NIVELES],
               loc="lower center", ncol=4, fontsize=9, frameon=False, bbox_to_anchor=(0.5, 0.0))


for clave, titulo, nombre in (("inh", "Riesgo inherente (antes de los controles)", "heatmap-antes.png"),
                              ("res", "Riesgo residual (solo controles probados)", "heatmap-despues.png")):
    fig, ax = plt.subplots(figsize=(7.2, 7.0))
    heatmap(ax, clave, titulo)
    leyenda(fig)
    fig.tight_layout(rect=(0, 0.075, 1, 1))
    fig.savefig(os.path.join(IMG, nombre), dpi=170)
    plt.close(fig)

fig, axs = plt.subplots(1, 2, figsize=(13.5, 7.0))
heatmap(axs[0], "inh", "ANTES: riesgo inherente")
heatmap(axs[1], "res", "DESPUÉS: riesgo residual (controles probados)")
leyenda(fig)
fig.suptitle("Matriz de calor Probabilidad x Impacto - OWASP Juice Shop (24 riesgos)", fontsize=13, fontweight="bold")
fig.tight_layout(rect=(0, 0.075, 1, 0.95))
fig.savefig(os.path.join(IMG, "heatmap-comparativo.png"), dpi=160)
plt.close(fig)

fig, ax = plt.subplots(figsize=(8, 4.2))
x = range(len(orden))
b1 = ax.bar([k - 0.2 for k in x], antes, 0.4, label="Inherente", color="#7f8c9a")
b2 = ax.bar([k + 0.2 for k in x], despues, 0.4, label="Residual", color=[c for *_, c in NIVELES])
for barras in (b1, b2):
    for b in barras:
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.15, str(int(b.get_height())), ha="center", fontsize=9)
ax.set_xticks(list(x))
ax.set_xticklabels(orden)
ax.set_ylabel("Número de riesgos")
ax.set_title("Riesgos por nivel: inherente vs. residual", fontweight="bold")
ax.legend(frameon=False)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
fig.tight_layout()
fig.savefig(os.path.join(IMG, "niveles-antes-despues.png"), dpi=160)
plt.close(fig)

print(f"Validación: {len(checks)} comprobaciones OK")
print("Nivel     Inherente  Residual")
for n, a, d in zip(orden, antes, despues):
    print(f"{n:<9} {a:>9}  {d:>8}")
for r in calc:
    print(f"{r['id']} {r['tipo']:<12} {r['P_inh']}x{r['I_inh']}={r['S_inh']:>2} {r['N_inh']:<7} -> {r['P_res']}x{r['I_res']}={r['S_res']:>2} {r['N_res']:<7}"
          f" [{r['decision']} ({r['estado_tratamiento']}){' + ' + r['decision_sec'] + ' (' + r['decision_sec_estado'] + ')' if r['decision_sec'] else ''}]")
