"""Genera docs/fase-6/tratamiento-riesgo.md desde datos/riesgos-calculados.json y comprueba que las cifras del
documento coinciden con el JSON. Uso: python -I generar_md.py <raíz del repositorio>"""
import json
import os
import re
import sys

ROOT = sys.argv[1] if len(sys.argv) > 1 else "."
F6 = os.path.join(ROOT, "docs", "fase-6")
# Opcional (cierre Fase 6): generar_md.py <raíz> <calculados.json> <salida.md> "<título>" para otra fotografía del riesgo.
ENTRADA = os.path.join(ROOT, sys.argv[2]) if len(sys.argv) > 2 else os.path.join(F6, "datos", "riesgos-calculados.json")
SALIDA = os.path.join(ROOT, sys.argv[3]) if len(sys.argv) > 3 else os.path.join(F6, "tratamiento-riesgo.md")
TITULO = sys.argv[4] if len(sys.argv) > 4 else "Fase 6 – Tratamiento formal del riesgo"
d = json.load(open(ENTRADA, encoding="utf-8"))
R = d["riesgos"]
M = d["metodo"]
VERIF = {"probado": "Probado", "inspeccionado": "Inspeccionado (configurado, no ejercitado)", "sin_verificar": "Sin verificar", "no_efectivo": "NO efectivo (probado)"}
EST = {"verificado": "Implementado", "disenado": "Diseñado (diff validado)", "propuesto": "Propuesto", "no_efectivo": "Implementado, no efectivo"}
DEFS = [
    ("Mitigar", "Reducir probabilidad o impacto con controles (ISO/IEC 27005: *modificar*). No elimina la causa."),
    ("Eliminar", "Suprimir la causa raíz (corregir el código o la configuración). Registrarla como plan no equivale a haberla eliminado."),
    ("Evitar", "No realizar la actividad o retirar la funcionalidad que origina el riesgo."),
    ("Transferir", "Compartir el riesgo con un tercero (proveedor gestionado, póliza, contrato). No transfiere la responsabilidad del titular; aquí solo está **propuesta**."),
    ("Aceptar", "Retener el riesgo de forma consciente, documentada, temporal y con condiciones (ISO/IEC 27005: *retener*)."),
]
L = []
w = L.append
w("# " + TITULO)
w("")
w("> **Documento generado** por `docs/fase-6/datos/generar_md.py` (tras `riesgo.py`, que valida los datos). No editar")
w("> las tablas a mano: modificar `datos/riesgos.json` y ejecutar `make risk`. Versión de datos: " + str(d.get("version")) + ".")
w("")
w("## 1. Método")
w(f"- **Marco:** {M['nota_normativa']}")
w(f"- **Escala:** {M['escala']}.")
w(f"- **Inherente:** {M['inherente_dread']} {M['inherente_cualitativa']}")
w(f"- **Residual:** {M['residual']}")
for pauta in M["pautas_reduccion"]:
    w(f"  - {pauta}")
w("- **Validación automática** (`datos/validacion-consistencia.txt`): 24 IDs únicos, escala 1-5, residual ≤ inherente,")
w("  reducciones solo con control probado, coherencia decisión/estado, aceptaciones con condiciones, transferencias")
w("  propuestas marcadas como tales, rutas de evidencia existentes y recuentos que suman 24. Prueba negativa del")
w("  validador: `datos/prueba-negativa-validador.txt`.")
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
tipos, imp = {}, {}
for r in R:
    tipos[r["tipo"]] = tipos.get(r["tipo"], 0) + 1
    for i in r["impactos"]:
        imp[i] = imp.get(i, 0) + 1
w("**Por tipo:** " + " · ".join(f"{k}: {v}" for k, v in sorted(tipos.items(), key=lambda x: -x[1])) + ".  ")
w("**Por impacto (riesgos que lo incluyen):** " + " · ".join(f"{k}: {v}" for k, v in sorted(imp.items(), key=lambda x: -x[1])) + ".")
w("")
w("## 4. Matriz de decisiones y plan de tratamiento")
w("| ID | Inherente | Decisión principal (estado) | Complementaria (estado) | Residual | Prioridad | Responsable (rol) | Revisión |")
w("|---|---|---|---|---|---|---|---|")
for r in R:
    sec = f"{r['decision_sec']} ({r['decision_sec_estado']})" if r["decision_sec"] else "—"
    w(f"| {r['id']} | {r['P_inh']}×{r['I_inh']}={r['S_inh']} {r['N_inh']} | **{r['decision']}** ({r['estado_tratamiento']}) | {sec} | "
      f"{r['P_res']}×{r['I_res']}={r['S_res']} **{r['N_res']}** | {r['prioridad']} | {r['responsable']} | {r['revision']} |")
w("")
cnt = {}
for r in R:
    cnt[r["decision"]] = cnt.get(r["decision"], 0) + 1
sec_c = {}
for r in R:
    if r["decision_sec"]:
        k = f"{r['decision_sec']} ({r['decision_sec_estado']})"
        sec_c[k] = sec_c.get(k, 0) + 1
