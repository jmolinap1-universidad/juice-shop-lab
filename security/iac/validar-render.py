"""Validación de la IaC de Render (render.yaml): esquema JSON oficial + política de seguridad propia.

Uso: python -I validar-render.py <raíz del repo> <esquema render.yaml.json> <salida.md>
Requiere: pyyaml, jsonschema (versiones fijadas en el Makefile / CI). Devuelve 0 si todo cumple, 1 si algo falla.

Equivale, para Render, a Checkov sobre Terraform (Fase 2): Checkov no tiene reglas para render.yaml, así que las
comprobaciones de seguridad se escriben aquí, una por requisito del proyecto, con su motivo.
"""
import json
import os
import re
import subprocess
import sys

import jsonschema
import yaml

ROOT, ESQUEMA, SALIDA = sys.argv[1:4]
bp = yaml.safe_load(open(os.path.join(ROOT, "render.yaml"), encoding="utf-8"))
esquema = json.load(open(ESQUEMA, encoding="utf-8"))
filas = []


def chk(nombre, ok, detalle="", motivo=""):
    filas.append((nombre, "OK" if ok else "**FALLO**", detalle, motivo))


errores = sorted(jsonschema.Draft202012Validator(esquema).iter_errors(bp), key=lambda e: list(e.path))
chk("Esquema oficial de Render (render.yaml.json)", not errores,
    "; ".join(f"{'/'.join(map(str, e.path))}: {e.message[:90]}" for e in errores[:3]) or "sin errores", "Sintaxis y campos válidos para la plataforma")

webs = [s for s in bp.get("services", []) if s.get("type") == "web"]
dbs = bp.get("databases", [])
chk("Un único servicio web", len(webs) == 1, f"{len(webs)}", "Plan gratuito: un servicio")
w = webs[0] if webs else {}
chk("Plan gratuito (sin costo)", w.get("plan") == "free" and all(d.get("plan") == "free" for d in dbs),
    f"web={w.get('plan')} bd={[d.get('plan') for d in dbs]}", "Regla del proyecto: entorno gratuito")
chk("Construcción Docker desde el Dockerfile cloud verificado", w.get("runtime") == "docker" and w.get("dockerfilePath") == "./deploy/cloud/Dockerfile"
    and os.path.exists(os.path.join(ROOT, "deploy/cloud/Dockerfile")), w.get("dockerfilePath", ""), "La fuente se comprueba contra el diff auditado al construir")
chk("Despliegue automático desactivado", str(w.get("autoDeployTrigger")) == "off", str(w.get("autoDeployTrigger")), "Cada despliegue es una decisión explícita")
chk("Chequeo de salud real", w.get("healthCheckPath") == "/healthz", w.get("healthCheckPath", ""), "/healthz atraviesa nginx y consulta la app")
rama = w.get("branch", "")
# Sin git en el contenedor, quien ejecuta pasa el resultado de `git ls-remote --heads origin <rama>` en RAMA_REMOTA
try:
    ramas = subprocess.run(["git", "-C", ROOT, "ls-remote", "--heads", "origin", rama], capture_output=True, text=True).stdout if rama else ""
except FileNotFoundError:
    ramas = os.environ.get("RAMA_REMOTA", "")
chk("La rama desplegada existe en el repositorio", bool(ramas.strip()), f"{rama} → {ramas.strip()[:12] or 'no encontrada'}", "Evita desplegar una rama inexistente")

env = w.get("envVars", [])
claves = {e["key"]: e for e in env}
sospechosos = [e["key"] for e in env if "value" in e and re.search(r"(?i)(secret|password|passw|token|private|htpasswd|api[_-]?key)", e["key"])]
chk("Ningún secreto con valor en el archivo", not sospechosos, ", ".join(sospechosos) or "ninguno", "Los secretos van como sync:false (los introduce el equipo)")
chk("Usuarios de la puerta como secreto (sync: false)", claves.get("BASIC_AUTH_HTPASSWD", {}).get("sync") is False, "", "Acceso restringido sin credenciales en el repo")
chk("Clave JWT generada por el contenedor", str(claves.get("JWT_CLAVE_EFIMERA", {}).get("value")) == "1" and "JWT_PRIVATE_KEY_B64" not in claves,
    "", "D-21: nadie manipula la clave de firma")
chk("BD conectada por referencia, no por cadena escrita", "fromDatabase" in claves.get("DATABASE_URL", {}), "", "La cadena con contraseña no está en el repo")
chk("IP real sin recursión (X-Forwarded-For)", claves.get("REAL_IP_HEADER", {}).get("value") == "X-Forwarded-For" and str(claves.get("REAL_IP_RECURSIVE", {}).get("value")) == "off",
    "", "Un X-Forwarded-For falsificado no salta el límite de intentos (probado en la nube)")
for d in dbs:
    chk(f"BD {d.get('name')}: sin acceso externo (ipAllowList vacía)", d.get("ipAllowList") == [], str(d.get("ipAllowList")), "Solo el servicio por la red privada")
    chk(f"BD {d.get('name')}: PostgreSQL 17 (versión probada)", str(d.get("postgresMajorVersion")) == "17", str(d.get("postgresMajorVersion")), "Misma versión que la prueba local del parche 13")
    chk(f"BD {d.get('name')}: misma región que el servicio", d.get("region") == w.get("region"), f"{d.get('region')} / {w.get('region')}", "La red privada de Render es por región")

fallos = sum(1 for f in filas if f[1] != "OK")
with open(SALIDA, "w", encoding="utf-8") as f:
    f.write("# Validación IaC de Render (render.yaml)\n\n")
    f.write(f"Esquema: `{os.path.basename(ESQUEMA)}` (https://render.com/schema/render.yaml.json), jsonschema Draft 2020-12.\n\n")
    f.write("| Comprobación | Resultado | Detalle | Motivo |\n|---|---|---|---|\n")
    for n, r, d, m in filas:
        f.write(f"| {n} | {r} | {d} | {m} |\n")
    f.write(f"\n**Resultado: {len(filas) - fallos} OK · {fallos} fallos.**\n")
print(f"IaC Render: {len(filas) - fallos} OK, {fallos} fallos")
sys.exit(1 if fallos else 0)
