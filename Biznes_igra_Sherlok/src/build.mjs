// Сборка комплекта: три PDF и страница-комплект (kit.html).
// Запуск: node src/build.mjs   (нужен Playwright с Chromium)
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';
import { DOCS, renderSheet } from './content/case.mjs';
import { FORM_SHEETS as F } from './content/forms.mjs';
import { overview, prep, script, keyView, debrief } from './content/guide.mjs';
import { SLIDES, renderSlide } from './content/slides.mjs';

const SRC = path.dirname(fileURLToPath(import.meta.url));
const OUT = path.resolve(SRC, '..');
const TMP = process.env.SHERLOCK_TMP || path.join(SRC, '.tmp');
fs.mkdirSync(TMP, { recursive: true });

const css = (f) => fs.readFileSync(path.join(SRC, 'styles', f), 'utf8');
const TOKENS = css('tokens.css'), COMPONENTS = css('components.css'), SLIDES_CSS = css('slides.css'), ARTIFACT = css('artifact.css');

/* ---------- Шрифты для PDF: встраиваем, чтобы печать не зависела от сети ---------- */
const RANGE = {
  cyrillic: 'U+0301,U+0400-045F,U+0490-0491,U+04B0-04B1,U+2116',
  latin: 'U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD',
};
const FAMILIES = { 'golos-text': ['Golos Text', [400, 500, 600, 700]], oswald: ['Oswald', [500, 600, 700]], 'jetbrains-mono': ['JetBrains Mono', [400, 500, 700]] };
const FONTS = Object.entries(FAMILIES).flatMap(([slug, [family, weights]]) =>
  weights.flatMap((w) => Object.keys(RANGE).map((sub) => {
    const b64 = fs.readFileSync(path.join(SRC, 'fonts', `${slug}-${sub}-${w}-normal.woff2`)).toString('base64');
    return `@font-face{font-family:"${family}";font-weight:${w};font-style:normal;src:url(data:font/woff2;base64,${b64}) format("woff2");unicode-range:${RANGE[sub]}}`;
  }))).join('\n');

// Неразрывные пробелы в суммах и телефонных номерах (только в тексте, теги и стили не трогаем).
const nb = (html) => html.replace(/(<style[\s\S]*?<\/style>|<script[\s\S]*?<\/script>|<[^>]+>)|(\+998) (\d\d) (\d{3}-\d\d-\d\d)|(\d) (?=\d{3}(?!\d))/g,
  (m, block, a, b, c, d) => (block ? block : a ? `<span class="nowrap">${a}\u00a0${b}\u00a0${c}</span>` : `${d}\u00a0`));

const page = (title, styles, body) => `<!doctype html><html lang="ru"><head><meta charset="utf-8"><title>${title}</title>
<style>${FONTS}\n${TOKENS}\nhtml{-webkit-print-color-adjust:exact;print-color-adjust:exact}\n${styles}</style></head><body>${nb(body)}</body></html>`;

