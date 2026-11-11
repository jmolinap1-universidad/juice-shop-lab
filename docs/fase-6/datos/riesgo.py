"""Fase 6 - Cálculo reproducible del riesgo inherente y residual + matrices de calor.

Entrada : docs/fase-6/datos/riesgos.json (registro de riesgos con DREAD de la Fase 1 y controles)
Salidas : docs/fase-6/datos/riesgos-calculados.json
          docs/fase-6/img/heatmap-antes.png, heatmap-despues.png, heatmap-comparativo.png, niveles-antes-despues.png
Uso     : python riesgo.py <directorio docs/fase-6>
Reglas  : ver "metodo" en riesgos.json (sin ajustes manuales: todo se deriva de los datos).
"""
import json
import math
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

BASE = sys.argv[1] if len(sys.argv) > 1 else "."
DATA = os.path.join(BASE, "datos", "riesgos.json")
OUT_JSON = os.path.join(BASE, "datos", "riesgos-calculados.json")
IMG = os.path.join(BASE, "img")
os.makedirs(IMG, exist_ok=True)

NIVELES = [("Bajo", 1, 4, "#2e9e4f"), ("Medio", 5, 9, "#f2c230"), ("Alto", 10, 16, "#f07f1e"), ("Crítico", 20, 25, "#d7263d")]


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
        p = math.ceil(((rep + e + di) / 3) / 2)
        i = math.ceil(((d + a) / 2) / 2)
        return p, i, "DREAD Fase 1"
    q = r["pi_cualitativa"]
    return q["P"], q["I"], "cualitativa"


def residual(r, p, i):
    ver = [c for c in r["controles"] if c["estado"] == "verificado"]
    if any(c["tipo"] in ("eliminacion", "evitacion") for c in ver):
        p_res = 1
    else:
        n = sum(1 for c in ver if c["tipo"] == "preventivo")
        p_res = max(1, p - (0 if n == 0 else 2 if n == 1 else 3))
    di = (1 if any(c["tipo"] == "detectivo" for c in ver) else 0) + (1 if any(c["tipo"] == "contencion" for c in ver) else 0)
    return p_res, max(1, i - di)


reg = json.load(open(DATA, encoding="utf-8"))
calc = []
for r in reg["riesgos"]:
    p, i, fuente = inherente(r)
    pr, ir = residual(r, p, i)
    calc.append({**{k: r[k] for k in ("id", "nombre", "origen", "owasp", "cwe", "tipo", "impactos", "decision", "decision_sec")},
                 "nota": r.get("nota", ""), "controles": r["controles"], "fuente_pi": fuente,
                 "P_inh": p, "I_inh": i, "S_inh": p * i, "N_inh": nivel(p * i),
                 "P_res": pr, "I_res": ir, "S_res": pr * ir, "N_res": nivel(pr * ir)})
json.dump({"metodo": reg["metodo"], "riesgos": calc}, open(OUT_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=2)


def heatmap(ax, clave, titulo):
    pk, ik = ("P_inh", "I_inh") if clave == "inh" else ("P_res", "I_res")
    celdas = {}
    for r in calc:
        celdas.setdefault((r[pk], r[ik]), []).append(r["id"])
    for p in range(1, 6):
        for i in range(1, 6):
            ax.add_patch(plt.Rectangle((i - 0.5, p - 0.5), 1, 1, facecolor=color(p * i), edgecolor="white", linewidth=2, alpha=0.9))
            ids = celdas.get((p, i), [])
            ax.text(i - 0.42, p + 0.36, str(p * i), fontsize=7, color="white", alpha=0.85, va="top")
            if ids:
                filas = [", ".join(ids[k:k + 3]) for k in range(0, len(ids), 3)]
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
    from matplotlib.patches import Patch
    fig.legend(handles=[Patch(color=c, label=f"{n} ({lo}-{hi})") for n, lo, hi, c in NIVELES],
               loc="lower center", ncol=4, fontsize=9, frameon=False, bbox_to_anchor=(0.5, 0.0))


for clave, titulo, nombre in (("inh", "Riesgo inherente (antes de los controles)", "heatmap-antes.png"),
                              ("res", "Riesgo residual (después de los controles verificados)", "heatmap-despues.png")):
    fig, ax = plt.subplots(figsize=(7.2, 7.0))
    heatmap(ax, clave, titulo)
    leyenda(fig)
    fig.tight_layout(rect=(0, 0.075, 1, 1))
    fig.savefig(os.path.join(IMG, nombre), dpi=170)
    plt.close(fig)

fig, axs = plt.subplots(1, 2, figsize=(13.5, 7.0))
heatmap(axs[0], "inh", "ANTES: riesgo inherente")
heatmap(axs[1], "res", "DESPUÉS: riesgo residual")
leyenda(fig)
fig.suptitle("Matriz de calor Probabilidad x Impacto - OWASP Juice Shop (24 riesgos)", fontsize=13, fontweight="bold")
fig.tight_layout(rect=(0, 0.075, 1, 0.95))
fig.savefig(os.path.join(IMG, "heatmap-comparativo.png"), dpi=160)
plt.close(fig)

# Distribucion por nivel antes / despues
orden = [n for n, *_ in NIVELES]
antes = [sum(1 for r in calc if r["N_inh"] == n) for n in orden]
despues = [sum(1 for r in calc if r["N_res"] == n) for n in orden]
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

print("Nivel     Inherente  Residual")
for n, a, d in zip(orden, antes, despues):
    print(f"{n:<9} {a:>9}  {d:>8}")
print()
for r in calc:
    print(f"{r['id']} {r['tipo']:<12} P{r['P_inh']}xI{r['I_inh']}={r['S_inh']:>2} {r['N_inh']:<7} -> P{r['P_res']}xI{r['I_res']}={r['S_res']:>2} {r['N_res']:<7} [{r['decision']}{'/' + r['decision_sec'] if r['decision_sec'] else ''}] ({r['fuente_pi']})")
