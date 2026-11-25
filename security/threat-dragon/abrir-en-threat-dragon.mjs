// Abre el modelo en OWASP Threat Dragon v2.6.2 REAL (Chromium/Playwright) e importa el JSON por la interfaz:
// sesión local → «Open an existing threat model» → pegar JSON → «Import». Después abre cada diagrama, cuenta los
// elementos y flujos dibujados por X6, abre el informe y comprueba que aparecen las 30 amenazas (T01-T20, TC01-TC10).
// Capturas de pantalla de cada paso. Solo contra la instancia local de Threat Dragon (red Docker interna).
// Uso: node abrir-en-threat-dragon.mjs <url-threat-dragon> <modelo.json> <carpeta-salida>
import { chromium } from 'playwright'
import fs from 'node:fs'

const [B, MODELO, OUT] = process.argv.slice(2)
if (!['threat-dragon', '127.0.0.1', 'localhost'].includes(new URL(B).hostname)) { console.error('FUERA DE ALCANCE'); process.exit(2) }
fs.mkdirSync(OUT, { recursive: true })
const texto = fs.readFileSync(MODELO, 'utf8')
const modelo = JSON.parse(texto)
const res = []; const errores = []
const fila = (p, esperado, obtenido, ok) => res.push({ p, esperado, obtenido: String(obtenido), ok })

const nav = await chromium.launch()
const page = await nav.newPage({ viewport: { width: 1900, height: 1300 } })
// Se excluye solo el aviso que el propio servidor de Threat Dragon provoca en cualquier página (directiva CSP obsoleta);
// se registra aparte para que conste.
const IGNORADO = "Unrecognized Content-Security-Policy directive 'prefetch-src'"
let ignorados = 0
page.on('console', m => { if (m.type() !== 'error') return; if (m.text().includes(IGNORADO)) { ignorados++; return } errores.push(m.text().slice(0, 200)) })
page.on('pageerror', e => errores.push(String(e).slice(0, 200)))
// La red del contenedor no tiene salida: lo que Threat Dragon pida a Internet falla por diseño y se informa aparte
const externos = new Set()
page.on('requestfailed', r => { const h = new URL(r.url()).hostname; if (h !== 'localhost') externos.add(h) })

await page.goto(B + '/', { waitUntil: 'domcontentloaded' })
await page.getByText('Login to Local Session').click()
await page.getByRole('link', { name: 'Open an existing threat model' }).click()
// fill() con 158 kB no termina en 30 s; se asigna el valor y se emite el evento input que escucha la vista (equivale a pegar)
await page.locator('textarea#json-input').evaluate((el, v) => { el.value = v; el.dispatchEvent(new Event('input', { bubbles: true })) }, texto)
await page.getByRole('button', { name: 'Import' }).click()
await page.waitForTimeout(2500)
await page.screenshot({ path: `${OUT}/01-modelo-importado.png`, fullPage: true })
const cuerpo = await page.locator('body').innerText()
fila('Importación del JSON por la interfaz', 'se muestra el modelo con su título', page.url(), cuerpo.includes(modelo.summary.title))

for (const d of modelo.detail.diagrams) {
  const nodos = d.cells.filter(c => c.shape !== 'flow' && c.shape !== 'trust-boundary-curve').length
  const flujos = d.cells.filter(c => c.shape === 'flow').length
  await page.getByText(d.title, { exact: true }).first().click()
  await page.locator('.x6-graph-svg, svg.x6-graph-svg').first().waitFor({ state: 'attached', timeout: 20000 })
  await page.waitForTimeout(3000)
  // Se excluye la paleta de figuras (stencil), que X6 dibuja como otro grafo
  const n = await page.locator('.x6-graph .x6-node').count() - await page.locator('.x6-widget-stencil .x6-node').count()
  const e = await page.locator('.x6-graph .x6-edge').count() - await page.locator('.x6-widget-stencil .x6-edge').count()
  await page.screenshot({ path: `${OUT}/0${d.id + 2}-diagrama-${d.id}.png`, fullPage: true })
  fila(`Diagrama ${d.id}: «${d.title}» — elementos y límites dibujados`, nodos, n, n === nodos)
  fila(`Diagrama ${d.id}: flujos de datos dibujados`, flujos, e, e === flujos)
  await page.goBack(); await page.waitForTimeout(1500)
}

const informe = page.getByText('Report', { exact: true }).first()
if (await informe.count()) {
  await informe.click(); await page.waitForTimeout(4000)
  const t = await page.locator('body').innerText()
  await page.screenshot({ path: `${OUT}/04-informe.png`, fullPage: true })
  fs.writeFileSync(`${OUT}/informe-texto.txt`, t)
  const ids = [...Array(20).keys()].map(i => `T${String(i + 1).padStart(2, '0')}`).concat([...Array(10).keys()].map(i => `TC${String(i + 1).padStart(2, '0')}`))
  const faltan = ids.filter(i => !t.includes(i + ' ·'))
  fila('Informe de Threat Dragon: amenazas T01-T20 y TC01-TC10', '30/30', `${30 - faltan.length}/30${faltan.length ? ' (faltan ' + faltan.join(', ') + ')' : ''}`, faltan.length === 0)
} else {
  fila('Informe de Threat Dragon', 'botón Report', 'no encontrado', false)
}
const propios = errores.filter(x => !(externos.size && x.includes('ERR_NAME_NOT_RESOLVED')))
fila('Errores de JavaScript en la consola (sin contar recursos externos bloqueados por el aislamiento)', 0, propios.length, propios.length === 0)
await nav.close()

const ok = res.filter(r => r.ok).length
let md = `# Modelo abierto en OWASP Threat Dragon v2.6.2 (navegador real)\n\nInstancia: \`${B}\` (contenedor local, red interna) · Chromium/Playwright · modelo \`${MODELO.split('/').pop()}\`\n\n| Prueba | Esperado | Obtenido | Resultado |\n|---|---|---|---|\n`
for (const r of res) md += `| ${r.p} | ${r.esperado} | ${r.obtenido} | ${r.ok ? 'OK' : '**FALLO**'} |\n`
md += `\n**Resultado: ${ok} OK · ${res.length - ok} fallos.**\n`
md += `\nAviso excluido del recuento (${ignorados} veces, emitido por la cabecera CSP del servidor de Threat Dragon, no por el modelo): \`${IGNORADO}\`.\n`
md += `
Recursos externos no resueltos (la red no tiene salida a Internet): ${[...externos].join(', ') || 'ninguno'}.
`
if (errores.length) md += '\nErrores de consola:\n' + errores.map(x => `- \`${x}\``).join('\n') + '\n'
fs.writeFileSync(`${OUT}/threat-dragon-navegador.md`, md)
console.log(`Threat Dragon (navegador): ${ok} OK · ${res.length - ok} fallos`)
