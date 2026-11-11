// Genera el documento Word de la Fase 6 (APA 7, Arial 12, justificado, interlineado 1.5).
// Datos: docs/fase-6/datos/riesgos-calculados.json, evidencia de evidence/fase-6, bitácora y MANIFEST.
// Uso (Docker): node build.js  -> ../Fase6_Operaciones_Monitoreo_Ciberseguridad.docx
// El índice usa toc-paginas.json (generado en una segunda pasada a partir del PDF) si existe.
const fs = require('fs')
const path = require('path')
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType, ImageRun,
  Table, TableRow, TableCell, WidthType, BorderStyle, ShadingType, PageBreak,
  Footer, PageNumber, LevelFormat, TabStopType, LeaderType, Tab, convertInchesToTwip
} = require('docx')

const ROOT = path.resolve(__dirname, '../../../..')
const F6 = path.join(ROOT, 'docs/fase-6')
const IMG = path.join(F6, 'entregable/img')
const OUT = path.join(F6, 'entregable/Fase6_Operaciones_Monitoreo_Ciberseguridad.docx')
const ARIAL = 'Arial'
const BLUE = '1F3864'
const R = JSON.parse(fs.readFileSync(path.join(F6, 'datos/riesgos-calculados.json'), 'utf8')).riesgos
const TOC = fs.existsSync(path.join(__dirname, 'toc-paginas.json')) ? JSON.parse(fs.readFileSync(path.join(__dirname, 'toc-paginas.json'), 'utf8')) : {}

