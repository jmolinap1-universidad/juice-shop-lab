// Renderiza cada diagramas/*.mmd a PNG (escala 3) con Mermaid 10.9.1 local en Chromium (Playwright 1.49.1).
const { chromium } = require('/work/node_modules/playwright');
const fs = require('fs'); const path = require('path');
(async () => {
  const dir = '/d'; const out = '/o';
  const b = await chromium.launch(); const p = await b.newPage({ deviceScaleFactor: 3, viewport: { width: 1600, height: 1200 } });
  await p.setContent('<html><body style="margin:0;background:#fff"><div id="c"></div></body></html>');
  await p.addScriptTag({ path: '/work/node_modules/mermaid/dist/mermaid.min.js' });
  await p.evaluate(() => mermaid.initialize({ startOnLoad: false, theme: 'neutral', securityLevel: 'strict',
    themeVariables: { fontFamily: 'Liberation Sans, Arial, sans-serif', fontSize: '20px' },
    flowchart: { htmlLabels: true, curve: 'basis', useMaxWidth: false, nodeSpacing: 28, rankSpacing: 38, padding: 10 }, sequence: { useMaxWidth: false, actorFontSize: 20, messageFontSize: 19, noteFontSize: 18, width: 120, actorMargin: 20, boxMargin: 6, messageMargin: 28 } }));
  for (const f of fs.readdirSync(dir).filter(x => x.endsWith('.mmd')).sort()) {
    const src = fs.readFileSync(path.join(dir, f), 'utf8');
    const svg = await p.evaluate(async (s) => (await mermaid.render('g' + Math.random().toString(36).slice(2), s)).svg, src);
    await p.evaluate((s) => { document.getElementById('c').innerHTML = s; const e = document.querySelector('#c svg'); e.style.maxWidth = 'none'; }, svg);
    const el = await p.$('#c svg');
    await el.screenshot({ path: path.join(out, f.replace('.mmd', '.png')), omitBackground: false });
    console.log('ok', f);
  }
  await b.close();
})().catch(e => { console.error(e); process.exit(1); });
