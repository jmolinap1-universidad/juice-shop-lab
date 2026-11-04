# Correcciones de código (white-box) — app-hardened

Diffs unificados sobre el código real de `app/` (Juice Shop v20.3.0), una corrección por vulnerabilidad.
Son la **remediación definitiva** en el código; en el entorno en ejecución de la Fase 6 el riesgo residual se
mide con el **WAF** como control compensatorio (ver `docs/fase-6/`), porque recompilar la aplicación desde
fuente queda fuera del tiempo del laboratorio.

**Estado:** Implementado como diff y **verificado con `git apply --check`** (6 de 7 aplican sin conflicto).

| # | Archivo | Vulnerabilidad | ASVS 5.0.0 | CWE | `git apply` |
|---|---|---|---|---|---|
| 01 | `routes/login.ts` | SQLi en login → consulta parametrizada | V1.2.4 | CWE-89 | OK |
| 02 | `routes/search.ts` | SQLi UNION en búsqueda → parametrizada | V1.2.4 | CWE-89 | OK |
| 03 | `lib/insecurity.ts` | MD5 sin sal → bcrypt (factor 12) | V11.4.2 | CWE-916 | OK |
| 04 | `lib/insecurity.ts` | Clave privada embebida → variable de entorno | V13.3.1 | CWE-798 | Manual* |
| 05 | `routes/userProfile.ts` | `eval()` sobre entrada → se elimina | V1.3.2 | CWE-95 | OK |
| 06 | `server.ts` | Asignación masiva de `role` en registro | V8.2.2 | CWE-915 | OK |
| 07 | `server.ts` | CORS comodín → origen explícito | V3.4.2 | CWE-942 | OK |

\* El patch 04 **no se aplica automáticamente a propósito**: su línea original contiene la clave privada de
prueba, que no se versiona (regla de no manejar secretos). El diff muestra la clave **redactada**; aplicar el
cambio de la línea `const privateKey = …` a mano.

## Aplicación
```bash
cd app
git apply ../app-hardened/patches/01-sqli-login.patch   # idem 02,03,05,06,07
# 04 se aplica manualmente (ver nota)
```

## Vulnerabilidades adicionales (tratadas por configuración, no por estos diffs)
- Listados de directorios (`/ftp`, `/encryptionkeys`, `/support/logs`) y `/metrics`: se bloquean en el WAF
  (nginx `deny` + parche virtual ModSecurity 100002). Corrección en código: retirar los `serve-index` de
  `server.ts` y proteger `/metrics`.
- Cabeceras de seguridad (CSP, HSTS) y rate limiting de login: añadidas en el WAF (`deploy/hardened/waf/`).
- XXE/SSRF (XML upload, imagen por URL): requieren endurecer el parser y una lista blanca de destinos [P].
