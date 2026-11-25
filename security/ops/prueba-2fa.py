"""Prueba funcional y de seguridad de la 2FA (TOTP) de Juice Shop sobre una instancia PROPIA.

Uso: python -I prueba-2fa.py <url-base> <salida.md> [archivo usuario:contraseña de la puerta /__acceso]
Requiere pyotp (versión fijada por quien ejecuta). Solo 127.0.0.1/localhost o el host exacto en HOST_CLOUD_AUTORIZADO.
Cuenta sintética creada en la prueba; nunca se escriben tokens ni el secreto TOTP en la salida.
"""
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.request
from urllib.parse import urlparse

import pyotp

B, SALIDA = sys.argv[1].rstrip("/"), sys.argv[2]
CRED = sys.argv[3] if len(sys.argv) > 3 else None
host = urlparse(B).hostname
if host not in ("127.0.0.1", "localhost") and host != os.environ.get("HOST_CLOUD_AUTORIZADO"):
    raise SystemExit(f"FUERA DE ALCANCE: {host}")

acceso = None
if CRED:
    u, p = open(CRED, encoding="utf-8").read().strip().split(":", 1)
    r = urllib.request.Request(B + "/__acceso", headers={"Authorization": "Basic " + base64.b64encode(f"{u}:{p}".encode()).decode()})
    with urllib.request.urlopen(r) as resp:
        acceso = resp.headers.get("Set-Cookie", "").split("lab_acceso=")[1].split(";")[0]


def api(ruta, metodo="GET", cuerpo=None, token=None):
    h = {"Content-Type": "application/json"}
    cookies = []
    if acceso:
        cookies.append(f"lab_acceso={acceso}")
    if token:
        h["Authorization"] = f"Bearer {token}"
        cookies.append(f"token={token}")
    if cookies:
        h["Cookie"] = "; ".join(cookies)
    req = urllib.request.Request(B + ruta, method=metodo, headers=h, data=json.dumps(cuerpo).encode() if cuerpo is not None else None)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            t = resp.read().decode() or "{}"
            return resp.status, json.loads(t) if t.strip().startswith("{") else {}
    except urllib.error.HTTPError as e:
        t = e.read().decode() or "{}"
        try:
            return e.code, json.loads(t)
        except ValueError:
            return e.code, {}


filas = []


def fila(prueba, esperado, obtenido, ok):
    filas.append((prueba, esperado, obtenido, "OK" if ok else "**FALLO**"))


ts = int(time.time())
EM, PW = f"tfa_{ts}@juice-sh.op", "Passw0rd!123"
s, _ = api("/api/Users", "POST", {"email": EM, "password": PW, "passwordRepeat": PW, "securityQuestion": {"id": 1}, "securityAnswer": "x"})
fila("Registro de cuenta sintética", "201", s, s == 201)
s, j = api("/rest/user/login", "POST", {"email": EM, "password": PW})
tok = j.get("authentication", {}).get("token")
fila("Login sin 2FA (solo contraseña)", "200 + token", f"{s} + {'token' if tok else 'sin token'}", s == 200 and bool(tok))
s, j = api("/rest/2fa/status", token=tok)
secreto, setup_tok = j.get("secret"), j.get("setupToken")
fila("Estado 2FA antes de activarla", "setup=false + secreto", f"{s} setup={j.get('setup')}", s == 200 and j.get("setup") is False and bool(secreto))
s, _ = api("/rest/2fa/status")
fila("Estado 2FA sin sesión", "401", s, s == 401)
totp = pyotp.TOTP(secreto)
malo = f"{(int(totp.now()) + 1) % 1000000:06d}"
s, _ = api("/rest/2fa/setup", "POST", {"password": PW, "setupToken": setup_tok, "initialToken": malo}, token=tok)
fila("Activar 2FA con código TOTP erróneo", "401", s, s == 401)
s, _ = api("/rest/2fa/setup", "POST", {"password": "incorrecta", "setupToken": setup_tok, "initialToken": totp.now()}, token=tok)
fila("Activar 2FA con contraseña errónea", "401", s, s == 401)
s, _ = api("/rest/2fa/setup", "POST", {"password": PW, "setupToken": setup_tok, "initialToken": totp.now()}, token=tok)
fila("Activar 2FA con contraseña y código correctos", "200", s, s == 200)
s, j = api("/rest/user/login", "POST", {"email": EM, "password": PW})
tmp = (j.get("data") or {}).get("tmpToken")
fila("Login con 2FA activa y solo la contraseña", "401 totp_token_required, sin token de sesión",
     f"{s} {j.get('status')}, {'token' if j.get('authentication') else 'sin token'}",
     s == 401 and j.get("status") == "totp_token_required" and not j.get("authentication") and bool(tmp))
s, j = api("/rest/2fa/verify", "POST", {"tmpToken": tmp, "totpToken": malo})
fila("Segundo factor con código erróneo", "401", s, s == 401 and not j.get("authentication"))
def b64url(d):
    return base64.urlsafe_b64encode(json.dumps(d, separators=(",", ":")).encode()).decode().rstrip("=")


# tmpToken forjado SIN firma (alg none) para el usuario 1: se arma aquí para no versionar nada con forma de JWT
forjado = b64url({"alg": "none"}) + "." + b64url({"userId": 1, "type": "password_valid_needs_second_factor_token"}) + "."
s, j = api("/rest/2fa/verify", "POST", {"tmpToken": forjado, "totpToken": totp.now()})
fila("Segundo factor con tmpToken forjado (alg none, usuario 1)", "401", s, s == 401 and not j.get("authentication"))
s, j = api("/rest/2fa/verify", "POST", {"tmpToken": tmp, "totpToken": totp.now()})
tok2 = (j.get("authentication") or {}).get("token")
fila("Segundo factor con código correcto", "200 + token", f"{s} + {'token' if tok2 else 'sin token'}", s == 200 and bool(tok2))
s, _ = api("/rest/2fa/disable", "POST", {"password": "incorrecta"}, token=tok2)
fila("Desactivar 2FA con contraseña errónea", "401", s, s == 401)
s, _ = api("/rest/2fa/disable", "POST", {"password": PW}, token=tok2)
obs = s == 200
fila("Desactivar 2FA con la contraseña y SIN segundo factor (diseño de Juice Shop)", "observación", s, True)

ok = sum(1 for f in filas if f[3] == "OK")
with open(SALIDA, "w", encoding="utf-8") as f:
    f.write(f"# Prueba de 2FA (TOTP) — {time.strftime('%Y-%m-%dT%H:%M:%S%z')}\n\nObjetivo: `{B}` · pyotp · cuenta sintética `{EM}` "
            "(tokens y secreto no registrados)\n\n| Prueba | Esperado | Obtenido | Resultado |\n|---|---|---|---|\n")
    for x in filas:
        f.write(f"| {x[0]} | {x[1]} | {x[2]} | {x[3]} |\n")
    f.write(f"\n**Resultado: {ok} OK · {len(filas) - ok} fallos.**\n")
    if obs:
        f.write("\n**Observación (debilidad de diseño, no corregida):** la 2FA se puede DESACTIVAR con una sesión válida y la "
                "contraseña, sin pedir el segundo factor. Quien robe una sesión y conozca la contraseña puede retirarla.\n")
print(f"2FA: {ok} OK · {len(filas) - ok} fallos · desactivar sin segundo factor: {'sí' if obs else 'no'}")
