"""Registro de riesgos del CIERRE DE BRECHAS (2026-11-24): delta explícito sobre el registro del cierre técnico.

Uso: python -I construir_riesgos_cierre_brechas.py <raíz del repositorio>
Entrada: docs/fase-6/datos/riesgos-cierre-tecnico.json. Salida: docs/fase-6/datos/riesgos-cierre-brechas.json.
Configuración evaluada: despliegue REAL en Render (imagen cloud Alpine, parches 01-14, WAF + RASP, puerta de acceso,
PostgreSQL free) y stack local vigente. Misma regla: solo baja un residual con un control 'verificado' + 'probado' con
evidencia; la detección y lo inspeccionado no reducen.
"""
import copy
import json
import os
import sys

ROOT = sys.argv[1] if len(sys.argv) > 1 else "."
SRC = os.path.join(ROOT, "docs", "fase-6", "datos", "riesgos-cierre-tecnico.json")
DST = os.path.join(ROOT, "docs", "fase-6", "datos", "riesgos-cierre-brechas.json")
EV = "evidence/cierre-brechas-2026-11-24"
NUBE = f"{EV}/10-validacion-render"


def c(nombre, tipo, estado, verif, evidencia):
    return {"control": nombre, "tipo": tipo, "estado": estado, "verificacion": verif, "evidencia": evidencia}


