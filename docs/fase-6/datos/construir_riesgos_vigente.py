"""Construye el registro de riesgos VIGENTE del cierre de la Fase 6 (riesgos-vigente.json).

Uso: python -I construir_riesgos_vigente.py <raíz del repositorio>
Parte del registro del hito A (docs/auditoria-final-2026-11-20/datos/riesgos-hito-a.json, que a su vez parte de v2) y
aplica un DELTA explícito solo donde hay evidencia nueva del cierre (evidence/fase-6/cierre-final-2026-11-21/).
Configuración evaluada: `make ops-corregido-up` = variante corregida con los parches 01-10 + WAF (con ALLOWED_METHODS y
la exclusión acotada de whoami) + RASP + SIEM (con redacción de tokens y alerta de ingesta).
No modifica v2 (Fase 6 histórica) ni el registro del hito A. riesgo.py valida que ninguna reducción carezca de un
control 'verificado' + 'probado'.
"""
import copy
import json
import os
import sys

ROOT = sys.argv[1] if len(sys.argv) > 1 else "."
SRC = os.path.join(ROOT, "docs", "auditoria-final-2026-11-20", "datos", "riesgos-hito-a.json")
DST = os.path.join(ROOT, "docs", "fase-6", "datos", "riesgos-vigente.json")
EV = "evidence/fase-6/cierre-final-2026-11-21"


def ctrl(nombre, tipo, estado, verif, evidencia):
    return {"control": nombre, "tipo": tipo, "estado": estado, "verificacion": verif, "evidencia": evidencia}


# DELTA: riesgo -> (controles que se SUSTITUYEN por prefijo {prefijo: nuevo}, controles que se AÑADEN, campos)
DELTA = {
    "R06": ({}, [
        ctrl("Parche 10: verificación de propietario en artículos de cesta (GET/PUT/DELETE y lista), direcciones (PUT) y opiniones (DELETE); 0/10 accesos ajenos con éxito, 7/7 operaciones del propietario correctas",
             "eliminacion", "verificado", "probado", f"{EV}/02-bola-recursos/despues-parche10-corregida-rasp-sin-waf.md"),
        ctrl("Alerta SIEM API_BOLA_AccesoAjenoDenegado (403 a objetos ajenos; inactiva con tráfico legítimo, activa con el intento cruzado)",
             "detectivo", "verificado", "probado", f"{EV}/10-siem/reglas-tras-disparadores.txt")],
        {"residual": {"P": 2, "I": 4,
                      "razon_P": "Verificación de propietario probada en el código para cestas, artículos de cesta, direcciones, tarjetas y opiniones (0/10 accesos ajenos, sin WAF y con WAF): P-3 respecto del inherente. No llega a 1 porque no se auditaron todos los objetos de la API (Complaints, PrivacyRequests, Recycles, Memories, historial de pedidos).",
                      "razon_I": "Sin contención probada; las alertas aportan visibilidad y no reducen el impacto."},
         "revision": "Ejecutar security/ops/bola-recursos.sh tras cualquier cambio de rutas o modelos",
         "pendiente": "Auditar el resto de objetos de la API (Complaints, PrivacyRequests, Recycles, Memories, historial de pedidos)"}),
    "R13": ({"CRS 941": ctrl("CRS 941 (XSS): 403 con dos vectores acotados (parámetro de búsqueda y cuerpo de una reseña); reglas 941100/941110/941160/941390 en el audit log",
                             "preventivo", "verificado", "probado", f"{EV}/07-waf/familias-waf.md")}, [],
        {"residual": {"P": 3, "I": 4,
                      "razon_P": "Una capa preventiva probada (CRS 941), pero solo con dos vectores y sin codificación de salida en la aplicación: P-1 (cobertura parcial, menor que la pauta de P-2).",
                      "razon_I": "Sin cambio."},
         "pendiente": "Codificación de salida en el frontend y pruebas XSS por cada campo que se muestra a otros usuarios"}),
    "R19": ({}, [
        ctrl("Alerta Ingesta_WAF_Ausente: latido del WAF cada 30 s; con el colector detenido pasó a pending (2 min) y firing (+1 min); resuelta al reanudar, 6/6 líneas recuperadas",
             "detectivo", "verificado", "probado", f"{EV}/10-siem/alerta-ingesta-ausente.txt"),
        ctrl("Descubrimiento de contenedores cada 5 s (antes 60 s): 5/5 detecciones del RASP llegan a Loki tras recrear la app",
             "preventivo", "verificado", "probado", f"{EV}/10-siem/hallazgo-perdida-ingesta.txt")],
        {"residual_sin_cambio": True,
         "pendiente": "Notificación a personas (Alertmanager/correo), alta disponibilidad y driver de logs que no dependa del descubrimiento"}),
    "R23": ({}, [
        ctrl("Variante corregida: extracción por SQLi eliminada en el código (A2/A3 sin datos sin WAF ni RASP)",
             "eliminacion", "verificado", "probado", f"{EV}/04-escenario-B-corregida/resumen-ataques.md"),
        ctrl("Variante corregida: lectura y alteración de objetos ajenos eliminadas en 5 tipos de recurso (parches 08 y 10)",
             "eliminacion", "verificado", "probado", f"{EV}/04-escenario-B-corregida/bola-recursos.md"),
        ctrl("Redacción de Authorization, Cookie y JWT antes de Loki (0 tokens visibles tras el ajuste)",
             "preventivo", "verificado", "probado", f"{EV}/10-siem/redaccion-tokens-loki.txt")],
        {"residual": {"P": 3, "I": 5,
                      "razon_P": "Las dos vías de extracción probadas (SQLi y objetos ajenos) están eliminadas en el código: P-1. No baja más porque XXE (R10), inyección NoSQL (R08) y SSRF (R11) no se han probado y la exposición de datos por otras rutas no está descartada.",
                      "razon_I": "La consecuencia legal y reputacional de una exposición no cambia; la transferencia solo está propuesta."},
         "pendiente": "Probar XXE, NoSQL y SSRF; póliza o cláusulas contractuales si hubiera datos reales"}),
    "R24": ({}, [
        ctrl("Redacción en Alloy de Authorization/Cookie/Set-Cookie y JWT en las tres fuentes antes de Loki (hallazgo: el audit log de ModSecurity guardaba el token de sesión)",
             "preventivo", "verificado", "probado", f"{EV}/10-siem/redaccion-tokens-loki.txt")],
        {"residual_sin_cambio": True,
         "pendiente": "Autenticación en Loki y Grafana sin acceso anónimo antes de cualquier despliegue fuera de 127.0.0.1; purgar de Loki las líneas anteriores a la redacción (requiere autorización: borra datos)"}),
}

