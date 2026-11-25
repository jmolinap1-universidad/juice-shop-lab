"""Cierre de brechas (2026-11-24): añade a trazabilidad.json la infraestructura REAL de Render + PostgreSQL.

Uso: python -I actualizar_trazabilidad_cloud.py <docs/auditoria-final-2026-11-20>
- amenazas_cloud: amenazas STRIDE nuevas del despliegue (elemento del DFD cloud), con DREAD propio (orden D, R, E, A, Di),
  riesgo del registro al que se vinculan, control y evidencia. El DREAD es valoración del equipo con la misma escala 1-10.
- escenarios: dos escenarios nuevos con la evidencia de A1-A12 (imagen cloud final en local y despliegue real en Render).
- capa_6_nota y capa_5_nota: la capa física y el perímetro cloud ahora existen en un proveedor real.
Idempotente (reemplaza por clave).
"""
import json
import os
import sys

BASE = sys.argv[1] if len(sys.argv) > 1 else "."
RUTA = os.path.join(BASE, "datos", "trazabilidad.json")
t = json.load(open(RUTA, encoding="utf-8"))
EV = "evidence/cierre-brechas-2026-11-24"

t["amenazas_cloud"] = [
    {"id": "TC01", "elemento": "Borde de Render → puerta /__acceso", "stride": "S, E", "amenaza": "Acceso no autorizado a la demostración pública (omisión de la puerta de acceso)",
     "dread": [8, 6, 5, 9, 8], "riesgo": "R21", "control": "Puerta propia; un 401 no entrega cookie; cookie de 256 bits Secure/HttpOnly/SameSite",
     "evidencia": f"{EV}/10-validacion-render/baterias/puerta-acceso.md"},
    {"id": "TC02", "elemento": "Borde de Render → login y puerta", "stride": "S, D", "amenaza": "Fuerza bruta evadiendo el límite con X-Forwarded-For falsificado",
     "dread": [6, 8, 7, 6, 7], "riesgo": "R16", "control": "IP real = última dirección de X-Forwarded-For (sin recursión); 429 al 5.º intento",
     "evidencia": f"{EV}/10-validacion-render/baterias/puerta-acceso.md"},
    {"id": "TC03", "elemento": "Servicio web → PostgreSQL administrado", "stride": "I, T", "amenaza": "BD administrada expuesta a Internet o con credenciales en el repositorio",
     "dread": [9, 5, 4, 9, 6], "riesgo": "R21", "control": "ipAllowList vacía; DATABASE_URL por referencia del Blueprint; TLS obligatorio",
     "evidencia": f"{EV}/05-iac-render/validacion.md"},
    {"id": "TC04", "elemento": "Panel de Render / repositorio", "stride": "I, S", "amenaza": "Secretos de la nube expuestos (clave JWT, usuarios de la puerta, API key)",
     "dread": [9, 4, 5, 9, 6], "riesgo": "R03", "control": "Clave JWT generada por el contenedor; secretos sync:false; API key de solo lectura fuera de git; Gitleaks en CI",
     "evidencia": "evidence/cierre-tecnico-2026-11-23/13-cloud/arranque-casos.md"},
    {"id": "TC05", "elemento": "Contenedor → logs de Render", "stride": "I", "amenaza": "Tokens, cookies o contraseñas en los logs de la plataforma o del SIEM",
     "dread": [7, 6, 4, 8, 5], "riesgo": "R23", "control": "Auditoría del WAF sin cabeceras ni cuerpos (A,F,H,Z); redacción en el colector; 0 secretos en Loki",
     "evidencia": f"{EV}/06-siem-render/extremo-a-extremo.md"},
    {"id": "TC06", "elemento": "Imagen del contenedor cloud", "stride": "T, E, D", "amenaza": "Paquetes del sistema vulnerables en la imagen del WAF (cadena de suministro)",
     "dread": [7, 4, 4, 9, 9], "riesgo": "R20", "control": "Base Alpine de la misma versión del WAF; puerta de release APTA (0 HIGH) en local y en CI",
     "evidencia": f"{EV}/08-puerta-release-local/cloud-alpine/puerta-release.md"},
    {"id": "TC07", "elemento": "Blueprint render.yaml", "stride": "T", "amenaza": "Configuración insegura del Blueprint (plan de pago, BD abierta, despliegue automático, rama equivocada)",
     "dread": [6, 5, 4, 8, 6], "riesgo": "R21", "control": "validar-render.py (esquema oficial + política) en CI; prueba negativa",
     "evidencia": f"{EV}/05-iac-render/prueba-negativa.md"},
    {"id": "TC08", "elemento": "Plataforma (plan free)", "stride": "D", "amenaza": "Indisponibilidad: suspensión por inactividad, vencimiento de la BD free (30 días), límite de memoria",
     "dread": [3, 9, 8, 9, 9], "riesgo": "R21", "control": "Supervisión del arranque (el contenedor se detiene si la app cae); memoria medida 132-204 MiB de 512; procedimiento de reactivación documentado",
     "evidencia": f"{EV}/09-validacion-imagen-alpine-local/recursos.txt"},
    {"id": "TC09", "elemento": "Contenedor → SIEM", "stride": "R", "amenaza": "Pérdida de trazabilidad de lo ocurrido en la nube (logs 7 días en Render, sin centralizar)",
     "dread": [5, 6, 5, 7, 6], "riesgo": "R19", "control": "Colector automático y autenticado (API de Render) → Loki con entorno=cloud; latencia medida 48 s; 6 alertas propias de la nube (4 disparadas extremo a extremo, ~1 min) y alerta de salud del colector",
     "evidencia": f"{EV}/13-alertas-cloud/LEAME.md"},
    {"id": "TC10", "elemento": "Cuenta de Render (plano de control)", "stride": "S, T, E", "amenaza": "Compromiso de la cuenta del equipo en Render o GitHub",
     "dread": [10, 3, 4, 10, 5], "riesgo": "R21", "control": "Inicio de sesión con GitHub; API key con permiso mínimo. MFA SIN VERIFICAR (pendiente del equipo)",
     "evidencia": f"{EV}/06-siem-render/api-key-render.md"},
]