DELTA = {
    "R21": ([
        c("Despliegue real en Render con puerta de acceso propia: sin cookie → 302, 401 sin cookie, cookie de 256 bits Secure/HttpOnly/SameSite, falsificada → 302; probado en la nube",
          "preventivo", "verificado", "probado", f"{NUBE}/baterias/puerta-acceso.md"),
        c("IaC de Render validada (esquema oficial + política: plan free, BD sin acceso externo, secretos sync:false, despliegue manual, rama existente): 15/15; prueba negativa detecta 4 fallos",
          "preventivo", "verificado", "probado", f"{EV}/05-iac-render/prueba-negativa.md"),
        c("TLS medido en el borde: 1.0/1.1 rechazadas, 1.2 y 1.3 aceptadas (TLS_AES_256_GCM_SHA384), HTTP→HTTPS 301, HSTS",
          "preventivo", "verificado", "probado", f"{NUBE}/tls.md"),
        c("Secretos fuera del repositorio y del panel: clave JWT generada por el contenedor (D-21); usuarios de la puerta como secreto; API key de Render de solo lectura (Monitoring)",
          "preventivo", "verificado", "inspeccionado", f"{EV}/06-siem-render/api-key-render.md"),
        c("Responsabilidad compartida con Render (borde Cloudflare, DDoS, centro de datos, cifrado en reposo declarado AES-256): sin contrato ni SLA revisado",
          "transferencia", "propuesto", "sin_verificar", "docs/cierre-tecnico/REQUISITOS_CLOUD_DISENO_VS_IMPLEMENTADO.md"),
     ],
     {"nombre": "Configuración insegura de la infraestructura cloud desplegada (Render + PostgreSQL)",
      "pi_cualitativa": {"P": 3, "I": 4, "justificacion": "Desplegado en Render (capa gratuita): la mala configuración cloud es frecuente (P3) y expondría datos y la demostración (I4)."},
      "decision": "Mitigar", "estado_tratamiento": "Ejecutado parcialmente", "decision_sec": "Transferir", "decision_sec_estado": "Propuesta",
      "responsable": "Operaciones cloud; Dueño del riesgo: líder del proyecto",
      "revision": "En cada despliegue: validar-render.py, puerta de release en CI y validar-cloud.sh contra el host",
      "pendiente": "MFA de las cuentas de GitHub y Render sin verificar; CDN/WAF gestionado y TLS 1.3 exclusivo requieren dominio propio; BD free vence el 2026-12-24",
      "residual": {"P": 2, "I": 4,
                   "razon_P": "Controles preventivos PROBADOS en la nube (puerta, IaC validada con prueba negativa, TLS medido): P-1. No baja a 1: un solo contenedor, TLS 1.2 aún aceptado, MFA sin verificar y sin CDN/WAF gestionado.",
                   "razon_I": "Sin cambio: con datos sintéticos, una brecha seguiría exponiendo la demostración y la cuenta."},
      "nota": "Hasta el 2026-11-23 el residual 1×4 se apoyaba en que NO había despliegue (evitación). Desde el despliegue en Render se valora con los controles probados en ejecución."}),
    "R20": ([
        c("Imagen cloud con base Alpine de la misma versión del WAF: Trivy CRITICAL 3→1 (marsdb, exceptuada) y HIGH 135→0; puerta de release APTA",
          "eliminacion", "verificado", "probado", f"{EV}/08-puerta-release-local/cloud-alpine/puerta-release.md"),
        c("Política de release en CI (GitHub Actions release.yml): IaC de Render, puerta de la imagen de la app y de la imagen cloud en cada cambio",
          "preventivo", "verificado", "probado", f"{EV}/11-ci-release/resultado-ci.md"),
     ],
     {"pendiente": "Sustituir marsdb antes de que venza su excepción (2026-12-31); revisar el informe informativo de Grype en cada construcción"}),
    "R13": ([
        c("Prueba de XSS en navegador real (Chromium): 6 vectores (DOM, reflejado, 4 almacenados); corregida 0/6 con y sin el modo seguro de Juice Shop; oficial sin modo seguro 5/6; imagen cloud 0/6",
          "eliminacion", "verificado", "probado", f"{EV}/02-xss-navegador/corregida-sms/resultados.md"),
        c("Parche 14: correo, nombre de usuario y última IP saneados siempre en el servidor (V5 y V6 se ejecutaban en la corregida sin modo seguro)",
          "eliminacion", "verificado", "probado", f"{EV}/02-xss-navegador/oficial-sms/resultados.md"),
        c("CSP del WAF (script-src 'self'): bloquea scripts en línea en la nube", "contencion", "verificado", "probado", f"{EV}/02-xss-navegador/cloud/resultados.md"),
     ],
     {"estado_tratamiento": "Ejecutado",
      "residual": {"P": 2, "I": 4,
                   "razon_P": "Los seis sumideros probados en navegador quedan cerrados en el código (eliminación probada): P-1. No baja a 1: el frontend conserva otros bypassSecurityTrustHtml (marcador de retos, captcha) y la CSP mantiene 'unsafe-inline' en estilos.",
                   "razon_I": "Sin cambio: un XSS en el panel de administración seguiría permitiendo actuar como administrador."},
      "pendiente": "Retirar los bypassSecurityTrustHtml restantes del frontend o cubrirlos con pruebas"}),
    "R06": ([
        c("Parche 14: PUT /api/Products/:id exige sesión y rol admin (antes: sin autenticación, cualquiera modificaba el catálogo); probado: 401 sin token",
          "eliminacion", "verificado", "probado", f"{EV}/02-xss-navegador/corregida-sms/resultados.md"),
     ],
     {"pendiente": "Auditar el resto de objetos y funciones de la API (BOLA/BFLA); el PUT de productos se halló en la prueba de XSS, no en la batería BOLA"}),
    "R19": ([
        c("Centralización AUTOMÁTICA y AUTENTICADA de eventos cloud: colector de la API de Render (HTTPS + clave de solo lectura) → Loki con entorno=cloud, redacción y cursor; prueba extremo a extremo con marca",
          "deteccion", "verificado", "probado", f"{EV}/06-siem-render/extremo-a-extremo.md"),
        c("Alertas propias de la nube (6 reglas, entorno=cloud): SQLi bloqueada, credenciales fallidas y límite en la puerta, RASP, arranque fallido y salud del colector; 4 disparadas extremo a extremo contra Render (~1 min) sin disparar reglas locales; reglas locales acotadas a entorno=local",
          "deteccion", "verificado", "probado", f"{EV}/13-alertas-cloud/LEAME.md"),
     ],
     {"estado_tratamiento": "Ejecutado parcialmente",
      "pendiente": "Monitoreo cloud 24/7: el colector depende del equipo local (un servicio permanente tendría costo); las reglas de RASP y de arranque fallido en la nube están cargadas pero no se provocaron",
      "nota": "La detección y las alertas no reducen el residual (regla del registro): R19 se mantiene 2×4."}),
    "R16": ([
        c("Límite de intentos en la nube: 429 al 5.º intento, también con X-Forwarded-For falsificado distinto en cada petición",
          "preventivo", "verificado", "probado", f"{NUBE}/baterias/puerta-acceso.md"),
        c("2FA (TOTP) de Juice Shop probada en local y en Render (13/13): con la 2FA activa la contraseña sola no da sesión (401 totp_token_required); código erróneo y tmpToken forjado (alg none) → 401",
          "preventivo", "verificado", "probado", f"{EV}/12-2fa/render.md"),
     ],
     {"pendiente": "Limitación por cuenta además de por IP (ataques distribuidos no probados); la 2FA es opcional por usuario y se DESACTIVA con la contraseña sin pedir el segundo factor (debilidad de diseño de Juice Shop hallada en la prueba, no corregida: exige cambiar backend y frontend)",
      "nota": "La 2FA no reduce el residual: es opcional y no protege a las cuentas que no la activan, que son todas las sembradas."}),
    "R03": ([
        c("En la nube la clave JWT la genera el contenedor en cada arranque (nadie la copia ni la pega; falla cerrada si no se activa): 5 casos de arranque",
          "preventivo", "verificado", "probado", "evidence/cierre-tecnico-2026-11-23/13-cloud/arranque-casos.md"),
     ], {}),
    "R24": ([
        c("Colector cloud endurecido: sin root (65534), sistema de archivos de solo lectura, sin capacidades, clave como secreto de Docker y redacción antes de Loki (probada con simulador)",
          "preventivo", "verificado", "probado", f"{EV}/06-siem-render/prueba-simulador/salida-colector.txt"),
     ], {}),
}

reg = json.load(open(SRC, encoding="utf-8"))
nuevo = copy.deepcopy(reg)
nuevo["version"] = reg.get("version", "") + "+cierre-brechas"
nuevo["metodo"]["configuracion_cierre_brechas"] = (
    "Despliegue real en Render (imagen cloud Alpine, parches 01-14, WAF + RASP + puerta de acceso, PostgreSQL free) y stack "
    "local vigente. Delta: docs/fase-6/datos/construir_riesgos_cierre_brechas.py.")
for r in nuevo["riesgos"]:
    if r["id"] in DELTA:
        controles, campos = DELTA[r["id"]]
        r["controles"].extend(controles)
        antes = (r["residual"]["P"], r["residual"]["I"])
        r.update(campos)
        if r.get("decision") != "Aceptar" and r.get("decision_sec") != "Aceptar":
            r.pop("aceptacion", None)
        if r["id"] == "R21":
            r["controles"] = [x for x in r["controles"] if not x["control"].startswith("No desplegar sin aprobación")]
        print(f"{r['id']}: {antes[0]}×{antes[1]} -> {r['residual']['P']}×{r['residual']['I']} (+{len(controles)} controles)")
json.dump(nuevo, open(DST, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("OK", DST)