/* ---------- Раздаточные материалы ---------- */
const env = (n) => DOCS.filter((d) => d.env === n).map(renderSheet).join('');
const SECTIONS = [
  { name: 'Наклейки на конверты', html: F.labels, copies: '1 на команду', where: 'Разрезать и наклеить на конверты' },
  { name: 'Конверт 1 «Сигнал»: документы 1–6', html: env(1), copies: '2 на команду', where: 'В конверт 1' },
  { name: 'Конверт 2 «Следы»: документы 7–11', html: env(2), copies: '2 на команду', where: 'В конверт 2' },
  { name: 'Конверт 3 «Развязка»: документы 12–15', html: env(3), copies: '2 на команду', where: 'В конверт 3' },
  { name: 'Правила игры', html: F.rules, copies: '1 на команду', where: 'На стол команды' },
  { name: 'Карточки ролей', html: F.roles, copies: '1 на команду', where: 'Разрезать, на стол команды' },
  { name: 'Доска расследования', html: F.board, copies: '1–2 на команду', where: 'На стол команды. Лучше увеличить до A3' },
  { name: 'Лента времени', html: F.timeline, copies: '1–2 на команду', where: 'На стол команды' },
  { name: 'Заключение рабочей группы', html: F.answer, copies: '1 на команду и 1 запасной', where: 'На стол команды' },
  { name: 'Разминка «Факт или версия?»', html: F.warmup, copies: '1 на участника', where: 'Раздать в блоке 2' },
  { name: 'Анкета участника', html: F.feedback, copies: '1 на участника', where: 'Раздать в блоке 10' },
  { name: 'Карточки «С понедельника я…»', html: F.pledge, copies: '1 лист на трёх участников', where: 'Разрезать, раздать в блоке 10' },
  { name: 'Карточки подсказок', html: F.hints, copies: '1 на команду', where: 'Разрезать, хранить у ведущего' },
  { name: 'Ключ: разгадка и подсчёт баллов', html: F.key, copies: '1', where: 'Ведущему' },
  { name: 'Ведомость баллов', html: F.score, copies: '1', where: 'Ведущему' },
  { name: 'Лист наблюдений', html: F.observe, copies: '1', where: 'Ведущему' },
];
let p = 2; // стр. 1 — титул с ведомостью
for (const s of SECTIONS) {
  s.pages = (s.html.match(/<article class="sheet/g) || []).length;
  s.range = s.pages > 1 ? `${p}–${p + s.pages - 1}` : `${p}`;
  p += s.pages;
}
const TOTAL_HANDOUT_PAGES = p - 1;
const manifestRows = SECTIONS.map((s) => `<tr><td class="nowrap">${s.range}</td><td>${s.name}</td><td>${s.copies}</td><td>${s.where}</td></tr>`).join('');
const manifest = (cls) => `<div class="scroll"><table class="${cls}"><thead><tr><th>Стр.</th><th>Что</th><th>Копий</th><th>Куда</th></tr></thead><tbody>${manifestRows}</tbody></table></div>`;

const handoutCover = `
<article class="sheet form">
  <header class="sheet-h"><span class="tag">Шерлок · дело № 27-Р</span><span class="tag tag-env">Ведущему</span><span class="docno">Комплект для печати</span></header>
  <h3 class="sheet-t">Раздаточные материалы</h3>
  <div class="sheet-b">
  <p>Бизнес-игра «Шерлок. Дело о платеже № 318». Печать: A4, с одной стороны, подходит чёрно-белая. Эту страницу печатать не обязательно.</p>
  <p class="mini-h">Ведомость печати</p>
  ${manifest('log wrap')}
  <p class="mini-h">Как собрать комплект</p>
  <ol class="spaced">
  <li>Напечатайте страницы в нужном количестве. Документы дела — по два экземпляра на команду, чтобы их читали несколько человек сразу.</li>
  <li>Разложите документы по трём конвертам для каждой команды и наклейте наклейки. Конверты остаются у вас до начала раунда.</li>
  <li>Остальное разложите на три стопки: на столы команд, участникам, себе.</li>
  </ol>
  <p class="doc-note">Пример. 4 команды и 20 участников — около 220 листов: 42 листа на команду, 2–3 листа на участника и 4 листа ведущему.</p>
  </div>
  <footer class="sheet-f">Все названия, имена, суммы и телефонные номера в материалах вымышлены. Совпадения случайны.</footer>
</article>`;

const HANDOUT_PRINT = `
@page{size:A4;margin:0}
body{margin:0;background:#fff}
.sheet{width:210mm;height:297mm;padding:13mm 15mm 9mm;font-size:10.3pt;break-after:page;overflow:hidden}
.sheet.doc{font-size:11.6pt}
.sheet.doc[data-doc="3"],.sheet.doc[data-doc="4"],.sheet.doc[data-doc="6"],.sheet.doc[data-doc="13"]{font-size:11pt}
.scroll{overflow:visible}
.board-sheet table.board{height:228mm}
.cards-roles .card{min-height:68mm}
.cards-hints .card{min-height:60mm}
.cards-labels .card{min-height:64mm;padding:1.1em 1em}
.cards-pledge .card{min-height:80mm;padding:.8em 1.1em}
.cards-pledge .lines i{height:2em}
.sheet:has(table.key){font-size:9.2pt}
.sheet:has(table.key) table.log.wrap td{padding:.3em .5em}
[data-doc="13"] .statement{margin-bottom:.75em}
[data-doc="7"] table.log td{padding-top:.12em;padding-bottom:.12em}
`;
const handoutsHtml = page('Шерлок — раздаточные материалы', COMPONENTS + HANDOUT_PRINT, handoutCover + SECTIONS.map((s) => s.html).join(''));

/* ---------- Руководство ведущего ---------- */
const GUIDE_PRINT = `
@page{size:A4;margin:17mm 17mm 19mm}
body{margin:0;background:#fff;color:var(--ink);font-family:var(--f-body);font-size:10.3pt;line-height:1.5}
.scroll{overflow:visible}
.g-cover{height:255mm;display:flex;flex-direction:column;break-after:page}
.g-cover .eyebrow{font-family:var(--f-display);font-weight:500;text-transform:uppercase;letter-spacing:.16em;font-size:11pt;color:var(--stamp);margin:0 0 6mm}
.g-cover h1{font-family:var(--f-display);font-weight:700;text-transform:uppercase;font-size:84pt;line-height:.95;margin:0}
.g-cover h1 span{display:block;font-size:24pt;font-weight:500;color:var(--muted);margin-top:5mm;line-height:1.2}
.g-cover .lead{font-size:13pt;max-width:135mm;margin:10mm 0 0}
.g-cover .box{margin-top:auto;border-top:3px solid var(--ink);padding-top:5mm;display:grid;grid-template-columns:1fr 1fr;gap:4mm 10mm}
.g-cover .box div{font-size:10pt}
.g-cover .box b{display:block;font-family:var(--f-display);text-transform:uppercase;letter-spacing:.08em;font-size:9pt;color:var(--muted);font-weight:600}
.g-cover .fine{font-size:8.5pt;color:var(--muted);margin-top:6mm}
.g-part{break-before:page}
.g-part>h1{font-family:var(--f-display);font-weight:700;text-transform:uppercase;font-size:30pt;line-height:1.05;margin:0 0 7mm;padding-bottom:2.5mm;border-bottom:3px solid var(--stamp)}
.g-part>h1 small{display:block;font-size:10pt;letter-spacing:.14em;font-weight:500;color:var(--stamp);margin-bottom:1.5mm}
.g-warn{border:2px solid var(--stamp);padding:3mm 4mm;margin:0 0 7mm;font-weight:600}
.sec{margin-bottom:8mm}
.sec h2{font-size:15.5pt}
h2,h3,.block-h,.goal{break-after:avoid}
.say,.do,.note,tr,ol.steps>li,ul.check>li,.copybox,dl.facts>div,.dstep h3{break-inside:avoid}
ol.steps,ul.check{display:block}
ol.steps>li{margin:0 0 .65em}
ol.steps>li::before{top:0}
ul.check>li{margin:0 0 .42em}
.block{margin-top:7mm}
table.t{font-size:9.4pt}
`;
const part = (n, title, body, warn = '') => `<div class="g-part"><h1><small>Часть ${n}</small>${title}</h1>${warn}${body}</div>`;
const guideHtml = page('Шерлок — руководство ведущего', COMPONENTS + GUIDE_PRINT, `
<div class="g-cover">
  <p class="eyebrow">Бизнес-игра для сотрудников банка · руководство ведущего</p>
  <h1>Шерлок<span>Дело о платеже № 318</span></h1>
  <p class="lead">Игра-расследование на три часа. Команды разбирают 15 документов вымышленного банка и выясняют, кто из семи сотрудников увёл со счёта клиента 870 000 000 сум.</p>
  <div class="box">
    <div><b>Кому</b>Сотрудникам банка из любых подразделений</div>
    <div><b>Сколько человек</b>8–25 участников, 2–5 команд</div>
    <div><b>Время</b>3 часа</div>
    <div><b>Ведущий</b>Один, опыт не нужен</div>
    <div><b>Что развивает</b>Аналитическое мышление, внимание к деталям, обоснование выводов, командную работу</div>
    <div><b>В комплекте</b>Руководство ведущего, раздаточные материалы, слайды для экрана</div>
  </div>
  <p class="fine">Банк, организации, люди, суммы и телефонные номера в игре вымышлены. Совпадения случайны.</p>
</div>
${part(1, 'Обзор', overview())}
${part(2, 'Подготовка', prep(manifest('t')))}
${part(3, 'Сценарий', script())}
${part(4, 'Разгадка', keyView(), '<p class="g-warn">Только для ведущего. Не показывайте участникам до разбора.</p>')}
${part(5, 'Дебриф и оценка результата', debrief())}`);

/* ---------- Слайды ---------- */
const slidesMarkup = SLIDES.map((s, i) => renderSlide(s, i, SLIDES.length)).join('');
const slidesHtml = page('Шерлок — слайды для экрана', SLIDES_CSS + `
@page{size:1280px 720px;margin:0}
body{margin:0;background:var(--s-bg)}
.slide{width:1280px;height:720px;break-after:page}`, slidesMarkup);

/* ---------- Страница-комплект ---------- */
const TABS = [['overview', 'Обзор'], ['prep', 'Подготовка'], ['script', 'Сценарий'], ['screen', 'Экран'], ['case', 'Материалы'], ['key', 'Разгадка'], ['debrief', 'Дебриф']];
const KIT_NOTE = '<p class="small">Три PDF-файла приложены к комплекту. Слайды с таймером открываются и здесь, на вкладке «Экран».</p>';
const vh = (title, lead) => `<h1 class="view-h">${title}</h1><p class="view-lead">${lead}</p>`;
const kitHtml = `<meta name="claude:viewport-fit-sides" content="cover">
<title>Бизнес-игра «Шерлок»</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Golos+Text:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&family=Oswald:wght@500;600;700&display=swap">
<style>
${TOKENS}
${ARTIFACT}
${COMPONENTS}
${SLIDES_CSS}
</style>
<header class="top"><div class="top-in">
  <div class="brand">Шерлок<small>дело № 27-Р</small></div>
  <nav class="tabs" role="tablist" aria-label="Разделы комплекта">
    ${TABS.map(([id, t], i) => `<button type="button" role="tab" data-tab="${id}" aria-controls="v-${id}" aria-selected="${i === 0}">${t}</button>`).join('')}
  </nav>
</div></header>
<main class="wrap">

<section class="view" id="v-overview" role="tabpanel">
  <div class="hero">
    <p class="eyebrow">Бизнес-игра для сотрудников банка · комплект ведущего</p>
    <h1>Шерлок<span>Дело о платеже № 318</span></h1>
    <p class="hero-lead">Игра-расследование на три часа. Команды разбирают 15 документов вымышленного банка и выясняют, кто из семи сотрудников увёл со счёта клиента 870 000 000 сум.</p>
    <div class="logline" aria-label="Три строки из журнала операций">
<div>16:51  T.ALIEV  ОП-04  Вход в систему</div>
<div>16:52  T.ALIEV  ОП-04  <b>Ввод п/п № 318 · 870 000 000</b></div>
<div>16:53  T.ALIEV  ОП-04  Выход из системы</div>
    </div>
    <p class="small">С этих трёх строк журнала начинается расследование. Алиева в это время в банке уже не было.</p>
    <ul class="chips"><li>3 часа</li><li>8–25 человек</li><li>1 ведущий</li><li>3 конверта</li><li>15 документов</li></ul>
  </div>
  ${overview().replace('<!--kit-note-->', KIT_NOTE)}
</section>

<section class="view" id="v-prep" role="tabpanel" hidden>
  ${vh('Подготовка', 'Чек-листы, печать, зал и приглашение. Отметки в чек-листах сохраняются в этом браузере.')}
  ${prep(manifest('t'))}
</section>

<section class="view" id="v-script" role="tabpanel" hidden>
  ${vh('Сценарий', 'Десять блоков по минутам. В синих блоках — слова ведущего, их можно читать с листа.')}
  ${script()}
</section>

<section class="view" id="v-screen" role="tabpanel" hidden>
  ${vh('Экран', 'Слайды для проектора с таймером раундов. Если в зале нет интернета, покажите PDF «Слайды для экрана» и засеките время на телефоне.')}
  <div class="stage" id="stage">
    <div class="stage-slide">${slidesMarkup}</div>
    <div class="stage-bar">
      <button type="button" class="btn" id="s-prev" aria-label="Предыдущий слайд">Назад</button>
      <span class="s-count" id="s-count">1 / ${SLIDES.length}</span>
      <button type="button" class="btn primary" id="s-next" aria-label="Следующий слайд">Дальше</button>
      <select id="s-jump" aria-label="Перейти к слайду">${SLIDES.map((s, i) => `<option value="${i}">${i + 1}. ${s.name}</option>`).join('')}</select>
      <div class="t-ctl" id="t-ctl" hidden>
        <span class="t-val" id="t-val">00:00</span>
        <button type="button" class="btn primary" id="t-go">Старт</button>
        <button type="button" class="btn" id="t-reset">Сброс</button>
        <button type="button" class="btn" id="t-plus">+1 мин</button>
      </div>
      <button type="button" class="btn" id="s-full">На весь экран</button>
    </div>
  </div>
  <p class="small stage-note">Клавиши: стрелки влево и вправо листают слайды, пробел запускает и останавливает таймер. Со слайда 16 начинается разгадка.</p>
</section>

<section class="view" id="v-case" role="tabpanel" hidden>
  ${vh('Материалы дела', '15 документов в трёх конвертах. Здесь их удобно читать и решать дело самому. Для печати берите PDF «Раздаточные материалы»: там ещё бланки, карточки и ключ.')}
  <div class="filters" role="group" aria-label="Фильтр по конвертам">
    <button type="button" class="btn" data-env-filter="0" aria-pressed="true">Все</button>
    <button type="button" class="btn" data-env-filter="1" aria-pressed="false">Конверт 1 · Сигнал</button>
    <button type="button" class="btn" data-env-filter="2" aria-pressed="false">Конверт 2 · Следы</button>
    <button type="button" class="btn" data-env-filter="3" aria-pressed="false">Конверт 3 · Развязка</button>
  </div>
  <div class="docs" id="docs">${DOCS.map(renderSheet).join('')}</div>
</section>

<section class="view" id="v-key" role="tabpanel" hidden>
  ${vh('Разгадка', 'Ответ, схема, доказательства и подсчёт баллов. Только для ведущего.')}
  <div class="gate" id="gate">
    <h2>Сначала решите дело сами</h2>
    <p>Это главный шаг подготовки. Пройдите три конверта на вкладке «Материалы» и только потом открывайте разгадку: так вы поймёте, где участникам будет трудно.</p>
    <button type="button" class="btn primary" id="gate-open">Показать разгадку</button>
    <button type="button" class="btn" data-go="case">К материалам дела</button>
  </div>
  <div id="key-body" hidden>${keyView()}</div>
</section>

<section class="view" id="v-debrief" role="tabpanel" hidden>
  ${vh('Дебриф', 'Разговор после игры, оценка результата и то, что делать дальше.')}
  ${debrief()}
</section>

</main>
<script>
${fs.readFileSync(path.join(SRC, 'kit.js'), 'utf8')}
</script>
`;

const kitOut = nb(kitHtml);
fs.writeFileSync(path.join(SRC, 'kit.html'), kitOut);
fs.writeFileSync(path.join(TMP, 'handouts.html'), handoutsHtml);
fs.writeFileSync(path.join(TMP, 'guide.html'), guideHtml);
fs.writeFileSync(path.join(TMP, 'slides.html'), slidesHtml);
// Локальный просмотр страницы-комплекта: та же обёртка, что добавляется при публикации.
fs.writeFileSync(path.join(TMP, 'kit-preview.html'), `<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>${FONTS}body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style></head><body>${kitOut}</body></html>`);

console.log(`kit.html ${(kitOut.length / 1024).toFixed(0)} KB · раздаточные: ${TOTAL_HANDOUT_PAGES} стр.`);
if (process.argv.includes('--html-only')) process.exit(0);

/* ---------- PDF ---------- */
const require = createRequire(import.meta.url);
let chromium;
try { ({ chromium } = require('playwright')); } catch { ({ chromium } = createRequire('/opt/node-tools/')('playwright')); }
const browser = await chromium.launch();
const pg = await browser.newPage();
const url = (f) => 'file://' + path.join(TMP, f);

await pg.goto(url('handouts.html'));
await pg.evaluate(() => document.fonts.ready);
const over = await pg.evaluate(() => [...document.querySelectorAll('.sheet')].map((s, i) => ({ i: i + 1, t: (s.querySelector('.sheet-t') || {}).textContent || '', over: s.scrollHeight - s.clientHeight })).filter((x) => x.over > 1));
if (over.length) console.log('ПЕРЕПОЛНЕНИЕ ЛИСТОВ:', JSON.stringify(over));
await pg.pdf({ path: path.join(OUT, '2_Razdatochnye_materialy.pdf'), preferCSSPageSize: true, printBackground: true });

await pg.goto(url('guide.html'));
await pg.evaluate(() => document.fonts.ready);
await pg.pdf({
  path: path.join(OUT, '1_Rukovodstvo_vedushchego.pdf'), preferCSSPageSize: true, printBackground: true, displayHeaderFooter: true,
  headerTemplate: '<span></span>',
  footerTemplate: '<div style="width:100%;font-size:7.5pt;color:#566076;font-family:Inter,DejaVu Sans,sans-serif;padding:0 17mm;display:flex;justify-content:space-between"><span>Шерлок. Руководство ведущего</span><span class="pageNumber"></span></div>',
});

await pg.setViewportSize({ width: 1280, height: 720 });
await pg.goto(url('slides.html'));
await pg.evaluate(() => document.fonts.ready);
await pg.pdf({ path: path.join(OUT, '3_Slaydy_dlya_ekrana.pdf'), preferCSSPageSize: true, printBackground: true });
await browser.close();
console.log('PDF готовы:', OUT);
