"""Google Pay course (RU) for the Retail block — animated slides without narration.

Animations play automatically after each slide appears (no clicks, no audio): elements fade in and rise
slightly into place, tap markers pulse, Morph moves shared objects between slides.
Everything stays inside the 13.333 x 7.5 in frame. Handwritten notes are rendered to PNG,
so they look the same on any computer. Run check_fit.py on the result to verify text fit and bounds.
"""
import copy
import os
import sys
from lxml import etree
from PIL import Image, ImageDraw, ImageFont
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
A = os.path.join(HERE, "assets")
SCR = os.path.join(HERE, "screens")
FONTS = os.path.join(HERE, "fonts")
HAND_DIR = os.path.join(HERE, "build_hand")
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "GooglePay", "GooglePay_kurs_RU.pptx")
os.makedirs(HAND_DIR, exist_ok=True)

INK, GREY, LIGHT, LINE = "1C1F1D", "7D857F", "B4BCB7", "DCE2DE"
ACCENT, LIME, MINT, MUTED = "02691A", "4CEA4C", "E6F8E6", "F3F5F4"
F_REG, F_MED, F_SEMI, F_LIGHT = "Manrope", "Manrope Medium", "Manrope SemiBold", "Manrope Light"
SW, SH = 13.333, 7.5


def _popup_bg(name):
    p = os.path.join(A, name)
    return p if os.path.exists(p) else os.path.join(A, "bg_main.jpg")


NOTES = {
    4: "Факт: Visa и Mastercard Ipak Yuli Bank — пресс-релиз ЦБ от 27.10.2026 и п. 1.3 публичной оферты банка. [Сверить: все ли карточные продукты подключаются.]",
    5: "[Сверить с продуктовой командой: на каких телефонах клиентов чаще всего не работает.]",
    7: "[Сверить: что предлагать клиенту без Visa/Mastercard — по процедуре банка.]",
    8: "Huawei, выпущенные после 2019 года, в большинстве продаются без сервисов Google.",
    12: "[Сверить: путь внутри Ipak Yuli Mobile. Приложение банка запрещает запись экрана — нужны макеты от команды приложения или фото экрана вторым телефоном.]",
    13: "[Сверить: название кнопки принятия оферты — в записи экрана её не видно.]",
    16: "ДОПУЩЕНИЕ: правила — черновик. Согласовать с информационной безопасностью и после этого убрать плашку «Черновик».",
    18: "[Сверить: где сотрудник смотрит статус карты, лимиты и причину отказа — по процедуре банка.]",
    22: "Сервис Google: google.com/android/find (в 2025 году переименован в Find Hub — в меню телефона название может отличаться). [Сверить: может ли банк сам отключить карту в телефоне, не блокируя пластик.]",
    25: "Служебный слайд. Тест собирается в iSpring по таблице GooglePay/GooglePay_test.xlsx.",
}

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(SW), Inches(SH)
BLANK = prs.slide_layouts[6]

MORPH = ('<mc:AlternateContent xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" '
         'xmlns:p159="http://schemas.microsoft.com/office/powerpoint/2015/09/main">'
         '<mc:Choice Requires="p159"><p:transition xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" '
         'xmlns:p14="http://schemas.microsoft.com/office/powerpoint/2010/main" spd="slow" p14:dur="1000">'
         '<p159:morph option="byObject"/></p:transition></mc:Choice>'
         '<mc:Fallback><p:transition xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" spd="slow"><p:fade/></p:transition></mc:Fallback>'
         '</mc:AlternateContent>')


# ---------------- helpers ----------------
def rgb(h):
    return RGBColor.from_string(h)


def set_name(shape, name):
    shape._element.xpath("./*[1]/p:cNvPr")[0].set("name", name)


def text_box(c, name, x, y, w, h, paras, anchor=MSO_ANCHOR.TOP):
    """paras: list of runs lists; run = (text, font, size, color[, bold]) or 'BR' or {'align':..}."""
    tb = c.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    set_name(tb, name)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    for i, runs in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        for r in runs:
            if r == "BR":
                p.add_line_break()
                continue
            if isinstance(r, dict):
                if "align" in r:
                    p.alignment = r["align"]
                if "after" in r:
                    p.space_after = Pt(r["after"])
                continue
            run = p.add_run()
            run.text = r[0]
            run.font.name, run.font.size, run.font.color.rgb = r[1], Pt(r[2]), rgb(r[3])
            if len(r) > 4 and r[4]:
                run.font.bold = True
        p.line_spacing = 1.0
    return tb


def add_shadow(shape, blur=0.35, dist=0.06, alpha=16):
    spPr = shape._element.spPr
    eff = etree.SubElement(spPr, qn("a:effectLst"))
    sh = etree.SubElement(eff, qn("a:outerShdw"))
    for k, v in (("blurRad", int(Inches(blur))), ("dist", int(Inches(dist))), ("dir", 5400000)):
        sh.set(k, str(v))
    sh.set("algn", "t")
    sh.set("rotWithShape", "0")
    c = etree.SubElement(sh, qn("a:srgbClr"))
    c.set("val", "000000")
    etree.SubElement(c, qn("a:alpha")).set("val", str(alpha * 1000))


def rect(c, name, kind, x, y, w, h, fill=None, line=None, line_w=None, alpha=None, adj=None, shadow=None):
    sh = c.shapes.add_shape(kind, Inches(x), Inches(y), Inches(w), Inches(h))
    set_name(sh, name)
    if fill:
        sh.fill.solid()
        sh.fill.fore_color.rgb = rgb(fill)
        if alpha is not None:
            clr = sh.fill._xPr.find(qn("a:solidFill"))[0]
            etree.SubElement(clr, qn("a:alpha")).set("val", str(int(alpha * 1000)))
    else:
        sh.fill.background()
    if line:
        sh.line.color.rgb = rgb(line)
        sh.line.width = Pt(line_w or 1)
    else:
        sh.line.fill.background()
    if adj is not None:
        sh.adjustments[0] = adj
    if shadow:
        add_shadow(sh, *shadow)
    tf = sh.text_frame
    tf.margin_left = tf.margin_right = Inches(0.06)
    tf.margin_top = tf.margin_bottom = 0
    return sh


