/* Генератор презентации PowerPoint из контента электронного курса.
   node build_pptx.js <папка js с контентом> <папка video курса> <выходной.pptx> [файлы контента через запятую]
   Пример: node build_pptx.js ../sales/course/js ../sales/course/video out.pptx config.js,content.js,content2.js */
const pptxgen = require('pptxgenjs');
const sharp = require('sharp');
const fs = require('fs');
const path = require('path');

const JS = path.resolve(process.argv[2]);
const VIDEO = path.resolve(process.argv[3]);
const OUT = path.resolve(process.argv[4]);
const FILES = (process.argv[5] || 'config.js,content.js,content2.js').split(',');
const A = path.join(__dirname, 'assets');
const THEME_FILE = process.argv[6] ? path.resolve(process.argv[6]) : null;

global.window = {};
FILES.forEach(f => require(path.join(JS, f)));
const COURSE = window.COURSE, CFG = window.COURSE_CONFIG || {};
delete global.window;                              // иначе pptxgenjs считает, что запущен в браузере
const MODW = (CFG.MODULE_WORD || 'Модуль');

const THEME = Object.assign({
  name: 'Emerald Course', headFontFace: 'Arial', bodyFontFace: 'Arial',
  colors: { dk1: '020D09', lt1: 'FFFFFF', dk2: '0B2A20', lt2: 'CFE3DA', accent1: '10B981', accent2: '34D399', accent3: '6EE7B7', accent4: '047857', accent5: 'F1F8F4', accent6: 'FBBF24', hlink: '6EE7B7', folHlink: 'A7F3D0' }
}, THEME_FILE ? JSON.parse(fs.readFileSync(THEME_FILE, 'utf8')) : {});
const BG_TITLE = THEME.bgTitle ? path.resolve(path.dirname(THEME_FILE), THEME.bgTitle) : path.join(A, 'bg_title.jpg');
const BG_CONTENT = THEME.bgContent ? path.resolve(path.dirname(THEME_FILE), THEME.bgContent) : path.join(A, 'bg_content.jpg');
delete THEME.bgTitle; delete THEME.bgContent;

const pres = new pptxgen();
pres.layout = 'LAYOUT_WIDE';                       // 13.33 x 7.5 дюйма
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.title = COURSE.title; pres.author = 'Ipak Yuli Bank'; pres.company = 'Ipak Yuli Bank';
const C = pres.SchemeColor;
const INK = C.background1, BODY = C.background2, CARD = C.text2, ACC = C.accent2, MINT = C.accent3, DEEP = C.accent4, LIGHT = C.accent5, DARK = C.text1, WARN = C.accent6;

const W = 13.333, MX = 0.6, CW = W - 2 * MX, BOTTOM = 6.85;
let TOP = 2.05;            // верх области контента (зависит от числа строк заголовка)
let K = 1;                 // множитель кегля: подбирается так, чтобы слайд был заполнен, но текст не выходил за края
let DRY = false, PAGES = 0; // пробный прогон без создания слайдов
const FAKE = { addText() {}, addShape() {}, addImage() {}, addTable() {}, addNotes() {} };

