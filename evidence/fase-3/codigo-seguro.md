# Prácticas de código seguro: fragmentos antes y después (extraídos del parche auditado)

Fuente única de los fragmentos: `app-hardened/patches/v2/correcciones-cierre-brechas.patch` (sha256 `fc3f765c…`, 22 archivos),
aplicado sobre `app/` = OWASP Juice Shop v20.3.0 (commit `f189f5212`). Se citan literalmente las líneas del diff (se omiten los
marcadores `vuln-code-snippet` del proyecto original). No se modificó ningún fragmento.

## SQLi — `routes/login.ts` (línea 34 del original; parches 01 v2 y 03 v2; riesgo R01)
Antes:
```ts
models.sequelize.query(`SELECT * FROM Users WHERE email = '${req.body.email || ''}' AND password = '${security.hash(req.body.password || '')}' AND deletedAt IS NULL`, { model: UserModel, plain: true })
```
Después:
```ts
models.sequelize.query('SELECT * FROM "Users" WHERE email = :email AND "deletedAt" IS NULL', { replacements: { email: req.body.email || '' }, model: UserModel, plain: true })
  .then((candidato) => {
    const authenticatedUser = candidato && security.verifyPassword(req.body.password || '', (candidato as UserModel).password) ? candidato : null
```
Prueba: caso A1 (`security/attacks/run.sh`). Imagen oficial: se obtiene un JWT de administrador sin credenciales válidas (`evidence/fase-4/antes/a1-req-resp.txt`). Variante sin WAF: 401 sin
token (`evidence/cierre-2026-11-20/03-corregida-sin-waf/`); Render: mitigado (`evidence/cierre-brechas-2026-11-24/10-validacion-render/baterias/ataques.txt`).

## XSS — `frontend/src/app/search-result/search-result.component.ts` (línea 146; parche 12) y `routes/saveLoginIp.ts` (parche 14; riesgo R13)
Antes / después (búsqueda, XSS DOM):
```ts
-      this.searchValue = this.sanitizer.bypassSecurityTrustHtml(queryParam)
+      this.searchValue = queryParam // sin bypass, Angular sanea el texto en [innerHTML]
```
Antes / después (última IP, XSS almacenado):
```ts
-      if (utils.isChallengeEnabled(challenges.httpHeaderXssChallenge)) { ... } else {
-        lastLoginIp = security.sanitizeSecure(lastLoginIp ?? '')
-      }
+      if (lastLoginIp !== undefined) lastLoginIp = security.sanitizeSecure(lastLoginIp)
```
Prueba: XSS en Chromium, 6 vectores (`evidence/cierre-brechas-2026-11-24/02-xss-navegador/`): imagen oficial sin modo seguro 5/6
ejecutados; variante corregida 0/6 con y sin modo seguro; imagen cloud 0/6.

## CSRF — `server.ts` (insertado tras la línea 317; parche 12; riesgo R13/R23)
Después (antes no existía comprobación de origen):
```ts
app.use((req: Request, res: Response, next: NextFunction) => {
  if (['GET', 'HEAD', 'OPTIONS'].includes(req.method)) { next(); return }
  const origen = req.headers.origin ?? req.headers.referer
  if (origen) {
    let hostOrigen = ''
    try { hostOrigen = new URL(origen).hostname } catch { hostOrigen = '' }
    const hostPropio = String(req.headers.host ?? '').replace(/:\d+$/, '')
    if (hostOrigen !== hostPropio) { res.status(403).json({ status: 'error', message: 'Origen no permitido' }); return }
  }
  next()
})
```
Prueba: T6 (Origin ajeno, 403, nombre sin cambiar) y control T6b (sin Origin ajeno, 302, cambio aplicado) en Render
(`evidence/cierre-brechas-2026-11-24/10-validacion-render/baterias/pruebas/resultados.md`).

## JWT — `lib/insecurity.ts` (línea 52 del original; parches 04 v2 y 11; riesgos R03 y R04)
Antes / después:
```ts
-export const isAuthorized = () => expressJwt(({ secret: publicKey }) as any)
+export const isAuthorized = () => expressjwt({ secret: publicKey, algorithms: ['RS256'] })
```
Con `express-jwt` 8.5.1, `jsonwebtoken` 9.0.3 y `jws` 4.0.1 (parche 11). La clave privada deja de estar en el código (parche 04 v2:
secreto montado o generado en el contenedor; sin secreto la app no arranca).
Prueba: `alg=none` y confusión HS256 con la clave pública: 401; token legítimo RS256: 200
(`evidence/cierre-tecnico-2026-11-23/04-despues-parches/jwt-algoritmos.md`); token firmado con la clave anterior: 401.
