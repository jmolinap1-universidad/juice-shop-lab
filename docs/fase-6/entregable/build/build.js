// Generador del documento de la Fase 6 — versión de cierre (v2). Produce un BORRADOR DE VALIDACIÓN:
//   ../BORRADOR_VALIDACION_Fase6_Operaciones_Monitoreo_Ciberseguridad.docx
// No sobrescribe el entregable institucional (Fase6_Operaciones_Monitoreo_Ciberseguridad.docx/.pdf), cuya carátula
// y maquetación final integra el equipo (ver docs/fase-6/INSTRUCCIONES_SINCRONIZACION_DOCUMENTO.md).
// Datos: docs/fase-6/datos/riesgos-calculados.json (validado por riesgo.py), evidencia de evidence/fase-6,
// bitácora y MANIFEST. Índice con hipervínculos internos; páginas reales en una segunda pasada (toc.js).
// Uso (Docker): NODE_PATH=/opt/node_modules node build.js
const fs = require('fs')
const path = require('path')
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType, ImageRun, Table, TableRow, TableCell,
  WidthType, BorderStyle, ShadingType, Footer, PageNumber, LevelFormat, TabStopType, LeaderType, Tab,
  convertInchesToTwip, Bookmark, InternalHyperlink
} = require('docx')

const ROOT = path.resolve(__dirname, '../../../..')
const F6 = path.join(ROOT, 'docs/fase-6')
const IMG = path.join(F6, 'entregable/img')
const OUT = path.join(F6, 'entregable/BORRADOR_VALIDACION_Fase6_Operaciones_Monitoreo_Ciberseguridad.docx')
const V = 'evidence/fase-6/validacion-2026-11-10'
const ARIAL = 'Arial'
const MONO = 'Courier New'
const BLUE = '1F3864'
const DATA = JSON.parse(fs.readFileSync(path.join(F6, 'datos/riesgos-calculados.json'), 'utf8'))
const R = DATA.riesgos
const DIST = DATA.distribucion
const TOC = fs.existsSync(path.join(__dirname, 'toc-paginas.json')) ? JSON.parse(fs.readFileSync(path.join(__dirname, 'toc-paginas.json'), 'utf8')) : {}

// ---------- numeración comprobada de figuras y tablas ----------
const FIG = { arq: 1, stack: 2, crs: 3, r22: 4, caida: 5, integ: 6, fp: 7, reglas: 8, grafana: 9, metricas: 10, proxy: 11, defensa: 12, hantes: 13, hdesp: 14, niveles: 15 }
const TAB = { controles: 1, owasp: 2, rasp: 3, reglas: 4, escenarios: 5, opciones: 6, registro: 7, decisiones: 8, plan: 9, aceptaciones: 10, residual: 11, niveles: 12 }
let nFig = 0
let nTab = 0

