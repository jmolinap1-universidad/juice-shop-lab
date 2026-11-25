"""Parche 14 (cierre de brechas, 2026-11-24) sobre la variante corregida (después de aplicar_cierre_tecnico.py).

Uso: python -I aplicar_cierre_brechas.py <directorio con el código exportado>

Hallazgos MEDIDOS con la prueba de XSS en navegador (security/xss/, evidence/cierre-brechas-2026-11-24/02-xss-navegador/),
con el modo seguro de Juice Shop desactivado para medir el código y no la detección de Docker:
  V5  XSS almacenado por el correo de registro: el servidor solo lo saneaba con el modo seguro activo y el panel de
      administración lo pinta con bypassSecurityTrustHtml → se ejecutaba en el navegador del administrador.
  V6  XSS almacenado por la cabecera True-Client-IP (/rest/saveLoginIp): mismo patrón, página «última IP».
  PUT /api/Products/:id sin autenticación (línea comentada en el original): cualquiera modificaba el catálogo
      (comprobado: 200 sin token). Ahora exige sesión y rol de administración (mismo patrón que las quejas del parche 12).
Cada reemplazo es literal y se comprueba (si el texto no aparece exactamente una vez, el script falla).
"""
import os
import sys

SRC = sys.argv[1]


def editar(ruta, cambios):
    p = os.path.join(SRC, ruta)
    texto = open(p, encoding="utf-8").read()
    for viejo, nuevo in cambios:
        n = texto.count(viejo)
        if n != 1:
            raise SystemExit(f"FALLO {ruta}: el texto esperado aparece {n} veces: {viejo[:80]!r}")
        texto = texto.replace(viejo, nuevo)
    open(p, "w", encoding="utf-8", newline="\n").write(texto)
    print(f"ok  {ruta} ({len(cambios)} cambios)")


editar("models/user.ts", [
    ("""        set (username: string) {
          if (utils.isChallengeEnabled(challenges.persistedXssUserChallenge)) {
            username = security.sanitizeLegacy(username)
          } else {
            username = security.sanitizeSecure(username)
          }
          this.setDataValue('username', username)""",
     """        set (username: string) {
          // Parche 14 (XSS almacenado): se sanea siempre, no solo con el modo seguro de Juice Shop
          username = security.sanitizeSecure(username)
          this.setDataValue('username', username)"""),
    ("""        set (email: string) {
          if (utils.isChallengeEnabled(challenges.persistedXssUserChallenge)) {
            challengeUtils.solveIf(challenges.persistedXssUserChallenge, () => {
              return email?.includes('<iframe src="javascript:alert(`xss`)">') ?? false
            })
          } else {
            email = security.sanitizeSecure(email)
          }
          this.setDataValue('email', email)""",
     """        set (email: string) {
          // Parche 14 (XSS almacenado, V5): el panel de administración pinta el correo con bypassSecurityTrustHtml;
          // el servidor lo sanea siempre (antes solo con el modo seguro activo)
          email = security.sanitizeSecure(email)
          this.setDataValue('email', email)"""),
])

editar("routes/saveLoginIp.ts", [
    ("""      if (utils.isChallengeEnabled(challenges.httpHeaderXssChallenge)) {
        challengeUtils.solveIf(challenges.httpHeaderXssChallenge, () => { return lastLoginIp === '<iframe src="javascript:alert(`xss`)">' })
      } else {
        lastLoginIp = security.sanitizeSecure(lastLoginIp ?? '')
      }""",
     """      // Parche 14 (XSS almacenado, V6): la página «última IP» la pinta con bypassSecurityTrustHtml; se sanea siempre
      if (lastLoginIp !== undefined) lastLoginIp = security.sanitizeSecure(lastLoginIp)"""),
])

editar("server.ts", [
    ("  // app.put('/api/Products/:id', security.isAuthorized()) // vuln-code-snippet vuln-line changeProductChallenge",
     "  app.put('/api/Products/:id', security.isAuthorized(), (req: Request, res: Response, next: NextFunction) => {\n"
     "    // Parche 14: modificar el catálogo exige sesión y rol de administración (antes: sin autenticación)\n"
     "    if (security.authenticatedUsers.from(req)?.data?.role !== 'admin') { res.status(403).json({ status: 'error', message: 'No autorizado para este recurso' }); return }\n"
     "    next()\n"
     "  })"),
])
print("Parche 14 aplicado.")
