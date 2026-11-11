"""Extrae de los logs vivos del WAF las líneas de una ventana temporal y redacta credenciales.

Uso: python -I extraer-logs-waf.py <audit.log> <access.log> <desde_epoch> <salida_dir>
- audit.log de ModSecurity (JSON por línea, transaction.time_stamp "Wed Nov 11 05:14:02 2026", UTC)
- access.log JSON del WAF (campo "time" ISO 8601)
Redacta: cabecera Authorization, JWT (eyJ...), campos "token" y "password" de cuerpos JSON.
"""
import json
import os
import re
import sys
from datetime import datetime, timezone

audit, access, desde, out = sys.argv[1], sys.argv[2], float(sys.argv[3]), sys.argv[4]
os.makedirs(out, exist_ok=True)
JWT = re.compile(r"eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+")


def redactar(s):
    s = JWT.sub("[JWT-REDACTADO]", s)
    s = re.sub(r'("[Aa]uthorization"\s*:\s*")[^"]*"', r'\1[REDACTADO]"', s)
    s = re.sub(r'(\\?"(?:password|passwordRepeat|token)\\?"\s*:\s*\\?")[^"\\]*', r"\1[REDACTADO]", s)
    return s


n_a = n_c = 0
with open(audit, encoding="utf-8", errors="replace") as f, open(os.path.join(out, "modsec-audit.redactado.log"), "w", encoding="utf-8") as o:
    for linea in f:
        try:
            t = json.loads(linea)["transaction"]["time_stamp"]
            ts = datetime.strptime(t, "%a %b %d %H:%M:%S %Y").replace(tzinfo=timezone.utc).timestamp()
        except Exception:
            continue
        if ts >= desde:
            o.write(redactar(linea))
            n_a += 1
with open(access, encoding="utf-8", errors="replace") as f, open(os.path.join(out, "waf-access.log"), "w", encoding="utf-8") as o:
    for linea in f:
        try:
            ts = datetime.fromisoformat(json.loads(linea)["time"]).timestamp()
        except Exception:
            continue
        if ts >= desde:
            o.write(redactar(linea))
            n_c += 1
print(f"audit: {n_a} transacciones · access: {n_c} peticiones · desde epoch {desde:.0f}")