def shape_text(sh, runs, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE):
    tf = sh.text_frame
    tf.vertical_anchor = anchor
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    for text, font, size, color in runs:
        r = p.add_run()
        r.text = text
        r.font.name, r.font.size, r.font.color.rgb = font, Pt(size), rgb(color)


def picture(c, name, path, x, y, h=None, w=None):
    im = Image.open(path)
    ar = im.width / im.height
    if h is not None and w is None:
        w = h * ar
    if w is not None and h is None:
        h = w / ar
    pic = c.shapes.add_picture(path, Inches(x), Inches(y), Inches(w), Inches(h))
    set_name(pic, name)
    return pic


def round_picture(pic, adj):
    pic.auto_shape_type = MSO_SHAPE.ROUNDED_RECTANGLE
    av = pic._element.spPr.find(qn("a:prstGeom")).find(qn("a:avLst"))
    for g in list(av):
        av.remove(g)
    gd = etree.SubElement(av, qn("a:gd"))
    gd.set("name", "adj")
    gd.set("fmla", f"val {adj}")


def pic_alpha(pic, amt):
    blip = pic._element.blipFill.find(qn("a:blip"))
    etree.SubElement(blip, qn("a:alphaModFix")).set("amt", str(int(amt * 1000)))


def group(c, name):
    g = c.shapes.add_group_shape()
    set_name(g, name)
    return g


_hand_n = [0]


