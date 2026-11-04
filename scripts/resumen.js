// Resume reportes de evidencia en Markdown (stdout). Uso:
//   node scripts/resumen.js <semgrep|grype|trivy|npm|osv|zap|hadolint> <archivo.json>
const fs = require('fs')
const [, , kind, file] = process.argv
const d = JSON.parse(fs.readFileSync(file, 'utf8'))
const count = (arr, f) => arr.reduce((m, x) => { const k = f(x); m[k] = (m[k] || 0) + 1; return m }, {})
const table = (obj, h) => {
  const rows = Object.entries(obj).sort((a, b) => b[1] - a[1])
  return `| ${h} | Cantidad |\n|---|---|\n` + rows.map(([k, v]) => `| ${k} | ${v} |`).join('\n')
}
const SEV = ['Critical', 'High', 'Medium', 'Low', 'Negligible', 'Unknown']

switch (kind) {
  case 'semgrep': {
    const r = d.results
    console.log(`Total: ${r.length}\n`)
    console.log(table(count(r, x => x.extra.severity), 'Severidad'), '\n')
    console.log(table(count(r, x => x.check_id.split('.').slice(-1)[0] + ' (' + [].concat(x.extra.metadata.cwe || '')[0].split(':')[0] + ')'), 'Regla (CWE)'), '\n')
    console.log('| Regla | Archivo:línea |\n|---|---|')
    r.filter(x => x.check_id.includes('juice-shop-rules') || x.extra.severity === 'ERROR')
      .forEach(x => console.log(`| ${x.check_id.split('.').slice(-1)[0]} | ${x.path}:${x.start.line} |`))
    break
  }
  case 'grype': {
    const uniq = {}
    d.matches.forEach(m => { uniq[m.vulnerability.id + '|' + m.artifact.name + '@' + m.artifact.version] = m })
    const ms = Object.values(uniq)
    console.log(`Coincidencias únicas (vuln×paquete): ${ms.length}; CVE/GHSA únicos: ${new Set(ms.map(m => m.vulnerability.id)).size}\n`)
    const c = count(ms, m => m.vulnerability.severity)
    console.log('| Severidad | Cantidad |\n|---|---|\n' + SEV.filter(s => c[s]).map(s => `| ${s} | ${c[s]} |`).join('\n'), '\n')
    console.log('| ID | Severidad | Paquete | Versión | Corregido en |\n|---|---|---|---|---|')
    ms.filter(m => ['Critical', 'High'].includes(m.vulnerability.severity))
      .sort((a, b) => SEV.indexOf(a.vulnerability.severity) - SEV.indexOf(b.vulnerability.severity))
      .forEach(m => console.log(`| ${m.vulnerability.id} | ${m.vulnerability.severity} | ${m.artifact.name} | ${m.artifact.version} | ${(m.vulnerability.fix.versions || []).join(', ') || '—'} |`))
    break
  }
  case 'trivy': {
    const vulns = (d.Results || []).flatMap(r => (r.Vulnerabilities || []).map(v => ({ ...v, Target: r.Target, Class: r.Class })))
    const uniq = {}; vulns.forEach(v => { uniq[v.VulnerabilityID + '|' + v.PkgName + '@' + v.InstalledVersion] = v })
    const vs = Object.values(uniq)
    const c = count(vs, v => v.Severity)
    console.log(`Imagen: ${d.ArtifactName}\nSO base: ${d.Metadata?.OS?.Family} ${d.Metadata?.OS?.Name}\nVulnerabilidades únicas (vuln×paquete): ${vs.length}\n`)
    console.log('| Severidad | Cantidad |\n|---|---|\n' + ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'UNKNOWN'].map(s => `| ${s} | ${c[s] || 0} |`).join('\n'), '\n')
    const byClass = count(vs, v => v.Class === 'lang-pkgs' ? 'Dependencias Node.js' : 'Sistema operativo')
    console.log(table(byClass, 'Origen'), '\n')
    const secrets = (d.Results || []).flatMap(r => (r.Secrets || []).map(s => `${r.Target}: ${s.RuleID} (${s.Severity})`))
    console.log(`Secretos detectados: ${secrets.length}`); secrets.slice(0, 20).forEach(s => console.log('- ' + s))
    const mis = (d.Results || []).flatMap(r => r.Misconfigurations || [])
    console.log(`\nMalas configuraciones: ${mis.length}`); mis.forEach(m => console.log(`- ${m.ID} ${m.Title} (${m.Severity})`))
    console.log('\n| ID | Sev. | Paquete | Instalada | Corregida |\n|---|---|---|---|---|')
    vs.filter(v => v.Severity === 'CRITICAL').forEach(v => console.log(`| ${v.VulnerabilityID} | ${v.Severity} | ${v.PkgName} | ${v.InstalledVersion} | ${v.FixedVersion || '—'} |`))
    break
  }
  case 'npm': {
    console.log(JSON.stringify(d.metadata.vulnerabilities))
    console.log('\n| Paquete | Severidad | Directa | Corrección disponible |\n|---|---|---|---|')
    Object.values(d.vulnerabilities).filter(v => ['critical', 'high'].includes(v.severity))
      .forEach(v => console.log(`| ${v.name} | ${v.severity} | ${v.isDirect ? 'sí' : 'no'} | ${typeof v.fixAvailable === 'object' ? v.fixAvailable.name + '@' + v.fixAvailable.version : v.fixAvailable} |`))
    break
  }
  case 'osv': {
    const pk = (d.results || []).flatMap(r => r.packages || [])
    const ids = new Set(pk.flatMap(p => p.vulnerabilities.map(v => v.id)))
    console.log(`Paquetes afectados: ${pk.length}; vulnerabilidades únicas: ${ids.size}`)
    pk.forEach(p => console.log(`- ${p.package.name}@${p.package.version}: ${p.groups.map(g => g.ids[0] + (g.max_severity ? ' (CVSS ' + g.max_severity + ')' : '')).join(', ')}`))
    break
  }
  case 'zap': {
    const alerts = d.site.flatMap(s => s.alerts)
    const risk = count(alerts, a => a.riskdesc.split(' ')[0])
    console.log(`Alertas: ${alerts.length}\n`); console.log(table(risk, 'Riesgo'), '\n')
    console.log('| Plugin | Alerta | Riesgo | CWE | Instancias |\n|---|---|---|---|---|')
    alerts.forEach(a => console.log(`| ${a.pluginid} | ${a.name || a.alert} | ${a.riskdesc} | ${a.cweid} | ${a.count || a.instances.length} |`))
    break
  }
  case 'hadolint': {
    console.log(`Avisos: ${d.length}`)
    d.forEach(x => console.log(`- L${x.line} ${x.code} (${x.level}): ${x.message}`))
    break
  }
}
