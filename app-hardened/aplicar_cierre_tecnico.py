"""Parches 11 y 12 (cierre técnico, 2026-11-23) sobre la variante corregida (después de aplicar_v2.py y aplicar_fase6.py).

Uso: python -I aplicar_cierre_tecnico.py <directorio con el código exportado>

Parche 11 — dependencias con CVE CRITICAL (R20) y JWT (R04):
  express-jwt 0.1.3 → 8.x y jsonwebtoken 0.4.0 → 9.x (algoritmo RS256 explícito; jws 4 exige el algoritmo al verificar),
  sanitize-html 1.4.2 → 2.x (retira lodash 2.4.2), se elimina `download` (arrastraba decompress sin corrección) y se usa
  fetch nativo; overrides: crypto-js ^4.2.0 (pdfkit) y tar ^7.5.19 (sqlite3).
Parche 12 — hallazgos medidos con security/ops/pruebas-cierre-tecnico.sh en la variante corregida:
  T3/T4 actualización masiva y de reseñas ajenas; T5 SSRF; T6 CSRF por cookie; T8 mensajes internos en 5xx (finale);
  T9 quejas de todas las cuentas; T10 reciclajes sin sesión y en lote; además, independencia de la detección de Docker:
  NoSQL `$where` (reseñas, pedidos) y XXE (entidades externas) se cierran en el código, y DOM XSS en la búsqueda.
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


# ---------------- Parche 11: dependencias y JWT ----------------
editar("package.json", [
    ('    "download": "^8.0.0",\n', ""),
    ('"express-jwt": "0.1.3",', '"express-jwt": "^8.4.1",'),
    ('    "jsonwebtoken": "0.4.0",\n', '    "jsonwebtoken": "^9.0.2",\n    "jws": "^4.0.0",\n'),
    ('"sanitize-html": "1.4.2",', '"sanitize-html": "^2.13.1",'),
    ('    "@types/download": "^8.0.5",\n', ""),
    ('    "@types/express-jwt": "^6.0.4",\n', ""),
    ('"@types/jsonwebtoken": "^8.5.9",', '"@types/jsonwebtoken": "^9.0.7",'),
    ('"@types/sanitize-html": "^1.27.2",', '"@types/sanitize-html": "^2.13.0",'),
    ('  "engines": {', '  "overrides": {\n    "crypto-js": "^4.2.0",\n    "tar": "^7.5.19",\n    "minimatch@^3": "^3.1.4"\n  },\n  "engines": {'),
])

editar("lib/insecurity.ts", [
    ("import expressJwt from 'express-jwt'", "import { expressjwt } from 'express-jwt'"),
    ("export const isAuthorized = () => expressJwt(({ secret: publicKey }) as any)",
     "// Parche 11: express-jwt 8 exige fijar el algoritmo (sin 'none' ni confusión RS/HS)\n"
     "export const isAuthorized = () => expressjwt({ secret: publicKey, algorithms: ['RS256'] })"),
    ("export const denyAll = () => expressJwt({ secret: '' + Math.random() } as any)",
     "export const denyAll = () => expressjwt({ secret: '' + Math.random(), algorithms: ['HS256'] })"),
    ("export const verify = (token: string) => token ? (jws.verify as ((token: string, secret: string) => boolean))(token, publicKey) : false",
     "export const verify = (token: string) => { try { return token ? jws.verify(token, 'RS256', publicKey) : false } catch { return false } }"),
])

editar("lib/utils.ts", [
    ("import download from 'download'\n", ""),
    ("import { ProxyAgent } from 'proxy-agent'\n", ""),
    ("const proxyAgent = new ProxyAgent()\n", ""),
    ("  downloadData: (url: string, options: download.DownloadOptions) => Promise<Buffer> = download\n) => {\n  try {\n    const data = await downloadData(url, { agent: proxyAgent })",
     "  // Parche 11: fetch nativo en lugar de `download` (retira decompress, CVE crítico sin corrección)\n"
     "  downloadData: (url: string) => Promise<Buffer> = async (direccion: string) => {\n"
     "    const respuesta = await fetch(direccion)\n"
     "    if (!respuesta.ok) throw new Error('HTTP ' + respuesta.status)\n"
     "    return Buffer.from(await respuesta.arrayBuffer())\n"
     "  }\n) => {\n  try {\n    const data = await downloadData(url)"),
])

# ---------------- Parche 12: hallazgos medidos ----------------
editar("routes/showProductReviews.ts", [
    ("    const id = !utils.isChallengeEnabled(challenges.noSqlCommandChallenge) ? Number(req.params.id) : utils.trunc(req.params.id, 40)",
     "    // Parche 12: id numérico siempre, sin depender de la detección de Docker; consulta por campo, no por $where\n    const id = Number(req.params.id)"),
    # Las reseñas sembradas guardan el producto como número y las creadas por usuarios como texto (createProductReviews
    # inserta req.params.id): se aceptan ambas formas del MISMO número entero, sin $where.
    ("    db.reviewsCollection.find({ $where: 'this.product == ' + id }).then((reviews: Review[]) => {",
     "    db.reviewsCollection.find({ product: { $in: Number.isInteger(id) ? [id, String(id)] : [] } }).then((reviews: Review[]) => {"),
])

editar("routes/trackOrder.ts", [
    ("    const id = !utils.isChallengeEnabled(challenges.reflectedXssChallenge) ? String(req.params.id).replace(/[^\\w-]+/g, '') : utils.trunc(req.params.id, 60)",
     "    // Parche 12: id saneado siempre; consulta por campo, no por $where\n    const id = String(req.params.id).replace(/[^\\w-]+/g, '')"),
    ("    db.ordersCollection.find({ $where: `this.orderId === '${id}'` }).then((order: any) => {",
     "    db.ordersCollection.find({ orderId: id }).then((order: any) => {"),
])

editar("routes/updateProductReviews.ts", [
    ("      { multi: true } // vuln-code-snippet vuln-line noSqlReviewsChallenge",
     "      { multi: false } // Parche 12: nunca actualización masiva"),
    ("        res.status(500).json(err)",
     "        res.status(500).json({ status: 'error', message: 'Internal server error' })"),
    ("// vuln-code-snippet start noSqlReviewsChallenge forgedReviewChallenge",
     "// Parche 12: solo la cuenta autora puede editar su reseña; el id debe ser texto (sin operadores NoSQL)\n"
     "export function resenaPropia () {\n"
     "  return async (req: Request, res: Response, next: NextFunction) => {\n"
     "    const user = security.authenticatedUsers.from(req)\n"
     "    if (!user || typeof req.body?.id !== 'string' || typeof req.body?.message !== 'string') {\n"
     "      res.status(400).json({ status: 'error', message: 'Bad request' })\n"
     "      return\n"
     "    }\n"
     "    try {\n"
     "      const review = await db.reviewsCollection.findOne({ _id: req.body.id })\n"
     "      if (!review || review.author !== user.data.email) {\n"
     "        res.status(403).json({ status: 'error', message: 'No autorizado para este recurso' })\n"
     "        return\n"
     "      }\n"
     "      next()\n"
     "    } catch {\n"
     "      res.status(500).json({ status: 'error', message: 'Internal server error' })\n"
     "    }\n"
     "  }\n"
     "}\n\n"
     "// vuln-code-snippet start noSqlReviewsChallenge forgedReviewChallenge"),
])

editar("lib/xml.ts", [
    ("      xmlRegisterFsInputProviders()",
     "      // Parche 12: sin proveedores de archivos: las entidades externas no se resuelven (XXE)\n      void xmlRegisterFsInputProviders"),
    ("libxml2.ParseOption.XML_PARSE_NOENT | libxml2.ParseOption.XML_PARSE_DTDLOAD | ", ""),
])

editar("routes/profileImageUrlUpload.ts", [
    ("import * as utils from '../lib/utils'",
     "import * as utils from '../lib/utils'\n"
     "import dns from 'node:dns/promises'\n"
     "import net from 'node:net'\n\n"
     "// Parche 12 (SSRF): solo http/https hacia direcciones públicas; se resuelve el nombre y se rechazan rangos internos.\n"
     "const esIpInterna = (ip: string): boolean => {\n"
     "  if (net.isIPv4(ip)) {\n"
     "    const [a, b] = ip.split('.').map(Number)\n"
     "    return a === 10 || a === 127 || a === 0 || (a === 169 && b === 254) || (a === 172 && b >= 16 && b <= 31) ||\n"
     "      (a === 192 && b === 168) || (a === 100 && b >= 64 && b <= 127)\n"
     "  }\n"
     "  const v = ip.toLowerCase()\n"
     "  return v === '::1' || v === '::' || v.startsWith('fc') || v.startsWith('fd') || v.startsWith('fe80') || v.startsWith('::ffff:')\n"
     "}\n"
     "async function urlExternaPermitida (url: string): Promise<boolean> {\n"
     "  try {\n"
     "    const destino = new URL(url)\n"
     "    if (!['http:', 'https:'].includes(destino.protocol)) return false\n"
     "    const direcciones = await dns.lookup(destino.hostname, { all: true })\n"
     "    return direcciones.length > 0 && direcciones.every(d => !esIpInterna(d.address))\n"
     "  } catch {\n"
     "    return false\n"
     "  }\n"
     "}"),
    ("          const response = await fetch(url)",
     "          if (!(await urlExternaPermitida(url))) {\n"
     "            res.status(400).json({ status: 'error', message: 'URL de imagen no permitida' })\n"
     "            return\n"
     "          }\n"
     "          const response = await fetch(url, { redirect: 'error' })"),
])

editar("routes/recycles.ts", [
    ("import * as utils from '../lib/utils'",
     "import * as utils from '../lib/utils'\nimport * as security from '../lib/insecurity'"),
    ("export const getRecycleItem = () => (req: Request, res: Response) => {\n  RecycleModel.findAll({\n    where: {\n      id: JSON.parse(req.params.id)\n    }",
     "export const getRecycleItem = () => (req: Request, res: Response) => {\n"
     "  // Parche 12: id numérico (sin JSON.parse ni lotes) y solo los reciclajes de la propia cuenta\n"
     "  const usuario = security.authenticatedUsers.from(req)\n"
     "  const id = Number(req.params.id)\n"
     "  if (!usuario || !Number.isInteger(id)) {\n"
     "    res.status(401).json({ status: 'error', message: 'No autorizado' })\n"
     "    return\n"
     "  }\n"
     "  RecycleModel.findAll({\n    where: {\n      id, UserId: usuario.data.id\n    }"),
])

editar("server.ts", [
    ("import { updateProductReviews } from './routes/updateProductReviews'",
     "import { updateProductReviews, resenaPropia } from './routes/updateProductReviews'"),
    ("  app.patch('/rest/products/reviews', security.isAuthorized(), updateProductReviews())",
     "  app.patch('/rest/products/reviews', security.isAuthorized(), resenaPropia(), updateProductReviews())"),
    ("  app.get('/api/Recycles/:id', recycles.getRecycleItem())",
     "  app.get('/api/Recycles/:id', security.isAuthorized(), recycles.getRecycleItem())"),
    ("  app.get('/api/Complaints', security.isAuthorized())",
     "  app.get('/api/Complaints', security.isAuthorized(), (req: Request, res: Response, next: NextFunction) => {\n"
     "    // Parche 12: la lista de quejas de todas las cuentas solo para administración\n"
     "    if (security.authenticatedUsers.from(req)?.data?.role !== 'admin') { res.status(403).json({ status: 'error', message: 'No autorizado para este recurso' }); return }\n"
     "    next()\n"
     "  })"),
    ("  app.use(cookieParser('kekse'))",
     "  app.use(cookieParser('kekse'))\n"
     "  /* Parche 12 (CSRF): perfil, imagen y borrado de datos se autentican con la cookie 'token'. Una petición que cambia\n"
     "     estado con Origin/Referer de otro sitio se rechaza. Se compara el nombre de host (el WAF reenvía Host sin puerto). */\n"
     "  app.use((req: Request, res: Response, next: NextFunction) => {\n"
     "    if (['GET', 'HEAD', 'OPTIONS'].includes(req.method)) { next(); return }\n"
     "    const origen = req.headers.origin ?? req.headers.referer\n"
     "    if (origen) {\n"
     "      let hostOrigen = ''\n"
     "      try { hostOrigen = new URL(origen).hostname } catch { hostOrigen = '' }\n"
     "      const hostPropio = String(req.headers.host ?? '').replace(/:\\d+$/, '')\n"
     "      if (hostOrigen !== hostPropio) { res.status(403).json({ status: 'error', message: 'Origen no permitido' }); return }\n"
     "    }\n"
     "    next()\n"
     "  })"),
    ("  finale.initialize({ app, sequelize: seq })",
     "  /* Parche 12: las respuestas 5xx de la capa REST genérica (finale) no exponen mensajes internos de la base de datos */\n"
     "  app.use('/api', (req: Request, res: Response, next: NextFunction) => {\n"
     "    const json = res.json.bind(res)\n"
     "    res.json = (cuerpo?: any) => res.statusCode >= 500 ? json({ status: 'error', message: 'Internal server error' }) : json(cuerpo)\n"
     "    next()\n"
     "  })\n"
     "  finale.initialize({ app, sequelize: seq })"),
])

# ---------------- Parche 13: base de datos administrada opcional (PostgreSQL) ----------------
# Sin DATABASE_URL todo sigue igual (SQLite local). Con DATABASE_URL la app usa PostgreSQL de verdad (no una BD decorativa).
editar("package.json", [
    ('    "pdfkit": "^0.11.0",\n', '    "pdfkit": "^0.11.0",\n    "pg": "^8.13.1",\n    "pg-hstore": "^2.3.4",\n'),
])
editar("models/index.ts", [
    ("import { Sequelize, Transaction } from 'sequelize'", "import { Sequelize, Transaction, DataTypes } from 'sequelize'"),
    ("function createSequelize (options?: { inMemory?: boolean }) {\n  return new Sequelize('database', 'username', 'password', {",
     "function createSequelize (options?: { inMemory?: boolean }) {\n"
     "  // Parche 13 (cierre técnico): con DATABASE_URL se usa PostgreSQL (BD administrada); sin ella, SQLite local.\n"
     "  if (process.env.DATABASE_URL && !options?.inMemory) {\n"
     "    const ssl = process.env.DATABASE_SSL === 'false' ? {} : { ssl: { require: true, rejectUnauthorized: process.env.DATABASE_SSL_VERIFY !== 'false' } }\n"
     "    return new Sequelize(process.env.DATABASE_URL, {\n"
     "      dialect: 'postgres',\n"
     "      dialectOptions: ssl,\n"
     "      logging: false,\n"
     "      // SQLite no limita la longitud de STRING y PostgreSQL sí (VARCHAR 255): en PostgreSQL se guardan como TEXT.\n"
     "      // Challenge.key es un ENUM con valores aparte, que Sequelize no crea como tipo en PostgreSQL: se guarda como TEXT\n"
     "      // (la aplicación valida las claves de reto por su cuenta).\n"
     "      hooks: {\n"
     "        beforeDefine: (atributos: any) => {\n"
     "          for (const k of Object.keys(atributos)) {\n"
     "            const a = atributos[k]\n"
     "            const clave = a?.type?.key ?? a?.key\n"
     "            if (k === 'cardNum' || k === 'mobileNum') {\n"
     "              // Tarjeta (16 dígitos) y teléfono (10): SQLite guarda enteros de 64 bits; INTEGER de PostgreSQL es de 32\n"
     "              if (a?.type) a.type = DataTypes.BIGINT; else atributos[k] = DataTypes.BIGINT\n"
     "            } else if (clave === 'STRING' || clave === 'ENUM') {\n"
     "              if (a?.type) { a.type = DataTypes.TEXT; delete a.values } else atributos[k] = DataTypes.TEXT\n"
     "            } else if (clave === 'NUMBER') {\n"
     "              // DataTypes.NUMBER genera 'NUMBER', válido en SQLite e inválido en PostgreSQL (los dos campos son enteros)\n"
     "              if (a?.type) a.type = DataTypes.INTEGER; else atributos[k] = DataTypes.INTEGER\n"
     "            }\n"
     "          }\n"
     "        }\n"
     "      }\n"
     "    })\n"
     "  }\n"
     "  return new Sequelize('database', 'username', 'password', {"),
])
editar("routes/login.ts", [
    ("'SELECT * FROM Users WHERE email = :email AND deletedAt IS NULL'",
     "'SELECT * FROM \"Users\" WHERE email = :email AND \"deletedAt\" IS NULL'"),
])
editar("routes/search.ts", [
    ("'SELECT * FROM Products WHERE ((name LIKE :q OR description LIKE :q) AND deletedAt IS NULL) ORDER BY name'",
     "'SELECT * FROM \"Products\" WHERE ((LOWER(name) LIKE LOWER(:q) OR LOWER(description) LIKE LOWER(:q)) AND \"deletedAt\" IS NULL) ORDER BY name'"),
])

editar("routes/search.ts", [
    # Hallado en la prueba con PostgreSQL: la comprobación del reto dbSchema consulta sqlite_master en CADA búsqueda; en
    # PostgreSQL la tabla no existe y la promesa sin catch terminaba el proceso de Node (denegación de servicio).
    ("        if (challengeUtils.notSolved(challenges.dbSchemaChallenge)) {",
     "        if (challengeUtils.notSolved(challenges.dbSchemaChallenge) && models.sequelize.getDialect() === 'sqlite') { // Parche 13"),
    ("          })\n        } // vuln-code-snippet hide-end",
     "          }).catch(() => {}) // Parche 13: un error de la consulta auxiliar nunca termina el proceso\n        } // vuln-code-snippet hide-end"),
])

editar("routes/b2bOrder.ts", [
    # Semgrep (regla propia node-eval-user-input): evaluación de datos del cliente con notevil, solo desactivada por el
    # modo seguro. Se elimina del código: las líneas de pedido se tratan como datos JSON, nunca como código.
    ("        vm.runInContext('safeEval(orderLinesData)', sandbox, { timeout: 2000 })",
     "        void sandbox\n        JSON.parse(String(orderLinesData)) // Parche 12: datos, no código (sin safeEval)"),
])

editar("routes/chat.ts", [
    ("          return await db.reviewsCollection.find({ $where: 'this.product == ' + productId }) as Review[]",
     "          return await db.reviewsCollection.find({ product: { $in: Number.isInteger(productId) ? [productId, String(productId)] : [] } }) as Review[] // Parche 12: sin $where"),
])

editar("frontend/src/app/search-result/search-result.component.ts", [
    ("this.searchValue = this.sanitizer.bypassSecurityTrustHtml(queryParam)",
     "this.searchValue = queryParam // Parche 12 (DOM XSS): sin bypass, Angular sanea el texto en [innerHTML]"),
])
print("Parches 11 y 12 aplicados.")
