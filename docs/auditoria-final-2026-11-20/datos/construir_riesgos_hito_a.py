"""Construye el registro de riesgos del hito A (riesgos-hito-a.json) a partir del registro v2 de la Fase 6.

Uso: python -I construir_riesgos_hito_a.py <raíz del repositorio>
No modifica docs/fase-6/datos/riesgos.json: aplica un DELTA explícito y revisable (abajo) solo donde hay evidencia
nueva de la variante corregida. Cada control nuevo apunta a su evidencia; el validador riesgo.py rechaza cualquier
reducción sin control 'verificado' + 'probado'.
Configuración evaluada: variante corregida (juice-corregida:local) + WAF + RASP + SIEM
(deploy/hardened/docker-compose.corregido.yml). La configuración por defecto del repositorio sigue siendo la de la Fase 6.
"""
import copy
import json
import os
import sys

ROOT = sys.argv[1] if len(sys.argv) > 1 else "."
SRC = os.path.join(ROOT, "docs", "fase-6", "datos", "riesgos.json")
DST = os.path.join(ROOT, "docs", "auditoria-final-2026-11-20", "datos", "riesgos-hito-a.json")
EV = "evidence/cierre-2026-11-20"
E03 = f"{EV}/03-corregida-sin-waf/resumen-ataques.md"
REG03 = f"{EV}/03-corregida-sin-waf/regresion-funcional.md"
BOLA03 = f"{EV}/03-corregida-sin-waf/bola/resultado-bola.md"
ARR = f"{EV}/03-corregida-sin-waf/arranque-sin-secreto.txt"
DIFF = "app-hardened/patches/v2/correcciones-hito-a.patch"


def ctrl(nombre, tipo, estado, verif, evidencia):
    return {"control": nombre, "tipo": tipo, "estado": estado, "verificacion": verif, "evidencia": evidencia}


# DELTA: (prefijo del control de parche a sustituir, controles nuevos, cambios del riesgo)
DELTA = {
    "R01": ("Parche 01", [ctrl("Parche 01 v2: consulta parametrizada + verificación scrypt (variante corregida); A1 sin token y HTTP 401 sin WAF ni RASP",
                                "eliminacion", "verificado", "probado", E03)],
            {"decision_sec_estado": "Ejecutado",
             "residual": {"P": 1, "I": 5,
                          "razon_P": "Causa eliminada y probada SIN WAF ni RASP (A1 → 401, sin token); WAF y RASP quedan como capas adicionales (el RASP bloqueó además el mismo payload, escenario 05): P=1.",
                          "razon_I": "Si una vía no probada prosperara, la consecuencia sería la misma (sesión de administrador). La corrección no reduce el impacto."},
             "revision": "Repetir run.sh sin WAF tras cualquier cambio en routes/login.ts",
             "pendiente": "Hacer de la variante corregida la imagen por defecto del despliegue (hoy es el override docker-compose.corregido.yml)"}),
    "R02": ("Parche 02", [ctrl("Parche 02: consulta parametrizada en la búsqueda (variante corregida); A2 y A3 sin datos sin WAF ni RASP y búsqueda legítima con resultados",
                                "eliminacion", "verificado", "probado", E03)],
            {"decision_sec_estado": "Ejecutado",
             "residual": {"P": 1, "I": 5,
                          "razon_P": "Causa eliminada y probada sin WAF ni RASP (A2/A3 mitigados; la búsqueda legítima devuelve productos): P=1.",
                          "razon_I": "La extracción de tablas tendría la misma consecuencia; la corrección no reduce el impacto."},
             "revision": "Repetir run.sh sin WAF tras cualquier cambio en routes/search.ts",
             "pendiente": "Corregir el aviso de tipos TS2339 (QueryTypes) del parche 02 y hacer de la variante la imagen por defecto"}),
    "R03": ("Parche 04", [ctrl("Parche 04 v2: clave privada fuera del código, cargada de un secreto montado y rotada; un token firmado con la clave antigua recibe HTTP 401",
                                "eliminacion", "verificado", "probado", REG03),
                           ctrl("Arranque fail-closed: sin secreto la aplicación no inicia (código de salida 1)",
                                "preventivo", "verificado", "probado", ARR)],
            {"estado_tratamiento": "Ejecutado",
             "residual": {"P": 2, "I": 5,
                          "razon_P": "La clave embebida ya no está en la imagen (Trivy: sin secreto private-key en insecurity.ts/.js) y los tokens de la clave antigua se rechazan: la causa se eliminó. No baja a 1 porque la clave nueva es un archivo en el host, sin gestor de secretos/KMS ni rotación automática.",
                          "razon_I": "Si la clave nueva se filtrara, forjar tokens tendría la misma consecuencia."},
             "revision": "En cada despliegue: generar una clave nueva (security/ops/generar-clave-jwt.sh) y comprobar el 401 con un token anterior",
             "pendiente": "Gestor de secretos / KMS y rotación automática (transferencia propuesta)"}),
    "R05": ("Parche 03", [ctrl("Parche 03 v2: scrypt con sal aleatoria (sin dependencias nuevas); 27/27 usuarios con scrypt, login y cambio de contraseña probados",
                                "eliminacion", "verificado", "probado", REG03)],
            {"estado_tratamiento": "Ejecutado",
             "residual": {"P": 1, "I": 5,
                          "razon_P": "MD5 sin sal eliminado para todas las cuentas (27/27 scrypt en la base del contenedor); revertir un hash filtrado deja de ser trivial: P=1. La ruta 2FA usa la misma función pero no se ejercitó.",
                          "razon_I": "Sin contención probada; la convención no reduce I por el algoritmo."},
             "revision": "Ejercitar el alta y la verificación de 2FA con la variante; en una base con datos reales, migrar hashes al iniciar sesión",
             "pendiente": "Prueba de 2FA; migración progresiva si la base no se re-siembra"}),
    "R06": ("Parche 08", [ctrl("Parche 08: verificación de propietario en /rest/basket/:id (variante corregida); A12 → 403 y la cesta propia → 200",
                                "eliminacion", "verificado", "probado", BOLA03)],
            {"estado_tratamiento": "Ejecutado parcialmente",
             "residual": {"P": 3, "I": 4,
                          "razon_P": "La lectura cruzada de cestas queda bloqueada en el código (403 sin WAF, con RASP y con la defensa completa): P-2. No baja más porque la verificación de propietario no cubre Addresses, Cards ni Feedbacks.",
                          "razon_I": "Sin contención probada; la heurística del SIEM solo aporta visibilidad."},
             "revision": "Al extender la verificación de propietario a otros recursos: repetir A12 por recurso",
             "pendiente": "Extender la verificación de propietario a Addresses, Cards y Feedbacks"}),
    "R07": ("Parche 06", [ctrl("Parche 06: lista blanca de campos en el registro (variante corregida); role=admin ignorado (role customer) sin WAF",
                                "eliminacion", "verificado", "probado", E03)],
            {"decision_sec_estado": "Ejecutado",
             "residual": {"P": 1, "I": 4,
                          "razon_P": "Causa eliminada y probada sin WAF (A7: role customer); el parche virtual del WAF queda como capa adicional: P=1.",
                          "razon_I": "Una cuenta de administrador creada por otra vía tendría la misma consecuencia."},
             "revision": "Repetir A7 sin WAF tras cambios en el registro de usuarios",
             "pendiente": "Hacer de la variante la imagen por defecto"}),
    "R09": ("Parche 05", [ctrl("Parche 05: eval() eliminado en routes/userProfile.ts (revisado en el diff). No ejercitable dinámicamente: Juice Shop desactiva esa rama en Docker (safetyMode auto, disabledEnv Docker)",
                                "eliminacion", "verificado", "inspeccionado", DIFF)],
            {"pendiente": "Revisar b2bOrder y captcha (vm); prueba dinámica del parche 05 fuera de Docker",
             "revision": "Al ejecutar la variante fuera de Docker o con safetyMode disabled"}),
    "R14": ("Parche 07", [ctrl("Parche 07: CORS con origen explícito (variante corregida); sin ACAO abierto con Origin externo y sin WAF",
                                "eliminacion", "verificado", "probado", E03)],
            {"decision_sec_estado": "Ejecutado",
             "residual": {"P": 1, "I": 3,
                          "razon_P": "Causa eliminada y probada sin WAF (A8 mitigado): P=1.",
                          "razon_I": "Sin cambio."},
             "revision": "Repetir A8 sin WAF tras cambios en la configuración CORS",
             "pendiente": "Hacer de la variante la imagen por defecto"}),
}

