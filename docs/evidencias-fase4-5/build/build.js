// Genera el documento Word de las Fases 4 y 5 (APA 7). Ejecutar con node (docx instalado en ./).
const fs = require('fs')
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType, ImageRun,
  Table, TableRow, TableCell, WidthType, BorderStyle, ShadingType, PageBreak,
  Header, Footer, PageNumber, TableOfContents, LevelFormat,
  TabStopType, LeaderType, Tab, convertInchesToTwip
} = require('docx')

const IMG = '../img/'
const ARIAL = 'Arial'
const BLUE = '1F3864'
const GREY = 'F2F2F2'

// ---------- helpers ----------
const img = (file, w, h) => new Paragraph({
  alignment: AlignmentType.CENTER,
  spacing: { before: 120, after: 40 },
  children: [new ImageRun({ type: 'jpg', data: fs.readFileSync(IMG + file), transformation: { width: w, height: h } })]
})
const figCaption = (n, txt) => new Paragraph({
  alignment: AlignmentType.CENTER, spacing: { after: 200 },
  children: [new TextRun({ text: `Figura ${n}. `, bold: true, font: ARIAL, size: 20 }), new TextRun({ text: txt, italics: true, font: ARIAL, size: 20 })]
})
const p = (text, opts = {}) => new Paragraph({
  alignment: opts.align || AlignmentType.JUSTIFIED,
  spacing: { line: 360, after: opts.after ?? 160 },
  indent: opts.indent ? { firstLine: convertInchesToTwip(0.5) } : undefined,
  children: Array.isArray(text) ? text : [new TextRun({ text, font: ARIAL, size: 24 })]
})
const bullet = (text) => new Paragraph({
  alignment: AlignmentType.JUSTIFIED, spacing: { line: 360, after: 80 },
  numbering: { reference: 'vinetas', level: 0 },
  children: Array.isArray(text) ? text : [new TextRun({ text, font: ARIAL, size: 24 })]
})
const run = (text, o = {}) => new TextRun({ text, font: ARIAL, size: o.size || 24, bold: o.bold, italics: o.it, color: o.color })
const h1 = (text) => new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun({ text, font: ARIAL })] })
const h2 = (text) => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun({ text, font: ARIAL })] })

// Tabla con anchos DXA (suman al ancho total). rows: array de arrays de strings; primera fila = encabezado.
function table(rows, widths) {
  const total = widths.reduce((a, b) => a + b, 0)
  const mk = (txt, head, w) => new TableCell({
    width: { size: w, type: WidthType.DXA },
    shading: head ? { type: ShadingType.CLEAR, fill: BLUE, color: 'auto' } : undefined,
    margins: { top: 40, bottom: 40, left: 80, right: 80 },
    children: [new Paragraph({ spacing: { after: 0, line: 276 }, children: [new TextRun({ text: txt, font: ARIAL, size: 19, bold: head, color: head ? 'FFFFFF' : '000000' })] })]
  })
  return new Table({
    width: { size: total, type: WidthType.DXA },
    columnWidths: widths,
    rows: rows.map((r, i) => new TableRow({ tableHeader: i === 0, children: r.map((c, j) => mk(c, i === 0, widths[j])) }))
  })
}