// ---------- helpers ----------
const pngSize = (buf) => ({ w: buf.readUInt32BE(16), h: buf.readUInt32BE(20) })
const run = (text, o = {}) => new TextRun({ text, font: o.mono ? MONO : ARIAL, size: o.size || 24, bold: o.bold, italics: o.it, color: o.color })
function rich (text, size = 24) {
  const out = []
  const re = /(\*\*[^*]+\*\*|`[^`]+`)/g
  let last = 0
  let m
  while ((m = re.exec(text))) {
    if (m.index > last) out.push(run(text.slice(last, m.index), { size }))
    const t = m[0]
    out.push(t.startsWith('**') ? run(t.slice(2, -2), { bold: true, size }) : run(t.slice(1, -1), { mono: true, size: size - 2 }))
    last = m.index + t.length
  }
  if (last < text.length) out.push(run(text.slice(last), { size }))
  return out
}
function fig (clave, file, caption, maxW = 600, maxH = 760) {
  nFig++
  if (FIG[clave] !== nFig) throw new Error(`Figura ${clave}: esperada ${FIG[clave]}, generada ${nFig}`)
  const buf = fs.readFileSync(file.includes('/') ? path.join(ROOT, file) : path.join(IMG, file))
  const { w, h } = pngSize(buf)
  const s = Math.min(maxW / w, maxH / h, 1)
  return [
    new Paragraph({ alignment: AlignmentType.CENTER, keepNext: true, spacing: { before: 120, after: 40 }, children: [new ImageRun({ type: 'png', data: buf, transformation: { width: Math.round(w * s), height: Math.round(h * s) } })] }),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 220 }, children: [run(`Figura ${nFig}. `, { bold: true, size: 20 }), run(caption, { it: true, size: 20 })] })
  ]
}
const p = (text, o = {}) => new Paragraph({
  alignment: o.align || AlignmentType.JUSTIFIED,
  spacing: { line: 360, after: o.after ?? 160 },
  indent: o.indent === false ? undefined : { firstLine: convertInchesToTwip(0.5) },
  children: Array.isArray(text) ? text : rich(text)
})
const bullet = (text) => new Paragraph({ alignment: AlignmentType.JUSTIFIED, spacing: { line: 360, after: 80 }, numbering: { reference: 'vinetas', level: 0 }, children: rich(text) })

// Títulos con marcador (para los hipervínculos del índice)
const ENTRADAS = [
  ['Introducción'], ['Objetivos'],
  ['1. Estrategia de Mitigación y Ciberseguridad'],
  ['1.1 Arquitectura operativa y defensa en profundidad', 1], ['1.2 Controles compensatorios por riesgo', 1],
  ['1.3 WAF: reglas para el OWASP Top 10:2025', 1], ['1.4 RASP: detección y bloqueo en tiempo de ejecución', 1],
  ['1.5 Monitoreo de APIs: heurística de comportamiento anómalo', 1], ['1.6 SIEM: centralización y correlación de logs', 1],
  ['1.7 Validación integral de los controles', 1],
  ['2. Tratamiento Formal del Riesgo'],
  ['2.1 Método de valoración', 1], ['2.2 Opciones de tratamiento', 1], ['2.3 Categorización del riesgo por tipo e impacto', 1],
  ['2.4 Matriz de decisiones y plan de tratamiento', 1], ['2.5 Justificación del riesgo residual', 1],
  ['2.6 Matriz de calor: probabilidad frente a impacto', 1], ['2.7 Lectura del riesgo residual', 1],
  ['Limitaciones y pendientes'], ['Conclusiones'], ['Referencias'], ['Anexos']
]
const ancla = Object.fromEntries(ENTRADAS.map(([t], i) => [t, `sec${String(i + 1).padStart(2, '0')}`]))
function titulo (text, nivel, saltoPagina) {
  if (!ancla[text]) throw new Error(`Título sin entrada de índice: ${text}`)
  return new Paragraph({
    heading: nivel === 1 ? HeadingLevel.HEADING_1 : HeadingLevel.HEADING_2,
    pageBreakBefore: !!saltoPagina,
    children: [new Bookmark({ id: ancla[text], children: [new TextRun({ text, font: ARIAL })] })]
  })
}
const h1 = (t, salto = true) => titulo(t, 1, salto)
const h2 = (t) => titulo(t, 2, false)
const h2Libre = (t) => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun({ text: t, font: ARIAL })] })

function tabla (clave, tituloTabla, rows, widths, size = 17) {
  nTab++
  if (TAB[clave] !== nTab) throw new Error(`Tabla ${clave}: esperada ${TAB[clave]}, generada ${nTab}`)
  const total = widths.reduce((a, b) => a + b, 0)
  const mk = (txt, head, w) => new TableCell({
    width: { size: w, type: WidthType.DXA },
    shading: head ? { type: ShadingType.CLEAR, fill: BLUE, color: 'auto' } : undefined,
    margins: { top: 30, bottom: 30, left: 70, right: 70 },
    children: [new Paragraph({ spacing: { after: 0, line: 252 }, children: head ? [new TextRun({ text: txt, font: ARIAL, size, bold: true, color: 'FFFFFF' })] : rich(String(txt), size) })]
  })
  return [
    new Paragraph({ keepNext: true, spacing: { before: 160, after: 40 }, children: [run(`Tabla ${nTab}`, { bold: true, size: 22 })] }),
    new Paragraph({ keepNext: true, spacing: { after: 80 }, children: [run(tituloTabla, { it: true, size: 22 })] }),
    new Table({ width: { size: total, type: WidthType.DXA }, columnWidths: widths, rows: rows.map((r, i) => new TableRow({ tableHeader: i === 0, cantSplit: true, children: r.map((c, j) => mk(c, i === 0, widths[j])) })) }),
    new Paragraph({ spacing: { after: 120 }, children: [run('Nota. Elaboración propia con datos del repositorio del laboratorio.', { size: 18, it: true })] })
  ]
}
const code = (lines, size = 14) => lines.map((l) => new Paragraph({ spacing: { after: 0, line: 220 }, shading: { type: ShadingType.CLEAR, fill: 'F2F2F2', color: 'auto' }, children: [new TextRun({ text: l || ' ', font: MONO, size })] }))

// ---------- carátula (provisional: el equipo integra la carátula institucional) ----------
const caratula = [
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 120 }, shading: { type: ShadingType.CLEAR, fill: 'FFF2CC', color: 'auto' }, children: [run('BORRADOR DE VALIDACIÓN TÉCNICA — no sustituye al documento institucional', { bold: true, size: 20, color: '7F6000' })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 240, after: 60 }, border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: BLUE } }, children: [run('[ Logo oficial UMG — pendiente: lo integra el equipo con la carátula institucional ]', { it: true, color: '808080', size: 20 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 240, after: 60 }, children: [run('UNIVERSIDAD MARIANO GÁLVEZ DE GUATEMALA', { bold: true, size: 28 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 40 }, children: [run('Maestría en Seguridad Informática', { size: 24 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 400 }, children: [run('Curso: Seguridad en Aplicaciones', { size: 24 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 500, after: 120 }, children: [run('Laboratorio de Seguridad de Aplicaciones sobre OWASP Juice Shop', { bold: true, size: 32, color: BLUE })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 800 }, children: [run('Fase 6: Operaciones, Monitoreo y Ciberseguridad', { bold: true, size: 28 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 300, after: 40 }, children: [run('Integrantes:', { bold: true })] }),
  ...['Molina Pérez, Juan Carlos', 'Sánchez Flores, Juan Walter Ernesto', 'García Gonzalez, Leopoldo Emanuel', 'Cambara Castillo, Vanessa Odeth']
    .map(n => new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 20 }, children: [run(n, { size: 22 })] })),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 300, after: 20 }, children: [run('Catedrático: Ing. Matthew Alexander Seigne Samayoa', { size: 22 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 300 }, children: [run('Guatemala, noviembre de 2026', { size: 22 })] })
]

// ---------- índice con hipervínculos ----------
const tocLine = (text, sub) => new Paragraph({
  spacing: { after: sub ? 30 : 60, line: 300 },
  indent: sub ? { left: convertInchesToTwip(0.3) } : undefined,
  tabStops: [{ type: TabStopType.RIGHT, position: 9360, leader: LeaderType.DOT }],
  children: [new InternalHyperlink({ anchor: ancla[text], children: [new TextRun({ text, font: ARIAL, size: sub ? 22 : 24, bold: !sub }), new TextRun({ children: [new Tab(), String(TOC[text] || '')], font: ARIAL, size: sub ? 22 : 24, bold: !sub })] })]
})
const indice = [new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun({ text: 'Índice', font: ARIAL })] }), ...ENTRADAS.map(([t, s]) => tocLine(t, !!s))]

// ---------- datos derivados ----------
const cuenta = (k, v) => R.filter(r => r[k] === v).length
const NIV = DIST.niveles
const crit = R.filter(r => r.N_res === 'Crítico')
const altos = R.filter(r => r.N_res === 'Alto')
const VERIF = { probado: 'Probado', inspeccionado: 'Inspeccionado', sin_verificar: 'Sin verificar', no_efectivo: 'No efectivo' }
const manifest6 = fs.readFileSync(path.join(ROOT, 'evidence/MANIFEST.sha256'), 'utf8').split('\n').filter(l => l.includes('./fase-6/'))
const bitacora6 = fs.readFileSync(path.join(ROOT, 'evidence/bitacora.md'), 'utf8').split('\n').filter(l => /^\| 2026-11-10T[^|]*\| 6 \|/.test(l))
const alertas = fs.readFileSync(path.join(ROOT, 'deploy/hardened/siem/rules/fake/alertas.yaml'), 'utf8').split('\n')
const validacion = fs.readFileSync(path.join(F6, 'datos/validacion-consistencia.txt'), 'utf8').split('\n')
const nChecks = validacion.filter(l => l.startsWith('OK')).length
const principal = (r) => r.controles.find(c => c.verificacion === 'probado' && c.tipo !== 'detectivo') || r.controles.find(c => c.verificacion === 'probado') || r.controles[0]

// ---------- cuerpo ----------
const body = [
  h1('Introducción'),
  p('Este documento presenta la Fase 6 del laboratorio de Seguridad de Aplicaciones sobre OWASP Juice Shop 20.3.0. La fase lleva los hallazgos de ciberdefensa (Fases 4 y 5) al plano de las **operaciones**: define un control compensatorio para cada riesgo, integra un cortafuegos de aplicaciones web (WAF), una protección en tiempo de ejecución (RASP) con monitoreo de API y un sistema de gestión de eventos (SIEM), y verifica con pruebas repetibles qué protege cada capa y qué no.'),
  p('La segunda parte formaliza el tratamiento del riesgo con el proceso de ISO/IEC 27005: 24 riesgos categorizados por tipo e impacto, una decisión de tratamiento por riesgo y matrices de calor antes y después de los controles. La escala, la derivación desde el análisis DREAD de la Fase 1 y las pautas de reducción son una **convención propia del equipo**: la norma define el proceso y las opciones de tratamiento, no una fórmula. El riesgo residual se fija por riesgo, con su justificación, y un validador automático rechaza cualquier reducción que no esté respaldada por un control **probado**.'),
  p('Todas las pruebas se realizaron sobre instancias propias, expuestas solo en 127.0.0.1 o en redes internas de Docker. Ningún componente reporta a servicios externos y cada resultado remite a evidencia con hash SHA-256 (Anexo A) y a la bitácora de comandos (Anexo B). Se distinguen cinco niveles de verificación: **probado** (una prueba demostró el efecto), **inspeccionado** (configuración comprobada, efecto no ejercitado), **diseñado** (corrección validada como diff, no desplegada), **propuesto** y **no efectivo**.'),
  p([run('Repositorio: '), run('https://github.com/jmolinap1-universidad/juice-shop-lab', { color: BLUE })], { indent: false }),
  h1('Objetivos', false),
  h2Libre('Objetivo general'),
  p('Operar la aplicación endurecida con controles en capas —perímetro, ejecución y monitoreo— y tratar formalmente cada riesgo, demostrando con evidencia verificable qué parte del riesgo inherente reduce cada control y cuál permanece.'),
  h2Libre('Objetivos específicos'),
  bullet('Definir controles compensatorios para cada riesgo identificado, con tipo, nivel de verificación y evidencia.'),
  bullet('Configurar un WAF frente al OWASP Top 10:2025, distinguiendo reglas instaladas, observadas y probadas.'),
  bullet('Integrar un RASP y un monitoreo de API que detecten comportamientos anómalos sin degradar la disponibilidad.'),
  bullet('Centralizar los registros de auditoría en un SIEM con reglas de correlación y alerta, y asegurar el propio SIEM.'),
  bullet('Construir la matriz de decisiones, la categorización por tipo e impacto y las matrices de calor inherente y residual.'),

  // ======================= 1 =======================
  h1('1. Estrategia de Mitigación y Ciberseguridad'),
  p('La estrategia aplica defensa en profundidad. El WAF filtra en el perímetro; el RASP vigila dentro de la aplicación las operaciones peligrosas; el endurecimiento del contenedor de la Fase 5 contiene el daño; y el SIEM observa todas las capas. Ninguna capa se considera suficiente por sí misma, y los controles compensatorios no sustituyen a la corrección de la causa en el código.'),
  h2('1.1 Arquitectura operativa y defensa en profundidad'),
  ...fig('arq', 'v2-01-arquitectura.png', 'Arquitectura operativa de la Fase 6 (versión de cierre): WAF en el perímetro, aplicación con RASP e integración rasp-guard en una red interna, y SIEM que consulta Docker a través de un proxy de solo lectura; todo expuesto solo en 127.0.0.1.'),
  p('El entorno se levanta con `make ops-up`, un archivo de Compose adicional que no altera la configuración auditada en la Fase 5. En la validación el WAF se publicó en `127.0.0.1:8088` porque el puerto 8080 estaba ocupado por un proceso Java del equipo, que no se interrumpió. La configuración resuelta de Compose publica solo `127.0.0.1:8088`, `127.0.0.1:3001` (Grafana) y `127.0.0.1:3100` (Loki). La telemetría externa está desactivada por configuración en los cuatro componentes; el tráfico de red saliente no se auditó con captura de red.'),
  ...fig('stack', 'v2-10-stack.png', 'Estado de los seis contenedores del entorno de operaciones tras la validación: WAF y aplicación healthy; solo Loki, Grafana y el WAF publican puertos, y únicamente en 127.0.0.1.', 600, 260),
  h2('1.2 Controles compensatorios por riesgo'),
  p(`Cada uno de los 24 riesgos tiene al menos un control, clasificado por tipo (preventivo, detectivo, de contención, de eliminación, de evitación o de transferencia) y por nivel de verificación. La Tabla ${TAB.controles} muestra el control principal de cada riesgo: el primero probado que no es solo detectivo o, si no existe, el control planificado. El detalle con todas las evidencias está en el Anexo D.`),
  ...tabla('controles', 'Control compensatorio principal por riesgo y su nivel de verificación',
    [['ID', 'Riesgo', 'Control principal', 'Tipo', 'Verificación']].concat(R.map(r => { const c = principal(r); return [r.id, r.nombre, c.control, c.tipo, VERIF[c.verificacion] || c.verificacion] })),
    [560, 2600, 3900, 1100, 1200], 15),
  p(`Los riesgos sin un control probado (entre ellos R03, R06, R08, R10, R11 y R15) no tienen hoy una protección compensatoria efectiva; su tratamiento depende de correcciones diseñadas o propuestas.`),
  h2('1.3 WAF: reglas para el OWASP Top 10:2025'),
  p('El WAF combina Nginx 1.30.6, ModSecurity 3.0.17 y el OWASP Core Rule Set 4.25.2 en nivel de paranoia 1, en modo de bloqueo con puntuación de anomalía (umbral entrante 5, saliente 4). Sobre el CRS se añadieron dos parches virtuales (100001, rol en el registro; 100002, `/metrics`), denegación de rutas internas, cabeceras de seguridad, ocultación del CORS permisivo y limitación de tasa del inicio de sesión. Un WAF **no** cubre los diez riesgos: cadena de suministro, diseño inseguro e integridad de software requieren medidas fuera del perímetro.'),
  ...fig('crs', '09-crs-inventario.png', 'Inventario de reglas del WAF desplegado: reglas por familia del CRS, configuración efectiva y parches virtuales cargados.', 560, 660),
  ...tabla('owasp', 'Cobertura del OWASP Top 10:2025: regla instalada, observada en logs, vector probado y corrección pendiente',
    [['OWASP 2025', 'Control WAF', 'Instalada', 'Observada', 'Probado y bloqueado', 'Raíz pendiente'],
      ['A01 Broken Access Control', 'Deny de rutas; VP 100001; CRS 930/931', 'Sí', '100001', 'Rutas y rol: 403. BOLA: NO', 'Parches 06 y 08'],
      ['A02 Security Misconfiguration', 'Cabeceras; CORS; deny /metrics + VP 100002; CRS 920/921/913', 'Sí', '920350, 100002', 'Cabeceras, ACAO oculto, /metrics 403', 'Parche 07; config. de la app'],
      ['A03 Supply Chain Failures', '—', '—', '—', 'No aplica al WAF', 'Actualizar dependencias'],
      ['A04 Cryptographic Failures', 'HSTS; CRS 950-956', 'Sí', 'No', 'Solo HSTS presente', 'Parches 03 y 04'],
      ['A05 Injection', 'CRS 942, 941, 932, 934, 943', 'Sí', '942xxx, 949110', 'Solo SQLi; XSS/RCE/LFI configurado, no probado', 'Parches 01, 02 y 05'],
      ['A06 Insecure Design', '—', '—', '—', 'No aplica al WAF', 'Modelado y parches'],
      ['A07 Authentication Failures', 'limit_req 5/min, ráfaga 3', 'Sí', '8 × 429', 'Fuerza bruta desde una IP', 'Limitación por cuenta'],
      ['A08 Integrity Failures', '—', '—', '—', 'No aplica al WAF', '—'],
      ['A09 Logging & Alerting Failures', 'Audit y access log JSON al SIEM', 'Sí', 'Sí', 'Ver 1.6', 'Notificaciones, HA'],
      ['A10 Exceptional Conditions', 'CRS 920 (peticiones malformadas)', 'Sí', '920350', 'No probado', 'Errores sin traza de pila']],
    [1500, 2350, 800, 1100, 2000, 1610], 15),
  p('Reglas observadas en los audit logs de la validación: 920350 (×43, solo advertencia), 942100 (×3), 942190 (×2), 942270 (×2), 942140 (×1), 949110 (×3), 100001 y 100002. El endpoint `/encryptionkeys/jwt.pub` sirve una **clave pública**: no es una vulnerabilidad y su bloqueo es reducción de superficie; el hallazgo real es la clave **privada** embebida en el código (R03). La regla 920350 («Host header is a numeric IP address») apareció en 43 de 43 peticiones auditadas porque el laboratorio se accede por IP, y además vuelve «relevante» cada petición para el audit log. Excluirla en el laboratorio queda como **recomendación**: no se aplicó para no alterar la configuración medida.'),
  h2('1.4 RASP: detección y bloqueo en tiempo de ejecución'),
  p('El RASP es **Aikido Zen 1.8.46** (código abierto, AGPL-3.0), cargado dentro del proceso Node.js con `NODE_OPTIONS` sobre la imagen oficial fijada por digest. Instrumenta `sqlite3`, el sistema de archivos, la ejecución de procesos, las peticiones HTTP salientes y `node:vm`, y sin token no reporta a terceros. Puede solo detectar (`AIKIDO_BLOCK=false`) o bloquear (`AIKIDO_BLOCK=true`).'),
  p('La primera iteración reveló que el modo bloqueo degradaba la disponibilidad. La causa está en el código de Sequelize: cada consulta corre dentro de `conn.serialize(async () => …)` (`query.js:183`). Zen bloquea **lanzando** un error síncrono desde `sqlite3.Database#all`; esa excepción rechaza la promesa de la función `async`, que `serialize` ignora. La consulta nunca se resuelve, la ruta no recibe el error y, según la configuración de Node, el proceso termina o la petición queda colgada.'),
  p('La solución es la integración `deploy/hardened/rasp/rasp-guard.js`, cargada después del agente y sin modificar Juice Shop ni Sequelize. Solo intercepta los errores cuyo mensaje empieza por `Zen has blocked`: los entrega por el callback de `sqlite3`, que es la vía de error que Sequelize sí propaga, y fija HTTP 403 en la respuesta de esa petición. Cualquier otro error se relanza, y se retiró `--unhandled-rejections=warn`, que habría ocultado otros fallos. La Tabla 3 y la Figura 4 comparan las configuraciones medidas sin WAF delante, con el código HTTP real de cada petición, una sonda de disponibilidad y el contador de reinicios.'),
  ...tabla('rasp', 'Configuraciones del RASP medidas sin WAF (A1-A3 = inyecciones SQL del arnés)',
    [['Escenario', 'Configuración', 'A1-A3', 'Disponibilidad', 'Reinicios', 'Lectura'],
      ['2a', 'Monitoreo', '200 (detectadas)', '41/41', '0 → 0', 'Detecta sin bloquear'],
      ['2b', 'Bloqueo por defecto', '000', '1/6', '0 → 1', 'Caída del proceso (auto-DoS)'],
      ['2c', 'Bloqueo + warn', '000 a los 20,0 s', '106/106', '0 → 0', 'Petición colgada: no es bloqueo válido'],
      ['2d', 'Bloqueo + rasp-guard', '403 en 0,04-0,15 s', '41/41', '0 → 0', 'Bloqueo controlado'],
      ['3b', 'Bloqueo + rasp-guard + SIEM', '403', '41/41', '0 → 0', 'Eventos en Loki; alerta en firing']],
    [900, 1900, 1700, 1300, 1000, 2560], 16),
  ...fig('r22', 'v2-02-r22-comparativa.png', 'Resumen literal de la evidencia de los escenarios del RASP: código HTTP y tiempo de A1-A3, disponibilidad medida por la sonda y contador de reinicios.', 600, 230),
  ...fig('caida', 'v2-04-rasp-caida.png', 'Escenario 2b: el primer bloqueo termina el proceso Node (rechazo no manejado), las peticiones obtienen 000 y la sonda falla 5 de 6 veces. Los «MITIGADO» que cuenta el arnés en esta corrida no son mitigaciones.', 600, 520),
  ...fig('integ', 'v2-03-rasp-integrado.png', 'Escenario 2d: cada bloqueo deja «Zen has blocked» y «rasp-guard … (HTTP 403)»; A1-A3 reciben 403 y el contenedor no se reinicia.', 600, 440),
  p('El alcance del RASP tiene límites que conviene declarar. Solo se probó el sink `sqlite3`: los bloqueos en `fs`, `http`, `child_process` y `vm` no se ejercitaron, por lo que R22 queda **ejecutado parcialmente**. El cuerpo del 403 lo genera el manejador de errores de Juice Shop, que muestra una traza de pila (comportamiento preexistente, A10). Además, el RASP no cubre exposiciones de configuración, asignación masiva, rate limit, BOLA ni NoSQL sobre MarsDB: sin WAF, A4-A12 siguen presentes.'),
  h2('1.5 Monitoreo de APIs: heurística de comportamiento anómalo'),
  p('El monitoreo de API se implementa como reglas de correlación sobre el registro de acceso del WAF, que no almacena cabeceras de autorización ni cuerpos. La regla `API_Enumeracion_Objetos_PosibleBOLA` (dos o más cestas distintas con HTTP 200 en cinco minutos) es una **heurística**: no comprueba la propiedad del objeto ni prueba que haya ocurrido un BOLA. La prueba del BOLA es el caso A12 con dos tokens.'),
  ...fig('fp', 'v2-09-falsos-positivos.png', 'Escenario 4: dos usuarios legítimos leen cada uno su propia cesta; todas las operaciones son correctas y, aun así, la heurística BOLA entra en firing: falso positivo demostrado.', 600, 360),
  p('El falso positivo se explica porque la correlación es global: todo el tráfico llega con la IP de la pasarela de Docker y la regla no conoce la identidad del usuario. Hay también un **falso negativo** (por análisis, no probado): un atacante que lea una sola cesta ajena en cinco minutos no alcanza el umbral. Como mejora se propone, sin implementarla, registrar un identificador seudónimo del usuario (por ejemplo, un HMAC del `sub` del JWT, nunca el token) para correlacionar objetos distintos por usuario; seguiría siendo una heurística. La regla de fuerza bruta se activó; la de errores 5xx está configurada, pero no se disparó en ningún escenario.'),
  h2('1.6 SIEM: centralización y correlación de logs'),
  p('El SIEM usa Grafana Alloy v1.10.2 para recolectar, Loki 3.5.5 para almacenar (30 días) y evaluar las reglas cada 15 segundos, y Grafana 12.1.1 para el panel. Las fuentes son el audit log de ModSecurity, el access log JSON del WAF y la salida estándar de la aplicación (incluido el RASP) y del WAF.'),
  ...tabla('reglas', 'Reglas de correlación del SIEM y su estado en los escenarios 3 (vía WAF) y 3b (RASP sin WAF)',
    [['Regla', 'Escenario 3', 'Escenario 3b', 'Comentario'],
      ['WAF_InyeccionSQL_Bloqueada', 'firing', 'firing', '3 eventos CRS 942'],
      ['WAF_ParcheVirtual_Activado', 'firing', 'firing', '100001 y 100002'],
      ['Login_FuerzaBruta_RateLimit', 'firing', 'firing', '8 respuestas 429'],
      ['Acceso_Rutas_Sensibles_Denegado', 'firing', 'firing', '403 en rutas internas'],
      ['API_Enumeracion_Objetos_PosibleBOLA', 'firing', 'firing', 'Heurística con falsos positivos'],
      ['RASP_Ataque_Detectado', 'inactive', 'firing', 'En 3 el WAF frenó la SQLi antes de la app'],
      ['App_Errores_5xx', 'inactive', 'inactive', 'Configurada, no disparada']],
    [3300, 1200, 1300, 3560], 16),
  ...fig('reglas', 'v2-06-siem-reglas.png', 'Estado de las siete reglas: cinco en firing vía WAF (la del RASP queda inactiva porque el WAF frenó la inyección) y la regla del RASP en firing cuando la app se ataca sin WAF.', 600, 420),
  ...fig('grafana', `${V}/03-waf-rasp-siem/capturas/grafana-dashboard-siem.png`, 'Panel del SIEM en Grafana para la ventana de los escenarios 3 y 3b: bloqueos del WAF, SQLi, rate limit, eventos del RASP, reglas por familia, respuestas por código y monitoreo BOLA.', 600, 500),
  ...fig('metricas', 'v2-07-siem-metricas.png', 'Métricas LogQL de la ventana del escenario 3: 13 respuestas 403, 8 respuestas 429, 3 eventos CRS 942, 920350 en 34 de 34 transacciones auditadas y 0 eventos del RASP.', 600, 280),
  p('La seguridad del propio SIEM también se trató (riesgo R24). En la primera iteración Alloy corría como root con `docker.sock` montado `:ro`, pero el montaje de solo lectura **no restringe la API de Docker**: quien controlara Alloy podía crear o ejecutar contenedores. Ahora Alloy corre como uid 473, sin capacidades y sin el socket, y consulta Docker a través de un proxy que solo permite lecturas (Figura 11). Al introducir el proxy, el SIEM dejó de ingerir los logs de contenedores durante unos 11 minutos, porque Alloy necesita `GET /networks`; se corrigió habilitando solo esa lectura. La incidencia muestra que hace falta una alerta por ausencia de datos de cada fuente. Loki sin autenticación, Grafana anónimo en loopback y el nodo único se aceptan temporalmente para el laboratorio: no son una configuración apta para producción.'),
  ...fig('proxy', 'v2-08-proxy-socket.png', 'Proxy del socket de Docker probado desde la red interna: lecturas 200; crear, detener, ejecutar, borrar contenedores y descargar imágenes 403. Alloy sin root, sin capacidades y sin socket.', 600, 420),
  h2('1.7 Validación integral de los controles'),
  p(`La Tabla ${TAB.escenarios} resume los escenarios ejecutados con el mismo arnés (código HTTP real de cada petición; 000 significa sin respuesta y nunca se cuenta como bloqueo). Antes de medir la protección se comprobó que el tráfico legítimo funcionara: en el escenario 4, las nueve operaciones de dos usuarios fueron correctas (siete con código 200/201 y dos inicios de sesión con token emitido), sin falsos positivos del WAF ni del RASP.`),
  ...tabla('escenarios', 'Escenarios de validación y qué capa protege en cada uno',
    [['#', 'Escenario', 'Resultado', 'Capa que actúa'],
      ['1', 'Línea base vulnerable', '11/11 condiciones + BOLA; A1-A3 con 200', 'Ninguna'],
      ['2a-2d', 'RASP sin WAF', 'Ver Tabla 3', 'RASP (solo inyección)'],
      ['3', 'WAF + RASP + SIEM', 'A1-A11 neutralizadas; A12 BOLA vulnerable (200)', 'WAF (perímetro); SIEM (detección)'],
      ['3b', 'RASP sin WAF con SIEM', 'A1-A3 con 403; alerta del RASP en firing', 'RASP + SIEM'],
      ['4', 'Tráfico legítimo', '9 operaciones correctas; heurística BOLA con falso positivo', 'Ninguna bloquea; SIEM alerta de más']],
    [700, 2300, 3700, 2660], 16),
  ...fig('defensa', 'v2-05-defensa-completa.png', 'Escenario 3 a través del WAF: las once condiciones A1-A11 quedan neutralizadas (403 del WAF en 0,008-0,018 s para la SQLi; 429 en fuerza bruta); el caso A12 (BOLA) sigue vulnerable con HTTP 200.', 600, 720),
  p('Los once casos A1-A11 son **condiciones del arnés**, no once explotaciones: cuatro son explotación demostrada y siete son exposiciones, configuraciones inseguras o ausencia de controles. A través del WAF quedan neutralizadas, pero la causa sigue en el código. El BOLA continúa explotable porque un WAF evalúa peticiones, no la propiedad de los objetos; su eliminación requiere desplegar el parche 08, que verifica el propietario y responde 403 y que está validado solo como diff.'),

  // ======================= 2 =======================
  h1('2. Tratamiento Formal del Riesgo'),
  p('El tratamiento sigue el ciclo de ISO/IEC 27005:2022 (identificar, analizar, evaluar, tratar). El registro contiene 24 riesgos: las 20 amenazas STRIDE de la Fase 1 y cuatro riesgos adicionales (despliegue en la nube, cumplimiento de protección de datos, el comportamiento del bloqueo del RASP y la seguridad del propio SIEM). Los datos están en `docs/fase-6/datos/riesgos.json`; `make risk` valida, calcula y regenera tablas y figuras.'),
  h2('2.1 Método de valoración'),
  bullet('**Escala:** probabilidad (P) e impacto (I) de 1 a 5; nivel = P × I: Bajo 1-4, Medio 5-9, Alto 10-16, Crítico 20-25. Es una convención del equipo; ISO/IEC 27005 no prescribe esta aritmética.'),
  bullet('**Inherente:** P = media(Reproducibilidad, Explotabilidad, Descubribilidad) / 2 e I = media(Daño, Afectados) / 2, ambas redondeadas hacia arriba, desde el DREAD de la Fase 1. R21-R24 usan una valoración cualitativa justificada; R22 se apoya en la medición del escenario 2b.'),
  bullet('**Residual:** valor explícito por riesgo, con el razonamiento de P y de I. P solo baja con controles preventivos, de eliminación o de evitación **probados**; I solo baja con contención o respuesta **probadas**. La detección aporta visibilidad y no reduce el impacto. Los controles inspeccionados, diseñados o propuestos no reducen el residual.'),
  bullet(`**Validación automática:** ${nChecks} comprobaciones (24 identificadores, escala, reducciones respaldadas, coherencia entre decisión y estado, aceptaciones con condiciones, transferencias propuestas marcadas como tales, rutas de evidencia existentes y recuentos que suman 24). Una prueba negativa confirma que el validador rechaza reducciones sin control probado.`),
  h2('2.2 Opciones de tratamiento'),
  ...tabla('opciones', 'Opciones de tratamiento y su uso en el proyecto',
    [['Decisión', 'Significado'],
      ['Mitigar', 'Reducir probabilidad o impacto con controles (ISO/IEC 27005: modificar). No elimina la causa.'],
      ['Eliminar', 'Suprimir la causa raíz (corregir el código o la configuración). Registrarla como plan no equivale a haberla eliminado.'],
      ['Evitar', 'No realizar la actividad o retirar la funcionalidad que origina el riesgo.'],
      ['Transferir', 'Compartir el riesgo con un tercero (proveedor gestionado, póliza o contrato). No transfiere la responsabilidad del titular; en este proyecto solo está propuesta.'],
      ['Aceptar', 'Retener el riesgo de forma consciente, documentada, temporal y con condiciones (ISO/IEC 27005: retener).']],
    [1700, 7660], 18),
  h2('2.3 Categorización del riesgo por tipo e impacto'),
  p(`Distribución por tipo: ${['Seguridad', 'Software', 'Técnico', 'Operacional', 'Cloud', 'Cumplimiento'].map(t => `${t} ${cuenta('tipo', t)}`).join('; ')}. Impactos (riesgos que los incluyen): ${['Reputacional', 'Legal', 'Financiero', 'Operacional'].map(i => `${i} ${R.filter(r => r.impactos.includes(i)).length}`).join('; ')}.`),
  ...tabla('registro', 'Registro de riesgos: tipo, impactos (principal primero), OWASP y CWE',
    [['ID', 'Riesgo', 'Tipo', 'Impactos', 'OWASP 2025', 'CWE']].concat(R.map(r => [r.id, r.nombre, r.tipo, r.impactos.join(', '), r.owasp, r.cwe])),
    [560, 3500, 1150, 1900, 1150, 1100], 15),
  h2('2.4 Matriz de decisiones y plan de tratamiento'),
  p(`Cada riesgo tiene una decisión principal y, si aplica, una complementaria, cada una con su estado real: Ejecutado, Ejecutado parcialmente, Planificado, Aceptado temporalmente o Propuesta. Decisiones principales: ${['Mitigar', 'Eliminar', 'Aceptar', 'Evitar', 'Transferir'].map(d => `${d} ${cuenta('decision', d)}`).join(', ')}. Transferir aparece solo como complementaria propuesta (R03, R21, R23): no existe contrato ni póliza, y transferir no exime al titular de su responsabilidad. Una decisión «Eliminar» en estado Planificado no significa que el riesgo esté eliminado.`),
  ...tabla('decisiones', 'Matriz de decisiones: inherente, decisión (estado), complementaria (estado), residual y prioridad',
    [['ID', 'Inherente', 'Decisión (estado)', 'Complementaria (estado)', 'Residual', 'Prioridad']].concat(R.map(r => [r.id, `${r.P_inh}×${r.I_inh}=${r.S_inh} ${r.N_inh}`, `${r.decision} (${r.estado_tratamiento})`, r.decision_sec ? `${r.decision_sec} (${r.decision_sec_estado})` : '—', `${r.P_res}×${r.I_res}=${r.S_res} ${r.N_res}`, r.prioridad])),
    [560, 1550, 2300, 2300, 1550, 1100], 15),
  ...tabla('plan', 'Plan de tratamiento: responsable (por rol), criterio de revisión y actividad pendiente',
    [['ID', 'Responsable (rol)', 'Revisión', 'Pendiente']].concat(R.map(r => [r.id, r.responsable, r.revision, r.pendiente])),
    [560, 2600, 2900, 3300], 14),
  p('Los responsables se expresan por rol; el equipo asigna la persona de cada rol. Las aceptaciones temporales (Tabla 10) se limitan al laboratorio: en producción no serían aceptaciones automáticas.'),
  ...tabla('aceptaciones', 'Aceptaciones temporales: quién acepta, motivo, condiciones y vigencia',
    [['ID', 'Quién acepta', 'Motivo', 'Condiciones', 'Vigencia']].concat(R.filter(r => r.aceptacion).map(r => [r.id, r.aceptacion.quien, r.aceptacion.motivo, r.aceptacion.condiciones, r.aceptacion.vigencia])),
    [560, 1800, 2400, 2600, 2000], 14),
  h2('2.5 Justificación del riesgo residual'),
  ...tabla('residual', 'Razonamiento del residual por riesgo (P e I)',
    [['ID', 'Inh. → Res.', 'Razón de P', 'Razón de I']].concat(R.map(r => [r.id, `${r.P_inh}×${r.I_inh} → ${r.P_res}×${r.I_res}`, r.razon_P, r.razon_I])),
    [560, 1100, 4700, 3000], 14),
  h2('2.6 Matriz de calor: probabilidad frente a impacto'),
  p('Las figuras ubican cada riesgo según su probabilidad y su impacto antes (inherente) y después (residual) de los controles probados. El número de la esquina de cada celda es el producto P × I.'),
  ...fig('hantes', 'docs/fase-6/img/heatmap-antes.png', `Matriz de calor del riesgo inherente: ${DIST.inherente[3]} riesgos críticos y ${DIST.inherente[2]} altos.`, 520, 520),
  ...fig('hdesp', 'docs/fase-6/img/heatmap-despues.png', `Matriz de calor del riesgo residual (solo controles probados): ${DIST.residual[3]} críticos (${crit.map(r => r.id).join(', ')}), ${DIST.residual[2]} altos, ${DIST.residual[1]} medios y ${DIST.residual[0]} bajo.`, 520, 520),
  ...fig('niveles', 'docs/fase-6/img/niveles-antes-despues.png', 'Distribución de los 24 riesgos por nivel: inherente frente a residual.', 560, 320),
  ...tabla('niveles', 'Riesgos por nivel antes y después de los controles probados',
    [['Nivel', 'Inherente', 'Residual']].concat(NIV.map((n, i) => [n, String(DIST.inherente[i]), String(DIST.residual[i])])).concat([['Total', String(DIST.inherente.reduce((a, b) => a + b)), String(DIST.residual.reduce((a, b) => a + b))]]),
    [3000, 3000, 3000], 18),
  h2('2.7 Lectura del riesgo residual'),
  bullet(`Quedan **${crit.length} riesgos críticos** (${crit.map(r => r.id).join(', ')}) y **${altos.length} altos**. La mayoría depende de correcciones de código diseñadas o propuestas, no desplegadas, y por eso no recibe reducción.`),
  bullet('Los controles desplegados son sobre todo **compensatorios**: reducen la probabilidad de los vectores probados en el perímetro y en ejecución, pero no eliminan la causa. Por eso las inyecciones SQL (R01, R02) bajan de Crítico a Alto y no más: el impacto, si un ataque prospera, es el mismo.'),
  bullet('**R06 (BOLA)** sigue crítico: la lectura cruzada continúa con HTTP 200 a través del WAF y la heurística del SIEM no protege. **R03** sigue crítico porque ningún control detecta un token forjado.'),
  bullet('**R21** es Bajo solo porque la nube no está desplegada (evitación probada); eso no valida la seguridad de la infraestructura, que debería probarse en ejecución antes de desplegar.'),
  bullet('**R22** y **R24** son riesgos introducidos por los propios controles. Se identificaron, se trataron y se verificaron dentro de la fase: un control nuevo también es una fuente de riesgo.'),

  // ======================= cierre =======================
  h1('Limitaciones y pendientes'),
  bullet('Parches 01-08 diseñados, no desplegados: la aplicación no se recompiló. Son la vía para reducir R01-R03, R05-R07, R09 y R14 y para cerrar el BOLA.'),
  bullet('WAF: solo la familia de inyección SQL está probada; XSS, RCE, LFI y fugas en respuestas están configuradas, sin prueba. La exclusión de la regla 920350 es una recomendación.'),
  bullet('RASP: los bloqueos en sinks distintos de `sqlite3` no se probaron; la respuesta 403 incluye la traza de pila del manejador de errores de Juice Shop.'),
  bullet('Monitoreo de API: la heurística BOLA tiene falsos positivos (demostrado) y falsos negativos (por análisis); la regla de 5xx no se validó con una ráfaga real.'),
  bullet('SIEM: un solo nodo, sin autenticación en Loki, sin notificaciones externas y sin alerta por pérdida de ingesta; el proxy del socket sigue siendo un componente de confianza.'),
  bullet('Nube (Fase 2): diseñada y validada estáticamente (plan sin conexión y Checkov), no desplegada; su seguridad en ejecución no está verificada.'),
  bullet('Documento: este archivo es un borrador de validación; la carátula institucional (logo oficial de la UMG) y la maquetación final las integra el equipo.'),
  h1('Conclusiones', false),
  p('La Fase 6 integró y validó una estrategia de defensa en profundidad con evidencia reproducible. El WAF neutralizó las once condiciones del arnés sin bloquear el tráfico legítimo. El RASP, con una integración que corrige un defecto de disponibilidad, bloquea las inyecciones SQL con HTTP 403 incluso con el perímetro evadido. El SIEM centraliza y correlaciona los eventos de las tres fuentes y activó cinco de siete reglas a través del WAF, más la del RASP cuando la aplicación se atacó directamente.'),
  p('La validación también demostró lo que los controles no hacen. El BOLA sigue abierto a través de todas las capas; la heurística de API produce falsos positivos; y la protección de la nube es solo de diseño. Operar los controles reveló además defectos que solo aparecen en funcionamiento: el bloqueo del RASP provocaba la caída del proceso o dejaba peticiones colgadas, el healthcheck del WAF lo marcaba como no saludable, el montaje de solo lectura del socket de Docker no protegía su API y el propio SIEM perdió la ingesta durante minutos. Todos se corrigieron o quedaron documentados con evidencia.'),
  p(`El tratamiento formal, con el residual justificado riesgo por riesgo y validado automáticamente, reduce los críticos de ${DIST.inherente[3]} a ${DIST.residual[3]} y los altos de ${DIST.inherente[2]} a ${DIST.residual[2]}. Es una reducción menor que la de una lectura optimista, pero defendible: el riesgo crítico restante depende de correcciones de código diseñadas y no desplegadas, que son la prioridad del trabajo siguiente.`),

  h1('Referencias'),
  ...[
    'Aikido Security. (2026). Zen for Node.js (Versión 1.8.46) [Software]. https://github.com/AikidoSec/firewall-node',
    'Grafana Labs. (s. f.-a). Grafana Alloy documentation. https://grafana.com/docs/alloy/latest/',
    'Grafana Labs. (s. f.-b). Grafana Loki documentation. https://grafana.com/docs/loki/latest/',
    'International Organization for Standardization. (2022). Information security, cybersecurity and privacy protection — Guidance on managing information security risks (ISO/IEC 27005:2022).',
    'Kent, K., y Souppaya, M. (2006). Guide to computer security log management (NIST Special Publication 800-92). National Institute of Standards and Technology. https://doi.org/10.6028/NIST.SP.800-92',
    'Kimminich, B. (2026). OWASP Juice Shop (Versión 20.3.0) [Software]. OWASP Foundation. https://github.com/juice-shop/juice-shop',
    'MITRE Corporation. (s. f.). CWE: Common Weakness Enumeration. https://cwe.mitre.org/',
    'OWASP CRS Project. (s. f.). OWASP CRS (Versión 4.25.2) [Software]. https://coreruleset.org/',
    'OWASP Foundation. (2023). OWASP API Security Top 10 – 2023. https://owasp.org/API-Security/editions/2023/en/0x11-t10/',
    'OWASP Foundation. (2025). OWASP Top 10:2025. https://owasp.org/Top10/2025/',
    'OWASP Foundation. (s. f.). ModSecurity (Versión 3.0.17) [Software]. https://github.com/owasp-modsecurity/ModSecurity',
    'Tecnativa. (s. f.). docker-socket-proxy (Versión 0.4.1) [Software]. https://github.com/Tecnativa/docker-socket-proxy'
  ].map(t => new Paragraph({ alignment: AlignmentType.LEFT, spacing: { line: 360, after: 120 }, indent: { left: convertInchesToTwip(0.5), hanging: convertInchesToTwip(0.5) }, children: [run(t)] })),

  h1('Anexos'),
  h2Libre('Anexo A. Integridad de la evidencia de la Fase 6'),
  p(`Extracto de \`evidence/MANIFEST.sha256\` (${manifest6.length} archivos de la Fase 6). Por espacio se muestran los primeros 16 caracteres de cada SHA-256; el valor completo está en el manifiesto y se verifica con \`sha256sum -c MANIFEST.sha256\` desde \`evidence/\`. El manifiesto solo incluye archivos versionados.`, { indent: false }),
  ...code(manifest6.map(l => l.replace(/^([0-9a-f]{16})[0-9a-f]{48} \*\.\//, '$1…  ')), 13),
  h2Libre('Anexo B. Bitácora de comandos de la Fase 6'),
  p('Entradas de `evidence/bitacora.md` con fase 6 (fecha, comando, herramienta y resultado). Las entradas «CORRECCIÓN» documentan corridas cuyos resultados del arnés no son mitigaciones.', { indent: false }),
  ...bitacora6.map(l => {
    const c = l.split('|').map(s => s.trim())
    return new Paragraph({ spacing: { after: 90, line: 264 }, children: [run(`${c[1]} · `, { bold: true, size: 17 }), run(c[3].replace(/`/g, ''), { mono: true, size: 15 }), run(` · ${c[4]} · ${c[5]}`, { size: 17 })] })
  }),
  h2Libre('Anexo C. Reglas de correlación del SIEM (LogQL)'),
  p('Contenido de `deploy/hardened/siem/rules/fake/alertas.yaml`, evaluado por el ruler de Loki.', { indent: false }),
  ...code(alertas),
  h2Libre('Anexo D. Controles por riesgo: implementación, verificación y evidencia'),
  ...R.flatMap(r => [
    new Paragraph({ keepNext: true, spacing: { before: 140, after: 40 }, children: [run(`${r.id} — ${r.nombre}`, { bold: true, size: 20 })] }),
    ...r.controles.map(c => new Paragraph({ spacing: { after: 30, line: 260 }, indent: { left: convertInchesToTwip(0.3) }, children: [run(`• ${c.control} `, { size: 18 }), run(`[${c.tipo}; ${VERIF[c.verificacion] || c.verificacion}] `, { size: 18, it: true }), run(c.evidencia, { mono: true, size: 15 })] })),
    ...(r.nota ? [new Paragraph({ spacing: { after: 60 }, indent: { left: convertInchesToTwip(0.3) }, children: [run(`Nota: ${r.nota}`, { size: 18, it: true })] })] : [])
  ]),
  h2Libre('Anexo E. Validación automática del registro de riesgos'),
  p(`Resumen de \`docs/fase-6/datos/validacion-consistencia.txt\`: ${nChecks} comprobaciones superadas y 0 fallas. Prueba negativa (\`prueba-negativa-validador.txt\`): al forzar sobre una copia una reducción de P en R13 (CSP solo inspeccionada) y de I en R04 (SCA, control detectivo), el validador termina con código 1 y señala ambas reglas.`, { indent: false })
]

const doc = new Document({
  creator: 'MASI-UMG 2026',
  title: 'Fase 6 - Operaciones, Monitoreo y Ciberseguridad (borrador de validación)',
  styles: {
    default: {
      document: { run: { font: ARIAL, size: 24 } },
      heading1: { run: { font: ARIAL, size: 30, bold: true, color: BLUE }, paragraph: { spacing: { before: 280, after: 140 }, keepNext: true, outlineLevel: 0 } },
      heading2: { run: { font: ARIAL, size: 26, bold: true, color: '2E2E2E' }, paragraph: { spacing: { before: 220, after: 100 }, keepNext: true, outlineLevel: 1 } }
    }
  },
  numbering: { config: [{ reference: 'vinetas', levels: [{ level: 0, format: LevelFormat.BULLET, text: '•', alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: convertInchesToTwip(0.5), hanging: convertInchesToTwip(0.25) } } } }] }] },
  sections: [
    { properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1440, bottom: 1440, left: 1440, right: 1440 } } }, children: caratula },
    {
      properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1440, bottom: 1440, left: 1440, right: 1440 } } },
      footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ children: ['Página ', PageNumber.CURRENT], font: ARIAL, size: 18 })] })] }) },
      children: [...indice, ...body]
    }
  ]
})

if (nFig !== Object.keys(FIG).length || nTab !== Object.keys(TAB).length) throw new Error(`Numeración incompleta: ${nFig} figuras, ${nTab} tablas`)
Packer.toBuffer(doc).then(b => {
  fs.writeFileSync(OUT, b)
  fs.writeFileSync(path.join(__dirname, 'toc-entradas.json'), JSON.stringify(ENTRADAS.map(e => e[0])))
  console.log('OK borrador', path.basename(OUT), b.length, 'bytes ·', nFig, 'figuras ·', nTab, 'tablas')
})
