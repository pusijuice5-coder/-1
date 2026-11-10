# -*- coding: utf-8 -*-
"""Небольшая надстройка над python-pptx: слайды в стиле шаблона (карточки, строки, крупные цифры)."""
import os, re
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR, MSO_AUTO_SIZE
from pptx.oxml.ns import qn
from lxml import etree
from PIL import ImageFont, Image

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, 'assets')
W, H, MX = 13.333, 7.5, 1.125
CW = W - 2 * MX                      # ширина рабочей области


def rgb(h):
    return RGBColor.from_string(h)


DARK, LIME, INK, MUTED = rgb('02691A'), rgb('4CEA4C'), rgb('101F16'), rgb('55655B')
CARD, LINE, WHITE, SOFT, PALE = rgb('F1F4F1'), rgb('D5DDD8'), rgb('FFFFFF'), rgb('DDF6DF'), rgb('CFE3D4')
RED, AMBER = rgb('B42318'), rgb('B7791F')

_FONTS = {}


def _font(sz, bold):
    key = (round(sz * 20), bold)
    if key not in _FONTS:
        fn = '/usr/share/fonts/opentype/inter/Inter-%s.otf' % ('Bold' if bold else 'Regular')
        _FONTS[key] = ImageFont.truetype(fn, key[0])
    return _FONTS[key]


def parse(s):
    """'обычный **жирный** текст' -> [(текст, жирный)]"""
    out = []
    for k, part in enumerate(re.split(r'\*\*', s)):
        if part:
            out.append((part, k % 2 == 1))
    return out or [('', False)]


def norm(paras, sz, bold, color):
    res = []
    for p in (paras if isinstance(paras, (list, tuple)) else [paras]):
        d = dict(t=p) if isinstance(p, str) else dict(p)
        d.setdefault('sz', sz); d.setdefault('b', bold); d.setdefault('color', color); d.setdefault('sa', 0); d.setdefault('sb', 0)
        res.append(d)
    return res


def lines_of(d, w_in):
    avail = w_in * 72 * 20
    n, cur = 1, 0.0
    for text, b in parse(d['t']):
        f = _font(d['sz'], b or d['b'])
        for tok in re.findall(r'[^\s\-]+\-?\s*|\-\s*|\s+', text.replace('\n', ' \n ')):
            if tok.strip() == '' and '\n' in tok:
                n += 1; cur = 0.0; continue
            wd = f.getlength(tok.rstrip()) if cur + f.getlength(tok.rstrip()) > avail else f.getlength(tok)
            if cur > 0 and cur + f.getlength(tok.rstrip()) > avail:
                n += 1; cur = f.getlength(tok)
            else:
                cur += f.getlength(tok)
    return n


def text_h(paras, w_in, sz=14, bold=False, lnsp=1.0):
    h = 0.0
    for d in norm(paras, sz, bold, None):
        h += lines_of(d, w_in) * d['sz'] * 1.21 * lnsp + d['sa'] + d['sb']
    return h / 72.0


class Deck:
    def __init__(self, base=os.path.join(ASSETS, 'base.pptx')):
        self.prs = Presentation(base)
        self.L = {l.name: l for l in self.prs.slide_layouts}
        self.n = 0
        self.warn = []

    def slide(self, title=None, dark=False, notes=None, logo=True, num=True):
        self.n += 1
        s = self.prs.slides.add_slide(self.L['Default Layout'] if (title and not dark) else self.L['No title layout'])
        sl = Slide(self, s, self.n, dark)
        if dark:
            s.background.fill.solid()
            s.background.fill.fore_color.rgb = DARK
        if title and not dark:
            t = s.shapes.title
            t.left, t.top, t.width, t.height = Inches(MX), Inches(0.52), Inches(9.3), Inches(0.95)
            t.text_frame.text = title
            t.text_frame.vertical_anchor = MSO_ANCHOR.TOP
            for p in t.text_frame.paragraphs:
                for r in p.runs:
                    r._r.get_or_add_rPr().set('lang', 'ru-RU')
            if text_h(title, 9.3, 28, True, 0.9) > 0.95:
                self.warn.append('слайд %d: заголовок в две строки' % self.n)
        elif title:
            sl.tx(MX, 0.6, 9.3, 0.6, title, sz=28, bold=True, color=WHITE)
        if logo and dark:          # на тёмных слайдах логотип слева: справа идёт паттерн
            s.shapes.add_picture(os.path.join(ASSETS, 'logo_white.png'), Inches(MX), Inches(0.85), height=Inches(0.62))
        elif logo:
            h = 0.36
            s.shapes.add_picture(os.path.join(ASSETS, 'logo_color.png'), Inches(W - MX - h * 2214 / 645), Inches(0.6), height=Inches(h))
        if num:
            sl.pagenum()
        if notes:
            s.notes_slide.notes_text_frame.text = notes
        return sl

    def save(self, path):
        self.prs.core_properties.title = 'Экспансия. Бизнес-симуляция'
        self.prs.save(path)
        for w in self.warn:
            print('ВНИМАНИЕ:', w)


