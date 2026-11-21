"""Aplica las correcciones v2 (parches 01, 03, 04) y el parche 09 sobre una COPIA exportada de app/.

Uso: python -I aplicar_v2.py <directorio con el código exportado>
Motivo (hito A, 2026-11-21): en la revisión de los parches v1 se detectó que
  - 01 + 03 rompían el inicio de sesión: bcrypt usa sal aleatoria y el login seguía comparando el hash en SQL;
    además 03 usaba `bcrypt` sin importarlo y cambiaba `hash` (MD5), que también se usa para ids de pedido y Gravatar;
  - 04 recurría a `encryptionkeys/jwt.key`, un directorio que la app sirve con listado: expondría la clave privada.
Cada reemplazo es literal y se comprueba: si el texto original no aparece, el script falla (no hay éxito falso).
"""
import os
import sys

SRC = sys.argv[1]


def editar(ruta, cambios):
    p = os.path.join(SRC, ruta)
    texto = open(p, encoding="utf-8").read()
    for viejo, nuevo in cambios:
        if callable(viejo):
            texto = viejo(texto)
            continue
        n = texto.count(viejo)
        if n != 1:
            raise SystemExit(f"FALLO {ruta}: el texto esperado aparece {n} veces: {viejo[:70]!r}")
        texto = texto.replace(viejo, nuevo)
    open(p, "w", encoding="utf-8", newline="\n").write(texto)
    print(f"ok  {ruta}")


def reemplazar_linea_que_empieza(prefijo, nuevo):
    def f(texto):
        lineas = texto.split("\n")
        idx = [i for i, l in enumerate(lineas) if l.startswith(prefijo)]
        if len(idx) != 1:
            raise SystemExit(f"FALLO: la línea que empieza por {prefijo[:50]!r} aparece {len(idx)} veces")
        lineas[idx[0]] = nuevo
        return "\n".join(lineas)
    return f


CLAVE = """// Parche 04 v2 (ASVS V13.3.1): la clave privada NO esta en el codigo ni en un directorio servido por la app.
// Se lee de un secreto montado (JWT_PRIVATE_KEY_FILE) o de JWT_PRIVATE_KEY; si falta, la aplicacion no arranca.
const privateKey = (() => {
  const archivo = process.env.JWT_PRIVATE_KEY_FILE
  const clave = archivo ? fs.readFileSync(archivo, 'utf8') : process.env.JWT_PRIVATE_KEY
  if (!clave?.includes('PRIVATE KEY')) throw new Error('JWT_PRIVATE_KEY_FILE o JWT_PRIVATE_KEY no configurada: se aborta el arranque')
  return clave
})()
// La clave publica de verificacion se deriva del par rotado (el archivo historico jwt.pub ya no se usa para verificar).
export const publicKey = crypto.createPublicKey(privateKey).export({ type: 'spki', format: 'pem' }).toString()"""

PASSWORDS = """export const hash = (data: string) => crypto.createHash('md5').update(data).digest('hex')
// Parche 03 v2 (ASVS V11.4.2): contrasenas con KDF resistente y sal (scrypt nativo de Node, sin dependencias nuevas).
// `hash` (MD5) se conserva SOLO para usos que no son contrasenas (ids de pedido, Gravatar, B2B).
export const hashPassword = (clear: string) => {
  const sal = crypto.randomBytes(16)
  return `scrypt:${sal.toString('hex')}:${crypto.scryptSync(clear, sal, 64).toString('hex')}`
}
export const verifyPassword = (clear: string, stored?: string) => {
  const [alg, salHex, hashHex] = String(stored ?? '').split(':')
  if (alg !== 'scrypt' || !salHex || !hashHex) return false
  const esperado = Buffer.from(hashHex, 'hex')
  const calculado = crypto.scryptSync(clear, Buffer.from(salHex, 'hex'), esperado.length)
  return calculado.length === esperado.length && crypto.timingSafeEqual(calculado, esperado)
}"""

editar("lib/insecurity.ts", [
    ("export const publicKey = fs ? fs.readFileSync('encryptionkeys/jwt.pub', 'utf8') : 'placeholder-public-key'\n", ""),
    (reemplazar_linea_que_empieza("const privateKey = '-----BEGIN RSA PRIVATE KEY-----", CLAVE), None),
    ("export const hash = (data: string) => crypto.createHash('md5').update(data).digest('hex')", PASSWORDS),
])

editar("models/user.ts", [
    ("this.setDataValue('password', security.hash(clearTextPassword))", "this.setDataValue('password', security.hashPassword(clearTextPassword))"),
])

editar("routes/login.ts", [
    ("models.sequelize.query(`SELECT * FROM Users WHERE email = '${req.body.email || ''}' AND password = '${security.hash(req.body.password || '')}' AND deletedAt IS NULL`, { model: UserModel, plain: true })",
     "models.sequelize.query('SELECT * FROM Users WHERE email = :email AND deletedAt IS NULL', { replacements: { email: req.body.email || '' }, model: UserModel, plain: true }) // parche 01 v2: consulta parametrizada"),
    ("      .then((authenticatedUser) => {",
     "      .then((candidato) => { // parche 03 v2: la contrasena se verifica con scrypt en la aplicacion, no por igualdad en SQL\n"
     "        const authenticatedUser = candidato && security.verifyPassword(req.body.password || '', (candidato as UserModel).password) ? candidato : null"),
])

editar("routes/changePassword.ts", [
    ("if (currentPassword && security.hash(currentPassword) !== loggedInUser.data.password)",
     "if (currentPassword && !security.verifyPassword(currentPassword, loggedInUser.data.password))"),
])

ruta = os.path.join(SRC, "routes/2fa.ts")
t = open(ruta, encoding="utf-8").read()
n = t.count("if (user.password !== security.hash(password))")
if n != 2:
    raise SystemExit(f"FALLO routes/2fa.ts: se esperaban 2 comparaciones y hay {n}")
open(ruta, "w", encoding="utf-8", newline="\n").write(t.replace("if (user.password !== security.hash(password))", "if (!security.verifyPassword(password, user.password))"))
print("ok  routes/2fa.ts (2 comparaciones)")

editar("server.ts", [
    ("  app.use(errorhandler())",
     "  // Parche 09 (A10:2025): errores sanitizados; sin trazas de pila ni detalles internos hacia el cliente.\n"
     "  app.use((err: Error & { status?: number, statusCode?: number }, req: Request, res: Response, next: NextFunction) => {\n"
     "    if (res.headersSent) { next(err); return }\n"
     "    const status = err.status ?? err.statusCode ?? (res.statusCode >= 400 ? res.statusCode : 500)\n"
     "    console.error(`error ${status} ${req.method} ${req.path}: ${err.message}`)\n"
     "    res.status(status).json({ status: 'error', message: status === 403 ? 'Forbidden' : status < 500 ? 'Bad request' : 'Internal server error' })\n"
     "  })"),
])
print("Correcciones v2 aplicadas.")