esc = [e for e in t["escenarios"] if e["clave"] not in ("cloud_local", "nube")]
esc += [
    {"clave": "cloud_local", "titulo": "Imagen cloud final (local)", "carpeta": f"{EV}/09-validacion-imagen-alpine-local/baterias/ataques",
     "descripcion": "imagen que se despliega en Render (Alpine, parches 01-14, WAF + RASP + puerta) con 0,1 vCPU, 512 MB y PostgreSQL 17, en local."},
    {"clave": "nube", "titulo": "Render (despliegue real)", "carpeta": f"{EV}/10-validacion-render/baterias/ataques",
     "descripcion": "https://juice-lab-masi-staging.onrender.com, host autorizado por el usuario; mismo arnés a través de la puerta de acceso."},
]
t["escenarios"] = esc
t["capa_6_nota"] = ("El laboratorio local corre en una estación personal (HW-01) sin datos reales. El despliegue real (Render, región "
                    "virginia) delega la seguridad física en el centro de datos del proveedor: responsabilidad compartida, no verificable "
                    "por el equipo (sin contrato ni SLA revisado). El diseño AWS de la Fase 2 sigue siendo solo diseño.")
t["capa_5_nota"] = ("Perímetro cloud REAL: borde de Render (Cloudflare + balanceador, TLS 1.2/1.3 medido, DDoS de la plataforma) y la "
                    "puerta propia en nginx (autenticación previa, límite de intentos, WAF). Sin CDN con caché ni WAF gestionado propios "
                    "(requieren dominio): ver docs/cierre-tecnico/REQUISITOS_CLOUD_DISENO_VS_IMPLEMENTADO.md.")
json.dump(t, open(RUTA, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"trazabilidad: {len(t['amenazas_cloud'])} amenazas cloud, {len(t['escenarios'])} escenarios")