reg = json.load(open(SRC, encoding="utf-8"))
nuevo = copy.deepcopy(reg)
nuevo["version"] = reg.get("version", "v2+hito-a").replace("+hito-a", "") + "+cierre-fase6"
nuevo["metodo"]["configuracion_vigente"] = (
    "make ops-corregido-up: variante corregida (parches 01-10) + WAF ModSecurity/CRS (ALLOWED_METHODS con PUT/PATCH/DELETE y "
    "exclusión acotada 932260 en GET /rest/user/whoami) + RASP Aikido Zen + SIEM (redacción de tokens, alerta de ingesta). "
    "Delta aplicado por docs/fase-6/datos/construir_riesgos_vigente.py sobre el registro del hito A.")
for r in nuevo["riesgos"]:
    if r["id"] not in DELTA:
        continue
    sustituir, anadir, campos = DELTA[r["id"]]
    for prefijo, c in sustituir.items():
        idx = [i for i, x in enumerate(r["controles"]) if x["control"].startswith(prefijo)]
        if len(idx) != 1:
            sys.exit(f"{r['id']}: se esperaba 1 control que empiece por '{prefijo}', hay {len(idx)}")
        r["controles"][idx[0]] = c
    r["controles"].extend(anadir)
    campos = dict(campos)
    campos.pop("residual_sin_cambio", None)
    antes = (r["residual"]["P"], r["residual"]["I"])
    r.update(campos)
    print(f"{r['id']}: residual P×I {antes[0]}×{antes[1]} -> {r['residual']['P']}×{r['residual']['I']}; +{len(anadir)} controles, {len(sustituir)} sustituidos")
json.dump(nuevo, open(DST, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("OK", DST)
