"""Registro de riesgos del CIERRE TÉCNICO (2026-11-23): delta explícito sobre el registro vigente de la Fase 6.

Uso: python -I construir_riesgos_cierre_tecnico.py <raíz del repositorio>
Entrada: docs/fase-6/datos/riesgos-vigente.json (cierre Fase 6, 21-nov). Salida: docs/fase-6/datos/riesgos-cierre-tecnico.json.
Configuración evaluada: artefacto de evidence/cierre-tecnico-2026-11-23/06-regresion/artefacto-final (variante
corregida-cierre-tecnico, parches 01-13) en el stack local vigente. Solo cambia un residual cuando hay un control
'verificado' + 'probado' con evidencia de este cierre; la detección y los controles inspeccionados no reducen.
"""
import copy
import json
import os
import sys

ROOT = sys.argv[1] if len(sys.argv) > 1 else "."
SRC = os.path.join(ROOT, "docs", "fase-6", "datos", "riesgos-vigente.json")
DST = os.path.join(ROOT, "docs", "fase-6", "datos", "riesgos-cierre-tecnico.json")
EV = "evidence/cierre-tecnico-2026-11-23"


def c(nombre, tipo, estado, verif, evidencia):
    return {"control": nombre, "tipo": tipo, "estado": estado, "verificacion": verif, "evidencia": evidencia}


