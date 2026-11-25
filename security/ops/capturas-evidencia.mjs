// Capturas reales para el índice de evidencias (Playwright 1.49.1, Chromium). Solo LEE páginas: no envía formularios ni ataques.
// Uso: node capturas-evidencia.mjs <modo> <salida>
//   modo github  : páginas PÚBLICAS de GitHub Actions del repositorio (sin sesión)
//   modo render  : puerta de acceso del despliegue autorizado (una petición GET sin credenciales) y datos TLS del navegador
//   modo grafana : panel del SIEM local (Grafana en la red interna del SIEM; lectura anónima de solo lectura)
import { chromium } from '/work/node_modules/playwright/index.mjs'
import fs from 'node:fs'

const [modo, OUT] = process.argv.slice(2)
fs.mkdirSync(OUT, { recursive: true })
const nav = await chromium.launch()
const ctx = await nav.newContext({ viewport: { width: 1600, height: 1000 }, deviceScaleFactor: 2, locale: 'es-ES' })
const page = await ctx.newPage()
const notas = []

async function captura(url, archivo, opciones = {}) {
  const r = await page.goto(url, { waitUntil: 'networkidle', timeout: 90000 }).catch(e => ({ error: String(e) }))
  await page.waitForTimeout(opciones.espera || 1500)
  await page.screenshot({ path: `${OUT}/${archivo}`, fullPage: opciones.completa !== false })
  const estado = r && r.status ? r.status() : r.error
  notas.push(`| ${archivo} | ${url} | ${estado} | ${new Date().toISOString()} |`)
  return r
}

if (modo === 'github') {
  const repo = 'https://github.com/jmolinap1-universidad/juice-shop-lab'
  await captura(`${repo}/actions/runs/${process.env.RUN_DEVSECOPS}`, '01-actions-devsecops-resumen.png')
  await captura(`${repo}/actions/runs/${process.env.RUN_RELEASE}`, '02-actions-release-resumen.png')
  await captura(`${repo}/actions/workflows/devsecops.yml`, '03-actions-devsecops-historial.png', { completa: false })
  await captura(`${repo}/actions/workflows/release.yml`, '04-actions-release-historial.png', { completa: false })
} else if (modo === 'render') {
  const host = process.env.HOST_CLOUD_AUTORIZADO
  if (host !== 'juice-lab-masi-staging.onrender.com') throw new Error('FUERA DE ALCANCE')
  const r = await captura(`https://${host}/`, '01-render-puerta-acceso.png', { espera: 2500 })
  const tls = r && r.securityDetails ? await r.securityDetails() : null
  // la primera respuesta es la redirección; se consulta también la propia puerta
  const r2 = await page.goto(`https://${host}/__acceso`).catch(() => null)
  const tls2 = r2 ? await r2.securityDetails() : null
  const d = tls2 || tls
  fs.writeFileSync(`${OUT}/02-render-tls-navegador.json`, JSON.stringify({
    url: `https://${host}/__acceso`, estado_http: r2 ? r2.status() : null,
    protocolo: d && d.protocol, emisor: d && d.issuer, sujeto: d && d.subjectName,
    valido_desde: d && new Date(d.validFrom * 1000).toISOString(), valido_hasta: d && new Date(d.validTo * 1000).toISOString(),
    fecha: new Date().toISOString(), cliente: 'Chromium (Playwright 1.49.1)'
  }, null, 2))
} else if (modo === 'repositorio') {
  // Vista pública del repositorio (sin sesión)
  await captura('https://github.com/jmolinap1-universidad/juice-shop-lab', '01-repositorio-inicio.png', { completa: false, espera: 2500 })
  await captura('https://github.com/jmolinap1-universidad/juice-shop-lab/tree/main/evidence', '02-repositorio-evidencias.png', { completa: false, espera: 2500 })
} else if (modo === 'sitio') {
  // Sitio publicado: la puerta exige autenticación; se usa la credencial de verificación del equipo (archivo montado, nunca impresa).
  const host = process.env.HOST_CLOUD_AUTORIZADO
  if (host !== 'juice-lab-masi-staging.onrender.com') throw new Error('FUERA DE ALCANCE')
  const [usuario, clave] = fs.readFileSync('/cred', 'utf8').trim().split(':')
  const ctx2 = await nav.newContext({ viewport: { width: 1600, height: 1000 }, deviceScaleFactor: 2, locale: 'es-ES', httpCredentials: { username: usuario, password: clave } })
  const p2 = await ctx2.newPage()
  const r = await p2.goto(`https://${host}/__acceso`, { waitUntil: 'load', timeout: 180000 })
  notas.push(`| (cookie de acceso) | https://${host}/__acceso | ${r.status()} | ${new Date().toISOString()} |`)
  for (const [ruta, archivo] of [['/#/', '01-sitio-tienda.png'], ['/#/search?q=apple', '02-sitio-busqueda.png'], ['/#/login', '03-sitio-login.png']]) {
    const rr = await p2.goto(`https://${host}${ruta}`, { waitUntil: 'networkidle', timeout: 180000 })
    await p2.waitForTimeout(4000)
    // cerrar los avisos de bienvenida y de cookies de Juice Shop si aparecen
    await p2.locator('button[aria-label="Close Welcome Banner"]').click({ timeout: 3000 }).catch(() => {})
    await p2.locator('a[aria-label="dismiss cookie message"], .cc-btn.cc-dismiss').first().click({ timeout: 3000 }).catch(() => {})
    await p2.waitForTimeout(1500)
    await p2.screenshot({ path: `${OUT}/${archivo}` })
    notas.push(`| ${archivo} | https://${host}${ruta} | ${rr ? rr.status() : ''} | ${new Date().toISOString()} |`)
  }
} else if (modo === 'grafana') {
  await captura('http://siem-grafana:3000/d/siem-juice?orgId=1&from=now-24h&to=now&kiosk', '01-grafana-siem-24h.png', { espera: 8000 })
}
fs.writeFileSync(`${OUT}/capturas.md`, `# Capturas (${modo})\n\n| Archivo | URL | HTTP | Fecha (UTC) |\n|---|---|---|---|\n${notas.join('\n')}\n`)
await nav.close()
console.log('ok', modo, notas.length)