def hand(c, name, text, x, y, size=28, rot=5, color=ACCENT, anchor="left"):
    """Handwritten note rendered to PNG (Caveat). text may contain '\\n'. Returns (picture, w, h)."""
    _hand_n[0] += 1
    scale = 6  # px per pt
    font = ImageFont.truetype(os.path.join(FONTS, "Caveat-600.ttf"), int(size * scale))
    lines = text.split("\n")
    asc, desc = font.getmetrics()
    lh = int((asc + desc) * 0.98)
    wmax = int(max(font.getlength(t) for t in lines)) + 40
    im = Image.new("RGBA", (wmax, lh * len(lines) + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    col = tuple(int(color[i:i + 2], 16) for i in (0, 2, 4)) + (255,)
    for i, t in enumerate(lines):
        d.text((20, 20 + i * lh), t, font=font, fill=col)
    im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
    im = im.crop(im.getchannel("A").getbbox())
    path = os.path.join(HAND_DIR, f"hand_{_hand_n[0]:02d}.png")
    im.save(path)
    w, h = im.width / (scale * 72), im.height / (scale * 72)
    if anchor == "right":
        x = x - w
    pic = picture(c, name, path, x, y, w=w, h=h)
    return pic, w, h


_MF = {}


def text_w(text, size, fname="Manrope-400.ttf"):
    if fname not in _MF:
        _MF[fname] = ImageFont.truetype(os.path.join(FONTS, fname), 100)
    return _MF[fname].getlength(text) * size / 100.0 / 72.0


def pill(c, name, x, y, text, color=ACCENT, size=10.5):
    w = text_w(text, size) + 0.42
    sh = rect(c, name, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, 0.3, fill="FFFFFF", line=color, line_w=1, adj=0.5)
    shape_text(sh, [(text, F_REG, size, color)])
    return w


def card(c, name, x, y, w, h, fill="FFFFFF", line=None, shadow=(0.45, 0.06, 14)):
    return rect(c, name, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h, fill=fill, line=line, line_w=1.5, adj=0.06, shadow=shadow)


def tap_marker(c, name, cx, cy, d=0.58):
    return rect(c, name, MSO_SHAPE.OVAL, cx - d / 2, cy - d / 2, d, d, fill=LIME, alpha=45, line="FFFFFF", line_w=2.5,
                shadow=(0.18, 0.02, 25))


def bullet_item(c, name, x, y, w, text, mark="✓", fill=LIME, mcol=ACCENT, size=14.5, h=0.7):
    g = group(c, name)
    dot = rect(g, f"{name}_dot", MSO_SHAPE.OVAL, x, y + 0.03, 0.32, 0.32, fill=fill)
    shape_text(dot, [(mark, F_SEMI, 10.5, mcol)])
    text_box(g, f"{name}_txt", x + 0.48, y, w - 0.48, h, [[(text, F_REG, size, INK)]])
    return g


def chrome(slide, bg):
    picture(slide, "!!bg", bg, 0, 0, w=SW, h=SH)
    picture(slide, "!!logo", f"{A}/logo.png", 0.55, 0.36, h=0.42)
    text_box(slide, "!!hdr", 8.6, 0.42, 4.2, 0.3, [[{"align": PP_ALIGN.RIGHT}, ("Курс · Google Pay", F_REG, 10, GREY)]])
    text_box(slide, "!!ftrL", 0.55, 7.0, 4, 0.28, [[("Розничный блок", F_REG, 10, GREY)]])
    text_box(slide, "!!ftrR", 8.6, 7.0, 4.2, 0.28, [[{"align": PP_ALIGN.RIGHT}, ("Ipak Yuli Bank", F_REG, 10, GREY)]])


def title2(slide, l1, l2, size=38, x=0.6, y=1.0, w=11.8, h=1.75):
    return text_box(slide, "!!title", x, y, w, h, [[(l1, F_MED, size, INK), "BR", (l2, F_MED, size, ACCENT)]])


P_NS = "http://schemas.openxmlformats.org/presentationml/2006/main"


class Anim:
    """Auto-playing entrance effects, mirroring PowerPoint's own XML (as in the Apple Pay course)."""

    def __init__(self, slide):
        self.slide = slide
        self.fx = []
        self.bld = []

    def _sp(self, shape):
        return shape.shape_id, shape._element.tag == qn("p:sp")

    def fade(self, shape, delay, dur=0.6):
        sp, is_sp = self._sp(shape)
        grp = ' grpId="0"' if is_sp else ""
        self.fx.append(
            f'<p:par><p:cTn id="0" presetID="10" presetClass="entr" presetSubtype="0" fill="hold"{grp} nodeType="withEffect">'
            f'<p:stCondLst><p:cond delay="{int(delay * 1000)}"/></p:stCondLst><p:childTnLst>'
            f'<p:set><p:cBhvr><p:cTn id="0" dur="1" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst></p:cTn>'
            f'<p:tgtEl><p:spTgt spid="{sp}"/></p:tgtEl><p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst></p:cBhvr>'
            f'<p:to><p:strVal val="visible"/></p:to></p:set>'
            f'<p:animEffect transition="in" filter="fade"><p:cBhvr><p:cTn id="0" dur="{int(dur * 1000)}"/>'
            f'<p:tgtEl><p:spTgt spid="{sp}"/></p:tgtEl></p:cBhvr></p:animEffect></p:childTnLst></p:cTn></p:par>')
        if is_sp:
            self.bld.append((sp, 0))

    def rise(self, shape, delay, dur=0.8, dy=0.035):
        """Fade in while rising dy (share of slide height) into place."""
        self.fade(shape, delay, dur=min(dur, 0.7))
        sp, is_sp = self._sp(shape)
        grp = ' grpId="1"' if is_sp else ""
        self.fx.append(
            f'<p:par><p:cTn id="0" presetID="42" presetClass="path" presetSubtype="0" decel="100000" fill="hold"{grp} nodeType="withEffect">'
            f'<p:stCondLst><p:cond delay="{int(delay * 1000)}"/></p:stCondLst><p:childTnLst>'
            f'<p:animMotion origin="layout" path="M 0 {dy:.5f} L 0 0 " pathEditMode="relative" rAng="0" ptsTypes="AA">'
            f'<p:cBhvr><p:cTn id="0" dur="{int(dur * 1000)}" fill="hold"/><p:tgtEl><p:spTgt spid="{sp}"/></p:tgtEl>'
            f'<p:attrNameLst><p:attrName>ppt_x</p:attrName><p:attrName>ppt_y</p:attrName></p:attrNameLst></p:cBhvr>'
            f'<p:rCtr x="0" y="{-int(dy * 50000)}"/></p:animMotion></p:childTnLst></p:cTn></p:par>')
        if is_sp:
            self.bld.append((sp, 1))

    def pulse(self, shape, delay, repeat=2, scale=115):
        sp, is_sp = self._sp(shape)
        self.fx.append(
            f'<p:par><p:cTn id="0" presetID="6" presetClass="emph" presetSubtype="0" repeatCount="{repeat * 1000}" '
            f'accel="50000" decel="50000" autoRev="1" fill="hold" grpId="2" nodeType="withEffect">'
            f'<p:stCondLst><p:cond delay="{int(delay * 1000)}"/></p:stCondLst><p:childTnLst>'
            f'<p:animScale><p:cBhvr><p:cTn id="0" dur="450" fill="hold"/><p:tgtEl><p:spTgt spid="{sp}"/></p:tgtEl></p:cBhvr>'
            f'<p:by x="{scale * 1000}" y="{scale * 1000}"/></p:animScale></p:childTnLst></p:cTn></p:par>')
        if is_sp:
            self.bld.append((sp, 2))

    def stagger(self, shapes, start=0.15, step=0.18, how="rise"):
        for i, sh in enumerate(shapes):
            getattr(self, how)(sh, start + i * step)
        return start + len(shapes) * step

    def xml(self):
        if not self.fx:
            return None
        seen = []
        for b in self.bld:
            if b not in seen:
                seen.append(b)
        bld = ("<p:bldLst>" + "".join(f'<p:bldP spid="{s}" grpId="{g}" animBg="1"/>' for s, g in seen) + "</p:bldLst>") if seen else ""
        x = (f'<p:timing xmlns:p="{P_NS}"><p:tnLst><p:par><p:cTn id="0" dur="indefinite" restart="never" nodeType="tmRoot"><p:childTnLst>'
             f'<p:seq concurrent="1" nextAc="seek"><p:cTn id="0" dur="indefinite" nodeType="mainSeq"><p:childTnLst>'
             f'<p:par><p:cTn id="0" fill="hold"><p:stCondLst><p:cond delay="indefinite"/><p:cond evt="onBegin" delay="0"><p:tn val="2"/></p:cond></p:stCondLst><p:childTnLst>'
             f'<p:par><p:cTn id="0" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>'
             + "".join(self.fx) +
             f'</p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn>'
             f'<p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>'
             f'<p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst></p:seq>'
             f'</p:childTnLst></p:cTn></p:par></p:tnLst>{bld}</p:timing>')
        el = etree.fromstring(x)
        for k, ctn in enumerate(el.iter(qn("p:cTn")), start=1):
            ctn.set("id", str(k))
        return el


def finish(slide, n, anim=None):
    clr = slide._element.find(qn("p:clrMapOvr"))
    trans = etree.fromstring(MORPH)
    clr.addnext(trans)
    if anim is not None:
        t = anim.xml()
        if t is not None:
            trans.addnext(t)
    if n in NOTES:
        slide.notes_slide.notes_text_frame.text = NOTES[n]


def new_slide():
    return prs.slides.add_slide(BLANK)


# ---------------- phone ----------------
SCR_W, SCR_H = 2.716, 6.05
BEZ = 0.09


def phone(slide, screen_path, x, y, sw=SCR_W, suffix=""):
    sh_ = sw * SCR_H / SCR_W
    b = BEZ * sw / SCR_W
    body = rect(slide, f"!!phone{suffix}", MSO_SHAPE.ROUNDED_RECTANGLE, x - b, y - b, sw + 2 * b, sh_ + 2 * b,
                fill="121413", adj=0.075, shadow=(0.45, 0.10, 22))
    pic = picture(slide, f"!!screen{suffix}", screen_path, x, y, w=sw, h=sh_)
    round_picture(pic, 5200)
    pt = (lambda rx, ry: (x + rx * sw, y + ry * sh_))
    pt.shapes = (body, pic)
    return pt


# ---------------- Morph-safe animation helpers ----------------
PREV = {"names": set()}


def names_of(slide):
    out = set()

    def walk(shapes):
        for sh in shapes:
            out.add(sh.name)
            if sh.shape_type == 6:
                walk(sh.shapes)
    walk(slide.shapes)
    return out


class SlideAnim(Anim):
    """Skips entrance effects on objects that Morph carries over from the previous slide."""

    def _carried(self, shape):
        return shape.name.startswith("!!") and shape.name in PREV["names"]

    def fade(self, shape, delay, dur=0.6):
        if not self._carried(shape):
            super().fade(shape, delay, dur)

    def rise(self, shape, delay, dur=0.8, dy=0.035):
        if not self._carried(shape):
            super().rise(shape, delay, dur, dy)


def done(slide, n, anim):
    finish(slide, n, anim)
    PREV["names"] = names_of(slide)


# ---------------- popups ----------------
def popup(n, bg, client_img, client_h, client_xy, title, sub, b1, b2_lead, b2, tags, bubble, note, note_xy):
    s = new_slide()
    an = SlideAnim(s)
    picture(s, "!!bg", bg, 0, 0, w=SW, h=SH)
    crd = rect(s, "!!card", MSO_SHAPE.ROUNDED_RECTANGLE, 0.8, 0.72, 11.73, 6.08, fill="FFFFFF", adj=0.04, shadow=(0.6, 0.12, 28))
    xb = rect(s, "pop_x", MSO_SHAPE.OVAL, 11.92, 0.95, 0.36, 0.36, fill="EEF1EF")
    shape_text(xb, [("✕", F_REG, 10, GREY)])
    t = text_box(s, "pop_title", 1.35, 1.25, 5.9, 1.35, [[(title, F_MED, 30, INK)]])
    sb = text_box(s, "pop_sub", 1.35, 2.7, 6.0, 0.75, [[(sub, F_MED, 16, INK)]])
    p1 = text_box(s, "pop_b1", 1.35, 3.55, 6.0, 0.7, [[(b1, F_REG, 14, INK)]])
    p2 = text_box(s, "pop_b2", 1.35, 4.35, 6.0, 0.95, [[(b2_lead, F_SEMI, 14, ACCENT), (b2, F_REG, 14, INK)]])
    tg = group(s, "pop_tags")
    px = 1.35
    for i, tag in enumerate(tags):
        px += pill(tg, f"pop_tag{i}", px, 5.55, tag) + 0.12
    cl = picture(s, "pop_client", client_img, client_xy[0], client_xy[1], h=client_h)
    bub = rect(s, "pop_bubble", MSO_SHAPE.ROUNDED_RECTANGULAR_CALLOUT, 7.45, 0.95, 3.25, 0.95, fill=MINT)
    bub.adjustments[0] = 0.12
    bub.adjustments[1] = 0.80
    bub.text_frame.margin_left = bub.text_frame.margin_right = Inches(0.15)
    shape_text(bub, [(bubble, F_MED, 12.5, ACCENT)])
    nt, _, _ = hand(s, "pop_note", note, note_xy[0], note_xy[1], size=26, rot=4)
    an.fade(crd, 0.0, 0.5)
    an.fade(xb, 0.3)
    an.rise(cl, 0.25, dy=0.03)
    an.rise(bub, 0.6)
    an.stagger([t, sb, p1, p2, tg], start=0.35, step=0.17)
    an.fade(nt, 1.4)
    done(s, n, an)
    return s


# ---------------- module map (dividers) ----------------
MODULES = [
    ("01", "Подойдёт ли мне Google Pay?", "три проверки", f"{A}/client.png",
     "Подойдёт ли Google Pay, решают три проверки", "«Мне подойдёт Google Pay?»"),
    ("02", "Помогите добавить карту", "пять шагов в Кошельке", f"{A}/hero.png",
     "Карта добавляется за пять шагов в Кошельке", "«Помогите добавить карту»"),
    ("03", "Оплата не прошла", "молчит или отказал", f"{A}/client3_terminal.png",
     "Оплата не прошла — сначала поймите, что ответил терминал", "«Не прошла оплата телефоном»"),
    ("04", "После подключения", "чек и потерянный телефон", f"{A}/client4_worried.png",
     "Карта в телефоне живёт отдельно от пластика", "«А если потеряю телефон?»"),
]


def divider(n, k):
    s = new_slide()
    an = SlideAnim(s)
    chrome(s, f"{A}/bg_main.jpg")
    lbl = text_box(s, "!!divlbl", 0.6, 1.0, 5, 0.35, [[(f"Ситуация {k + 1} из 4", F_SEMI, 14, ACCENT)]])
    ttl = text_box(s, "!!divttl", 0.6, 1.4, 7.6, 1.3, [[(MODULES[k][4], F_MED, 28, INK)]])
    sub = text_box(s, "!!divsub", 0.6, 2.8, 7.6, 0.35, [[("Курс — четыре ситуации, с которыми клиенты приходят в офис.", F_REG, 13, GREY)]])
    q, _, _ = hand(s, "!!divquote", MODULES[k][5], 12.75, 1.55, size=28, rot=3, anchor="right")
    cw, gap, cy, ch = 2.88, 0.2, 3.45, 3.35
    cards = []
    for i, (num, title, sub_, img, _t, _s) in enumerate(MODULES):
        x = 0.6 + i * (cw + gap)
        act = i == k
        g = group(s, f"mcard{i}")
        card(g, f"m{i}_bg", x, cy, cw, ch, fill="FFFFFF" if act else MUTED, line=ACCENT if act else None,
             shadow=(0.45, 0.06, 16) if act else None)
        text_box(g, f"m{i}_num", x + 0.25, cy + 0.18, 1.2, 0.55, [[(num, F_LIGHT, 28, ACCENT if act else LIGHT)]])
        text_box(g, f"m{i}_ttl", x + 0.25, cy + 0.78, cw - 0.5, 0.62, [[(title, F_SEMI, 14, INK if act else GREY)]])
        text_box(g, f"m{i}_sub", x + 0.25, cy + 1.42, cw - 0.5, 0.3, [[(sub_, F_REG, 11, ACCENT if act else LIGHT)]])
        ih = 1.45
        iw = ih * Image.open(img).width / Image.open(img).height
        p = picture(g, f"m{i}_img", img, x + cw - iw - 0.2, cy + ch - ih - 0.12, h=ih)
        if not act:
            pic_alpha(p, 40)
        cards.append(g)
    an.fade(lbl, 0.1)
    an.rise(ttl, 0.2)
    an.fade(sub, 0.45)
    an.stagger(cards, start=0.55, step=0.15)
    an.fade(q, 1.3)
    an.pulse(cards[k], 1.6, repeat=1, scale=104)
    done(s, n, an)


# ---------------- walkthrough step ----------------
def step_frame(s, an, idx, num, ttl, txt, txt_w=4.6):
    chrome(s, f"{A}/bg_main.jpg")
    t = text_box(s, "!!title", 0.6, 1.1, 6.6, 1.5, [[("Добавить карту —", F_MED, 38, INK), "BR", ("пять шагов в Кошельке", F_MED, 38, ACCENT)]])
    dots = []
    for d_i in range(5):
        state = "done" if (d_i < idx or idx == 5) else ("active" if d_i == idx else "todo")
        fill = {"done": LIME, "active": ACCENT, "todo": "E3E8E4"}[state]
        tcol = {"done": ACCENT, "active": "FFFFFF", "todo": GREY}[state]
        dot = rect(s, f"!!dot{d_i}", MSO_SHAPE.OVAL, 0.62 + d_i * 0.46, 2.78, 0.34, 0.34, fill=fill)
        shape_text(dot, [(str(d_i + 1), F_SEMI, 10, tcol)])
        dots.append(dot)
    a = text_box(s, "!!stepnum", 0.6, 3.3, 1.5, 1.0, [[(num, F_LIGHT, 54, ACCENT)]])
    b = text_box(s, "!!stepttl", 2.15, 3.38, txt_w + 0.3, 0.95, [[(ttl, F_MED, 22, INK)]])
    c = text_box(s, "!!steptxt", 2.15, 4.4, txt_w, 1.7, [[(txt, F_REG, 14.5, INK)]])
    an.rise(t, 0.1)
    an.stagger(dots, start=0.3, step=0.07, how="fade")
    an.stagger([a, b, c], start=0.55, step=0.15)
    if idx < 5:
        an.pulse(dots[idx], 1.0, repeat=1, scale=125)


def phone_step(n, idx, scr, num, ttl, txt, taps, note=None):
    s = new_slide()
    an = SlideAnim(s)
    step_frame(s, an, idx, num, ttl, txt)
    pt = phone(s, f"{SCR}/{scr}.png", 9.4, 0.72)
    for sh in pt.shapes:
        an.rise(sh, 0.3, dy=0.03)
    for t_i, (rx, ry) in enumerate(taps):
        cx, cy = pt(rx, ry)
        m = tap_marker(s, "!!tap" if t_i == 0 else f"tap{t_i}", cx, cy)
        an.fade(m, 0.9 + t_i * 0.6, 0.4)
        an.pulse(m, 1.2 + t_i * 0.6)
    if note:
        h_, _, _ = hand(s, "hand", note[0], note[1], note[2], size=26, rot=4)
        an.fade(h_, 1.6)
    done(s, n, an)


# =============== 1: cover ===============
s = new_slide()
an = SlideAnim(s)
chrome(s, f"{A}/bg_cover.jpg")
k_ = text_box(s, "!!kicker", 0.62, 1.2, 6, 0.35, [[("Курс для сотрудников Розничного блока", F_SEMI, 14, ACCENT)]])
t_ = text_box(s, "!!title", 0.6, 1.65, 7.6, 2.2, [[("Google Pay", F_MED, 52, INK), "BR", ("за три проверки", F_MED, 52, ACCENT)]])
n_, _, _ = hand(s, "!!note", "— как Apple Pay,\nно на Android", 5.0, 1.55, size=28, rot=6)
s_ = text_box(s, "!!sub", 0.62, 4.05, 6.3, 1.9, [
    [("Клиенты Ипак Йули теперь платят телефоном на Android через Google Pay. Устроен он как Apple Pay, а сбои у него другие.", F_REG, 15, INK), {"after": 8}],
    [("Три проверки — карта, телефон, настройки — помогут клиенту прямо в офисе.", F_SEMI, 15, INK)]])
h_ = picture(s, "!!hero", f"{A}/hero.png", 9.05, 0.5, h=6.95)
an.fade(h_, 0.2, 0.8)
an.stagger([k_, t_, s_], start=0.35, step=0.2)
an.fade(n_, 1.2)
done(s, 1, an)

# =============== 2: same / new ===============
s = new_slide()
an = SlideAnim(s)
chrome(s, f"{A}/bg_main.jpg")
t_ = title2(s, "Многое — как в Apple Pay,", "новое — в самом Android", size=36)
gl = group(s, "colL")
card(gl, "c_left", 0.6, 3.0, 5.95, 3.6)
text_box(gl, "c_left_h", 0.95, 3.28, 5.3, 0.45, [[("Так же, как в Apple Pay", F_SEMI, 17, INK)]])
L = [bullet_item(s, "l1", 0.95, 3.95, 5.35, "В телефоне — виртуальный номер карты, а не номер пластика"),
     bullet_item(s, "l2", 0.95, 4.8, 5.35, "При добавлении банк проверяет карту"),
     bullet_item(s, "l3", 0.95, 5.45, 5.35, "Удалить карту из телефона ≠ заблокировать её")]
gr = group(s, "colR")
card(gr, "c_right", 6.78, 3.0, 5.95, 3.6)
text_box(gr, "c_right_h", 7.13, 3.28, 5.3, 0.45, [[("Новое — на Android", F_SEMI, 17, ACCENT)]])
R = [bullet_item(s, "r1", 7.13, 3.95, 5.35, "Нужен NFC и сервисы Google — подходит не каждый телефон", mark="!", fill=ACCENT, mcol="FFFFFF"),
     bullet_item(s, "r2", 7.13, 4.8, 5.35, "Кошелёк — приложение для оплаты по умолчанию", mark="!", fill=ACCENT, mcol="FFFFFF"),
     bullet_item(s, "r3", 7.13, 5.45, 5.35, "Humo и Uzcard пока не подключаются", mark="!", fill=ACCENT, mcol="FFFFFF")]
an.rise(t_, 0.1)
an.rise(gl, 0.3)
an.stagger(L, start=0.5, step=0.15)
an.rise(gr, 1.0)
an.stagger(R, start=1.2, step=0.15)
done(s, 2, an)

# =============== 3: map / divider 1 ===============
divider(3, 0)

# =============== 4-6: three checks ===============
ITEMS = [
    ("01", "Карта", "проверка 1 из 3", "Visa или Mastercard Ипак Йули",
     "Humo и Uzcard Google Pay пока не принимает — их обещают подключить позже.", ["#тип карты"]),
    ("02", "Телефон", "проверка 2 из 3", "Android с NFC и сервисами Google",
     "Нет сервисов Google — как на многих новых Huawei — Кошелёк не установится.", ["#NFC", "#Google Play"]),
    ("03", "Настройки", "проверка 3 из 3", "NFC, блокировка экрана, Кошелёк по умолчанию",
     "Без блокировки экрана бесконтактная оплата не включится.", ["#по умолчанию"]),
]
LX, LW = 6.95, 5.8
for k in range(3):
    s = new_slide()
    an = SlideAnim(s)
    chrome(s, f"{A}/bg_main.jpg")
    t_ = text_box(s, "!!title", 0.6, 1.2, 5.9, 3.0, [[("Подойдёт ли", F_MED, 38, INK), "BR", ("Google Pay —", F_MED, 38, INK), "BR",
                                                      ("решают", F_MED, 38, ACCENT), "BR", ("три проверки", F_MED, 38, ACCENT)]])
    n_, _, _ = hand(s, "!!note", "до подключения!", 3.2, 4.3, size=26, rot=5)
    m_ = text_box(s, "!!sum", 0.62, 5.75, 5.6, 0.55, [[("Все три — до того, как клиент начнёт добавлять карту.", F_REG, 14, INK)]])
    an.rise(t_, 0.1)
    y = 1.35
    for i, (num, ttl, lbl, head, txt, tags) in enumerate(ITEMS):
        active = i == k
        h = 2.45 if active else 0.78
        row = [rect(s, f"!!it{i}_line", MSO_SHAPE.RECTANGLE, LX, y, LW, 0.022 if active else 0.012, fill=INK if active else LINE)]
        col = INK if active else LIGHT
        row.append(text_box(s, f"!!it{i}_num", LX, y + 0.22, 0.55, 0.36, [[(num, F_REG, 14, col)]]))
        row.append(text_box(s, f"!!it{i}_ttl", LX + 0.6, y + 0.18, 3.0, 0.45, [[(ttl, F_MED, 19 if active else 16, col)]]))
        row.append(text_box(s, f"!!it{i}_lbl", LX + LW - 2.0, y + 0.24, 2.0, 0.3, [[{"align": PP_ALIGN.RIGHT}, (lbl, F_REG, 10.5, GREY if active else LIGHT)]]))
        for sh in row:
            an.rise(sh, 0.3 + i * 0.18)
        if active:
            det = [text_box(s, f"!!it{i}_head", LX + 0.6, y + 0.8, 5.15, 0.4, [[(head, F_SEMI, 14.5, INK)]]),
                   text_box(s, f"!!it{i}_txt", LX + 0.6, y + 1.22, 5.1, 0.62, [[(txt, F_REG, 13, INK)]])]
            tg = group(s, f"!!it{i}_tags")
            px = LX + 0.6
            for t_i, t in enumerate(tags):
                px += pill(tg, f"it{i}_tag{t_i}", px, y + 1.95, t) + 0.12
            det.append(tg)
            an.stagger(det, start=0.9, step=0.15)
        y += h
    le = rect(s, "!!list_end", MSO_SHAPE.RECTANGLE, LX, y, LW, 0.012, fill=LINE)
    an.fade(le, 0.9)
    an.fade(m_, 1.2)
    an.fade(n_, 1.5)
    done(s, 4 + k, an)

# =============== 7-8: situations ===============
popup(7, _popup_bg("bg_popup.jpg"), f"{A}/client.png", 4.95, (8.85, 1.82), "Humo пока не добавить",
      "Google Pay сейчас принимает только Visa и Mastercard.",
      "Humo и Uzcard обещают подключить позже — даты пока нет.",
      "Что делать: ", "спросите, есть ли у клиента Visa или Mastercard Ипак Йули, — её и добавляем.",
      ["#проверка 1", "#карта"], "«Почему моя Humo не добавляется?»", "пока — нет!", (4.4, 5.35))
popup(8, _popup_bg("bg_popup.jpg"), f"{A}/client2_huawei.png", 4.95, (8.95, 1.82), "Кошелёк не скачался — нет сервисов Google",
      "Так бывает на многих новых Huawei.",
      "Без сервисов Google Кошелёк не установить — и Google Pay не подключить.",
      "Что делать: ", "проверьте, есть ли на телефоне Google Play. Нет — скажите клиенту, что здесь Google Pay не заработает.",
      ["#проверка 2", "#телефон"], "«Кошелёк не скачивается — что не так?»", "нет Google Play —\nнет Google Pay", (4.35, 5.25))

# =============== 9: divider 2 ===============
divider(9, 1)

# =============== 10-15: walkthrough ===============
phone_step(10, 0, "scr_home", "01", "Нажмите «+»", "Откройте Кошелёк — кнопка «+» внизу экрана.", [(0.604, 0.944)])
phone_step(11, 1, "scr_addlist", "02", "Выберите «Платежная карта»", "Первая строка в списке «Добавить в Кошелек».", [(0.16, 0.268)])
phone_step(12, 2, "scr_payopts", "03", "Проще — из Ipak Yuli Mobile",
           "Кошелёк откроет приложение банка. Нет приложения — «Новая кредитная или дебетовая карта»: данные карты клиент вводит сам.",
           [(0.135, 0.419), (0.115, 0.858)], note=("через приложение банка", 3.3, 6.15))

s = new_slide()
an = SlideAnim(s)
step_frame(s, an, 3, "04", "Подтвердите и примите оферту",
           "Нажмите «Добавить в Кошелек». Кошелёк проверит карту и покажет публичную оферту банка — клиент читает её и принимает.",
           txt_w=4.1)
pa = phone(s, f"{SCR}/scr_confirm.png", 6.95, 0.98, sw=2.45)
cx, cy = pa(0.82, 0.855)
m = tap_marker(s, "!!tap", cx, cy, d=0.52)
ar = text_box(s, "arrow", 9.47, 3.45, 0.5, 0.6, [[{"align": PP_ALIGN.CENTER}, ("→", F_MED, 26, ACCENT)]])
pb = phone(s, f"{SCR}/scr_offer.png", 10.15, 0.98, sw=2.45, suffix="B")
an.pulse(m, 0.6)
an.fade(ar, 1.1)
for sh in pb.shapes:
    an.rise(sh, 1.3, dy=0.03)
done(s, 13, an)

phone_step(14, 4, "scr_default", "05", "Нажмите «Сделать основной»",
           "Это третья проверка — настройки: Кошелёк станет приложением для оплаты по умолчанию.", [(0.82, 0.855)])
phone_step(15, 5, "scr_done", "✓", "Готово", "Бесконтактная оплата настроена. В магазине клиент подносит телефон к терминалу.", [],
           note=("можно платить!", 4.4, 5.9))

# =============== 16: rules (draft) ===============
s = new_slide()
an = SlideAnim(s)
chrome(s, f"{A}/bg_main.jpg")
t_ = title2(s, "Помогаете — но данные карты", "вводит только клиент", size=36)
RULES = ["Номер карты и CVV клиент вводит сам", "Код из SMS клиент никому не называет — даже вам", "Карту клиента — только на телефон клиента"]
G = []
for i, rtxt in enumerate(RULES):
    x = 0.6 + i * 4.19
    g = group(s, f"rule{i}")
    card(g, f"rule{i}_bg", x, 3.0, 3.95, 2.95)
    text_box(g, f"rule{i}_n", x + 0.35, 3.2, 1.0, 0.8, [[(str(i + 1), F_LIGHT, 40, ACCENT)]])
    text_box(g, f"rule{i}_t", x + 0.35, 4.15, 3.3, 1.5, [[(rtxt, F_MED, 17, INK)]])
    G.append(g)
draft = rect(s, "draft", MSO_SHAPE.ROUNDED_RECTANGLE, 9.45, 6.25, 3.25, 0.36, fill="FFFFFF", line="B3261E", line_w=1, adj=0.5)
shape_text(draft, [("Черновик: согласовать с ИБ", F_REG, 10.5, "B3261E")])
an.rise(t_, 0.1)
an.stagger(G, start=0.35, step=0.2)
an.fade(draft, 1.2)
done(s, 16, an)

# =============== 17: divider 3 ===============
divider(17, 2)

# =============== 18: silent vs declined ===============
s = new_slide()
an = SlideAnim(s)
chrome(s, f"{A}/bg_main.jpg")
t_ = title2(s, "Терминал молчит — дело в телефоне,", "отказал — дело в карте", size=34)
gl = group(s, "colL")
card(gl, "col_l", 0.6, 2.95, 5.95, 3.35)
text_box(gl, "col_l_h", 0.95, 3.2, 5.3, 0.45, [[("Терминал молчит", F_SEMI, 18, INK), ("  → телефон", F_MED, 15, ACCENT)]])
L = [bullet_item(s, "li1", 0.95, 3.9, 5.35, "Телефон разблокирован"),
     bullet_item(s, "li2", 0.95, 4.55, 5.35, "Поднесли задней стороной на пару секунд"),
     bullet_item(s, "li3", 0.95, 5.2, 5.35, "NFC включён, Кошелёк — по умолчанию")]
gr = group(s, "colR")
card(gr, "col_r", 6.78, 2.95, 5.95, 3.35)
text_box(gr, "col_r_h", 7.13, 3.2, 5.3, 0.45, [[("Терминал отказал", F_SEMI, 18, INK), ("  → карта", F_MED, 15, ACCENT)]])
R = [bullet_item(s, "ri1", 7.13, 3.9, 5.35, "Проверьте карту, как при отказе по пластику"),
     bullet_item(s, "ri2", 7.13, 4.7, 5.35, "Баланс, лимиты и статус карты — по обычной процедуре банка")]
bt = text_box(s, "bottom", 0.62, 6.45, 9.5, 0.35, [[("Терминал не принимает бесконтактную оплату? Поможет другой терминал.", F_REG, 12.5, GREY)]])
an.rise(t_, 0.1)
an.rise(gl, 0.3)
an.stagger(L, start=0.5, step=0.15)
an.rise(gr, 1.0)
an.stagger(R, start=1.2, step=0.15)
an.fade(bt, 1.6)
done(s, 18, an)

# =============== 19: situation terminal ===============
popup(19, _popup_bg("bg_popup_s18.jpg"), f"{A}/client3_terminal.png", 4.85, (8.4, 1.88), "Терминал молчит — начните с телефона",
      "Разблокирован ли телефон? Включён ли NFC? Кошелёк — по умолчанию?",
      "Откройте настройки вместе с клиенткой: NFC включён, Кошелёк выбран для оплаты по умолчанию.",
      "Что сказать: ", "«Перед оплатой разблокируйте телефон и поднесите его задней стороной к терминалу».",
      ["#оплата", "#телефон"], "«Подношу телефон — ничего не происходит»", "сначала телефон!", (4.4, 5.4))

# =============== 20: divider 4 ===============
divider(20, 3)

# =============== 21: virtual number ===============
s = new_slide()
an = SlideAnim(s)
chrome(s, f"{A}/bg_main.jpg")
t_ = title2(s, "В чеке — виртуальный номер карты,", "поэтому цифры другие", size=34)


def bank_card(c, name, x, y, fill, digits, label, sub):
    g = group(c, name)
    text_box(g, f"{name}_lbl", x, y - 0.5, 4.2, 0.38, [[(label, F_SEMI, 15, INK)]])
    rect(g, f"{name}_c", MSO_SHAPE.ROUNDED_RECTANGLE, x, y, 3.9, 2.4, fill=fill, adj=0.08, shadow=(0.4, 0.08, 20))
    picture(g, f"{name}_logo", f"{A}/logo_white.png", x + 0.3, y + 0.28, h=0.42)
    text_box(g, f"{name}_d", x + 0.3, y + 1.75, 3.2, 0.42, [[(digits, F_MED, 18, "FFFFFF")]])
    text_box(g, f"{name}_s", x, y + 2.52, 4.4, 0.3, [[(sub, F_REG, 11.5, GREY)]])
    return g


gp = bank_card(s, "plastic", 1.6, 3.3, ACCENT, "•• 4417", "Пластиковая карта", "пример цифр")
nq = text_box(s, "neq", 6.0, 3.75, 1.2, 1.3, [[{"align": PP_ALIGN.CENTER}, ("≠", F_LIGHT, 60, ACCENT)]])
gt = bank_card(s, "token", 7.65, 3.3, "8CC63F", "•• 8253", "Карта в телефоне", "виртуальный номер — свой у каждого телефона")
bt = text_box(s, "bottom", 0.62, 6.4, 11.6, 0.4, [[("Последние цифры в чеке — от виртуального номера, а не от пластика. Это нормально.", F_REG, 13.5, INK)]])
an.rise(t_, 0.1)
an.rise(gp, 0.35)
an.fade(nq, 0.8)
an.pulse(nq, 1.1, repeat=1, scale=120)
an.rise(gt, 0.95)
an.fade(bt, 1.5)
done(s, 21, an)

# =============== 22: lost phone ===============
s = new_slide()
an = SlideAnim(s)
chrome(s, f"{A}/bg_main.jpg")
t_ = title2(s, "Потерян телефон — блокируем", "через «Найти устройство»", size=34)
STEPS3 = [("Откройте «Найти устройство» с другого телефона или компьютера", "google.com/android/find"),
          ("Заблокируйте телефон или сотрите данные — карты удалятся вместе с ними", ""),
          ("Пластиковая карта продолжает работать", "")]
G = []
for i, (t1, t2) in enumerate(STEPS3):
    x = 0.6 + i * 4.19
    g = group(s, f"lp{i}")
    card(g, f"lp{i}_bg", x, 2.95, 3.95, 3.1)
    text_box(g, f"lp{i}_n", x + 0.35, 3.12, 1.0, 0.8, [[(str(i + 1), F_LIGHT, 40, ACCENT)]])
    text_box(g, f"lp{i}_t", x + 0.35, 4.05, 3.3, 1.3, [[(t1, F_MED, 16, INK)]])
    if t2:
        text_box(g, f"lp{i}_u", x + 0.35, 5.45, 3.3, 0.3, [[(t2, F_REG, 12, ACCENT)]])
    G.append(g)
an.rise(t_, 0.1)
an.stagger(G, start=0.35, step=0.22)
done(s, 22, an)

# =============== 23: situation deleted card ===============
popup(23, _popup_bg("bg_popup_s22.jpg"), f"{A}/client4_worried.png", 4.95, (9.05, 1.82), "Удалили из Кошелька — пластик работает",
      "Удаление карты из телефона не блокирует карту.",
      "Пластиковой картой можно пользоваться как раньше.",
      "Что сказать: ", "«Захотите снова платить телефоном — просто добавьте карту заново».",
      ["#после подключения"], "«Я удалила карту из Кошелька — она заблокирована?»", "удалить ≠ заблокировать", (4.4, 5.4))

# =============== 24: cheat sheet ===============
s = new_slide()
an = SlideAnim(s)
chrome(s, f"{A}/bg_main.jpg")
t_ = title2(s, "Сначала три проверки,", "потом пять шагов", size=38)
an.rise(t_, 0.1)
x = 0.6
for i, txt in enumerate(["Карта", "Телефон", "Настройки", "5 шагов в Кошельке"]):
    w = text_w(txt, 14, "Manrope-600.ttf") + 0.55
    g = group(s, f"chip{i}")
    c = rect(g, f"chip{i}_bg", MSO_SHAPE.ROUNDED_RECTANGLE, x, 3.0, w, 0.6, fill=ACCENT if i == 3 else "FFFFFF",
             line=None if i == 3 else ACCENT, line_w=1.25, adj=0.5)
    shape_text(c, [(txt, F_SEMI, 14, "FFFFFF" if i == 3 else ACCENT)])
    if i < 3:
        text_box(g, f"chip{i}_ar", x + w + 0.13, 3.03, 0.4, 0.5, [[("→", F_MED, 18, GREY)]])
    an.rise(g, 0.35 + i * 0.18)
    x += w + 0.62
for i, txt in enumerate(["Терминал молчит — дело в телефоне", "Терминал отказал — дело в карте", "Телефон потерян — «Найти устройство»"]):
    g = bullet_item(s, f"fl{i}", 0.6, 4.1 + i * 0.66, 8.0, txt, mark=str(i + 1), fill=MINT, size=16, h=0.5)
    an.rise(g, 1.15 + i * 0.15)
h_, _, _ = hand(s, "hand", "сфотографируйте этот экран!", 7.9, 5.9, size=26, rot=4)
an.fade(h_, 1.8)
done(s, 24, an)

# =============== 25: test intro ===============
s = new_slide()
an = SlideAnim(s)
chrome(s, f"{A}/bg_cover.jpg")
t_ = text_box(s, "!!title", 0.6, 1.6, 8.0, 2.8, [[("Проверьте себя:", F_MED, 48, INK), "BR", ("шесть ситуаций", F_MED, 48, ACCENT), "BR", ("из офиса", F_MED, 48, ACCENT)]])
s_ = text_box(s, "!!sub", 0.62, 4.65, 6.0, 0.4, [[("Выберите, что вы сделаете в каждой ситуации.", F_REG, 15, INK)]])
b = rect(s, "btn", MSO_SHAPE.ROUNDED_RECTANGLE, 0.62, 5.35, 2.4, 0.58, fill=ACCENT, adj=0.5)
shape_text(b, [("Начать тест", F_SEMI, 14, "FFFFFF")])
h_ = picture(s, "!!hero", f"{A}/hero.png", 9.05, 0.5, h=6.95)
an.fade(h_, 0.2, 0.8)
an.rise(t_, 0.3)
an.rise(s_, 0.6)
an.rise(b, 0.8)
an.pulse(b, 1.4, repeat=2, scale=106)
done(s, 25, an)

# =============== 26: end ===============
s = new_slide()
an = SlideAnim(s)
chrome(s, f"{A}/bg_cover.jpg")
t_ = text_box(s, "!!title", 0.6, 1.7, 8.0, 1.0, [[("Курс завершён", F_MED, 52, INK)]])
s_ = text_box(s, "!!sub", 0.62, 3.0, 6.0, 0.95, [[("На следующем приёме начните с трёх проверок: ", F_REG, 17, INK), ("карта, телефон, настройки.", F_SEMI, 17, ACCENT)]])
b = rect(s, "btn", MSO_SHAPE.ROUNDED_RECTANGLE, 0.62, 4.25, 2.2, 0.58, fill=ACCENT, adj=0.5)
shape_text(b, [("Завершить", F_SEMI, 14, "FFFFFF")])
h_ = picture(s, "!!hero", f"{A}/hero.png", 9.05, 0.5, h=6.95)
an.rise(t_, 0.2)
an.rise(s_, 0.45)
an.rise(b, 0.7)
an.fade(h_, 0.2, 0.8)
done(s, 26, an)

prs.save(OUT)
print("saved", OUT, "slides:", len(prs.slides))
