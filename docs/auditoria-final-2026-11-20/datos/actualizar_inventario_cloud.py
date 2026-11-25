"""Cierre de brechas (2026-11-24): incorpora al inventario la infraestructura REAL de Render y PostgreSQL.

Uso: python -I actualizar_inventario_cloud.py <docs/auditoria-final-2026-11-20>
Idempotente: inserta o reemplaza por ID y actualiza los activos cuyo estado cambió. Después se ejecuta generar_inventario.py.
Fuente de cada dato: docs/cierre-tecnico/DESPLIEGUE_CLOUD_RENDER.md y evidence/cierre-tecnico-2026-11-23/13-cloud/,
evidence/cierre-brechas-2026-11-24/.
"""
import json
import os
import sys

BASE = sys.argv[1] if len(sys.argv) > 1 else "."
RUTA = os.path.join(BASE, "datos", "inventario.json")
d = json.load(open(RUTA, encoding="utf-8"))

NUEVOS = [
    {"id": "SRV-06", "f1": "nuevo", "nombre": "Render: servicio web juice-lab-masi-staging (contenedor WAF + app corregida + RASP)",
     "tipo": "Servicios", "ubicacion": "Cloud", "estado": "Implementado",
     "proceso": "Venta en línea (demostración con acceso restringido)",
     "descripcion": "Plan free (512 MB, 0,1 vCPU, región virginia), construido por Render desde main con deploy/cloud/Dockerfile; fuente verificada contra el diff auditado; puerta /__acceso; https://juice-lab-masi-staging.onrender.com.",
     "C": "A", "I": "A", "D": "M",
     "just": "Procesa credenciales y datos (sintéticos) de las cuentas y aloja la defensa del perímetro (C, I altas); es una demostración sin compromiso de disponibilidad y se suspende sin tráfico (D media).",
     "prop": "PROP", "cust": "OPS",
     "acceso": "Público solo hasta la puerta de acceso; dentro, usuarios del htpasswd (hoy: verificador); administración por la cuenta de Render del equipo",
     "rel": "Ejecuta SW-11 con SW-08 y SW-09; usa SRV-07; detrás de SRV-08; gobernado por SRV-09"},
    {"id": "SRV-07", "f1": "A13 (cloud)", "nombre": "Render PostgreSQL 17 (juice-lab-db, plan free)",
     "tipo": "Servicios", "ubicacion": "Cloud", "estado": "Implementado",
     "proceso": "Persistencia de datos de la tienda",
     "descripcion": "BD administrada del parche 13 (DATABASE_URL por referencia del Blueprint); ipAllowList vacía (sin acceso externo); TLS en la red privada sin verificar el certificado; cifrado en reposo AES-256 según Render; vence el 2026-12-24.",
     "C": "A", "I": "A", "D": "M",
     "just": "Contiene INF-01 a INF-09 de la demostración (C, I altas); Juice Shop la resiembra al arrancar y es una demostración (D media).",
     "prop": "PROP", "cust": "OPS",
     "acceso": "Solo el servicio SRV-06 por la red privada de Render; panel de Render (cuenta del equipo)",
     "rel": "Almacena INF-01 a INF-09 para SRV-06; sustituye a SW-04 en la nube"},
    {"id": "SRV-08", "f1": "nuevo", "nombre": "Borde de Render (Cloudflare + balanceador con TLS)",
     "tipo": "Servicios", "ubicacion": "Cloud", "estado": "Implementado",
     "proceso": "Terminación TLS y enrutamiento",
     "descripcion": "Certificado de Google Trust Services (*.onrender.com); TLS 1.2 y 1.3 aceptadas, 1.0/1.1 rechazadas (medido); HTTP→HTTPS 301; protección DDoS de la plataforma; reescribe la cabecera Server (cloudflare). Lo gestiona Render (responsabilidad compartida).",
     "C": "M", "I": "A", "D": "A",
     "just": "Todo el tráfico pasa por él; un fallo o una configuración insegura detiene o expone el servicio (I, D altas); no almacena datos (C media).",
     "prop": "PROP", "cust": "OPS",
     "acceso": "Render (proveedor); el equipo solo configura dominios en el panel",
     "rel": "Delante de SRV-06"},
    {"id": "SRV-09", "f1": "nuevo", "nombre": "Cuenta y workspace de Render, Blueprint render.yaml",
     "tipo": "Servicios", "ubicacion": "Cloud", "estado": "Implementado",
     "proceso": "Gestión de la infraestructura cloud (IaC)",
     "descripcion": "Workspace del equipo con el Blueprint juice-lab-masi-staging (sincronizado desde main), variables de entorno y secretos (sync:false), despliegue manual; validado con security/iac/validar-render.py (15/15).",
     "C": "A", "I": "A", "D": "M",
     "just": "Controla el despliegue, los secretos y la BD: comprometerla equivale a controlar el servicio (C, I altas).",
     "prop": "PROP", "cust": "OPS",
     "acceso": "Integrante propietario de la cuenta (inicio de sesión con GitHub); API key de solo lectura de Monitoring",
     "rel": "Gobierna SRV-06 y SRV-07; versionado en SRV-02"},
    {"id": "INF-16", "f1": "nuevo", "nombre": "Secretos de la nube (usuarios de la puerta, clave JWT efímera, API key de Render)",
     "tipo": "Información", "ubicacion": "Cloud", "estado": "Implementado",
     "proceso": "Control de acceso a la demostración y a la API",
     "descripcion": "BASIC_AUTH_HTPASSWD (hashes bcrypt, secreto de Render); clave JWT generada en el contenedor en cada arranque (D-21); API key de Render de solo lectura (Monitoring) en un archivo local ignorado por git, montada como secreto de Docker.",
     "C": "A", "I": "A", "D": "M",
     "just": "Su divulgación abre la puerta o la API de logs (C alta); su alteración permite suplantar o bloquear (I alta).",
     "prop": "PROP", "cust": "OPS",
     "acceso": "Panel de Render (equipo); contenedor SRV-06; host local del laboratorio (API key)",
     "rel": "Protege SRV-06 y SRV-09; usada por SW-12"},
    {"id": "INF-17", "f1": "nuevo", "nombre": "Registros de la nube (logs de Render y eventos con entorno=cloud en Loki)",
     "tipo": "Información", "ubicacion": "Cloud", "estado": "Implementado",
     "proceso": "Monitoreo y respuesta a incidentes",
     "descripcion": "Salida del contenedor en Render (auditoría del WAF sin cabeceras ni cuerpos, accesos, app + RASP); retención de 7 días en Render; copia en el Loki local con entorno=cloud mediante SW-12.",
     "C": "M", "I": "A", "D": "M",
     "just": "Son la prueba forense de lo ocurrido en la nube (I alta); se redactan antes de guardarse (C media).",
     "prop": "PROP", "cust": "SEC",
     "acceso": "Panel de Render; API de logs con la clave de solo lectura; Grafana local (127.0.0.1)",
     "rel": "Producidos por SRV-06; centralizados por SW-12 en SW-10"},
    {"id": "SW-12", "f1": "nuevo", "nombre": "Colector de eventos de Render (colector-render)",
     "tipo": "Software", "ubicacion": "Local", "estado": "Implementado",
     "proceso": "Centralización de eventos cloud en el SIEM",
     "descripcion": "deploy/hardened/siem/colector-render.py: consulta GET /v1/logs con Bearer (clave de solo lectura), redacta, conserva un cursor y escribe en Loki por la red interna; sin root, sistema de archivos de solo lectura, sin capacidades.",
     "C": "A", "I": "M", "D": "B",
     "just": "Maneja la API key (C alta); un fallo deja de copiar eventos, pero Render los conserva 7 días (I media, D baja).",
     "prop": "PROP", "cust": "SEC",
     "acceso": "Proceso del contenedor (uid 65534); operadores de Docker en el host",
     "rel": "Usa INF-16; alimenta INF-17 en SW-10"},
]

