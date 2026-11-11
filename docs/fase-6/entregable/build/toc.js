// Segunda pasada del índice: lee el texto del PDF (pdftotext -layout, páginas separadas por \f) y localiza
// la página real de cada título de toc-entradas.json. Escribe toc-paginas.json para volver a ejecutar build.js.
const fs = require('fs')
const pages = fs.readFileSync('pdf.txt', 'utf8').split('\f')
const entradas = JSON.parse(fs.readFileSync('toc-entradas.json', 'utf8'))
const esc = s => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
const mapa = {}
let desde = 2 // salta la carátula y el inicio del índice
for (const e of entradas) {
  const exacta = new RegExp('^\\s*' + esc(e) + '\\s*$', 'm')
  const prefijo = new RegExp('^\\s*' + esc(e.slice(0, 30)))
  let pagina = 0
  for (let i = desde; i < pages.length; i++) {
    const lineas = pages[i].split('\n')
    const ok = exacta.test(pages[i]) || lineas.some(l => prefijo.test(l) && !/\.{4,}/.test(l))
    if (ok) { pagina = i + 1; desde = i; break }
  }
  mapa[e] = pagina || ''
  console.log(String(pagina || '??').padStart(3) + '  ' + e)
}
const total = pages.filter(p => p.trim()).length
console.log('páginas con contenido:', total)
fs.writeFileSync('toc-paginas.json', JSON.stringify(mapa, null, 1))