class Slide:
    def __init__(self, deck, s, n, dark):
        self.d, self.s, self.n, self.dark = deck, s, n, dark

    # ---- текст
    def tx(self, x, y, w, h, paras, sz=14, color=None, bold=False, align='l', anchor='t', lnsp=1.0, check=True):
        color = color or (WHITE if self.dark else INK)
        tb = self.s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.auto_size = MSO_AUTO_SIZE.NONE
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        tf.vertical_anchor = {'t': MSO_ANCHOR.TOP, 'm': MSO_ANCHOR.MIDDLE, 'b': MSO_ANCHOR.BOTTOM}[anchor]
        self._fill_tf(tf, paras, sz, color, bold, align, lnsp)
        for dd in norm(paras, sz, bold, color):          # слово шире блока разорвётся посередине
            for text, b_ in parse(dd['t']):
                for word in re.findall(r'[^\s\-]+\-?', text):
                    if _font(dd['sz'], b_ or dd['b']).getlength(word) / 20 / 72 > w + 0.01:
                        self.d.warn.append('слайд %d: слово шире блока: %s' % (self.n, word))
        if check:
            need = text_h(paras, w, sz, bold, lnsp)
            if need > h + 0.04:
                self.d.warn.append('слайд %d: текст выше блока (%.2f > %.2f): %s' % (self.n, need, h, str(paras)[:60]))
        return tb

    def _fill_tf(self, tf, paras, sz, color, bold, align, lnsp):
        first = True
        for d in norm(paras, sz, bold, color):
            p = tf.paragraphs[0] if first else tf.add_paragraph()
            first = False
            p.alignment = {'l': PP_ALIGN.LEFT, 'c': PP_ALIGN.CENTER, 'r': PP_ALIGN.RIGHT}[d.get('align', align)]
            p.line_spacing = lnsp
            if d['sa']:
                p.space_after = Pt(d['sa'])
            if d['sb']:
                p.space_before = Pt(d['sb'])
            for text, b in parse(d['t']):
                r = p.add_run()
                r.text = text
                r.font.size = Pt(d['sz'])
                r.font.bold = bool(b or d['b'])
                r.font.color.rgb = d['color']
                r._r.get_or_add_rPr().set('lang', 'ru-RU')

    def pagenum(self):
        tb = self.s.shapes.add_textbox(Inches(W - MX - 0.6), Inches(H - 0.52), Inches(0.6), Inches(0.25))
        tf = tb.text_frame
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.RIGHT
        fld = etree.SubElement(p._p, qn('a:fld'), id='{B6F15528-21DE-4FAA-801E-634DDDAF4B2B}', type='slidenum')
        rpr = etree.SubElement(fld, qn('a:rPr'), lang='ru-RU', sz='1000')
        sf = etree.SubElement(rpr, qn('a:solidFill'))
        etree.SubElement(sf, qn('a:srgbClr'), val='B9E3C1' if self.dark else '8A988F')
        etree.SubElement(fld, qn('a:t')).text = str(self.n)

    # ---- фигуры
    def rect(self, x, y, w, h, fill=CARD, r=0.16, shadow=False, line=None, shape=MSO_SHAPE.ROUNDED_RECTANGLE):
        sp = self.s.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
        if shape == MSO_SHAPE.ROUNDED_RECTANGLE:
            sp.adjustments[0] = min(0.5, r / min(w, h))
        if fill is None:
            sp.fill.background()
        else:
            sp.fill.solid()
            sp.fill.fore_color.rgb = fill
        if line is None:
            sp.line.fill.background()
        else:
            sp.line.color.rgb = line
            sp.line.width = Pt(1)
        sp.shadow.inherit = False
        if shadow:
            sppr = sp._element.spPr
            eff = sppr.find(qn('a:effectLst'))
            if eff is not None:
                sppr.remove(eff)
            eff = etree.SubElement(sppr, qn('a:effectLst'))
            sh = etree.SubElement(eff, qn('a:outerShdw'), blurRad='381000', dist='114300', dir='5400000', algn='t', rotWithShape='0')
            c = etree.SubElement(sh, qn('a:srgbClr'), val='02691A')
            etree.SubElement(c, qn('a:alpha'), val='28000')
        sp.text_frame.text = ''
        return sp

    def chip(self, x, y, d, label, fill=LIME, color=INK, sz=None):
        sp = self.rect(x, y, d, d, fill=fill, shape=MSO_SHAPE.OVAL)
        tf = sp.text_frame
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        self._fill_tf(tf, str(label), sz or d * 36, color, True, 'c', 1.0)
        return sp

    def pill(self, x, y, w, h, label, fill=SOFT, color=DARK, sz=12, bold=True):
        sp = self.rect(x, y, w, h, fill=fill, r=h / 2)
        tf = sp.text_frame
        tf.margin_left = tf.margin_right = Inches(0.08)
        tf.margin_top = tf.margin_bottom = 0
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        self._fill_tf(tf, label, sz, color, bold, 'c', 1.0)
        return sp

    def card(self, x, y, w, h, head=None, body=None, accent=False, num=None, pad=0.28, hsz=16, bsz=13, fill=None, big=None, bigsz=40, gap=0.1):
        self.rect(x, y, w, h, fill=(DARK if accent else (fill or CARD)), shadow=accent)
        cy = y + pad
        iw = w - 2 * pad
        hc = WHITE if accent else INK
        bc = rgb('DCEFE0') if accent else MUTED
        if num is not None:
            self.chip(x + pad, cy, 0.42, num, fill=LIME, color=INK, sz=13)
            cy += 0.42 + 0.2
        if big is not None:
            bh = bigsz * 1.15 / 72
            self.tx(x + pad, cy, iw, bh, big, sz=bigsz, bold=True, color=(LIME if accent else DARK))
            cy += bh + 0.08
        if head:
            hh = text_h(head, iw, hsz, True)
            self.tx(x + pad, cy, iw, hh, head, sz=hsz, bold=True, color=hc)
            cy += hh + gap
        if body:
            bh = text_h(body, iw, bsz, False, 1.05)
            self.tx(x + pad, cy, iw, bh, body, sz=bsz, color=bc, lnsp=1.05, check=False)
            cy += bh
        if cy > y + h - pad * 0.6 + 0.02:
            self.d.warn.append('слайд %d: карточка переполнена (%.2f > %.2f): %s' % (self.n, cy - y, h, str(head)[:40]))
        return cy

    def line(self, x1, y1, x2, y2, color=LINE, wpt=1.25, arrow=False, dash=False):
        c = self.s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
        c.line.color.rgb = color
        c.line.width = Pt(wpt)
        ln = c.line._get_or_add_ln()
        if dash:
            etree.SubElement(ln, qn('a:prstDash'), val='dash')
        if arrow:
            etree.SubElement(ln, qn('a:tailEnd'), type='triangle', w='med', len='med')
        return c

    def picture(self, name, x, y, w=None, h=None, crop=None):
        pic = self.s.shapes.add_picture(os.path.join(ASSETS, name), Inches(x), Inches(y), Inches(w) if w else None, Inches(h) if h else None)
        if crop:
            pic.crop_left, pic.crop_top, pic.crop_right, pic.crop_bottom = crop
        return pic


def cols(n, gap=0.22, x0=MX, total=CW):
    w = (total - gap * (n - 1)) / n
    return [(x0 + i * (w + gap), w) for i in range(n)]