ACTUALIZAR = {
    "SW-11": {"estado": "Implementado",
              "nombre": "Variante corregida de Juice Shop (parches 01-14)",
              "descripcion": "Variante corregida-cierre-brechas: parches 01-14 verificados contra app-hardened/patches/v2/correcciones-cierre-brechas.patch (22 archivos). Publicada en Render (SRV-06) y en la imagen local juice-corregida-rasp:local."},
    "SRV-02": {"descripcion": "Repositorio jmolinap1-universidad/juice-shop-lab; devsecops.yml (política de informe del laboratorio) y release.yml (política de release: IaC de Render, puerta de la imagen de la app y de la imagen cloud)."},
    "SRV-05": {"estado": "Propuesto, no desplegado",
               "descripcion": "Diseño AWS de la Fase 2 (Terraform, solo plan + Checkov). No desplegado: el despliegue real es Render (SRV-06 a SRV-09), gratuito; AWS exigiría costos."},
    "SW-04": {"descripcion": "SQLite embebida: motor de la instancia vulnerable y del laboratorio local. En la nube la sustituye PostgreSQL (SRV-07) vía DATABASE_URL (parche 13)."},
}

ids = {a["id"]: i for i, a in enumerate(d["activos"])}
for n in NUEVOS:
    if n["id"] in ids:
        d["activos"][ids[n["id"]]] = n
    else:
        d["activos"].append(n)
for i, cambios in ACTUALIZAR.items():
    d["activos"][ids[i]].update(cambios)
d["alcance"] = ("Laboratorio OWASP Juice Shop v20.3.0 (MASI-UMG 2026): instancia vulnerable local (127.0.0.1), entorno endurecido "
                "local (WAF, RASP, SIEM), variante corregida (parches 01-14), repositorio y CI en GitHub, despliegue REAL en Render "
                "(capa gratuita, acceso restringido) y arquitectura AWS solo DISEÑADA. Inventario con criterios de ISO/IEC 27001:2022 "
                "(control 5.9). Actualizado el 2026-11-24 con la infraestructura cloud real.")
json.dump(d, open(RUTA, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"inventario: {len(d['activos'])} activos ({len(NUEVOS)} cloud nuevos/actualizados, {len(ACTUALIZAR)} modificados)")