DELTA = {
    "R04": ([c("Parche 11: express-jwt 8.5.1 + jsonwebtoken 9.0.3 + jws 4.0.1 con RS256 fijo; alg=none y confusión HS256 con la clave pública → 401; token legítimo → 200",
               "eliminacion", "verificado", "probado", f"{EV}/04-despues-parches/jwt-algoritmos.md")],
            {"decision": "Eliminar", "estado_tratamiento": "Ejecutado", "decision_sec": "", "decision_sec_estado": "",
             "residual": {"P": 1, "I": 5, "razon_P": "Bibliotecas actualizadas y algoritmo fijado; los dos ataques de algoritmo probados se rechazan (401): causa eliminada.",
                          "razon_I": "Si se comprometiera la clave de firma, la consecuencia sería la misma; la corrección no reduce el impacto."},
             "revision": "En cada construcción: puerta de release (Trivy) sin CVE de jsonwebtoken/jws",
             "pendiente": "Ninguno en el código; vigilar nuevas versiones con la puerta de release"}),
    "R08": ([c("Parche 12: reseñas y pedidos consultados por campo (sin $where), id sin operadores, sin actualización masiva; T1-T3 protegidos incluso con el modo seguro desactivado (la imagen oficial sí es vulnerable)",
               "eliminacion", "verificado", "probado", f"{EV}/05-sin-modo-seguro/corregida/resultados.md")],
            {"estado_tratamiento": "Ejecutado",
             "residual": {"P": 1, "I": 4, "razon_P": "Las tres vías probadas (lectura de reseñas, pedidos, actualización masiva) quedan cerradas en el código y no dependen de la detección de Docker.",
                          "razon_I": "Sin cambio."},
             "pendiente": "marsdb sigue sin versión corregida (ver R20)"}),
    "R10": ([c("Parche 12: parser XML sin NOENT ni DTDLOAD y sin proveedores de archivos; con el modo seguro desactivado la imagen oficial resuelve /etc/hostname y la corregida no",
               "eliminacion", "verificado", "probado", f"{EV}/05-sin-modo-seguro/xxe-dirigida.md")],
            {"estado_tratamiento": "Ejecutado",
             "residual": {"P": 1, "I": 5, "razon_P": "La entidad externa ya no se resuelve (probado con el reto habilitado): causa eliminada.",
                          "razon_I": "Sin cambio."},
             "pendiente": "Ninguno en el código"}),
    "R11": ([c("Parche 12: la URL de imagen se valida (http/https, resolución DNS solo a IP públicas, sin redirecciones); T5: la app ya no pide la URL interna (0 peticiones en el log del WAF)",
               "preventivo", "verificado", "probado", f"{EV}/06-regresion/artefacto-final/sin-waf/pruebas/resultados.md")],
            {"estado_tratamiento": "Ejecutado",
             "residual": {"P": 2, "I": 3, "razon_P": "Una capa preventiva probada: P-2. No baja a 1: queda la ventana de rebinding DNS entre la validación y la descarga, y la red de la app no restringe el egreso.",
                          "razon_I": "Sin cambio."},
             "pendiente": "Restringir el egreso de la app (red interna sin salida) o fijar la IP validada en la descarga"}),
    "R13": ([c("Parche 12: búsqueda sin bypassSecurityTrustHtml (Angular sanea el término) y sanitize-html 2.18.2", "eliminacion", "verificado", "inspeccionado", "app-hardened/patches/v2/correcciones-cierre-tecnico.patch")],
            {"pendiente": "Prueba en navegador de XSS DOM y almacenado por cada campo mostrado a otros usuarios"}),
    "R18": ([c("Parche 12: b2bOrder ya no evalúa las líneas de pedido como código (vm/notevil); el reto RCE queda sin vía de ejecución", "eliminacion", "verificado", "inspeccionado", "app-hardened/patches/v2/correcciones-cierre-tecnico.patch")],
            {}),
    "R20": ([c("Parches 11 y base distroless actualizada: Trivy CRITICAL 11→1 y HIGH 33→2 sobre la imagen en ejecución (misma base de datos de vulnerabilidades); el CRITICAL restante (marsdb) no tiene versión corregida",
               "eliminacion", "verificado", "probado", f"{EV}/08-pipeline-release/puerta-release.md"),
             c("Puerta de release (scripts/pipeline-release.sh + security/release/politica-release.json): bloquea CRITICAL/HIGH sin excepción vigente; prueba negativa con la imagen oficial: BLOQUEADA (41 incumplimientos)",
               "preventivo", "verificado", "probado", f"{EV}/08-pipeline-release/prueba-negativa-imagen-oficial/puerta-release.md")],
            {"decision": "Eliminar", "estado_tratamiento": "Ejecutado parcialmente", "decision_sec": "Aceptar", "decision_sec_estado": "Aceptado temporalmente",
             "aceptacion": {"quien": "Líder del proyecto (rol de dueño del riesgo; el equipo asigna la persona)",
                            "motivo": "marsdb 0.6.11 (GHSA-5mrr-rgp6-x4gr) no tiene versión corregida; sustituirlo exige reescribir reseñas y pedidos. Las consultas $where se eliminaron del código.",
                            "condiciones": "Solo con la puerta de release vigente; excepción registrada en security/release/politica-release.json; sin datos reales.",
                            "vigencia": "Hasta 2026-12-31 (vence la excepción de la política)."},
             "residual": {"P": 2, "I": 5, "razon_P": "Queda un CRITICAL sin corrección y su vía conocida ($where) está eliminada; la puerta impide introducir nuevos CRITICAL/HIGH sin excepción: P-2.",
                          "razon_I": "Sin cambio."},
             "revision": "En cada construcción (puerta de release) y al vencer la excepción (2026-12-31)",
             "pendiente": "Sustituir marsdb por un almacén mantenido (o por la BD relacional del parche 13)"}),
    "R23": ([c("Parche 12: XXE, NoSQL y SSRF cerrados en el código (probados), además de SQLi y BOLA", "eliminacion", "verificado", "probado", f"{EV}/05-sin-modo-seguro/corregida/resultados.md")],
            {"residual": {"P": 2, "I": 5, "razon_P": "Las vías de extracción probadas (SQLi, BOLA en 5 objetos, NoSQL, XXE, SSRF) están cerradas en el código: P-1 adicional. No llega a 1: quedan objetos de la API sin auditar y la dependencia marsdb.",
                          "razon_I": "La consecuencia legal y reputacional no cambia; la transferencia solo está propuesta."},
             "pendiente": "Auditar el resto de objetos de la API; póliza o cláusulas si hubiera datos reales"}),
}

reg = json.load(open(SRC, encoding="utf-8"))
nuevo = copy.deepcopy(reg)
nuevo["version"] = reg.get("version", "") + "+cierre-tecnico"
nuevo["metodo"]["configuracion_cierre_tecnico"] = (
    "Variante corregida-cierre-tecnico (parches 01-13, dependencias actualizadas, base distroless nueva) en el stack local vigente "
    "(make ops-corregido-up) con WAF, RASP, SIEM y notificación local. Delta: docs/fase-6/datos/construir_riesgos_cierre_tecnico.py.")
for r in nuevo["riesgos"]:
    if r["id"] in DELTA:
        controles, campos = DELTA[r["id"]]
        r["controles"].extend(controles)
        antes = (r["residual"]["P"], r["residual"]["I"])
        r.update(campos)
        if r.get("decision") != "Aceptar" and r.get("decision_sec") != "Aceptar":
            r.pop("aceptacion", None)
        print(f"{r['id']}: {antes[0]}×{antes[1]} -> {r['residual']['P']}×{r['residual']['I']} (+{len(controles)} controles)")
json.dump(nuevo, open(DST, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("OK", DST)
