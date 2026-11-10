// node html2pdf.cjs input.html output.pdf [header.html footer.html]
const fs = require('fs');
let pw;
try { pw = require('playwright'); } catch (e) { pw = require('/opt/node-tools/node_modules/playwright'); }
(async () => {
  const [inp, out, headerFile, footerFile] = process.argv.slice(2);
  const b = await pw.chromium.launch();
  const p = await b.newPage();
  await p.goto('file://' + require('path').resolve(inp));
  await p.evaluate(() => document.fonts.ready);
  const over = await p.evaluate(() => [...document.querySelectorAll('.page')].map((s, i) => ({ i: i + 1, t: (s.querySelector('h1,h2') || {}).textContent || '', over: Math.max(s.scrollHeight - s.clientHeight, (s.querySelector('.pb') ? s.querySelector('.pb').scrollHeight - s.querySelector('.pb').clientHeight : 0)) })).filter((x) => x.over > 1));
  if (over.length) console.log('ПЕРЕПОЛНЕНИЕ:', JSON.stringify(over));
  const opt = { path: out, preferCSSPageSize: true, printBackground: true };
  if (headerFile) {
    opt.displayHeaderFooter = true;
    opt.headerTemplate = fs.readFileSync(headerFile, 'utf8');
    opt.footerTemplate = fs.readFileSync(footerFile, 'utf8');
  }
  await p.pdf(opt);
  await b.close();
})();
