# Prueba de 2FA (TOTP) — 2026-11-25T08:57:11+0000

Objetivo: `https://juice-lab-masi-staging.onrender.com` · pyotp · cuenta sintética `tfa_1795597025@juice-sh.op` (tokens y secreto no registrados)

| Prueba | Esperado | Obtenido | Resultado |
|---|---|---|---|
| Registro de cuenta sintética | 201 | 201 | OK |
| Login sin 2FA (solo contraseña) | 200 + token | 200 + token | OK |
| Estado 2FA antes de activarla | setup=false + secreto | 200 setup=False | OK |
| Estado 2FA sin sesión | 401 | 401 | OK |
| Activar 2FA con código TOTP erróneo | 401 | 401 | OK |
| Activar 2FA con contraseña errónea | 401 | 401 | OK |
| Activar 2FA con contraseña y código correctos | 200 | 200 | OK |
| Login con 2FA activa y solo la contraseña | 401 totp_token_required, sin token de sesión | 401 totp_token_required, sin token | OK |
| Segundo factor con código erróneo | 401 | 401 | OK |
| Segundo factor con tmpToken forjado (alg none, usuario 1) | 401 | 401 | OK |
| Segundo factor con código correcto | 200 + token | 200 + token | OK |
| Desactivar 2FA con contraseña errónea | 401 | 401 | OK |
| Desactivar 2FA con la contraseña y SIN segundo factor (diseño de Juice Shop) | observación | 200 | OK |

**Resultado: 13 OK · 0 fallos.**

**Observación (debilidad de diseño, no corregida):** la 2FA se puede DESACTIVAR con una sesión válida y la contraseña, sin pedir el segundo factor. Quien robe una sesión y conozca la contraseña puede retirarla.