// ---------- carátula ----------
const caratula = [
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 240, after: 60 }, border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: BLUE } }, children: [run('[ Logo oficial UMG — insertar ]', { it: true, color: '808080', size: 20 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 240, after: 60 }, children: [run('UNIVERSIDAD MARIANO GÁLVEZ DE GUATEMALA', { bold: true, size: 28 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 40 }, children: [run('Maestría en Seguridad Informática', { size: 24 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 400 }, children: [run('Curso: Seguridad en Aplicaciones', { size: 24 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 600, after: 120 }, children: [run('Laboratorio de Seguridad de Aplicaciones sobre OWASP Juice Shop', { bold: true, size: 32, color: BLUE })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 600 }, children: [run('Fase 4: Implementación de Ciberdefensa', { bold: true, size: 26 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 600 }, children: [run('Fase 5: Despliegue Seguro e Infraestructura Cloud', { bold: true, size: 26 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 400, after: 40 }, children: [run('Integrantes:', { bold: true })] }),
  ...['Molina Pérez, Juan Carlos', 'Sánchez Flores, Juan Walter Ernesto', 'García Gonzalez, Leopoldo Emanuel', 'Cambara Castillo, Vanessa Odeth']
    .map(n => new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 20 }, children: [run(n, { size: 22 })] })),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 300, after: 20 }, children: [run('Catedrático: Ing. Matthew Alexander Seigne Samayoa', { size: 22 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 300 }, children: [run('Guatemala, noviembre de 2026', { size: 22 })] }),
  new Paragraph({ children: [new PageBreak()] })
]

// ---------- índice (estático con guía de puntos) ----------
const tocLine = (text, page, sub) => new Paragraph({
  spacing: { after: sub ? 40 : 60, line: 300 },
  indent: sub ? { left: convertInchesToTwip(0.3) } : undefined,
  tabStops: [{ type: TabStopType.RIGHT, position: 9360, leader: LeaderType.DOT }],
  children: [
    new TextRun({ text, font: ARIAL, size: sub ? 22 : 24, bold: !sub }),
    new TextRun({ children: [new Tab(), String(page)], font: ARIAL, size: sub ? 22 : 24, bold: !sub })
  ]
})
const indice = [
  h1('Índice'),
  tocLine('Introducción', 3),
  tocLine('Objetivos', 3),
  tocLine('Fase 4: Implementación de Ciberdefensa', 5),
  tocLine('4.1 Pruebas de penetración – Caja negra (Black Box)', 5, true),
  tocLine('4.2 Pruebas basadas en riesgos – Caja gris / blanca', 7, true),
  tocLine('4.3 Modelado y ejecución de casos de abuso (Abuse Cases)', 8, true),
  tocLine('4.4 Delimitación del perímetro del software', 10, true),
  tocLine('Fase 5: Despliegue Seguro e Infraestructura Cloud', 12),
  tocLine('5.1 Escaneo de contenedores y artefactos', 12, true),
  tocLine('5.2 Hardening de Infraestructura como Código (IaC)', 14, true),
  tocLine('Conclusiones', 18),
  tocLine('Referencias', 18),
  tocLine('Anexos', 19),
  new Paragraph({ children: [new PageBreak()] })
]

// ---------- contenido ----------
const body = [
  h1('Introducción'),
  p('El presente documento recopila las evidencias de las Fases 4 y 5 del proyecto de laboratorio de Seguridad de Aplicaciones, desarrollado sobre OWASP Juice Shop versión 20.3.0, una aplicación web deliberadamente vulnerable mantenida por la Open Worldwide Application Security Project (OWASP). La Fase 4 corresponde a la implementación de ciberdefensa mediante pruebas ofensivas y defensivas que simulan un ataque real, mientras que la Fase 5 aborda el despliegue seguro y la seguridad de la infraestructura (contenedores e Infraestructura como Código).'),
  p('Todas las pruebas se ejecutaron bajo estrictas reglas de aislamiento: la instancia vulnerable únicamente escuchó en la dirección de bucle local (127.0.0.1) o dentro del contenedor efímero de integración continua, sin exponerse a Internet, y solo se evaluaron instancias propias del laboratorio. Cada hallazgo se respalda con evidencia verificable (capturas, reportes de herramientas y registros), cuyo valor hash SHA-256 se conserva en el manifiesto del repositorio, garantizando trazabilidad y la ausencia de resultados inventados.'),
  p([run('Repositorio del proyecto: ', {}), run('https://github.com/jmolinap1-universidad/juice-shop-lab', { color: BLUE })]),

  h1('Objetivos'),
  h2('Objetivo general'),
  p('Evaluar la postura de seguridad de una aplicación web real mediante pruebas de penetración y análisis de su infraestructura de despliegue, documentando con evidencia verificable las vulnerabilidades identificadas y los controles de aseguramiento aplicados.'),
  h2('Objetivos específicos'),
  bullet('Ejecutar pruebas de penetración de caja negra, gris y blanca sobre la aplicación, identificando vulnerabilidades explotables.'),
  bullet('Modelar y ejecutar casos de abuso que representen el uso malintencionado de funciones legítimas.'),
  bullet('Delimitar la superficie de ataque y el perímetro del software.'),
  bullet('Analizar las imágenes de contenedor en busca de vulnerabilidades del sistema operativo base y de las dependencias.'),
  bullet('Auditar la Infraestructura como Código (Dockerfiles y Terraform) para evitar configuraciones inseguras.'),
  new Paragraph({ children: [new PageBreak()] }),

  // ======================= FASE 4 =======================
  h1('Fase 4: Implementación de Ciberdefensa'),
  p('La Fase 4 comprende la realización de pruebas ofensivas y defensivas simulando un ataque real. Se emplearon técnicas de caja negra (sin conocimiento previo), caja gris y blanca (con acceso a arquitectura y código), la ejecución de casos de abuso y la delimitación del perímetro del software. La herramienta principal de automatización fue un conjunto de scripts propios ejecutados con cURL contra la instancia local, complementados con OWASP ZAP y Nmap.'),
  img('01-app-homepage.jpg', 430, 322),
  figCaption(1, 'Aplicación OWASP Juice Shop v20.3.0 en ejecución en el laboratorio local (http://127.0.0.1:3000).'),

  h2('4.1 Pruebas de penetración – Caja negra (Black Box)'),
  p('Las pruebas de caja negra simulan a un atacante externo sin conocimiento del código ni credenciales. Se realizó reconocimiento de la superficie expuesta con Nmap y un análisis dinámico pasivo con OWASP ZAP (perfil baseline), además de intentos de explotación a ciegas.'),
  img('09-nmap.jpg', 300, 556),
  figCaption(2, 'Reconocimiento con Nmap 7.98: el puerto 3000/tcp se encuentra abierto; el banner revela el servicio HTTP y la cabecera permisiva Access-Control-Allow-Origin: *.'),
  img('06-zap-reporte-resumen.jpg', 430, 327),
  figCaption(3, 'Resumen del reporte de OWASP ZAP 2.17.0 (baseline): 2 alertas de riesgo medio, 4 bajas y 3 informativas, 0 falsos positivos.'),
  img('07-zap-alertas.jpg', 430, 322),
  figCaption(4, 'Detalle de alertas de ZAP: ausencia de Content Security Policy (CSP) y configuración incorrecta de CORS (Cross-Domain Misconfiguration), entre otras.'),

  h2('4.2 Pruebas basadas en riesgos – Caja gris / blanca (Gray/White Box)'),
  p('Con acceso a la arquitectura, las API y el código fuente, se verificó la lógica de autenticación y el control de acceso. Se confirmó una inyección SQL en el inicio de sesión (routes/login.ts) que permite autenticarse como administrador sin credenciales, y una inyección SQL de tipo UNION en la búsqueda (routes/search.ts) que extrae la tabla de usuarios completa, incluyendo correos y hashes de contraseñas MD5. También se verificó el control de acceso roto por asignación masiva (BOLA/mass assignment) al registrar un usuario con rol de administrador.'),
  img('02-sqli-union-users.jpg', 440, 335),
  figCaption(5, 'Inyección SQL UNION en la búsqueda: la respuesta expone los correos y los hashes MD5 de todas las cuentas (p. ej. admin@juice-sh.op).'),

  h2('4.3 Modelado y ejecución de casos de abuso (Abuse Cases)'),
  p('Se definieron y ejecutaron escenarios donde un atacante abusa de funciones legítimas. El conjunto automatizado security/attacks/run.sh ejecutó once casos contra la instancia local, obteniendo 11 de 11 vectores explotables (riesgo inherente). Entre ellos: fuerza bruta en el inicio de sesión sin bloqueo (12 intentos sin respuesta 429), exfiltración masiva de usuarios vía inyección SQL, y creación de cuentas privilegiadas.'),
  img('08-ataques-antes-consola.jpg', 300, 556),
  figCaption(6, 'Salida del conjunto de casos de ataque automatizados: 11 de 11 casos resultan VULNERABLE en la aplicación sin controles (riesgo inherente).'),
  p('Como evidencia complementaria de casos de abuso sobre funciones legítimas, la Figura 7 muestra el acceso sin autenticación al endpoint de métricas Prometheus (/metrics), que expone telemetría interna de la aplicación.'),
  img('05-metrics-expuesto.jpg', 430, 327),
  figCaption(7, 'Exfiltración de información: el endpoint /metrics se sirve sin autenticación, revelando métricas internas (conteos de peticiones, tiempos de arranque, CPU).'),

  h2('4.4 Delimitación del perímetro del software'),
  p('Se mapeó la superficie de ataque expuesta a partir del código: 102 rutas declaradas (50 GET, 40 POST, 13 PUT, 5 DELETE, 1 PATCH), 79 endpoints REST/API únicos y 14 modelos de datos expuestos como API CRUD automática. Se identificaron puntos de entrada de archivos (carga de ZIP/XML/YAML, imagen por URL con riesgo de SSRF) y rutas estáticas con listado de directorios habilitado, que exponen documentos internos y material criptográfico.'),
  table([
    ['Elemento del perímetro', 'Detalle', 'Riesgo asociado'],
    ['Listado de directorios', '/ftp, /encryptionkeys, /support/logs', 'Exposición de documentos y claves (CWE-548)'],
    ['Endpoint de diagnóstico', '/metrics (Prometheus, sin autenticación)', 'Divulgación de información (CWE-200)'],
    ['Carga de archivos', '/file-upload, /profile/image/url, /rest/memories', 'XXE, SSRF (CWE-611, CWE-918)'],
    ['API CRUD automática', '14 modelos vía finale.resource', 'Control de acceso roto / IDOR (CWE-639)'],
    ['Autenticación', 'JWT RS256 con clave privada embebida', 'Falsificación de tokens (CWE-798)']
  ], [3200, 4000, 2400]),
  new Paragraph({ spacing: { after: 120 }, children: [] }),
  img('03-ftp-directory-listing.jpg', 430, 322),
  figCaption(8, 'Listado de directorios habilitado en /ftp: documentos internos accesibles (acquisitions.md, coupons_2013.md.bak, incident-support.kdbx).'),
  img('04-encryptionkeys-listing.jpg', 430, 322),
  figCaption(9, 'Listado del directorio /encryptionkeys: se expone material criptográfico (jwt.pub, premium.key).'),
  new Paragraph({ children: [new PageBreak()] }),

  // ======================= FASE 5 =======================
  h1('Fase 5: Despliegue Seguro e Infraestructura Cloud (Release & CloudSec)'),
  p('La Fase 5 evalúa la seguridad del despliegue: el escaneo de contenedores y artefactos en busca de vulnerabilidades, y el hardening de la Infraestructura como Código (IaC). Todas las herramientas se ejecutaron mediante Docker con versiones fijas, tanto en local como en el flujo de integración continua de GitHub Actions, garantizando reproducibilidad.'),

  h2('5.1 Escaneo de contenedores y artefactos'),
  p('Se analizó la imagen oficial de Juice Shop (fijada por digest) con Trivy 0.75.0 y, de forma independiente, con Grype 0.120.1 sobre el SBOM generado con Syft (formato CycloneDX). Trivy identificó 11 vulnerabilidades críticas y 32 altas, además de 5 secretos y 66 malas configuraciones embebidas en los archivos de reto de la propia aplicación. La mayoría de las vulnerabilidades se concentran en las dependencias de Node.js (81) frente a las del sistema operativo base Debian 13 (45).'),
  img('10-trivy-imagen.jpg', 300, 556),
  figCaption(10, 'Escaneo de la imagen con Trivy 0.75.0: 11 vulnerabilidades CRITICAL y 32 HIGH; detección de secretos y malas configuraciones.'),
  img('11-grype-sbom.jpg', 300, 556),
  figCaption(11, 'Verificación independiente con Grype 0.120.1 sobre el SBOM (Syft): 12 críticas y 44 altas, confirmando los hallazgos de Trivy.'),
  p('Hallazgo relevante: el re-empaquetado o endurecimiento de la imagen no reduce las vulnerabilidades de las dependencias de la aplicación, pues residen en su código fuente; su corrección corresponde a la actualización de dependencias (documentada como trabajo propuesto, ya que rompe los retos de Juice Shop). El endurecimiento de la Fase 5 se centra en lo que sí es verificable: la higiene del Dockerfile y el endurecimiento del tiempo de ejecución del contenedor.'),

  h2('5.2 Hardening de Infraestructura como Código (IaC)'),
  p('Se auditaron los Dockerfiles con Hadolint 2.15.1 y la Infraestructura como Código (Dockerfiles, Terraform y Compose) con Checkov 3.4.0. El Dockerfile endurecido (app-hardened/Dockerfile) corrige los 11 avisos del original (consolidación de instrucciones RUN y fijación de imágenes base por digest), quedando en 0 avisos. Checkov validó 144 comprobaciones sin fallos en la arquitectura Terraform de la nube (con 5 omisiones justificadas) y 47 sin fallos en los Dockerfiles y archivos de despliegue.'),
  img('12-hadolint.jpg', 300, 556),
  figCaption(12, 'Hadolint: el Dockerfile original presenta 11 avisos (DL3059, DL3006); el Dockerfile endurecido queda en 0 avisos.'),
  img('13-checkov.jpg', 430, 327),
  figCaption(13, 'Checkov 3.4.0: 144/0 en la arquitectura Terraform (Fase 2) y 47/0 en Dockerfiles y despliegue (Fase 5).'),
  p('Adicionalmente, se verificó el endurecimiento del tiempo de ejecución del contenedor mediante docker inspect: sistema de archivos raíz de solo lectura, eliminación de todas las capacidades de Linux (cap_drop ALL), prohibición de nuevos privilegios (no-new-privileges), usuario no root (65532), límites de procesos y memoria, y modo de producción. Se comprobó que la aplicación responde correctamente (HTTP 200) y que una escritura en el sistema de archivos raíz es bloqueada (EROFS).'),
  img('14-docker-inspect-hardening.jpg', 300, 556),
  figCaption(14, 'Verificación del endurecimiento del runtime con docker inspect: FS de solo lectura, cap_drop ALL, no-new-privileges, límites y escritura bloqueada (EROFS).'),
  new Paragraph({ children: [new PageBreak()] }),

  // ======================= CIERRE =======================
  h1('Conclusiones'),
  p('Las pruebas de la Fase 4 confirmaron un riesgo inherente alto a crítico: 11 de 11 vectores evaluados resultaron explotables, incluyendo el compromiso total de la aplicación como administrador por dos vías independientes (inyección SQL y asignación masiva de rol). El reconocimiento de caja negra y el análisis de caja gris/blanca permitieron mapear con precisión la superficie de ataque y la causa raíz de cada vulnerabilidad en el código.'),
  p('La Fase 5 evidenció que las vulnerabilidades de las dependencias del contenedor no se resuelven con el empaquetado de la imagen, sino con la actualización del código; no obstante, el endurecimiento del Dockerfile (de 11 a 0 avisos de Hadolint), la auditoría de la Infraestructura como Código (Checkov 144/0 y 47/0) y el endurecimiento verificable del tiempo de ejecución reducen de forma medible la superficie de ataque del host y del contenedor.'),
  p('En conjunto, el trabajo demuestra la aplicación de un enfoque DevSecOps con evidencia reproducible y trazable, sentando la base para la fase de mitigación (WAF, correcciones de código y medición del riesgo residual).'),

  h1('Referencias'),
  ...[
    'OWASP Foundation. (2026). OWASP Juice Shop (Versión 20.3.0) [Software]. https://owasp-juice.shop',
    'OWASP Foundation. (2025). OWASP Top 10:2025. https://owasp.org/Top10/',
    'OWASP Foundation. (2025). OWASP Application Security Verification Standard (ASVS) 5.0.0. https://owasp.org/www-project-application-security-verification-standard/',
    'Aqua Security. (2026). Trivy (Versión 0.75.0) [Software]. https://trivy.dev',
    'Anchore. (2026). Grype y Syft [Software]. https://github.com/anchore',
    'Checkov by Prisma Cloud. (2026). Checkov (Versión 3.4.0) [Software]. https://www.checkov.io',
    'hadolint. (2026). Hadolint (Versión 2.15.1) [Software]. https://github.com/hadolint/hadolint',
    'Nmap Project. (2026). Nmap (Versión 7.98) [Software]. https://nmap.org',
    'OWASP Foundation. (2026). OWASP Zed Attack Proxy (ZAP) (Versión 2.17.0) [Software]. https://www.zaproxy.org'
  ].map(r => new Paragraph({
    alignment: AlignmentType.JUSTIFIED, spacing: { line: 360, after: 120 },
    indent: { left: convertInchesToTwip(0.5), hanging: convertInchesToTwip(0.5) },
    children: [new TextRun({ text: r, font: ARIAL, size: 24 })]
  })),

  h1('Anexos'),
  p('Toda la evidencia (reportes JSON/SARIF/HTML, capturas y registros) está versionada en el repositorio del proyecto, con su valor hash SHA-256 en evidence/MANIFEST.sha256 y una entrada por comando en evidence/bitacora.md. Los entornos se reproducen con: make lab-up (laboratorio vulnerable) y make hard-up (entorno endurecido).')
]

// ---------- documento ----------
const doc = new Document({
  creator: 'MASI-UMG 2026',
  title: 'Fases 4 y 5 - Seguridad en Aplicaciones',
  styles: {
    default: {
      document: { run: { font: ARIAL, size: 24 } },
      title: { run: { font: ARIAL, size: 44, bold: true, color: BLUE }, paragraph: { spacing: { after: 240 } } },
      heading1: { run: { font: ARIAL, size: 30, bold: true, color: BLUE }, paragraph: { spacing: { before: 280, after: 140 }, keepNext: true, outlineLevel: 0 } },
      heading2: { run: { font: ARIAL, size: 26, bold: true, color: '2E2E2E' }, paragraph: { spacing: { before: 200, after: 100 }, keepNext: true, outlineLevel: 1 } }
    }
  },
  numbering: {
    config: [{
      reference: 'vinetas',
      levels: [{ level: 0, format: LevelFormat.BULLET, text: '•', alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: convertInchesToTwip(0.5), hanging: convertInchesToTwip(0.25) } } } }]
    }]
  },
  sections: [
    { properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1440, bottom: 1440, left: 1440, right: 1440 } } }, children: caratula },
    {
      properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1440, bottom: 1440, left: 1440, right: 1440 } } },
      footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ children: ['Página ', PageNumber.CURRENT], font: ARIAL, size: 18 })] })] }) },
      children: [...indice, ...body]
    }
  ]
})

Packer.toBuffer(doc).then(b => { fs.writeFileSync('Fases4y5_SeguridadAplicaciones.docx', b); console.log('OK docx', b.length, 'bytes') })
