"""Genera RIESGO_RESIDUAL_HITO_A.md comparando el residual v2 (Fase 6) con el del hito A. Solo lee los JSON calculados.

Uso: python -I generar_comparativo_riesgo.py <raíz del repositorio>
"""
import json
import os
import sys

ROOT = sys.argv[1] if len(sys.argv) > 1 else "."
A = os.path.join(ROOT, "docs", "auditoria-final-2026-11-20")
V2 = json.load(open(os.path.join(ROOT, "docs", "fase-6", "datos", "riesgos-calculados.json"), encoding="utf-8"))
HA = json.load(open(os.path.join(A, "riesgo-hito-a", "riesgos-calculados.json"), encoding="utf-8"))
r2 = {r["id"]: r for r in V2["riesgos"]}
L = []
w = L.append
w("# Riesgo residual tras el hito A (variante corregida + defensa en profundidad)")
w("")
w("> Generado por `datos/generar_comparativo_riesgo.py` a partir de `docs/fase-6/datos/riesgos-calculados.json` (v2) y")
w("> `riesgo-hito-a/riesgos-calculados.json`. El registro del hito A se construye con `datos/construir_riesgos_hito_a.py`")
w("> (delta explícito sobre v2) y se valida con el mismo `riesgo.py` de la Fase 6: "
  + open(os.path.join(A, "riesgo-hito-a", "validacion-consistencia.txt"), encoding="utf-8").read().splitlines()[1].lstrip("# ") + ".")
w("")
w("**Configuración evaluada:** " + HA["metodo"]["configuracion_hito_a"])
w("")
w("**Alcance de la afirmación:** el residual del hito A vale para esa configuración. La configuración por defecto del")
w("repositorio (`make ops-up`, imagen oficial + WAF/RASP/SIEM) conserva el residual v2 de la Fase 6.")
w("")
w("## 1. Distribución por nivel")
w("| Nivel | Inherente | Residual v2 (Fase 6) | Residual hito A |")
w("|---|---|---|---|")
for i, n in enumerate(HA["distribucion"]["niveles"]):
    w(f"| {n} | {HA['distribucion']['inherente'][i]} | {V2['distribucion']['residual'][i]} | {HA['distribucion']['residual'][i]} |")
w("")
w("## 2. Riesgos que cambian")
w("| Riesgo | Inherente | Residual v2 | Residual hito A | Control que lo justifica (evidencia) | Razón de P |")
w("|---|---|---|---|---|---|")
for r in HA["riesgos"]:
    a = r2[r["id"]]
    ctrls_v2 = {c["control"] for c in a["controles"]}
    nuevos = [c for c in r["controles"] if c["control"] not in ctrls_v2]
    if (a["P_res"], a["I_res"]) == (r["P_res"], r["I_res"]) and not nuevos:
        continue
    ctrl = "<br>".join(f"{c['control']} [{c['verificacion']}] (`{c['evidencia']}`)" for c in nuevos)
    w(f"| {r['id']} {r['nombre']} | {r['P_inh']}×{r['I_inh']}={r['S_inh']} {r['N_inh']} | {a['P_res']}×{a['I_res']}={a['S_res']} {a['N_res']} | "
      f"**{r['P_res']}×{r['I_res']}={r['S_res']} {r['N_res']}** | {ctrl} | {r['razon_P']} |")
w("")
w("## 3. Lo que NO cambia y por qué")
w("- **I (impacto)** no baja en ningún riesgo corregido: la convención del equipo solo reduce I con contención o respuesta probadas.")
w("- **R09** (eval): el parche 05 está aplicado, pero la rama de código está desactivada en Docker; queda «inspeccionado» y no reduce.")
w("- **R20** (dependencias con CVE): Trivy baja de 11 a 9 CRITICAL en la variante (`evidence/cierre-2026-11-20/02-escaneos/resumen-trivy.md`),"
  " pero quedan 8 CRITICAL en dependencias que no se actualizaron; la aceptación temporal sigue vigente.")
w("- **R23** (datos personales): sigue Crítico en este registro. La extracción por SQLi está eliminada, pero no se re-evaluó"
  " con el equipo el resto de vías (BOLA en otros recursos, XXE): queda como candidato a revisión, no como reducción.")
w("")
w("## 4. Riesgos que siguen Crítico en el hito A")
for r in HA["riesgos"]:
    if r["N_res"] == "Crítico":
        w(f"- **{r['id']} {r['nombre']}** — {r['P_res']}×{r['I_res']}={r['S_res']}. Pendiente: {r['pendiente']}")
w("")
w("Mapas de calor: `riesgo-hito-a/img/` (mismo generador que la Fase 6).")
open(os.path.join(A, "RIESGO_RESIDUAL_HITO_A.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
print("OK RIESGO_RESIDUAL_HITO_A.md")