w("**Decisiones principales:** " + " · ".join(f"{k}: {v}" for k, v in sorted(cnt.items(), key=lambda x: -x[1])) + ".  ")
w("**Complementarias:** " + " · ".join(f"{k}: {v}" for k, v in sorted(sec_c.items(), key=lambda x: -x[1])) + ".")
w("Los responsables se expresan por **rol**; el equipo asigna a la persona concreta de cada rol.")
w("")
w("### 4.1 Aceptaciones temporales")
w("| ID | Quién acepta | Motivo | Condiciones | Vigencia |")
w("|---|---|---|---|---|")
for r in R:
    a = r.get("aceptacion")
    if a:
        w(f"| {r['id']} | {a['quien']} | {a['motivo']} | {a['condiciones']} | {a['vigencia']} |")
w("")
w("## 5. Justificación del riesgo residual (por riesgo)")
w("| ID | Inherente | Residual | Razón de P | Razón de I | Actividad pendiente |")
w("|---|---|---|---|---|---|")
for r in R:
    w(f"| {r['id']} | {r['P_inh']}×{r['I_inh']} ({r['fuente_pi']}) | {r['P_res']}×{r['I_res']} | {r['razon_P']} | {r['razon_I']} | {r['pendiente']} |")
w("")
cual = [r for r in R if r["fuente_pi"] == "Cualitativa"]
if cual:
    w("**Justificación de las valoraciones inherentes cualitativas:** " + " ".join(f"{r['id']}: {r['justificacion_inherente']}" for r in cual))
    w("")
w("## 6. Controles por riesgo: implementación, verificación y evidencia")
for r in R:
    w(f"### {r['id']} — {r['nombre']}")
    w("| Control | Tipo | Implementación | Verificación | Evidencia |")
    w("|---|---|---|---|---|")
    for c in r["controles"]:
        w(f"| {c['control']} | {c['tipo']} | {EST.get(c['estado'], c['estado'])} | {VERIF.get(c['verificacion'], c['verificacion'])} | `{c['evidencia']}` |")
    if r.get("nota"):
        w(f"\n*Nota:* {r['nota']}")
    w("")
w("## 7. Matriz de calor (Probabilidad × Impacto)")
w("![Comparativo](img/heatmap-comparativo.png)")
w("")
niv, inh, res = d["distribucion"]["niveles"], d["distribucion"]["inherente"], d["distribucion"]["residual"]
w("| Nivel | Inherente | Residual |")
w("|---|---|---|")
for n, a, b in zip(niv, inh, res):
    w(f"| {n} | {a} | {b} |")
w(f"| **Total** | {sum(inh)} | {sum(res)} |")
w("")
w("Archivos: `img/heatmap-antes.png`, `img/heatmap-despues.png`, `img/heatmap-comparativo.png`, `img/niveles-antes-despues.png`.")
w("")
w("## 8. Lectura del residual")
altos = [r for r in R if r["N_res"] in ("Alto", "Crítico")]
crit = [r for r in R if r["N_res"] == "Crítico"]
# Lectura derivada de los DATOS del registro (antes eran frases fijas que quedaban desactualizadas en los registros
# posteriores: p. ej. «R06 sigue crítico» o «R21 es Bajo porque la nube no está desplegada»; corregido el 2026-11-24).
pend = [r for r in altos if r["estado_tratamiento"] in ("Planificado", "Propuesta")]
w(f"- Quedan **{len(crit)} riesgos críticos**" + (f" ({', '.join(r['id'] for r in crit)})" if crit else "") +
  f" y **{len(altos) - len(crit)} altos**" + (f"; de ellos, {len(pend)} con el tratamiento solo planificado o propuesto "
                                               f"({', '.join(r['id'] for r in pend)}), que no reciben reducción." if pend else "."))
w("- Una reducción solo se aplica con un control verificado y PROBADO; la detección y lo inspeccionado no reducen.")
RR = {r["id"]: r for r in R}
if "R06" in RR and RR["R06"]["N_res"] == "Crítico":
    w("- **R06 (BOLA)** sigue crítico: la lectura cruzada continúa con HTTP 200 a través del WAF. La alerta del SIEM es una")
    w("  heurística con falsos positivos demostrados, no una verificación de propietario.")
if "R21" in RR:
    r21 = RR["R21"]
    if r21["decision"] == "Evitar":
        w(f"- **R21** es {r21['N_res']} solo porque la nube **no está desplegada** (evitación probada); eso no valida la seguridad de la infraestructura.")
    else:
        w(f"- **R21 (cloud)** se valora sobre el despliegue REAL: {r21['P_res']}×{r21['I_res']} {r21['N_res']}, con controles probados en la "
          f"nube. Pendiente: {r21.get('pendiente', '')}.")
open(SALIDA, "w", encoding="utf-8").write("\n".join(L) + "\n")

# Comprobación cruzada documento <-> JSON
md = "\n".join(L)
filas = dict((m.group(1), (int(m.group(2)), int(m.group(3)))) for m in re.finditer(r"^\| (Bajo|Medio|Alto|Crítico) \| (\d+) \| (\d+) \|$", md, re.M))
assert all(filas[n] == (a, b) for n, a, b in zip(niv, inh, res)), "tabla de niveles del documento != JSON"
assert len(re.findall(r"^\| R\d\d \| \d×\d=\d+ ", md, re.M)) == 24, "la matriz de decisiones no tiene 24 filas"
print(f"tratamiento-riesgo.md generado ({len(L)} líneas); tablas coherentes con el JSON (24 riesgos; {inh} -> {res})")
