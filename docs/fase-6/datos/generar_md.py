"""Genera docs/fase-6/tratamiento-riesgo.md a partir de datos/riesgos-calculados.json (sin edicion manual de tablas)."""
import json
import os
import sys

BASE = sys.argv[1] if len(sys.argv) > 1 else "."
d = json.load(open(os.path.join(BASE, "datos", "riesgos-calculados.json"), encoding="utf-8"))
R = d["riesgos"]
EST = {"verificado": "Verificado", "disenado": "Diseñado (diff validado)", "propuesto": "Propuesto", "no_efectivo": "NO efectivo (verificado)"}
DEFS = [
    ("Mitigar", "Reducir probabilidad o impacto con controles (ISO/IEC 27005: *modificar*)."),
    ("Eliminar", "Suprimir la causa raíz del riesgo (corrección del código o de la configuración)."),
    ("Evitar", "Dejar de realizar la actividad o retirar la funcionalidad que origina el riesgo."),
    ("Transferir", "Compartir el riesgo con un tercero (proveedor gestionado, póliza, contrato)."),
    ("Aceptar", "Retener el riesgo de forma consciente, documentada y temporal (ISO/IEC 27005: *retener*)."),
]
L = []
w = L.append
w("# Fase 6 – Tratamiento formal del riesgo (ISO/IEC 27005)")
w("")
w("> **Documento generado** por `docs/fase-6/datos/generar_md.py` desde `riesgos-calculados.json`, que a su vez")
w("> produce `riesgo.py` a partir de `riesgos.json`. No editar las tablas a mano: cambiar los datos y regenerar (`make risk`).")
w("")
w("## 1. Método (reproducible)")
w("- **Escala:** Probabilidad (P) e Impacto (I) de 1 a 5; nivel = P × I → **Bajo 1-4 · Medio 5-9 · Alto 10-16 · Crítico 20-25**.")
w("- **Inherente:** para las amenazas de la Fase 1, P = ⌈media(R, E, Di)/2⌉ e I = ⌈media(D, A)/2⌉ sobre el DREAD de")
w("  `docs/fase-1/fase1-modelado-amenazas.md` §5. Los riesgos sin DREAD (cloud, cumplimiento, operativos y el hallazgo del")
w("  RASP) usan una **valoración cualitativa** del equipo y se marcan como tal.")
w("- **Residual** (solo cuentan controles **verificados con evidencia**):")
for regla in d["metodo"]["residual"]:
    w(f"  - {regla}.")
w("")
w("## 2. Opciones de tratamiento")
w("| Decisión | Significado en este proyecto |")
w("|---|---|")
for k, v in DEFS:
    w(f"| **{k}** | {v} |")
w("")
w("## 3. Registro de riesgos: categorización por tipo e impacto")
w("| ID | Riesgo | Origen | Tipo | Impactos (principal primero) | OWASP 2025 | CWE |")
w("|---|---|---|---|---|---|---|")
for r in R:
    w(f"| {r['id']} | {r['nombre']} | {r['origen']} | {r['tipo']} | {', '.join(r['impactos'])} | {r['owasp']} | {r['cwe']} |")
w("")
tipos = {}
for r in R:
    tipos[r["tipo"]] = tipos.get(r["tipo"], 0) + 1
w("**Por tipo:** " + " · ".join(f"{k}: {v}" for k, v in sorted(tipos.items(), key=lambda x: -x[1])) + ".")
imp = {}
for r in R:
    for i in r["impactos"]:
        imp[i] = imp.get(i, 0) + 1
w("**Por impacto (riesgos que lo incluyen):** " + " · ".join(f"{k}: {v}" for k, v in sorted(imp.items(), key=lambda x: -x[1])) + ".")
w("")
w("## 4. Matriz de decisiones por riesgo")
w("| ID | Inherente (P×I) | Decisión | Secundaria | Residual (P×I) | Observación |")
w("|---|---|---|---|---|---|")
for r in R:
    w(f"| {r['id']} | {r['P_inh']}×{r['I_inh']}={r['S_inh']} **{r['N_inh']}** | **{r['decision']}** | {r['decision_sec'] or '—'} | "
      f"{r['P_res']}×{r['I_res']}={r['S_res']} **{r['N_res']}** | {r['nota'] or ''} |")
w("")
cuenta = {}
for r in R:
    cuenta[r["decision"]] = cuenta.get(r["decision"], 0) + 1
w("**Decisiones principales:** " + " · ".join(f"{k}: {v}" for k, v in sorted(cuenta.items(), key=lambda x: -x[1])) + ".")
sec = {}
for r in R:
    if r["decision_sec"]:
        sec[r["decision_sec"]] = sec.get(r["decision_sec"], 0) + 1
w("**Decisiones secundarias:** " + " · ".join(f"{k}: {v}" for k, v in sorted(sec.items(), key=lambda x: -x[1])) + ". Las cinco opciones (Aceptar, Eliminar, Evitar, Mitigar, Transferir) se aplican; *Transferir* actúa como complemento en R03, R21 y R23.")
w("")
w("## 5. Controles compensatorios por riesgo (con estado y evidencia)")
for r in R:
    w(f"### {r['id']} — {r['nombre']}")
    w("| Control | Tipo | Estado | Evidencia |")
    w("|---|---|---|---|")
    for c in r["controles"]:
        w(f"| {c['control']} | {c['tipo']} | {EST.get(c['estado'], c['estado'])} | `{c['evidencia']}` |")
    w("")
w("## 6. Matriz de calor (Probabilidad × Impacto)")
w("![Comparativo](img/heatmap-comparativo.png)")
w("")
niv = ["Bajo", "Medio", "Alto", "Crítico"]
w("| Nivel | Inherente | Residual |")
w("|---|---|---|")
for n in niv:
    w(f"| {n} | {sum(1 for r in R if r['N_inh'] == n)} | {sum(1 for r in R if r['N_res'] == n)} |")
w("")
w("Archivos: `img/heatmap-antes.png`, `img/heatmap-despues.png`, `img/heatmap-comparativo.png`, `img/niveles-antes-despues.png`.")
w("")
w("## 7. Lectura honesta del residual")
res_altos = [r for r in R if r["N_res"] in ("Alto", "Crítico")]
w(f"- Quedan **{len(res_altos)} riesgos Alto/Crítico**: " + ", ".join(f"{r['id']} ({r["N_res"]})" for r in res_altos) + ".")
w("  Su tratamiento definitivo (parches de código, actualización de dependencias, parser XML, lista blanca SSRF) está")
w("  **diseñado o propuesto, no desplegado**, por lo que el método no les concede reducción.")
w("- **R03** (clave privada JWT embebida) sigue **Crítico**: ningún control desplegado detecta un token forjado; requiere")
w("  desplegar el parche 04 con un gestor de secretos.")
w("- **R06** (BOLA) baja solo en impacto: el WAF **no** lo bloquea (verificado, `evidence/fase-6/defensa-completa/bola/`);")
w("  el SIEM lo **detecta** (`API_Enumeracion_Objetos_PosibleBOLA`) y el parche 08 lo eliminaría en código.")
w("- Las aceptaciones (R04, R20, R24) son **temporales y limitadas al laboratorio**, con su condición de revisión.")
open(os.path.join(BASE, "tratamiento-riesgo.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
print("tratamiento-riesgo.md generado:", len(L), "líneas")