/* ---------- текстовые утилиты ---------- */
function dec(s) { return String(s).replace(/&nbsp;/g, ' ').replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>'); }
function strip(h) { return dec(String(h || '').replace(/<br\s*\/?>/gi, ' ').replace(/<\/(p|li|div|h3)>/gi, ' ').replace(/<[^>]+>/g, '')).replace(/\s+/g, ' ').trim(); }
/* HTML -> абзацы [{kind:'p'|'li'|'ex'|'h', runs:[{text,b,em}]}] */
function parse(html) {
  const out = []; let cur = null, b = 0, em = 0, kind = 'p'; const spans = [];
  const push = () => { if (cur) { cur.runs = cur.runs.filter(r => r.text); if (cur.runs.length) { cur.runs[0].text = cur.runs[0].text.replace(/^\s+/, ''); const l = cur.runs[cur.runs.length - 1]; l.text = l.text.replace(/\s+$/, ''); if (cur.runs.some(r => r.text.trim())) out.push(cur); } } cur = null; };
  const re = /<(\/?)([a-z0-9]+)([^>]*)>|([^<]+)/gi; let m;
  while ((m = re.exec(String(html || '')))) {
    if (m[4] !== undefined) { const t = dec(m[4]).replace(/\s+/g, ' '); if (t.trim() || cur) { if (!cur) cur = { kind, runs: [] }; cur.runs.push({ text: t, b: b > 0, em: em > 0 }); } continue; }
    const close = m[1] === '/', tag = m[2].toLowerCase(), at = m[3] || '';
    if (tag === 'b' || tag === 'strong') b += close ? -1 : 1;
    else if (tag === 'i' || tag === 'em') em += close ? -1 : 1;
    else if (tag === 'br') push();
    else if (tag === 'p' || tag === 'div' || tag === 'ul') { push(); kind = 'p'; }
    else if (tag === 'li') { push(); kind = close ? 'p' : 'li'; }
    else if (tag === 'h3') { push(); kind = close ? 'p' : 'h'; }
    else if (tag === 'span') { if (!close) { const ex = /class="ex"/.test(at); spans.push(ex); if (ex) { push(); kind = 'ex'; } } else if (spans.pop()) { push(); kind = 'p'; } }
  }
  push(); return out;
}
function ptext(p) { return p.runs.map(r => r.text).join(''); }
/* оценка высоты текста в дюймах */
function lines(text, fs_, w, bold) { fs_ *= K; const cpl = Math.max(6, Math.floor(w * 72 / (fs_ * (bold ? 0.6 : 0.545)))); let n = 0; String(text).split('\n').forEach(l => { n += Math.max(1, Math.ceil(l.length / cpl)); }); return n; }
function H(text, fs_, w, bold) { return lines(text, fs_, w, bold) * fs_ * K * 1.22 / 72; }
function parasH(ps, fs_, w, gap) { let h = 0; ps.forEach((p, i) => { const f = p.kind === 'h' ? fs_ + 2 : fs_; h += H(ptext(p), f, p.kind === 'li' ? w - 0.25 : w, p.kind === 'h') + (i ? (gap || 0.08) : 0); }); return h; }
/* абзацы -> runs pptxgenjs */
function runs(ps, o) {
  o = o || {}; const res = [];
  ps.forEach((p, pi) => {
    const last = pi === ps.length - 1;
    if (p.kind === 'li') { res.push({ text: ptext(p), options: { bullet: { indent: 14 }, color: o.color || BODY, breakLine: !last, paraSpaceAfter: 4 } }); return; }
    p.runs.forEach((r, ri) => {
      const end = ri === p.runs.length - 1, op = { bold: r.b || p.kind === 'h', color: r.em ? MINT : (r.b || p.kind === 'h') ? (o.strong || INK) : (p.kind === 'ex' ? (o.ex || MINT) : (o.color || BODY)), italic: p.kind === 'ex' };
      if (p.kind === 'h') op.fontSize = (o.fontSize || 14) + 2;
      if (end && !last) { op.breakLine = true; }
      if (end) op.paraSpaceAfter = 5;
      res.push({ text: r.text, options: op });
    });
  });
  return res;
}
function titleRuns(t, up) { const parts = String(t).split(/\*([^*]+)\*/); return parts.map((x, i) => ({ text: up === false ? x : x.toUpperCase(), options: { color: i % 2 ? ACC : INK } })).filter(r => r.text); }
function clean(t) { return String(t || '').replace(/\*/g, ''); }

/* ---------- макеты ---------- */
const LOGO = path.join(A, 'logo.png'); const LOGO_R = 960 / 279;
pres.defineSlideMaster({ title: 'TITLE', background: { path: BG_TITLE }, objects: [{ image: { x: MX, y: 0.45, h: 0.5, w: 0.5 * LOGO_R, path: LOGO } }] });
pres.defineSlideMaster({ title: 'DIVIDER', background: { path: BG_TITLE }, objects: [{ image: { x: W - MX - 0.42 * LOGO_R, y: 0.42, h: 0.42, w: 0.42 * LOGO_R, path: LOGO } }] });
pres.defineSlideMaster({
  title: 'CONTENT', background: { path: BG_CONTENT },
  objects: [
    { image: { x: W - MX - 0.36 * LOGO_R, y: 0.36, h: 0.36, w: 0.36 * LOGO_R, path: LOGO } },
    { text: { text: clean(COURSE.title), options: { x: MX, y: 7.02, w: 6, h: 0.3, fontSize: 9, color: MINT, margin: 0 } } },
    { placeholder: { options: { name: 'title', type: 'title', x: MX, y: 0.82, w: CW - 0.2, h: 1.1, fontSize: 27, bold: true, color: INK, align: 'left', valign: 'top', margin: 0 }, text: '' } }
  ],
  slideNumber: { x: W - MX - 0.6, y: 7.0, w: 0.6, h: 0.3, fontSize: 9, color: MINT, align: 'right' }
});

/* ---------- изображения ---------- */
const sizeCache = {};
async function dims(f) { if (!sizeCache[f]) { const m = await sharp(f).metadata(); sizeCache[f] = [m.width, m.height]; } return sizeCache[f]; }
async function charImg(slide, pose, x, y, h, flip, maxW) {
  let f = path.join(A, 'char', pose + '.png'); if (!fs.existsSync(f)) f = path.join(A, 'char', 'smile.png');
  const [w0, h0] = await dims(f); let w = h * w0 / h0; const mw = maxW || (W - x - 0.25);
  if (w > mw) { const k = mw / w; y += h * (1 - k); h *= k; w = mw; }
  slide.addImage({ path: f, x, y, w, h, flipH: !!flip, objectName: 'Наставник', altText: 'Иллюстрация: наставник курса' }); return w;
}
/* иконки из плеера курса */
let IC = {};
try { const src = fs.readFileSync(path.join(JS, 'app.js'), 'utf8'); const a = src.indexOf('var IC = {'), b = src.indexOf('};', a); IC = eval('(' + src.slice(a + 9, b + 1) + ')'); } catch (e) { IC = {}; }
async function icon(name) {
  const f = path.join(A, 'ico', name + '.png');
  if (!fs.existsSync(f)) {
    const svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="160" height="160" fill="none" stroke="#' + THEME.colors.accent3 + '" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">' + (IC[name] || IC.spark || '<circle cx="12" cy="12" r="8"/>') + '</svg>';
    await sharp(Buffer.from(svg)).png().toFile(f);
  }
  return f;
}

/* ---------- базовые элементы ---------- */
let SECTION = '';
function kickerText(s) { const m = s.mod; return (s.kicker || (m.num ? MODW + ' ' + m.num + ' · ' + (m.short || m.track || clean(m.title)) : clean(m.title))).replace(/<[^>]+>/g, '').toUpperCase(); }
function base(s, opt) {
  opt = opt || {};
  const tt = clean(opt.title || s.title || s.mod.title); TOP = tt.length > 44 ? 2.05 : 1.62; PAGES++;
  if (DRY) return FAKE;
  const sl = pres.addSlide({ masterName: 'CONTENT', sectionTitle: SECTION });
  sl.addText(kickerText(s) + (opt.suffix ? ' · ' + opt.suffix.toUpperCase() : ''), { x: MX, y: 0.42, w: 9.6, h: 0.3, fontSize: 10.5, bold: true, color: MINT, charSpacing: 2, margin: 0, isTextBox: true, objectName: 'Раздел' });
  sl.addText(titleRuns(opt.title || s.title || s.mod.title), { placeholder: 'title' });
  return sl;
}
function card(sl, x, y, w, h, o) {
  o = o || {};
  sl.addShape(pres.ShapeType.roundRect, { x, y, w, h, rectRadius: 0.1, fill: { color: o.fill || CARD, transparency: o.tr === undefined ? 12 : o.tr }, line: { color: o.line || DEEP, width: 0.75 }, objectName: o.name || 'Карточка' });
}
function txt(sl, content, x, y, w, h, o) {
  o = Object.assign({ fontSize: 14 }, o || {});
  o.fontSize = Math.round(o.fontSize * K * 2) / 2;
  if (Array.isArray(content)) content.forEach(r => { if (r.options && r.options.fontSize && !r.options._k) { r.options.fontSize = Math.round(r.options.fontSize * K * 2) / 2; r.options._k = 1; } });
  if (Array.isArray(content)) content = content.map(r => { const op = Object.assign({}, r.options); delete op._k; return { text: r.text, options: op }; });
  sl.addText(content, Object.assign({ x, y, w, h, color: BODY, valign: 'top', margin: 0, isTextBox: true }, o));
}
/* подбор масштаба: fn() -> [нижняя граница контента, флаг]; число слайдов и флаг не должны меняться */
async function fit(fn, cands) {
  DRY = true; K = 1; PAGES = 0; const r1 = await fn(), p1 = PAGES; let best = 1;
  for (const c of (cands || [1.4, 1.3, 1.2, 1.1])) { K = c; PAGES = 0; const r = await fn(); if (PAGES === p1 && r[0] <= BOTTOM + 0.03 && r[1] === r1[1]) { best = c; break; } }
  if (process.env.DEBUG_FIT) console.log('fit K=' + best, 'pages=' + p1, 'y1=' + r1[0].toFixed(2));
  DRY = false; K = best; const out = await fn(); K = 1; return out;
}
function badge(sl, label, x, y, sz, o) {
  o = o || {};
  sl.addText(String(label), { x, y, w: o.w || sz, h: sz, shape: pres.ShapeType.roundRect, rectRadius: 0.08, fill: { color: o.fill || ACC }, color: o.color || DARK, bold: true, fontSize: o.fs || 13, align: 'center', valign: 'middle', margin: 0, objectName: 'Метка' });
}
function notes(sl, s, extra) {
  const parts = [];
  if (extra) parts.push(extra);
  if (s && s.say) parts.push('Комментарий наставника (' + (CFG.MENTOR_NAME || 'наставник') + '): ' + strip(s.say.text));
  if (parts.length) sl.addNotes(parts.join('\n\n'));
}
/* реплика наставника внизу слайда; возвращает true, если поместилась */
async function sayStrip(sl, s, y) {
  if (!s.say) return false;
  const t = strip(s.say.text), w = 9.6, th = H(t, 13, w - 0.5) + 0.36, h = Math.max(0.95, th);
  if (y + 0.15 + Math.max(h, 1.25) > BOTTOM + 0.05) return false;
  const top = BOTTOM - Math.max(h, 1.25);
  const cw = await charImg(sl, s.say.pose || 'explain', MX, top, 1.25, s.say.flip);
  const bx = MX + cw + 0.2;
  sl.addShape(pres.ShapeType.roundRect, { x: bx, y: BOTTOM - h, w, h, rectRadius: 0.12, fill: { color: LIGHT }, line: { color: LIGHT, width: 0 }, objectName: 'Реплика наставника' });
  txt(sl, [{ text: (CFG.MENTOR_NAME || 'Наставник').toUpperCase() + '  ', options: { bold: true, color: DEEP, fontSize: 9.5, charSpacing: 1.5, breakLine: true } }, { text: t, options: { color: DARK } }], bx + 0.25, BOTTOM - h + 0.13, w - 0.5, h - 0.2, { fontSize: 13 });
  return true;
}
function leadBlock(sl, s, y, w) {
  if (!s.lead) return y;
  const t = strip(s.lead), h = H(t, 14.5, w || CW - 0.4) + 0.05;
  txt(sl, runs(parse(s.lead), { fontSize: 14.5 }), MX, y, w || CW - 0.4, h, { fontSize: 14.5 });
  return y + h + 0.22;
}

/* ---------- слайды по типам экранов ---------- */
const R = {};

R.hero = async s => {
  const sl = pres.addSlide({ masterName: 'TITLE', sectionTitle: SECTION });
  sl.addText(strip(s.kicker).toUpperCase(), { x: MX, y: 1.45, w: 7.6, h: 0.3, fontSize: 11, bold: true, color: MINT, charSpacing: 2, margin: 0, isTextBox: true });
  sl.addText(titleRuns(s.title), { x: MX, y: 1.9, w: 7.9, h: 2.3, fontSize: 46, bold: true, valign: 'top', margin: 0, isTextBox: true, objectName: 'Заголовок' });
  txt(sl, strip(s.lead), MX, 4.3, 7.4, 1.5, { fontSize: 15 });
  txt(sl, s.chips.map(strip).join('   ·   '), MX, 6.05, 8.2, 0.4, { fontSize: 12.5, color: MINT, bold: true });
  await charImg(sl, s.pose || 'explain', 8.3, 1.55, 5.0);
};

/* обложка с иллюстрацией */
R.cover = async s => {
  const sl = pres.addSlide({ masterName: 'TITLE', sectionTitle: SECTION });
  const img = path.join(JS, '..', s.img);
  if (fs.existsSync(img)) { sl.addImage({ path: img, x: 0, y: 0, w: W, h: 7.5, altText: 'Иллюстрация: караван на Шёлковом пути' }); sl.addShape(pres.ShapeType.rect, { x: 0, y: 0, w: 8.6, h: 7.5, fill: { color: DARK, transparency: 25 }, line: { color: DARK, width: 0 } }); sl.addImage({ path: LOGO, x: MX, y: 0.45, h: 0.5, w: 0.5 * LOGO_R, altText: 'Логотип Ipak Yuli Bank' }); }
  sl.addText(strip(s.kicker).toUpperCase(), { x: MX, y: 1.7, w: 7.6, h: 0.3, fontSize: 11, bold: true, color: MINT, charSpacing: 2, margin: 0, isTextBox: true });
  sl.addText(titleRuns(s.title), { x: MX, y: 2.15, w: 7.6, h: 1.3, fontSize: 54, bold: true, valign: 'top', margin: 0, isTextBox: true, objectName: 'Заголовок' });
  txt(sl, strip(s.lead), MX, 3.6, 7.0, 1.6, { fontSize: 15 });
  txt(sl, s.chips.map(strip).join('   ·   '), MX, 5.5, 7.6, 0.4, { fontSize: 12.5, color: MINT, bold: true });
};
/* карта маршрута -> ряд карточек */
R.route = s => R.cards(Object.assign({}, s, { cols: s.items.length, items: s.items.map(c => ({ num: c.n, h: c.h, t: c.t })) }));

R.module = async s => {
  const m = s.mod, sl = pres.addSlide({ masterName: 'DIVIDER', sectionTitle: SECTION });
  sl.addText(m.num, { x: MX, y: 1.15, w: 3.5, h: 2.2, fontSize: 130, bold: true, color: ACC, margin: 0, isTextBox: true, objectName: 'Номер' });
  if (s.say) await charImg(sl, s.say.pose || 'explain', 1.0, 3.75, 2.9, s.say.flip);
  const x = 4.5, w = W - MX - x;
  sl.addText((MODW + ' ' + m.num + (m.track ? ' · ' + m.track : '')).toUpperCase(), { x, y: 1.25, w, h: 0.3, fontSize: 10.5, bold: true, color: MINT, charSpacing: 2, margin: 0, isTextBox: true });
  const t = clean(s.title || m.title), th = Math.max(0.62, Math.ceil(t.length / Math.floor(w * 72 / (30 * 0.74))) * 30 * 1.16 / 72);
  sl.addText(titleRuns(s.title || m.title), { x, y: 1.65, w, h: th, fontSize: 30, bold: true, valign: 'top', margin: 0, isTextBox: true, objectName: 'Заголовок' });
  let y = 1.65 + th + 0.2;
  if (s.lead) { const lh = H(strip(s.lead), 14.5, w); txt(sl, strip(s.lead), x, y, w, lh, { fontSize: 14.5 }); y += lh + 0.28; }
  const gh = s.goals.reduce((a, g) => a + H(g, 14, w - 1.0) + 0.14, 0) + 0.85;
  card(sl, x, y, w, gh);
  txt(sl, 'После этого раздела вы сможете', x + 0.3, y + 0.22, w - 0.6, 0.35, { fontSize: 15, bold: true, color: INK });
  let gy = y + 0.68;
  s.goals.forEach(g => { const h = H(g, 14, w - 1.0); txt(sl, '+', x + 0.3, gy - 0.03, 0.3, 0.3, { fontSize: 16, color: ACC, bold: true }); txt(sl, g, x + 0.7, gy, w - 1.0, h); gy += h + 0.14; });
  if (s.meta) txt(sl, s.meta.join('   ·   '), x, Math.min(y + gh + 0.2, 6.75), w, 0.3, { fontSize: 11.5, color: MINT, bold: true });
  notes(sl, s);
};

R.text = s => fit(async () => {
  const sl = base(s); let y = leadBlock(sl, s, TOP); const y0 = y;
  const hasAside = !!s.aside, lw = hasAside ? 7.5 : (s.say ? 9.3 : CW);
  (s.blocks || []).forEach(b => { const h = H(strip(b), 14, lw); txt(sl, runs(parse(b)), MX, y, lw, h); y += h + 0.18; });
  (s.list || []).forEach(li => { const h = H(strip(li), 14, lw - 0.4); txt(sl, '+', MX, y - 0.03, 0.3, 0.3, { fontSize: 16, color: ACC, bold: true }); txt(sl, runs(parse(li)), MX + 0.4, y, lw - 0.4, h); y += h + 0.2; });
  if (hasAside) {
    const a = s.aside, x = MX + 7.9, w = CW - 7.9; let h = 0.5;
    const parts = [];
    if (a.big) { parts.push({ text: strip(a.big), options: { fontSize: 40, bold: true, color: ACC, breakLine: true } }); h += 0.75; }
    if (a.h) { parts.push({ text: strip(a.h), options: { fontSize: 15, bold: true, color: INK, breakLine: true, paraSpaceAfter: 5 } }); h += H(strip(a.h), 15, w - 0.6, true) + 0.1; }
    if (a.t) { parts.push({ text: strip(a.t), options: { fontSize: 13, color: BODY, breakLine: !!(a.list || a.src), paraSpaceAfter: 5 } }); h += H(strip(a.t), 13, w - 0.6) + 0.1; }
    (a.list || []).forEach((l, i) => { parts.push({ text: strip(l), options: { fontSize: 13, color: BODY, bullet: { indent: 13 }, breakLine: i < a.list.length - 1 || !!a.src, paraSpaceAfter: 4 } }); h += H(strip(l), 13, w - 0.85) + 0.07; });
    if (a.src) { parts.push({ text: strip(a.src), options: { fontSize: 10, color: MINT } }); h += H(strip(a.src), 10, w - 0.6) + 0.1; }
    const ay = y0;
    card(sl, x, ay, w, h, { fill: DEEP, tr: 45, line: ACC });
    txt(sl, parts, x + 0.3, ay + 0.25, w - 0.6, h - 0.4, { fontSize: 13 });
    y = Math.max(y, ay + h + 0.1);
  } else if (s.say) { await charImg(sl, s.say.pose || 'explain', 10.2, 2.7, 3.3, s.say.flip); }
  const placed = hasAside ? await sayStrip(sl, s, y) : false;
  notes(sl, s);
  return [y, placed];
});

/* сетка карточек с разбиением на слайды */
async function grid(s, items, cols, render, measure, opt) {
  opt = opt || {}; const gap = 0.22, cw = (CW - gap * (cols - 1)) / cols;
  const rowsArr = []; for (let i = 0; i < items.length; i += cols) rowsArr.push(items.slice(i, i + cols));
  let page = 0, sl = null, y = 0, first = true;
  const start = () => { sl = base(s, { suffix: page ? 'продолжение' : opt.suffix, title: opt.title }); y = first ? leadBlock(sl, opt.lead === false ? {} : s, TOP) : TOP; if (first && opt.sub) { txt(sl, opt.sub, MX, y, CW, 0.3, { fontSize: 12, color: MINT, bold: true }); y += 0.4; } first = false; page++; };
  start();
  for (const row of rowsArr) {
    const h = Math.max.apply(null, row.map(it => measure(it, cw)));
    if (y + h > BOTTOM + 0.02 && y > TOP + 0.5) start();
    for (let c = 0; c < row.length; c++) await render(sl, row[c], MX + c * (cw + gap), y, cw, h);
    y += h + gap;
  }
  return { sl, y };
}

R.cards = s => fit(async () => {
  const cols = s.cols || Math.min(s.items.length, 3);
  const measure = (c, w) => {
    let h = 0.5; const iw = w - 0.5;
    if (c.ico || c.num || c.ava) h += 0.6; if (c.big) h += 0.8;
    h += H(strip(c.h), 15, iw, true) + 0.08;
    if (c.t) h += H(strip(c.t), 13, iw) + 0.08;
    (c.list || []).forEach(l => { h += H(strip(l), 13, iw - 0.25) + 0.07; });
    if (c.ex) h += H(strip(c.ex), 12.5, iw) + 0.1;
    return h;
  };
  const render = async (sl, c, x, y, w, h) => {
    const light = /light/.test(c.cls || ''), glow = /glow/.test(c.cls || s.variant || '');
    card(sl, x, y, w, h, light ? { fill: LIGHT, tr: 0, line: LIGHT } : glow ? { fill: DEEP, tr: 45, line: ACC } : {});
    let cy = y + 0.25; const ix = x + 0.25, iw = w - 0.5;
    if (c.ico) { sl.addShape(pres.ShapeType.roundRect, { x: ix, y: cy, w: 0.48, h: 0.48, rectRadius: 0.08, fill: { color: DEEP, transparency: 30 }, line: { color: ACC, width: 0.5 } }); sl.addImage({ path: await icon(c.ico), x: ix + 0.1, y: cy + 0.1, w: 0.28, h: 0.28, altText: 'Иконка' }); cy += 0.6; }
    else if (c.ava) { sl.addText(c.ava, { x: ix, y: cy, w: 0.5, h: 0.5, shape: pres.ShapeType.ellipse, fill: { color: ACC }, color: DARK, bold: true, fontSize: 12, align: 'center', valign: 'middle', margin: 0 }); cy += 0.62; }
    else if (c.num) { badge(sl, c.num, ix, cy, 0.36, { w: Math.max(0.36, 0.2 + String(c.num).length * 0.12), fs: 12 }); cy += 0.6; }
    const parts = [];
    if (c.big) parts.push({ text: strip(c.big), options: { fontSize: 40, bold: true, color: ACC, breakLine: true } });
    parts.push({ text: strip(c.h), options: { fontSize: 15, bold: true, color: light ? DARK : INK, breakLine: !!(c.t || c.list || c.ex), paraSpaceAfter: 5 } });
    if (c.t) parts.push({ text: strip(c.t), options: { fontSize: 13, color: light ? DARK : BODY, breakLine: !!(c.list || c.ex), paraSpaceAfter: 5 } });
    (c.list || []).forEach((l, i) => parts.push({ text: strip(l), options: { fontSize: 13, color: light ? DARK : BODY, bullet: { indent: 13 }, breakLine: i < c.list.length - 1 || !!c.ex, paraSpaceAfter: 3 } }));
    if (c.ex) parts.push({ text: strip(c.ex), options: { fontSize: 12.5, italic: true, color: MINT } });
    txt(sl, parts, ix, cy, iw, y + h - cy - 0.15, { fontSize: 13 });
  };
  const g = await grid(s, s.items, cols, render, measure);
  let y = g.y;
  if (s.src) { const h = H(strip(s.src), 10, CW); if (y + h < BOTTOM + 0.1) { txt(g.sl, strip(s.src), MX, y, CW, h, { fontSize: 10, color: MINT }); y += h + 0.1; } }
  const placed = await sayStrip(g.sl, s, y);
  notes(g.sl, s);
  return [y - 0.2, placed];
});

R.flip = s => fit(async () => {
  const cols = s.cols || Math.min(s.items.length, 3);
  const measure = (c, w) => 0.5 + (c.sub ? 0.3 : 0) + H(strip(c.h), 15, w - 0.5, true) + 0.1 + parasH(parse(c.back), 13, w - 0.5);
  const render = async (sl, c, x, y, w, h) => {
    card(sl, x, y, w, h);
    const parts = [];
    if (c.sub) parts.push({ text: strip(c.sub).toUpperCase(), options: { fontSize: 9.5, bold: true, color: MINT, charSpacing: 1.5, breakLine: true, paraSpaceAfter: 4 } });
    parts.push({ text: strip(c.h), options: { fontSize: 15, bold: true, color: INK, breakLine: true, paraSpaceAfter: 5 } });
    runs(parse(c.back)).forEach(r => { r.options.fontSize = 13; parts.push(r); });
    txt(sl, parts, x + 0.25, y + 0.22, w - 0.5, h - 0.35, { fontSize: 13 });
  };
  const g = await grid(s, s.items, cols, render, measure);
  notes(g.sl, s);
  return [g.y - 0.22, false];
});

/* элементы-«аккордеон»: метка + заголовок + текст, в две колонки */
function accMeasure(c, w) { return 0.45 + H(strip(c.h), 14.5, w - 1.15, true) + 0.08 + parasH(parse(c.body), 13, w - 1.15, 0.07); }
async function accRender(sl, c, x, y, w, h) {
  card(sl, x, y, w, h);
  badge(sl, c.k, x + 0.22, y + 0.22, 0.42, { fill: DEEP, color: MINT, fs: 13 });
  const parts = [{ text: strip(c.h), options: { fontSize: 14.5, bold: true, color: INK, breakLine: true, paraSpaceAfter: 5 } }];
  runs(parse(c.body)).forEach(r => { r.options.fontSize = 13; parts.push(r); });
  txt(sl, parts, x + 0.85, y + 0.2, w - 1.1, h - 0.3, { fontSize: 13 });
}
R.accordion = s => fit(async () => {
  const items = s.items.map((c, i) => Object.assign({ k: c.k || (i + 1) }, c));
  const g = await grid(s, items, 2, accRender, accMeasure);
  notes(g.sl, s);
  return [g.y - 0.22, false];
});

function tableSlide(s, head, rows, opt) {
  opt = opt || {}; const fsz = 12, fo = Math.round(12 * K * 2) / 2, first = 0.24, n = head.length, widths = head.map((_, i) => i === 0 ? CW * first : CW * (1 - first) / (n - 1));
  const rh = r => Math.max.apply(null, r.map((c, i) => H(strip(c), fsz, widths[i] - 0.3, i === 0))) + 0.24;
  let i = 0, page = 0, last = null, endY = 0;
  while (i < rows.length) {
    const sl = base(s, { suffix: (opt.suffix || '') + (page ? (opt.suffix ? ', ' : '') + 'продолжение' : '') || undefined }); last = sl;
    let y = page === 0 ? leadBlock(sl, s, TOP) : TOP; if (opt.suffix && page === 0) { /* метка вкладки уже в строке раздела */ }
    const body = []; let h = 0.4;
    while (i < rows.length && (y + h + rh(rows[i]) <= BOTTOM + 0.02 || !body.length)) { h += rh(rows[i]); body.push(rows[i]); i++; }
    const data = [head.map(c => ({ text: strip(c).toUpperCase(), options: { bold: true, color: MINT, fontSize: Math.round(10 * K), fill: { color: DEEP }, charSpacing: 1 } }))]
      .concat(body.map(r => r.map((c, ci) => ({ text: strip(c), options: { bold: ci === 0, color: ci === 0 ? INK : BODY, fontSize: fo, fill: { color: CARD } } }))));
    sl.addTable(data, { x: MX, y, w: CW, colW: widths, rowH: [0.4].concat(body.map(rh)), border: { type: 'solid', color: THEME.colors.accent4, pt: 0.5 }, margin: [0.06, 0.14, 0.06, 0.14], valign: 'middle', fontFace: THEME.bodyFontFace, objectName: 'Таблица' });
    endY = y + h; page++;
  }
  return { sl: last, y: endY };
}
R.table = s => fit(async () => { const t = tableSlide(s, s.head, s.rows); notes(t.sl, s); return [t.y, false]; }, [1.3, 1.15]);

R.tabs = async s => {
  for (const t of s.tabs) {
    if (t.rows) await fit(async () => { const r = tableSlide(s, t.head, t.rows, { suffix: t.label }); notes(r.sl, s); return [r.y, false]; }, [1.3, 1.15]);
    else if (t.acc) await fit(async () => {
      const items = t.acc.map((c, i) => Object.assign({ k: i + 1 }, c));
      const g = await grid(s, items, 2, accRender, accMeasure, { suffix: t.label });
      notes(g.sl, s); return [g.y - 0.22, false];
    });
  }
};

R.steps = s => fit(async () => {
  const items = s.items.map((c, i) => Object.assign({ n: c.n || ('0' + (i + 1)).slice(-2) }, c));
  const bw = 4.7, sw = CW - 2.75 - bw - 0.5;
  const measure = c => Math.max(0.5 + parasH(parse(c.body), 13, bw - 0.2, 0.06), 0.5 + parasH(parse(c.side), 12.5, sw - 0.2, 0.05), 1.05);
  const render = async (sl, c, x, y, w, h) => {
    card(sl, x, y, w, h);
    sl.addText(String(c.n), { x: x + 0.25, y: y + 0.18, w: 2.3, h: 0.6, fontSize: String(c.n).length > 2 ? 24 : 30, bold: true, color: ACC, margin: 0, isTextBox: true });
    txt(sl, strip(c.full || c.h), x + 0.25, y + 0.78, 2.3, h - 0.9, { fontSize: 13.5, bold: true, color: INK });
    txt(sl, runs(parse(c.body), { fontSize: 13 }), x + 2.75, y + 0.24, bw - 0.2, h - 0.4, { fontSize: 13 });
    sl.addShape(pres.ShapeType.roundRect, { x: x + 2.75 + bw + 0.15, y: y + 0.14, w: sw + 0.2, h: h - 0.28, rectRadius: 0.08, fill: { color: DEEP, transparency: 50 }, line: { color: DEEP, width: 0.5 } });
    txt(sl, runs(parse(c.side), { fontSize: 12.5 }), x + 2.75 + bw + 0.3, y + 0.26, sw - 0.1, h - 0.45, { fontSize: 12.5 });
  };
  const g = await grid(s, items, 1, render, measure);
  notes(g.sl, s);
  return [g.y - 0.22, false];
});

R.compare = s => fit(async () => {
  const sl = base(s); let y = leadBlock(sl, s, TOP);
  const gap = 0.25, w = (CW - gap) / 2;
  const colH = c => 0.75 + c.items.reduce((a, t) => a + H(strip(t), 14, w - 1.0) + 0.16, 0) + 0.1;
  const h = Math.max(colH(s.left), colH(s.right));
  const draw = (c, x, right) => {
    card(sl, x, y, w, h, right ? { fill: DEEP, tr: 45, line: ACC } : (s.bad ? { line: WARN } : {}));
    txt(sl, strip(c.h).toUpperCase(), x + 0.3, y + 0.24, w - 0.6, 0.35, { fontSize: 12.5, bold: true, color: right ? MINT : (s.bad ? WARN : BODY), charSpacing: 1.5 });
    let cy = y + 0.75;
    c.items.forEach(t => { const ih = H(strip(t), 14, w - 1.0); txt(sl, right ? '✓' : '—', x + 0.3, cy, 0.3, 0.3, { fontSize: 14, bold: true, color: right ? ACC : (s.bad ? WARN : BODY) }); txt(sl, strip(t), x + 0.7, cy, w - 1.0, ih); cy += ih + 0.16; });
  };
  draw(s.left, MX, false); draw(s.right, MX + w + gap, true);
  const placed = await sayStrip(sl, s, y + h + 0.1);
  notes(sl, s);
  return [y + h, placed];
});

R.video = async s => {
  const sl = base(s); const y = TOP + 0.05, pw = 6.9, ph = pw * 9 / 16;
  const poster = path.join(VIDEO, path.basename(s.poster));
  if (fs.existsSync(poster)) sl.addImage({ path: poster, x: MX, y, w: pw, h: ph, objectName: 'Кадр из видеоролика', altText: 'Кадр из видеоролика' });
  sl.addShape(pres.ShapeType.rect, { x: MX, y, w: pw, h: ph, fill: { color: DARK, transparency: 100 }, line: { color: DEEP, width: 1 } });
  txt(sl, 'Видеоролик с озвучкой открывается в электронном курсе. Файл в пакете: ' + s.src, MX, y + ph + 0.15, pw, 0.5, { fontSize: 11, color: MINT });
  const x = MX + pw + 0.4, w = CW - pw - 0.4;
  txt(sl, 'ТЕКСТ РОЛИКА', x, y, w, 0.3, { fontSize: 10.5, bold: true, color: MINT, charSpacing: 2 });
  const ps = []; s.transcript.forEach(t => parse(t).forEach(p => ps.push(p)));
  const total = strip(s.transcript.join(' ')).length, fsz = total > 760 ? 11.5 : 12.5;
  txt(sl, runs(ps, { fontSize: fsz }).map(r => { r.options.fontSize = fsz; return r; }), x, y + 0.4, w, BOTTOM - y - 0.4, { fontSize: fsz });
  notes(sl, s, 'Текст ролика (озвучка): ' + strip(s.transcript.join(' ')));
};

const LET = ['А', 'Б', 'В', 'Г', 'Д', 'Е'];
function rot(n, k) { const o = []; for (let i = 0; i < n; i++) o.push((i + k) % n); return o; }
let QN = 0;
async function questionSlide(s, q, label, pose) {
  const order = rot(q.opts.length, 1 + (QN++ % (q.opts.length - 1 || 1)));
  return fit(async () => {
  const sl = base(s, { suffix: label }); const multi = Array.isArray(q.a), right = multi ? q.a : [q.a], w = 9.4;
  let y = TOP; const qt = strip(q.q), qh = H(qt, 18, w, true);
  txt(sl, qt, MX, y, w, qh, { fontSize: 18, bold: true, color: INK }); y += qh + 0.12;
  if (multi) { txt(sl, 'Выберите все верные варианты', MX, y, w, 0.3, { fontSize: 11.5, color: MINT }); y += 0.38; } else y += 0.1;
  const ans = [];
  order.forEach((oi, k) => {
    const t = strip(q.opts[oi]), h = Math.max(0.56, H(t, 14, w - 1.1) + 0.28);
    card(sl, MX, y, w, h); badge(sl, LET[k], MX + 0.18, y + (h - 0.36) / 2, 0.36, { fill: DEEP, color: MINT, fs: 12.5 });
    txt(sl, t, MX + 0.75, y, w - 1.0, h, { valign: 'middle' });
    if (right.indexOf(oi) >= 0) ans.push(LET[k]);
    y += h + 0.14;
  });
  await charImg(sl, pose || 'think', 10.45, 2.9, 3.1);
  sl.addNotes('Верный ответ: ' + ans.join(', ') + '.\n' + strip(q.why));
  return [y, false];
  }, [1.3, 1.2, 1.1]);
}
R.quiz = async s => { for (let i = 0; i < s.questions.length; i++) await questionSlide(s, s.questions[i], 'вопрос ' + (i + 1) + ' из ' + s.questions.length, ['think', 'curious', 'doubt'][i % 3]); };

R.classify = s => fit(async () => {
  const items = s.items.map((it, i) => Object.assign({ i: i + 1 }, it));
  const measure = (it, w) => Math.max(0.6, H(strip(it.t), 14, w - 1.1) + 0.3);
  const render = async (sl, it, x, y, w, h) => { card(sl, x, y, w, h); badge(sl, it.i, x + 0.18, y + (h - 0.36) / 2, 0.36, { fill: DEEP, color: MINT, fs: 12.5 }); txt(sl, strip(it.t), x + 0.75, y, w - 1.0, h, { valign: 'middle' }); };
  const g = await grid(s, items, 2, render, measure, { sub: 'Категории: ' + s.cats.join('  ·  ') });
  g.sl.addNotes('Ответы: ' + s.items.map((it, i) => (i + 1) + ' — ' + s.cats[it.a] + (it.why ? ' (' + strip(it.why) + ')' : '')).join('; ') + '.');
  return [g.y - 0.22, false];
});

R.sort = s => fit(async () => {
  const n = s.items.length, order = rot(n, 2).reverse();
  const items = order.map((oi, k) => ({ k: LET[k], t: s.items[oi], oi }));
  const measure = (it, w) => Math.max(0.6, H(strip(it.t), 14, w - 1.1) + 0.3);
  const render = async (sl, it, x, y, w, h) => { card(sl, x, y, w, h); badge(sl, it.k, x + 0.18, y + (h - 0.36) / 2, 0.36, { fill: DEEP, color: MINT, fs: 12.5 }); txt(sl, strip(it.t), x + 0.75, y, w - 1.0, h, { valign: 'middle' }); };
  const g = await grid(s, items, 1, render, measure);
  const right = s.items.map((_, i) => items.find(x => x.oi === i).k).join(' → ');
  g.sl.addNotes('Правильный порядок: ' + right + '.');
  return [g.y - 0.22, false];
});

R.dialog = async s => {
  const c = s.client; let sl = base(s, { suffix: 'условия' });
  card(sl, MX, TOP, 5.2, 3.6);
  sl.addText(c.ini, { x: MX + 0.35, y: TOP + 0.3, w: 0.9, h: 0.9, shape: pres.ShapeType.ellipse, fill: { color: ACC }, color: DARK, bold: true, fontSize: 26, align: 'center', valign: 'middle', margin: 0 });
  txt(sl, [{ text: strip(c.name), options: { fontSize: 17, bold: true, color: INK, breakLine: true } }, { text: strip(c.role), options: { fontSize: 12.5, color: MINT } }], MX + 1.45, TOP + 0.38, 3.5, 0.8);
  txt(sl, strip(c.ctx), MX + 0.35, TOP + 1.45, 4.5, 2.0, { fontSize: 13.5 });
  const x = MX + 5.6, w = CW - 5.6;
  txt(sl, [{ text: 'Как работать с тренажёром', options: { fontSize: 16, bold: true, color: INK, breakLine: true, paraSpaceAfter: 8 } },
    { text: 'В диалоге ' + s.steps.length + ' шагов. На каждом слайде — реплика клиента и три варианта ответа сотрудника.', options: { bullet: { indent: 14 }, breakLine: true, paraSpaceAfter: 6 } },
    { text: 'Выберите лучший вариант и объясните почему.', options: { bullet: { indent: 14 }, breakLine: true, paraSpaceAfter: 6 } },
    { text: 'Разбор каждого варианта приведён в заметках к слайду.', options: { bullet: { indent: 14 } } }], x, TOP + 0.1, w - 2.6, 3.2, { fontSize: 14 });
  await charImg(sl, 'curious', W - MX - 2.6, TOP + 0.9, 3.2);
  for (let k = 0; k < s.steps.length; k++) {
    const sp = s.steps[k];
    await fit(async () => {
    const sl = base(s, { suffix: 'шаг ' + (k + 1) + ' из ' + s.steps.length });
    let y = TOP; const ct = strip(sp.c), bw = 8.6, bh = H(ct, 15, bw - 0.6) + 0.62;
    sl.addShape(pres.ShapeType.roundRect, { x: MX, y, w: bw, h: bh, rectRadius: 0.12, fill: { color: LIGHT }, line: { color: LIGHT, width: 0 }, objectName: 'Реплика клиента' });
    txt(sl, [{ text: strip(c.name).toUpperCase(), options: { fontSize: 9.5, bold: true, color: DEEP, charSpacing: 1.5, breakLine: true } }, { text: ct, options: { fontSize: 15, color: DARK } }], MX + 0.3, y + 0.14, bw - 0.6, bh - 0.2);
    y += bh + 0.25;
    const order = rot(sp.opts.length, (k + 1) % sp.opts.length), nt = [];
    order.forEach((oi, j) => {
      const o = sp.opts[oi], t = strip(o.t), h = Math.max(0.6, H(t, 13, CW - 1.1) + 0.28);
      card(sl, MX, y, CW, h); badge(sl, LET[j], MX + 0.18, y + (h - 0.36) / 2, 0.36, { fill: DEEP, color: MINT, fs: 12.5 });
      txt(sl, t, MX + 0.75, y, CW - 1.0, h, { fontSize: 13, valign: 'middle' });
      nt.push(LET[j] + ' — ' + (o.s === 2 ? 'лучший ответ' : o.s === 1 ? 'можно лучше' : 'неудачно') + '. ' + strip(o.fb));
      y += h + 0.14;
    });
    sl.addNotes(nt.join('\n'));
    return [y, false];
    }, [1.35, 1.25, 1.15]);
  }
};

R.exam = async s => {
  const sl = base(s); const n = s.questions.length, pass = CFG.PASS_SCORE || 80, gap = 0.22, w = (CW - 2 * gap - 3.0) / 3;
  [[String(n), 'вопросов', s.note || 'По всем разделам курса.'], [pass + '%', 'проходной балл', 'Нужно ответить верно минимум на ' + Math.ceil(n * pass / 100) + ' из ' + n + '.'], ['∞', 'попыток', 'В электронном курсе тест можно пройти повторно.']].forEach((c, i) => {
    const x = MX + i * (w + gap); card(sl, x, TOP + 0.2, w, 2.6);
    txt(sl, [{ text: c[0], options: { fontSize: 44, bold: true, color: ACC, breakLine: true } }, { text: c[1], options: { fontSize: 15, bold: true, color: INK, breakLine: true, paraSpaceAfter: 5 } }, { text: c[2], options: { fontSize: 13, color: BODY } }], x + 0.3, TOP + 0.45, w - 0.6, 2.2);
  });
  await charImg(sl, 'books', W - MX - 2.7, TOP + 0.1, 3.4);
  txt(sl, 'Верные ответы и пояснения приведены в заметках к слайдам с вопросами.', MX, TOP + 3.1, 9, 0.4, { fontSize: 12, color: MINT });
  for (let i = 0; i < n; i++) await questionSlide(s, s.questions[i], 'вопрос ' + (i + 1) + ' из ' + n, ['think', 'curious', 'doubt', 'search'][i % 4]);
};

R.finish = async s => {
  const sl = pres.addSlide({ masterName: 'TITLE', sectionTitle: SECTION });
  sl.addText('КУРС ПРОЙДЕН', { x: MX, y: 1.2, w: 7, h: 0.3, fontSize: 11, bold: true, color: MINT, charSpacing: 2, margin: 0, isTextBox: true });
  sl.addText(titleRuns(s.title), { x: MX, y: 1.5, w: 8.2, h: 1.2, fontSize: 34, bold: true, valign: 'top', margin: 0, isTextBox: true, objectName: 'Заголовок' });
  const lh = H(strip(s.lead), 14, 8.0); txt(sl, strip(s.lead), MX, 2.8, 8.0, lh);
  let y = 2.8 + lh + 0.2; txt(sl, strip(s.planTitle), MX, y, 8, 0.35, { fontSize: 15, bold: true, color: INK }); y += 0.42;
  s.plan.forEach(p => { const h = Math.max(0.5, H(strip(p), 13, 7.2) + 0.22); card(sl, MX, y, 8.2, h); sl.addShape(pres.ShapeType.roundRect, { x: MX + 0.2, y: y + (h - 0.24) / 2, w: 0.24, h: 0.24, rectRadius: 0.04, fill: { color: DARK, transparency: 100 }, line: { color: ACC, width: 1.25 } }); txt(sl, strip(p), MX + 0.65, y, 7.4, h, { fontSize: 13, valign: 'middle' }); y += h + 0.1; });
  await charImg(sl, 'celebrate', 9.0, 1.9, 4.3);
};

(async () => {
  let n = 0;
  for (const m of COURSE.modules) {
    SECTION = (m.num ? m.num + ' · ' : '') + clean(m.title);
    pres.addSection({ title: SECTION });
    for (const s of m.screens) { s.mod = m; const before = pres.slides ? pres.slides.length : 0; await (R[s.type] || R.text)(s); n++; }
  }
  await pres.writeFile({ fileName: OUT });
  const { applyTheme } = require('./apply_theme.js');
  await applyTheme(OUT, THEME);
  console.log('screens', n, '->', OUT);
})().catch(e => { console.error(e); process.exit(1); });
