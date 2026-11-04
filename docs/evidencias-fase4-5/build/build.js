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
  tocLine('4.3 Modelado y ejecución de casos de abuso (Abuse Cases)', 9, true),
  tocLine('4.4 Delimitación del perímetro del software', 11, true),
  tocLine('Fase 5: Despliegue Seguro e Infraestructura Cloud', 13),
  tocLine('5.1 Escaneo de contenedores y artefactos', 13, true),
  tocLine('5.2 Hardening de Infraestructura como Código (IaC)', 15, true),
  tocLine('Delimitación de alcance: despliegue cloud diferido', 20),
  tocLine('Conclusiones', 20),
  tocLine('Referencias', 21),
  tocLine('Anexos', 21),
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
  p('Con acceso a la arquitectura, las API y el código fuente, se verificó la lógica de autenticación y el control de acceso. Se confirmó una inyección SQL en el inicio de sesión (routes/login.ts) que permite autenticarse como administrador sin credenciales, y una inyección SQL de tipo UNION en la búsqueda (routes/search.ts) que extrae la tabla de usuarios completa, incluyendo correos y hashes de contraseñas MD5.'),
  img('02-sqli-union-users.jpg', 440, 335),
  figCaption(5, 'Inyección SQL UNION en la búsqueda: la respuesta expone los correos y los hashes MD5 de todas las cuentas (p. ej. admin@juice-sh.op).'),
  p([run('Control de acceso: dos hallazgos ', { bold: true }), run('distintos', { bold: true, it: true }), run('. Es importante no confundir dos debilidades diferentes de control de acceso. La ', {}), run('asignación masiva', { bold: true }), run(' (mass assignment, CWE-915) permite que el registro acepte el parámetro no filtrado "role": "admin" y crea una cuenta privilegiada. En cambio, el ', {}), run('BOLA/IDOR', { bold: true }), run(' (Broken Object Level Authorization, CWE-639) es la falta de verificación de propiedad de un objeto entre usuarios distintos.', {})]),
  p('Para demostrar un BOLA genuino se crearon dos cuentas propias de laboratorio con datos ficticios (A, víctima; B, atacante). Autenticado como B, se solicitó la cesta de compras de A mediante GET /rest/basket/{id de A} empleando el token de B. La aplicación respondió HTTP 200 devolviendo la cesta de A, demostrando que no verifica la propiedad del objeto. La prueba se contrastó con un control negativo (B accede a su propia cesta).'),
  table([
    ['Campo', 'Valor observado'],
    ['Cuenta A (víctima)', 'cesta id 6 — UserId 26'],
    ['Cuenta B (atacante)', 'cesta id 7 — UserId 27'],
    ['Petición', 'GET /rest/basket/6 con el token de B'],
    ['Esperado (si fuera seguro)', 'HTTP 401/403, o solo la cesta propia de B'],
    ['Observado', 'HTTP 200 devolviendo la cesta de A (UserId 26 ≠ 27)'],
    ['Clasificación', 'VULNERABLE — BOLA/IDOR (CWE-639, OWASP API1:2023 / A01)']
  ], [3200, 6400]),
  p('Evidencia: evidence/fase-4/bola/ (resultado-bola.md, cross-read.json, own-read.json). Limitación: la prueba demuestra la lectura de la cesta por identificador; no se generaliza a todos los objetos de la API.'),

  h2('4.3 Modelado y ejecución de casos de abuso (Abuse Cases)'),
  p('Se definieron y ejecutaron escenarios donde un atacante abusa de funciones legítimas. El conjunto automatizado security/attacks/run.sh ejecutó once casos contra la instancia local. Para no sobreafirmar los resultados, cada observación se clasifica en una de cuatro clases: explotación demostrada, exposición observada, configuración insegura o ausencia de control. El resultado es: 4 vulnerabilidades explotadas (dos inyecciones SQL que comprometen la base de datos, enumeración de esquema y asignación masiva de rol), 4 exposiciones de información (listado de directorios, documento interno, métricas y clave pública), 2 configuraciones inseguras (CORS permisivo y ausencia de cabeceras) y 1 ausencia de control (sin limitación de intentos de inicio de sesión: 12 intentos con respuesta 401 y sin 429, lo que evidencia la falta de bloqueo pero no demuestra que se adivinara contraseña alguna).'),
  img('08-ataques-antes-consola.jpg', 300, 556),
  figCaption(6, 'Salida del conjunto de casos de ataque: las 11 pruebas registran una debilidad cada una; 4 constituyen explotación demostrada y 7 son exposiciones, configuraciones inseguras o ausencia de controles (riesgo inherente).'),
  p('Como evidencia complementaria de casos de abuso sobre funciones legítimas, la Figura 7 muestra el acceso sin autenticación al endpoint de métricas Prometheus (/metrics), que expone telemetría interna de la aplicación.'),
  img('05-metrics-expuesto.jpg', 430, 327),
  figCaption(7, 'Exfiltración de información: el endpoint /metrics se sirve sin autenticación, revelando métricas internas (conteos de peticiones, tiempos de arranque, CPU).'),

  h2('4.4 Delimitación del perímetro del software'),
  p('Se mapeó la superficie de ataque expuesta a partir del código con un conteo reproducible (comando grep sobre app/server.ts): 109 rutas declaradas (50 GET, 40 POST, 13 PUT, 5 DELETE, 1 PATCH; la suma coincide: 50+40+13+5+1 = 109), aproximadamente 81 endpoints bajo /rest, /api y /b2b, y 14 modelos de datos expuestos como API CRUD automática. Se identificaron puntos de entrada de archivos (carga de ZIP/XML/YAML, imagen por URL con riesgo de SSRF) y rutas estáticas con listado de directorios habilitado, que exponen documentos internos y material criptográfico. No se identificaron webhooks entrantes ni salientes (no aplica). Dado que la aplicación solo escuchó en 127.0.0.1, el perímetro evaluado es local y no un servicio publicado en Internet.'),
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
  p('Se auditaron los Dockerfiles con Hadolint 2.15.1 y la Infraestructura como Código (Dockerfiles, Terraform y Compose) con Checkov 3.4.0. Es necesario distinguir dos artefactos: el Dockerfile auditado app-hardened/Dockerfile (una propuesta de construcción desde el código fuente que corrige los 11 avisos del original y queda en 0, pero que no es la imagen desplegada) y el Dockerfile realmente desplegado deploy/hardened/Dockerfile, que produce la imagen juice-hardened:local a partir de la imagen oficial fijada por digest y cuyo endurecimiento proviene del tiempo de ejecución. Por tanto, la mejora de Hadolint pertenece al artefacto propuesto; la imagen en ejecución conserva las CVE de la imagen base, que se mitigan en runtime pero no se eliminan (su eliminación requiere recompilar con dependencias actualizadas, trabajo de la fase siguiente). Checkov validó 144 comprobaciones sin fallos en la arquitectura Terraform de la nube (con 5 omisiones justificadas) y 47 sin fallos en los Dockerfiles y archivos de despliegue.'),
  img('12-hadolint.jpg', 300, 556),
  figCaption(12, 'Hadolint: el Dockerfile original presenta 11 avisos (DL3059, DL3006); el Dockerfile endurecido queda en 0 avisos.'),
  img('13-checkov.jpg', 430, 327),
  figCaption(13, 'Checkov 3.4.0: 144/0 en la arquitectura Terraform (Fase 2) y 47/0 en Dockerfiles y despliegue (Fase 5).'),
  p('Adicionalmente, se verificó el endurecimiento del tiempo de ejecución del contenedor mediante docker inspect: sistema de archivos raíz de solo lectura, eliminación de todas las capacidades de Linux (cap_drop ALL), prohibición de nuevos privilegios (no-new-privileges), usuario no root (65532), límites de procesos y memoria, y modo de producción. Se comprobó que la aplicación responde correctamente (HTTP 200) y que una escritura en el sistema de archivos raíz es bloqueada (EROFS).'),
  img('14-docker-inspect-hardening.jpg', 300, 556),
  figCaption(14, 'Verificación del endurecimiento del runtime con docker inspect: FS de solo lectura, cap_drop ALL, no-new-privileges, límites y escritura bloqueada (EROFS).'),
  new Paragraph({ children: [new PageBreak()] }),

  // ======================= CIERRE =======================
  h1('Delimitación de alcance: despliegue cloud diferido'),
  p('Durante la entrega de las Fases 4 y 5, la evaluación práctica se realizó en una estación local mediante contenedores Docker y la ejecución controlada de herramientas de seguridad; la aplicación vulnerable no estuvo publicada en Internet. La infraestructura AWS se conserva como arquitectura objetivo definida en Terraform y sometida a análisis estático y validaciones de configuración (Checkov, terraform validate y plan), sin aplicar los recursos en una cuenta cloud. Esta separación permite obtener evidencias reproducibles de ciberdefensa, escaneo de imágenes y hardening de IaC, evitando costos y la exposición innecesaria de una aplicación deliberadamente vulnerable. El despliegue cloud y la verificación operativa de los controles administrados (ALB, WAFv2, RDS, API Gateway, CDN, KMS y SIEM) quedan planificados para la etapa final, previa autorización del equipo y aceptación del alcance por el catedrático.'),

  h1('Conclusiones'),
  p('Las pruebas de la Fase 4 confirmaron un riesgo inherente alto: de las 11 observaciones registradas, 4 constituyen vulnerabilidades explotadas —incluido el compromiso total de la aplicación como administrador por dos vías independientes (inyección SQL y asignación masiva de rol)— y 7 corresponden a exposiciones de información, configuraciones inseguras o ausencia de controles. Adicionalmente, una prueba específica con dos cuentas confirmó un BOLA/IDOR genuino (lectura de la cesta de otro usuario). El reconocimiento de caja negra y el análisis de caja gris/blanca permitieron mapear con precisión la superficie de ataque y la causa raíz de cada hallazgo en el código, sin atribuir cobertura total del OWASP Top 10 ni afirmar más de lo demostrado.'),
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