reg = json.load(open(SRC, encoding="utf-8"))
nuevo = copy.deepcopy(reg)
nuevo["version"] = f"{reg.get('version', 'v2')}+hito-a"
nuevo["metodo"]["configuracion_hito_a"] = ("Variante corregida (juice-corregida:local, parches 02, 05-08 y v2 01/03/04/09) + WAF + RASP + SIEM "
                                           "(deploy/hardened/docker-compose.corregido.yml). Delta aplicado por construir_riesgos_hito_a.py.")
cambios = []
for r in nuevo["riesgos"]:
    if r["id"] not in DELTA:
        continue
    prefijo, controles, campos = DELTA[r["id"]]
    antes = [c for c in r["controles"] if c["control"].startswith(prefijo)]
    if len(antes) != 1:
        sys.exit(f"{r['id']}: se esperaba 1 control que empiece por '{prefijo}', hay {len(antes)}")
    i = r["controles"].index(antes[0])
    r["controles"][i:i + 1] = controles
    res_antes = (r["residual"]["P"], r["residual"]["I"])
    r.update(campos)
    cambios.append((r["id"], res_antes, (r["residual"]["P"], r["residual"]["I"])))
# Solo texto (sin cambio de valor): el pendiente de R23 citaba el parche 08 como no aplicado.
r23 = next(r for r in nuevo["riesgos"] if r["id"] == "R23")
r23["pendiente"] = ("Re-evaluar con el equipo las vías restantes de extracción (BOLA en Addresses/Cards/Feedbacks, XXE R10) "
                    "tras eliminar la SQLi y el BOLA de cestas; póliza o cláusulas si hubiera datos reales")
json.dump(nuevo, open(DST, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
for rid, a, b in cambios:
    print(f"{rid}: residual P×I {a[0]}×{a[1]} -> {b[0]}×{b[1]}")
print("OK", DST)
