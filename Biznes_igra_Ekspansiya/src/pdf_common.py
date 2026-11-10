# -*- coding: utf-8 -*-
"""Общее для печатных материалов: стили, логотипы, печать HTML в PDF."""
import os, base64, subprocess, io
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, 'assets')
TMP = os.environ.get('EXP_TMP', os.path.join(HERE, '.tmp'))
os.makedirs(TMP, exist_ok=True)


def data_uri(name, max_w=None):
    im = Image.open(os.path.join(ASSETS, name))
    if max_w and im.size[0] > max_w:
        im = im.resize((max_w, round(im.size[1] * max_w / im.size[0])), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, 'PNG', optimize=True)
    return 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()


LOGO = data_uri('logo_color.png', 900)
LOGO_W = data_uri('logo_white.png', 900)
LOGO_SMALL = data_uri('logo_color.png', 360)
PATTERN = data_uri('pattern.png', 1000)

CSS = """
* { box-sizing: border-box }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact }
body { margin: 0; font-family: Inter, Arial, sans-serif; color: #101F16; font-size: 10pt; line-height: 1.46; font-feature-settings: "tnum" }
h1 { font-size: 21pt; line-height: 1.12; margin: 0 0 3mm; font-weight: 700; letter-spacing: -0.012em }
h2 { font-size: 12.5pt; line-height: 1.2; margin: 6mm 0 2.2mm; font-weight: 700; color: #02691A }
h3 { font-size: 10.5pt; margin: 4mm 0 1.4mm; font-weight: 700 }
p { margin: 0 0 2.2mm }
ul, ol { margin: 0 0 2.4mm; padding-left: 5mm }
li { margin: 0 0 1.1mm }
.lead { font-size: 11.5pt; line-height: 1.42; color: #3D4C43; margin-bottom: 5mm }
.small { font-size: 8.5pt; color: #5E6E64 }
.muted { color: #5E6E64 }
b, strong { font-weight: 700 }
table { border-collapse: collapse; width: 100% }
th { background: #02691A; color: #fff; font-weight: 600; font-size: 8.5pt; line-height: 1.25; text-align: left; padding: 1.9mm 2.2mm; vertical-align: bottom }
td { border-bottom: 0.25mm solid #D5DDD8; padding: 1.9mm 2.2mm; vertical-align: top; font-size: 9.4pt }
td.n, th.n { text-align: center }
td.r, th.r { text-align: right }
tr.sum td { font-weight: 700; border-bottom: 0 }
.card { background: #F1F4F1; border-radius: 2.5mm; padding: 4mm 4.6mm }
.card.dark { background: #02691A; color: #fff }
.card.soft { background: #DDF6DF }
.card h3 { margin-top: 0 }
.grid2 { display: grid; grid-template-columns: 1fr 1fr; gap: 4mm }
.grid3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 4mm }
.num { display: inline-flex; width: 5.6mm; height: 5.6mm; border-radius: 50%; background: #4CEA4C; color: #101F16; font-weight: 700; font-size: 8.5pt; align-items: center; justify-content: center; flex: none }
.steps { list-style: none; padding: 0; margin: 0 0 3mm }
.steps li { display: grid; grid-template-columns: 8mm 1fr; margin-bottom: 2mm }
.fill { border-bottom: 0.3mm solid #8E9B93; display: inline-block; min-width: 30mm; height: 5mm; vertical-align: bottom }
.lines div { border-bottom: 0.25mm solid #AEB9B2; height: 8.2mm }
.cb { display: inline-block; width: 3.6mm; height: 3.6mm; border: 0.35mm solid #101F16; border-radius: 0.6mm; vertical-align: -0.6mm; margin-right: 1.5mm }
"""

PAGE_CSS = """
@page { size: A4; margin: 0 }
.page { width: 210mm; height: 297mm; padding: 15mm 17mm 12mm; page-break-after: always; overflow: hidden; display: flex; flex-direction: column }
.ph { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8mm; flex: none }
.ph img { height: 8.4mm }
.ph span { font-size: 8pt; color: #5E6E64 }
.pb { flex: 1; min-height: 0 }
.pf { flex: none; padding-top: 3mm; display: flex; justify-content: space-between; font-size: 7.5pt; color: #8A988F }
.form td, .form th { border: 0.3mm solid #8E9B93 }
.form th { background: #F1F4F1; color: #101F16; font-weight: 700; text-align: center; vertical-align: middle }
.form td { height: 10mm; vertical-align: middle }
.form td.lab { background: #F1F4F1; font-weight: 600; width: 44mm }
.cutline { border-top: 0.3mm dashed #8A988F; margin: 5mm -17mm; }
"""


def page(label, body, footer='Бизнес-симуляция «Экспансия»', pageno=''):
    return ('<section class="page"><div class="ph"><img src="%s"><span>%s</span></div><div class="pb">%s</div>'
            '<div class="pf"><span>%s</span><span>%s</span></div></section>' % (LOGO, label, body, footer, pageno))


def html_doc(title, css, body):
    return '<!doctype html><html lang="ru"><head><meta charset="utf-8"><title>%s</title><style>%s</style></head><body>%s</body></html>' % (title, css, body)


def to_pdf(html, out, header=None, footer=None, name='doc'):
    src = os.path.join(TMP, name + '.html')
    open(src, 'w', encoding='utf8').write(html)
    args = ['node', os.path.join(HERE, 'html2pdf.cjs'), src, out]
    if header:
        hf, ff = os.path.join(TMP, name + '_h.html'), os.path.join(TMP, name + '_f.html')
        open(hf, 'w', encoding='utf8').write(header)
        open(ff, 'w', encoding='utf8').write(footer)
        args += [hf, ff]
    r = subprocess.run(args, capture_output=True, text=True)
    if r.stdout.strip():
        print(r.stdout.strip())
    if r.returncode:
        raise SystemExit(r.stderr)
    return out