// ---------- helpers ----------
function pngSize (buf) { return { w: buf.readUInt32BE(16), h: buf.readUInt32BE(20) } }
let nFig = 0
let nTab = 0
const figuras = []
function fig (file, caption, maxW = 600, maxH = 760) {
  const full = file.includes('/') ? path.join(ROOT, file) : path.join(IMG, file)
  const buf = fs.readFileSync(full)
  const { w, h } = pngSize(buf)
  const s = Math.min(maxW / w, maxH / h, 1)
  nFig++
  figuras.push(caption)
  return [
    new Paragraph({ alignment: AlignmentType.CENTER, keepNext: true, spacing: { before: 120, after: 40 }, children: [new ImageRun({ type: 'png', data: buf, transformation: { width: Math.round(w * s), height: Math.round(h * s) } })] }),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 220 }, children: [new TextRun({ text: `Figura ${nFig}. `, bold: true, font: ARIAL, size: 20 }), new TextRun({ text: caption, italics: true, font: ARIAL, size: 20 })] })
  ]
}
const run = (text, o = {}) => new TextRun({ text, font: o.mono ? 'Consolas' : ARIAL, size: o.size || 24, bold: o.bold, italics: o.it, color: o.color })
// Texto con **negrita** y `código` sencillos
function rich (text, size = 24) {
  const out = []
  const re = /(\*\*[^*]+\*\*|`[^`]+`)/g
  let last = 0
  let m
  while ((m = re.exec(text))) {
    if (m.index > last) out.push(run(text.slice(last, m.index), { size }))
    const t = m[0]
    if (t.startsWith('**')) out.push(run(t.slice(2, -2), { bold: true, size }))
    else out.push(run(t.slice(1, -1), { mono: true, size: size - 2 }))
    last = m.index + t.length
  }
  if (last < text.length) out.push(run(text.slice(last), { size }))
  return out
}
const p = (text, o = {}) => new Paragraph({
  alignment: o.align || AlignmentType.JUSTIFIED,
  spacing: { line: 360, after: o.after ?? 160 },
  indent: o.indent === false ? undefined : { firstLine: convertInchesToTwip(0.5) },
  children: Array.isArray(text) ? text : rich(text)
})
const bullet = (text) => new Paragraph({ alignment: AlignmentType.JUSTIFIED, spacing: { line: 360, after: 80 }, numbering: { reference: 'vinetas', level: 0 }, children: rich(text) })
const h1 = (text) => new Paragraph({ heading: HeadingLevel.HEADING_1, pageBreakBefore: true, children: [new TextRun({ text, font: ARIAL })] })
const h2 = (text) => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun({ text, font: ARIAL })] })
function tabla (titulo, rows, widths, size = 18) {
  nTab++
  const total = widths.reduce((a, b) => a + b, 0)
  const mk = (txt, head, w) => new TableCell({
    width: { size: w, type: WidthType.DXA },
    shading: head ? { type: ShadingType.CLEAR, fill: BLUE, color: 'auto' } : undefined,
    margins: { top: 30, bottom: 30, left: 70, right: 70 },
    children: [new Paragraph({ spacing: { after: 0, line: 252 }, children: head ? [new TextRun({ text: txt, font: ARIAL, size, bold: true, color: 'FFFFFF' })] : rich(String(txt), size) })]
  })
  return [
    new Paragraph({ keepNext: true, spacing: { before: 160, after: 40 }, children: [run(`Tabla ${nTab}`, { bold: true, size: 22 })] }),
    new Paragraph({ keepNext: true, spacing: { after: 80 }, children: [run(titulo, { it: true, size: 22 })] }),
    new Table({ width: { size: total, type: WidthType.DXA }, columnWidths: widths, rows: rows.map((r, i) => new TableRow({ tableHeader: i === 0, cantSplit: true, children: r.map((c, j) => mk(c, i === 0, widths[j])) })) }),
    new Paragraph({ spacing: { after: 120 }, children: [run('Nota. Elaboración propia con datos del repositorio del laboratorio.', { size: 18, it: true })] })
  ]
}
const code = (lines) => lines.map((l, i) => new Paragraph({ spacing: { after: 0, line: 240 }, shading: { type: ShadingType.CLEAR, fill: 'F2F2F2', color: 'auto' }, children: [new TextRun({ text: l || " ", font: "Consolas", size: 14 })], keepLines: true }))

// ---------- carátula ----------
const caratula = [
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 240, after: 60 }, border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: BLUE } }, children: [run('[ Logo oficial UMG — insertar ]', { it: true, color: '808080', size: 20 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 240, after: 60 }, children: [run('UNIVERSIDAD MARIANO GÁLVEZ DE GUATEMALA', { bold: true, size: 28 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 40 }, children: [run('Maestría en Seguridad Informática', { size: 24 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 400 }, children: [run('Curso: Seguridad en Aplicaciones', { size: 24 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 600, after: 120 }, children: [run('Laboratorio de Seguridad de Aplicaciones sobre OWASP Juice Shop', { bold: true, size: 32, color: BLUE })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 900 }, children: [run('Fase 6: Operaciones, Monitoreo y Ciberseguridad', { bold: true, size: 28 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 400, after: 40 }, children: [run('Integrantes:', { bold: true })] }),
  ...['Molina Pérez, Juan Carlos', 'Sánchez Flores, Juan Walter Ernesto', 'García Gonzalez, Leopoldo Emanuel', 'Cambara Castillo, Vanessa Odeth']
    .map(n => new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 20 }, children: [run(n, { size: 22 })] })),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 300, after: 20 }, children: [run('Catedrático: Ing. Matthew Alexander Seigne Samayoa', { size: 22 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 300 }, children: [run('Guatemala, noviembre de 2026', { size: 22 })] })
]

// ---------- índice (dos pasadas: páginas reales leídas del PDF) ----------
const ENTRADAS = [
  ['Introducción'], ['Objetivos'],
  ['1. Estrategia de Mitigación y Ciberseguridad'],
  ['1.1 Arquitectura operativa y defensa en profundidad', 1], ['1.2 Controles compensatorios por riesgo', 1],
  ['1.3 WAF: reglas para bloquear el OWASP Top 10:2025', 1], ['1.4 RASP y monitoreo de APIs en tiempo de ejecución', 1],
  ['1.5 SIEM: centralización de logs de auditoría', 1], ['1.6 Verificación integral de los controles', 1],
  ['2. Tratamiento Formal del Riesgo'],
  ['2.1 Método de valoración reproducible', 1], ['2.2 Opciones de tratamiento', 1],
  ['2.3 Categorización del riesgo por tipo e impacto', 1], ['2.4 Matriz de decisiones por riesgo', 1],
  ['2.5 Matriz de calor: probabilidad frente a impacto', 1], ['2.6 Lectura del riesgo residual', 1],
  ['Limitaciones y trabajo futuro'], ['Conclusiones'], ['Referencias'], ['Anexos']
]
const tocLine = (text, sub) => new Paragraph({
  spacing: { after: sub ? 30 : 60, line: 300 },
  indent: sub ? { left: convertInchesToTwip(0.3) } : undefined,
  tabStops: [{ type: TabStopType.RIGHT, position: 9360, leader: LeaderType.DOT }],
  children: [new TextRun({ text, font: ARIAL, size: sub ? 22 : 24, bold: !sub }), new TextRun({ children: [new Tab(), String(TOC[text] || '')], font: ARIAL, size: sub ? 22 : 24, bold: !sub })]
})
const indice = [new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun({ text: 'Índice', font: ARIAL })] }), ...ENTRADAS.map(([t, s]) => tocLine(t, !!s))]

// ---------- datos derivados ----------
const cuenta = (k, v) => R.filter(r => r[k] === v).length
const NIV = ['Bajo', 'Medio', 'Alto', 'Crítico']
const resAltos = R.filter(r => ['Alto', 'Crítico'].includes(r.N_res))
const ESTADO = { verificado: 'Verificado', disenado: 'Diseñado (diff validado)', propuesto: 'Propuesto', no_efectivo: 'NO efectivo (verificado)' }
const bitacora6 = fs.readFileSync(path.join(ROOT, 'evidence/bitacora.md'), 'utf8').split('\n').filter(l => /^\| 2026-11-10T[^|]*\| 6 \|/.test(l) || (/^\| 2026-11-10T/.test(l) && l.includes('fase-6')))
const manifest6 = fs.readFileSync(path.join(ROOT, 'evidence/MANIFEST.sha256'), 'utf8').split('\n').filter(l => l.includes('./fase-6/'))
const alertas = fs.readFileSync(path.join(ROOT, 'deploy/hardened/siem/rules/fake/alertas.yaml'), 'utf8').split('\n')

// ---------- cuerpo ----------
const body = [
  new Paragraph({ heading: HeadingLevel.HEADING_1, pageBreakBefore: true, children: [new TextRun({ text: 'Introducción', font: ARIAL })] }),
  p('El presente documento recopila la evidencia de la Fase 6 del laboratorio de Seguridad de Aplicaciones desarrollado sobre OWASP Juice Shop versión 20.3.0. Esta fase traslada los hallazgos de las fases de ciberdefensa (Fases 4 y 5) al plano de las **operaciones**: define controles compensatorios para cada riesgo, los integra en un entorno ejecutable y verifica, con pruebas repetibles, qué protegen realmente y qué no. Los componentes operativos son un cortafuegos de aplicaciones web (WAF), una protección en tiempo de ejecución dentro de la aplicación (RASP) con monitoreo de API, y un sistema de gestión de eventos (SIEM) que centraliza los registros de auditoría y genera alertas.'),
  p('La segunda parte formaliza el **tratamiento del riesgo** siguiendo ISO/IEC 27005: cada riesgo se categoriza por tipo e impacto, recibe una decisión (aceptar, eliminar, evitar, mitigar o transferir) y se representa en una matriz de calor de probabilidad frente a impacto antes y después de los controles. Para evitar valoraciones arbitrarias, la probabilidad y el impacto se derivan del análisis DREAD de la Fase 1 mediante un procedimiento reproducible, y solo los controles **verificados con evidencia** reducen el riesgo residual.'),
  p('Todas las pruebas se ejecutaron bajo las reglas de aislamiento del laboratorio: los servicios solo escucharon en la dirección de bucle local (127.0.0.1) o en redes internas de Docker, únicamente se evaluaron instancias propias y ningún componente envió telemetría a servicios externos. Cada resultado remite a archivos de evidencia cuyo hash SHA-256 figura en el manifiesto del repositorio (Anexo A) y a la bitácora de comandos (Anexo B).'),
  p([run('Repositorio del proyecto: '), run('https://github.com/jmolinap1-universidad/juice-shop-lab', { color: BLUE })], { indent: false }),

  new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun({ text: 'Objetivos', font: ARIAL })], spacing: { before: 360 } }),
  h2('Objetivo general'),
  p('Operar la aplicación endurecida con controles de ciberseguridad en capas —perímetro, ejecución y monitoreo— y tratar formalmente cada riesgo identificado, demostrando con evidencia verificable la reducción del riesgo inherente al riesgo residual.'),
  h2('Objetivos específicos'),
  bullet('Definir un control compensatorio para cada riesgo identificado en las fases de ciberdefensa, indicando su tipo, estado y evidencia.'),
  bullet('Configurar un WAF con reglas que cubran el OWASP Top 10:2025 y verificar su efecto sin bloquear el tráfico legítimo.'),
  bullet('Integrar un RASP y reglas de monitoreo de API que detecten comportamientos anómalos en tiempo de ejecución.'),
  bullet('Centralizar los registros de auditoría en un SIEM con reglas de correlación y alerta.'),
  bullet('Construir la matriz de decisiones de tratamiento, la categorización por tipo e impacto y las matrices de calor antes y después de los controles.'),

  // ======================= 1 =======================
  h1('1. Estrategia de Mitigación y Ciberseguridad'),
  p('La estrategia aplica defensa en profundidad: ningún control se considera suficiente por sí mismo. El WAF filtra en el perímetro; el RASP vigila dentro de la aplicación las operaciones peligrosas (consultas a la base de datos, acceso a archivos, llamadas de red); el endurecimiento del contenedor de la Fase 5 contiene el daño si algo se ejecuta; y el SIEM observa todas las capas para detectar lo que las demás no bloquean. La capa de operaciones se añadió como un archivo de Compose adicional, sin modificar la configuración auditada en la Fase 5.'),
  h2('1.1 Arquitectura operativa y defensa en profundidad'),
  ...fig('00-arquitectura.png', 'Arquitectura operativa de la Fase 6: WAF en el perímetro, aplicación con RASP en una red interna sin puertos publicados y SIEM (Alloy, Loki y Grafana) en una red propia; todo expuesto solo en 127.0.0.1.'),
  p('El entorno se levanta con `make ops-up` (equivalente a `docker compose -f docker-compose.yml -f docker-compose.ops.yml up -d --build` en `deploy/hardened/`). En esta ejecución el WAF se publicó en `127.0.0.1:8088` porque el puerto 8080 estaba ocupado por un proceso Java del equipo; no se interrumpió ese proceso y el puerto quedó parametrizado (`WAF_PORT`). Ningún componente reporta a terceros: el RASP se ejecuta sin token de su proveedor (registra «No token provided, disabling reporting»), Loki y Alloy tienen la telemetría desactivada y Grafana se sirve en solo lectura, sin formulario de inicio de sesión.'),
  ...fig('10-stack.png', 'Estado de los cinco contenedores del entorno de operaciones (docker ps): WAF y aplicación con RASP en estado healthy; Loki (3100) y Grafana (3001) publicados solo en 127.0.0.1.', 600, 300),
  p('Durante la puesta en marcha se detectó y corrigió un fallo operativo heredado: el healthcheck de la imagen del WAF consulta `https://localhost:8443/healthz`, pero la plantilla del laboratorio solo sirve HTTP en el puerto 8080, por lo que el contenedor figuraba como **unhealthy** aunque filtraba correctamente. Un orquestador lo habría reiniciado o retirado de servicio. Se reemplazó por una comprobación HTTP sobre el mismo endpoint `/healthz`, y el estado pasó a healthy sin cambios en el tráfico (Figura 2).'),

  h2('1.2 Controles compensatorios por riesgo'),
  p('Para cada uno de los 24 riesgos del registro (Sección 2) se definió al menos un control, clasificado por tipo —preventivo, detectivo, de contención, de eliminación, de evitación o de transferencia— y por estado: **verificado** (con evidencia en el repositorio), **diseñado** (corrección validada como diff con `git apply --check`, no desplegada) o **propuesto**. La Tabla 1 resume el control compensatorio principal por riesgo; el detalle completo con todas las evidencias está en el Anexo D.'),
  ...tabla('Control compensatorio principal por riesgo y estado',
    [['ID', 'Riesgo', 'Control compensatorio principal', 'Tipo', 'Estado']].concat(R.map(r => {
      const ver = r.controles.find(c => c.estado === 'verificado' && c.tipo !== 'eliminacion') || r.controles.find(c => c.estado === 'verificado') || r.controles[0]
      return [r.id, r.nombre, ver.control, ver.tipo, ESTADO[ver.estado] || ver.estado]
    })), [620, 2700, 3700, 1100, 1240], 16),
  p('Los riesgos cuyo único control está diseñado o propuesto (por ejemplo R03, clave privada JWT embebida; R08, inyección NoSQL; R10, XXE) no tienen hoy un control compensatorio efectivo desplegado; se mantienen así en el registro para no sobrestimar la protección.'),

  h2('1.3 WAF: reglas para bloquear el OWASP Top 10:2025'),
  p('El WAF combina Nginx 1.30.6, ModSecurity 3.0.17 y el OWASP Core Rule Set (CRS) 4.25.2 en nivel de paranoia 1, en modo de bloqueo y con puntuación de anomalía (umbral entrante 5, saliente 4). Sobre el CRS se añadieron controles propios: dos parches virtuales (100001, asignación masiva del rol en el registro; 100002, endpoint `/metrics`), denegación de rutas internas, cabeceras de seguridad, ocultación del CORS permisivo de la aplicación y limitación de tasa del inicio de sesión. La Figura 3 muestra el inventario real de reglas cargadas, extraído del contenedor en ejecución.'),
  ...fig('09-crs-inventario.png', 'Inventario de reglas del WAF desplegado: número de reglas por familia del CRS, configuración efectiva (paranoia, umbrales, motor) y parches virtuales propios cargados.', 560, 700),
  ...tabla('Cobertura del OWASP Top 10:2025 por los controles del WAF',
    [['OWASP Top 10:2025', 'Control en el WAF', 'Reglas', 'Verificación'],
      ['A01 Broken Access Control', 'Deny de rutas internas; VP 100001; CRS 930/931 (LFI/RFI)', '27', 'Rutas y VP bloquean (403). El BOLA NO es bloqueable por un WAF (verificado)'],
      ['A02 Security Misconfiguration', 'Cabeceras; ocultar CORS; deny /metrics + VP 100002; CRS 920/921, 913', '103', 'Cabeceras, CORS y /metrics verificados; CRS 920 activo'],
      ['A03 Software Supply Chain Failures', '— (no es función del WAF)', '—', 'SCA en CI (Fase 3)'],
      ['A04 Cryptographic Failures', 'HSTS; CRS 950-956 (fugas en respuestas)', '125', 'HSTS presente; 95x sin eventos'],
      ['A05 Injection', 'CRS 942 (SQLi), 941 (XSS), 932 (RCE), 934 (genérica, Node.js), 943', '195', 'CRS 942 bloqueó las 3 SQLi'],
      ['A06 Insecure Design', '— (diseño)', '—', 'Modelado de amenazas y parches'],
      ['A07 Authentication Failures', 'limit_req 5/min, ráfaga 3 en el login (429)', '—', '8 respuestas 429'],
      ['A08 Software or Data Integrity Failures', '—', '—', 'No aplica al WAF'],
      ['A09 Security Logging and Alerting Failures', 'Audit log y access log en JSON hacia el SIEM', '—', 'Ingestado en Loki (1.5)'],
      ['A10 Mishandling of Exceptional Conditions', 'CRS 920 (peticiones malformadas); alerta de 5xx', '68', 'Configurado; sin ráfagas 5xx']],
    [2100, 3300, 800, 3160], 16),
  p('La columna «Reglas» suma las reglas con identificador de las familias del CRS indicadas (Figura 3). Se identificó además **ruido operativo**: la regla 920350 («Host header is a numeric IP address») se activa en casi todas las peticiones porque el laboratorio se accede por IP. Es de severidad *warning* y no bloquea por sí sola, pero consume margen del umbral de anomalía; con un nombre de dominio desaparece. Se propone excluirla en el laboratorio (`SecRuleRemoveById 920350`) como ajuste fino, sin aplicarlo en esta entrega para no alterar la configuración medida.'),

  h2('1.4 RASP y monitoreo de APIs en tiempo de ejecución'),
  p('Como RASP se integró **Aikido Zen 1.8.46**, un agente de código abierto (licencia AGPL-3.0) que se carga dentro del proceso Node.js e instrumenta los puntos donde un ataque produce efecto: el controlador `sqlite3`, el sistema de archivos, la ejecución de procesos, las peticiones HTTP salientes y `node:vm`. Se incorporó sin modificar el código de Juice Shop, con un Dockerfile que copia el agente sobre la imagen oficial fijada por digest y lo precarga mediante `NODE_OPTIONS=--require @aikidosec/firewall`. Tiene dos modos: monitoreo (`AIKIDO_BLOCK=false`, detecta y registra) y bloqueo (`AIKIDO_BLOCK=true`).'),
  ...fig('02-rasp-arranque.png', 'Arranque del agente RASP: sin token no hay reporte externo; se confirman como soportados sqlite3 5.1.7, Express 4.22.3 y los módulos de Node instrumentados.', 600, 420),
  p('Para medir el RASP **aislado del WAF** se ejecutó el mismo arnés de la Fase 4 (`security/attacks/run.sh`) desde la red interna de Docker directamente contra la aplicación, lo que simula que el perímetro fue evadido. Se realizaron tres corridas (Tabla 3).'),
  ...tabla('Corridas del RASP sin WAF delante',
    [['Corrida', 'Configuración', 'Resultado', 'Evidencia'],
      ['1', 'Monitoreo (AIKIDO_BLOCK=false)', '3 SQLi detectadas (body.email; query.q ×2) en sqlite3.all; no se bloquean (esperado)', 'evidence/fase-6/rasp/01-deteccion-sin-bloqueo/'],
      ['2', 'Bloqueo con la configuración por defecto', 'El primer bloqueo terminó el proceso Node (RestartCount=1). Corrida inválida para medir mitigación (HTTP 000)', 'evidence/fase-6/rasp/02-bloqueo-caida-del-proceso/'],
      ['3', 'Bloqueo + --unhandled-rejections=warn', 'A1-A3 bloqueadas en el sink sin caídas (RestartCount 0); A4-A12 siguen vulnerables sin WAF (fuera del alcance del RASP)', 'evidence/fase-6/rasp/03-bloqueo-sin-caida/']],
    [900, 2300, 3700, 2460], 16),
  ...fig('03-rasp-deteccion.png', 'Corrida 1, modo monitoreo: el RASP detecta las tres inyecciones SQL indicando operación (sqlite3.all), origen del dato (body.email, query.q) e IP.', 600, 260),
  p('La corrida 2 reveló un **hallazgo operativo** relevante. En modo bloqueo, el agente lanza un error dentro de Sequelize que queda como rechazo de promesa no manejado y, con la configuración predeterminada de Node.js 24, termina el proceso. Cada intento de inyección detectado se convertía así en una caída del servicio: un atacante podía usar el propio control como vector de denegación de servicio (OWASP A10:2025, CWE-248/755). Los resultados de esa corrida no se usan como mitigación: tras la caída, las peticiones obtuvieron `HTTP 000` (conexión rechazada), que el arnés interpreta como ausencia de datos. La carpeta se conservó y se marcó como inválida.'),
  ...fig('04-rasp-caida.png', 'Corrida 2 (extracto): bloqueo de la inyección en body.email seguido de la excepción no manejada que termina el proceso y del reinicio del agente.', 600, 520),
  p('El riesgo se trató con la decisión **Eliminar**: se configuró `--unhandled-rejections=warn`, de modo que el error queda registrado sin terminar el proceso. La corrida 3 confirmó el bloqueo de A1-A3 en el sink con `RestartCount` igual a 0. Como efecto residual, la petición bloqueada se queda sin respuesta mientras el resto del servicio sigue operativo; la integración definitiva consistiría en capturar el error en la capa de datos y responder 403.'),
  ...fig('05-rasp-bloqueo.png', 'Corrida 3: el RASP bloquea las tres inyecciones (body.email y query.q) sin caída del proceso; RestartCount = 0.', 600, 380),
  p('El **alcance real del RASP** es la inyección en los sinks instrumentados. No cubre exposiciones de configuración (listados, `/metrics`), asignación masiva, ausencia de rate limit ni BOLA (su protección IDOR requiere integrar el identificador de inquilino en el código), y solo soporta inyección NoSQL en MongoDB, no en MarsDB. Por eso es una capa adicional y no sustituye al WAF ni a la corrección del código.'),
  p('El **monitoreo de API** se implementó como reglas de correlación sobre el registro de acceso del WAF, que en formato JSON no incluye cabeceras de autorización ni cuerpos. La regla `API_Enumeracion_Objetos_PosibleBOLA` alerta cuando se consultan dos o más cestas distintas en cinco minutos y es el control **detectivo** del BOLA que el WAF no puede bloquear. `Login_FuerzaBruta_RateLimit` vigila las ráfagas 429 y `App_Errores_5xx` las tasas anómalas de errores. Limitación del laboratorio: todo el tráfico llega desde la IP de la pasarela de Docker, por lo que la correlación es global; en producción se agruparía por cliente o usuario.'),

  h2('1.5 SIEM: centralización de logs de auditoría'),
  p('El SIEM se construyó con la pila de Grafana: **Alloy v1.10.2** recolecta los registros, **Loki 3.5.5** los almacena (retención de 30 días) y evalúa las reglas de correlación cada 15 segundos, y **Grafana 12.1.1** presenta el panel de seguridad. Las fuentes son el audit log de ModSecurity (una transacción JSON por línea), el registro de acceso JSON del WAF y la salida estándar de la aplicación y del WAF, que incluye las detecciones del RASP.'),
  ...tabla('Reglas de correlación y alerta del SIEM y su estado durante las pruebas',
    [['Regla', 'Lógica (ventana de 5 min)', 'Riesgo', 'Estado'],
      ['WAF_InyeccionSQL_Bloqueada', 'Eventos CRS 942xxx > 0', 'R01, R02', 'firing'],
      ['WAF_ParcheVirtual_Activado', 'Reglas 10000x > 0', 'R07, R17', 'firing'],
      ['Login_FuerzaBruta_RateLimit', '≥ 3 respuestas 429', 'R16', 'firing'],
      ['Acceso_Rutas_Sensibles_Denegado', '403 en rutas sensibles > 0', 'R12, R17', 'firing'],
      ['API_Enumeracion_Objetos_PosibleBOLA', '≥ 2 cestas distintas con 200', 'R06', 'firing'],
      ['RASP_Ataque_Detectado', 'Líneas «Zen has blocked|detected» > 0', 'R01, R02', 'firing'],
      ['App_Errores_5xx', '> 5 respuestas 5xx', 'R18', 'inactive']],
    [3100, 3000, 1300, 1960], 17),
  ...fig('07-siem-reglas.png', 'Estado de las reglas del SIEM tras la prueba de defensa completa: seis reglas en firing con su hora de activación; App_Errores_5xx inactiva porque no hubo ráfagas de errores.', 600, 420),
  ...fig('evidence/fase-6/siem/capturas/grafana-dashboard-siem.png', 'Panel «SIEM - Juice Shop endurecido» en Grafana durante el periodo de pruebas: bloqueos del WAF, SQLi bloqueadas, rate limit, eventos del RASP, reglas por familia OWASP, respuestas por código HTTP, monitoreo de BOLA y registros crudos.', 600, 520),
  ...fig('08-siem-metricas.png', 'Métricas del periodo de pruebas obtenidas con consultas LogQL a Loki: 13 respuestas 403, 8 respuestas 429, 3 eventos CRS 942, ambos parches virtuales activados, 3 detecciones y 4 bloqueos del RASP, y 3 cestas distintas accedidas.', 600, 300),
  p('Tras la primera captura se corrigió la expresión de la regla del RASP, que también contaba las líneas de advertencia de Node y daba 11 eventos en lugar de 7 (3 detecciones y 4 bloqueos). Ahora solo cuenta las líneas propias del agente (`^Zen has (blocked|detected)`). El SIEM es de un solo nodo y Alloy lee la salida de los contenedores mediante el socket de Docker en solo lectura; ambos aspectos se registran como riesgo aceptado para el laboratorio (R24).'),

  h2('1.6 Verificación integral de los controles'),
  p('Un control que bloquea tráfico legítimo es un problema operativo. Por eso, antes de medir la protección, se comprobó que la aplicación siguiera funcionando a través del WAF y del RASP: navegación, búsqueda, registro sin el campo `role`, inicio de sesión, consulta de la cesta propia y lectura de reseñas respondieron correctamente (Figura 11), sin falsos positivos.'),
  ...fig('01-funcional.png', 'Control de falsos positivos: seis peticiones legítimas a través de WAF y RASP con respuesta 200/201; el token emitido se redacta en la evidencia.', 600, 300),
  p('A continuación se ejecutó el arnés completo contra el punto de entrada real (WAF y aplicación con RASP). Para que el rate limit del inicio de sesión (control de A10) no impidiera obtener los tokens de las dos cuentas de la prueba de BOLA y se confundiera con un control de autorización, se introdujo una pausa configurable antes del caso A12 (`A12_DELAY=65`).'),
  ...fig('06-defensa-completa.png', 'Defensa completa a través del WAF: A1-A11 mitigados (11/11). El caso A12 (BOLA) sigue vulnerable: la cuenta B leyó la cesta de A con HTTP 200. El encabezado «riesgo inherente» del resultado A12 es un texto fijo del arnés; esta corrida mide el estado residual.', 600, 740),
  p('El resultado confirma el valor y los límites de cada capa. Los once casos A1-A11 quedan mitigados, pero el **BOLA sigue explotable**: un WAF evalúa peticiones, no la propiedad de los objetos, y la petición de la cuenta B es sintácticamente legítima. El SIEM sí lo **detecta** (`API_Enumeracion_Objetos_PosibleBOLA`) y su eliminación requiere la corrección de código del parche 08, que verifica el propietario de la cesta y responde 403; el parche está validado como diff, pero la aplicación no se recompiló en esta entrega.'),

  // ======================= 2 =======================
  h1('2. Tratamiento Formal del Riesgo'),
  p('El tratamiento sigue el ciclo de ISO/IEC 27005:2022: identificar, analizar, evaluar y tratar. El registro contiene **24 riesgos**: las 20 amenazas STRIDE de la Fase 1 (que incluyen los casos A1-A12 de la Fase 4) y cuatro riesgos adicionales (despliegue en la nube, cumplimiento de protección de datos, el hallazgo del RASP y el riesgo que introduce el propio SIEM). Los datos están en `docs/fase-6/datos/riesgos.json`; el cálculo y las figuras se regeneran con `make risk`.'),
  h2('2.1 Método de valoración reproducible'),
  bullet('**Escala:** probabilidad (P) e impacto (I) de 1 a 5; nivel = P × I: Bajo 1-4, Medio 5-9, Alto 10-16, Crítico 20-25.'),
  bullet('**Riesgo inherente:** P = ⌈media(Reproducibilidad, Explotabilidad, Descubribilidad) / 2⌉ e I = ⌈media(Daño, Afectados) / 2⌉, a partir del DREAD de la Fase 1. Los cuatro riesgos sin DREAD (R21-R24) usan una valoración cualitativa del equipo, marcada como tal.'),
  bullet('**Riesgo residual:** solo cuentan los controles verificados con evidencia. Una eliminación o evitación verificada lleva P a 1; si no la hay, un control preventivo verificado resta 2 a P y dos o más restan 3 (mínimo 1). Una detección verificada resta 1 a I y una contención verificada otro 1 (mínimo 1).'),
  bullet('**Controles diseñados o propuestos** no reducen el residual: se informan como plan de tratamiento.'),
  h2('2.2 Opciones de tratamiento'),
  ...tabla('Opciones de tratamiento y su equivalencia con ISO/IEC 27005',
    [['Decisión', 'Significado en este proyecto'],
      ['Mitigar', 'Reducir probabilidad o impacto con controles (ISO/IEC 27005: modificar).'],
      ['Eliminar', 'Suprimir la causa raíz del riesgo (corrección del código o de la configuración).'],
      ['Evitar', 'Dejar de realizar la actividad o retirar la funcionalidad que origina el riesgo.'],
      ['Transferir', 'Compartir el riesgo con un tercero (proveedor gestionado, póliza o contrato).'],
      ['Aceptar', 'Retener el riesgo de forma consciente, documentada y temporal (ISO/IEC 27005: retener).']],
    [1700, 7660], 19),
  h2('2.3 Categorización del riesgo por tipo e impacto'),
  p(`Cada riesgo se clasifica por **tipo** (Seguridad, Software, Técnico, Operacional, Cloud y Cumplimiento) y por las categorías de **impacto** que afectaría (Reputacional, Operacional, Financiero y Legal); el impacto principal aparece primero. Distribución por tipo: ${['Seguridad', 'Software', 'Técnico', 'Operacional', 'Cloud', 'Cumplimiento'].map(t => `${t}: ${cuenta('tipo', t)}`).join('; ')}. Impactos más frecuentes: ${['Reputacional', 'Legal', 'Financiero', 'Operacional'].map(i => `${i}: ${R.filter(r => r.impactos.includes(i)).length}`).join('; ')}.`),
  ...tabla('Registro de riesgos: categorización por tipo e impacto',
    [['ID', 'Riesgo', 'Tipo', 'Impactos', 'OWASP 2025', 'CWE']].concat(R.map(r => [r.id, r.nombre, r.tipo, r.impactos.join(', '), r.owasp, r.cwe])),
    [560, 3500, 1150, 1900, 1150, 1100], 16),
  h2('2.4 Matriz de decisiones por riesgo'),
  p(`Las cinco opciones se aplican. Como decisión principal: ${['Mitigar', 'Eliminar', 'Evitar', 'Aceptar', 'Transferir'].map(d => `${d} ${cuenta('decision', d)}`).join(', ')}; Transferir actúa como decisión complementaria en R03 (gestor de secretos o KMS del proveedor cloud), R21 (servicios gestionados y responsabilidad compartida) y R23 (póliza de ciberriesgo o cláusulas contractuales). Las tres aceptaciones (R04, R20 y R24) son temporales y se limitan al laboratorio: actualizar las bibliotecas rompe los retos de Juice Shop y el SIEM de un solo nodo es suficiente para la prueba; en producción la decisión sería Eliminar.`),
  ...tabla('Matriz de decisiones: riesgo inherente, decisión y riesgo residual',
    [['ID', 'Inherente P×I', 'Decisión', 'Complementaria', 'Residual P×I', 'Fuente P/I']].concat(R.map(r => [r.id, `${r.P_inh}×${r.I_inh} = ${r.S_inh} ${r.N_inh}`, r.decision, r.decision_sec || '—', `${r.P_res}×${r.I_res} = ${r.S_res} ${r.N_res}`, r.fuente_pi === 'cualitativa' ? 'Cualitativa' : 'DREAD F1'])),
    [600, 1900, 1300, 1500, 1900, 2160], 17),
  h2('2.5 Matriz de calor: probabilidad frente a impacto'),
  p('Las figuras siguientes ubican cada riesgo según su probabilidad y su impacto antes (inherente) y después (residual) de aplicar los controles verificados. El número de la esquina de cada celda es el producto P × I.'),
  ...fig('docs/fase-6/img/heatmap-antes.png', 'Matriz de calor del riesgo inherente: 8 riesgos críticos y 15 altos, concentrados en probabilidades 4-5.', 520, 520),
  ...fig('docs/fase-6/img/heatmap-despues.png', 'Matriz de calor del riesgo residual tras los controles verificados: 1 crítico (R03), 9 altos, 9 medios y 5 bajos.', 520, 520),
  ...fig('docs/fase-6/img/niveles-antes-despues.png', 'Distribución de los 24 riesgos por nivel: inherente frente a residual.', 560, 320),
  ...tabla('Riesgos por nivel antes y después de los controles',
    [['Nivel', 'Inherente', 'Residual']].concat(NIV.map(n => [n, String(cuenta('N_inh', n)), String(cuenta('N_res', n))])),
    [3000, 3000, 3000], 19),
  h2('2.6 Lectura del riesgo residual'),
  bullet(`Quedan **${resAltos.length} riesgos Alto o Crítico** (${resAltos.map(r => r.id).join(', ')}). Su tratamiento definitivo —parches de código, actualización de dependencias, parser XML seguro, lista blanca contra SSRF— está diseñado o propuesto, pero no desplegado, por lo que el método no les concede reducción.`),
  bullet('**R03** (clave privada JWT embebida) sigue **Crítico**: ningún control desplegado detecta un token forjado con esa clave. La prioridad es desplegar el parche 04 con un gestor de secretos.'),
  bullet('**R06** (BOLA) baja solo en impacto: el WAF no lo bloquea (verificado) y el SIEM lo detecta. El parche 08 lo eliminaría.'),
  bullet('Los mayores descensos corresponden a riesgos con controles preventivos verificados en varias capas: R01 y R02 (SQLi: WAF + RASP + alerta), R12 y R17 (rutas sensibles), R16 (fuerza bruta) y R19 (registro sin alertas, eliminado con el SIEM).'),
  bullet('R22, el riesgo introducido por el propio RASP, se identificó, se trató y se verificó dentro de la fase; muestra que cada control nuevo también debe evaluarse como fuente de riesgo.'),

  // ======================= cierre =======================
  new Paragraph({ heading: HeadingLevel.HEADING_1, pageBreakBefore: true, children: [new TextRun({ text: 'Limitaciones y trabajo futuro', font: ARIAL })] }),
  bullet('Los parches de código 01-08 se validaron como diff, pero la aplicación no se recompiló; desplegarlos permitiría medir el residual sin depender del WAF y reduciría R03, R05, R06, R07, R09 y R14.'),
  bullet('RASP: integrar su protección IDOR y gestionar el error de bloqueo en la capa de datos para responder 403 en lugar de dejar la petición sin respuesta.'),
  bullet('SIEM de un solo nodo, sin alta disponibilidad ni notificaciones externas; en producción se usaría un clúster gestionado, el driver de registros de Docker en lugar del socket y la notificación por Alertmanager, correo o chat.'),
  bullet('La infraestructura cloud de la Fase 2 no se desplegó para evitar costos: el diseño en Terraform está validado estáticamente con Checkov (144 aprobadas, 0 fallidas).'),
  bullet('Las reglas del CRS distintas de la 942 (XSS, RCE, LFI y fugas en respuestas) están cargadas, pero esta fase no las ejercitó con pruebas específicas; su cobertura se documenta como configurada, no verificada.'),
  new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun({ text: 'Conclusiones', font: ARIAL })], spacing: { before: 360 } }),
  p('La Fase 6 integró y verificó una estrategia de defensa en profundidad sobre la aplicación endurecida. El WAF mitigó los once casos A1-A11 sin bloquear el tráfico legítimo, el RASP detectó y bloqueó las inyecciones SQL dentro de la aplicación incluso con el perímetro evadido, y el SIEM centralizó los registros y activó seis de sus siete reglas durante las pruebas, incluida la detección del BOLA que ningún control perimetral bloquea.'),
  p('La operación también reveló fallos que solo aparecen al poner los controles en funcionamiento: el RASP en modo bloqueo provocaba la caída del proceso, el healthcheck del WAF lo marcaba como no saludable y una regla del SIEM sobrecontaba eventos. Los tres se corrigieron y se verificaron con evidencia. Esta experiencia confirma que un control desplegado no equivale a un control efectivo hasta que se prueba.'),
  p(`El tratamiento formal del riesgo, calculado de forma reproducible a partir del DREAD de la Fase 1, redujo los riesgos críticos de ${cuenta('N_inh', 'Crítico')} a ${cuenta('N_res', 'Crítico')} y los altos de ${cuenta('N_inh', 'Alto')} a ${cuenta('N_res', 'Alto')}. El residual no es nulo: el riesgo crítico restante (R03) y varios altos dependen de correcciones de código diseñadas pero no desplegadas. Presentarlos así, sin conceder reducciones a controles no verificados, es la base honesta para priorizar el trabajo siguiente.`),

  new Paragraph({ heading: HeadingLevel.HEADING_1, pageBreakBefore: true, children: [new TextRun({ text: 'Referencias', font: ARIAL })] }),
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
    'OWASP Foundation. (s. f.). ModSecurity (Versión 3.0.17) [Software]. https://github.com/owasp-modsecurity/ModSecurity'
  ].map(t => new Paragraph({ alignment: AlignmentType.LEFT, spacing: { line: 360, after: 120 }, indent: { left: convertInchesToTwip(0.5), hanging: convertInchesToTwip(0.5) }, children: [run(t)] })),

  new Paragraph({ heading: HeadingLevel.HEADING_1, pageBreakBefore: true, children: [new TextRun({ text: 'Anexos', font: ARIAL })] }),
  h2('Anexo A. Integridad de la evidencia de la Fase 6 (SHA-256)'),
  p('Extracto de `evidence/MANIFEST.sha256` con los archivos de la Fase 6. Se verifica con `sha256sum -c MANIFEST.sha256` desde `evidence/`. El manifiesto solo incluye archivos versionados; las corridas locales ignoradas por git no figuran.', { indent: false }),
  ...code(manifest6.map(l => l.replace(/^([0-9a-f]{64}) \*\.\//, '$1  '))),
  h2('Anexo B. Bitácora de comandos de la Fase 6'),
  p('Entradas de `evidence/bitacora.md` del 2026-11-10 (fecha, fase, comando, herramienta y resultado). La entrada «CORRECCIÓN» documenta la corrida inválida del RASP.', { indent: false }),
  ...bitacora6.map(l => {
    const c = l.split('|').map(s => s.trim())
    return new Paragraph({ spacing: { after: 100, line: 276 }, children: [run(`${c[1]} · Fase ${c[2]} · `, { bold: true, size: 18 }), run(c[3].replace(/`/g, ''), { mono: true, size: 16 }), run(` · ${c[4]} · ${c[5]}`, { size: 18 })] })
  }),
  h2('Anexo C. Reglas de correlación del SIEM (LogQL)'),
  p('Contenido de `deploy/hardened/siem/rules/fake/alertas.yaml`, evaluado por el ruler de Loki.', { indent: false }),
  ...code(alertas),
  h2('Anexo D. Controles compensatorios detallados por riesgo'),
  ...R.flatMap(r => [
    new Paragraph({ keepNext: true, spacing: { before: 140, after: 40 }, children: [run(`${r.id} — ${r.nombre}`, { bold: true, size: 20 })] }),
    ...r.controles.map(c => new Paragraph({ spacing: { after: 30, line: 260 }, indent: { left: convertInchesToTwip(0.3) }, children: [run(`• ${c.control} `, { size: 18 }), run(`[${c.tipo}; ${ESTADO[c.estado] || c.estado}] `, { size: 18, it: true }), run(c.evidencia, { mono: true, size: 16 })] })),
    ...(r.nota ? [new Paragraph({ spacing: { after: 60 }, indent: { left: convertInchesToTwip(0.3) }, children: [run(`Nota: ${r.nota}`, { size: 18, it: true })] })] : [])
  ])
]

const doc = new Document({
  creator: 'MASI-UMG 2026',
  title: 'Fase 6 - Operaciones, Monitoreo y Ciberseguridad',
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

Packer.toBuffer(doc).then(b => {
  fs.writeFileSync(OUT, b)
  fs.writeFileSync(path.join(__dirname, 'toc-entradas.json'), JSON.stringify(ENTRADAS.map(e => e[0])))
  console.log('OK docx', b.length, 'bytes ·', nFig, 'figuras ·', nTab, 'tablas')
})
