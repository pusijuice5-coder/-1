"""Google Pay course v2 (RU): four-step client journey, Morph navigation, Magnific visuals and videos.

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
    5: "Факт: Visa и Mastercard Ipak Yuli Bank — пресс-релиз ЦБ от 27.10.2026 и п. 1.3 публичной оферты банка. [Сверить: все ли карточные продукты подключаются.]",
    6: "[Сверить: что предлагать клиенту без Visa/Mastercard — по процедуре банка.]",
    7: "Huawei, выпущенные после 2019 года, в большинстве продаются без сервисов Google.",
    11: "[Сверить: путь внутри Ipak Yuli Mobile. Приложение банка запрещает запись экрана — нужны макеты от команды приложения или фото экрана вторым телефоном.]",
    12: "[Сверить: название кнопки принятия оферты — в записи экрана её не видно.]",
    15: "ДОПУЩЕНИЕ: правила — черновик. Согласовать с информационной безопасностью и после этого убрать плашку «Черновик».",
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


# ======================= v2 =======================
from pptx.media import Video
from pptx.parts.media import MediaPart
from pptx.opc.constants import RELATIONSHIP_TYPE as RT

V2 = os.path.join(A, "v2")
BUILD = os.path.join(HERE, "build_hand")
TILE = "0A5524"          # deep emerald for tiles
WHITE_T = "E9F5EC"       # soft white text on dark
STAGES = [
    ("Проверить", "Подойдёт ли клиенту Google Pay?", "Карта · телефон · настройки",
     "Подойдёт ли Google Pay, решают три проверки: карта, телефон, настройки", "icon_check.png", "scene_1"),
    ("Подключить", "Как добавить карту в Кошелёк?", "5 шагов, проще — из Ipak Yuli Mobile",
     "Карта добавляется за пять шагов — проще всего из Ipak Yuli Mobile", "icon_add.png", "scene_2"),
    ("Оплатить", "Почему не прошла оплата?", "Молчит — телефон, отказал — карта",
     "Оплата не прошла — сначала поймите, что ответил терминал", "icon_pay.png", "scene_3"),
    ("Защитить", "Чек, потеря телефона, удаление карты", "Потерян — «Найти устройство», пластик работает",
     "Карта в телефоне живёт отдельно от пластика", "icon_shield.png", "scene_4"),
]
_scene_bg = Image.open(os.path.join(V2, "scene_1.jpg")).convert("RGB").getpixel((60, 540))
SCENE_BG = "%02X%02X%02X" % _scene_bg


class AnimV2(SlideAnim):
    def __init__(self, slide):
        super().__init__(slide)
        self.media = []

    def play(self, shape, delay, dur_ms):
        sp = shape.shape_id
        self.fx.append(
            f'<p:par><p:cTn id="0" presetID="1" presetClass="mediacall" presetSubtype="0" fill="hold" nodeType="withEffect">'
            f'<p:stCondLst><p:cond delay="{int(delay * 1000)}"/></p:stCondLst><p:childTnLst><p:cmd type="call" cmd="playFrom(0.0)">'
            f'<p:cBhvr><p:cTn id="0" dur="{dur_ms}" fill="hold"/><p:tgtEl><p:spTgt spid="{sp}"/></p:tgtEl></p:cBhvr></p:cmd>'
            f'</p:childTnLst></p:cTn></p:par>')
        self.media.append(sp)

    def xml(self):
        el = super().xml()
        if el is None or not self.media:
            return el
        P = "{http://schemas.openxmlformats.org/presentationml/2006/main}"
        root_children = el.find(P + "tnLst").find(P + "par").find(P + "cTn").find(P + "childTnLst")
        for sp in self.media:
            node = etree.fromstring(
                f'<p:video xmlns:p="{P_NS}"><p:cMediaNode vol="80000"><p:cTn id="0" fill="hold">'
                f'<p:stCondLst><p:cond delay="indefinite"/></p:stCondLst></p:cTn>'
                f'<p:tgtEl><p:spTgt spid="{sp}"/></p:tgtEl></p:cMediaNode></p:video>')
            root_children.append(node)
        for k, ctn in enumerate(el.iter(qn("p:cTn")), start=1):
            ctn.set("id", str(k))
        return el


def add_video(s, mp4, poster, x, y, w, h, name):
    """Embedded mp4 with a poster frame; falls back to the poster picture when the mp4 is missing."""
    if not os.path.exists(mp4):
        return picture(s, name, poster, x, y, w=w, h=h), None
    video = Video.from_path_or_file_like(mp4, "video/mp4")
    media_part = MediaPart.new(s.part.package, video)
    r_media = s.part.relate_to(media_part, RT.MEDIA)
    r_video = s.part.relate_to(media_part, RT.VIDEO)
    _, r_img = s.part.get_or_add_image_part(poster)
    spid = max(int(e.get("id")) for e in s.shapes._spTree.iter(qn("p:cNvPr"))) + 1
    E = lambda v: int(Inches(v))
    xml = (f'<p:pic xmlns:p="{P_NS}" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
           f'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
           f'<p:nvPicPr><p:cNvPr id="{spid}" name="{name}"><a:hlinkClick r:id="" action="ppaction://media"/></p:cNvPr>'
           f'<p:cNvPicPr><a:picLocks noChangeAspect="1"/></p:cNvPicPr>'
           f'<p:nvPr><a:videoFile r:link="{r_video}"/><p:extLst><p:ext uri="{{DAA4B4D4-6D71-4841-9C94-3DE7FCFB9230}}">'
           f'<p14:media xmlns:p14="http://schemas.microsoft.com/office/powerpoint/2010/main" r:embed="{r_media}"/></p:ext></p:extLst></p:nvPr></p:nvPicPr>'
           f'<p:blipFill><a:blip r:embed="{r_img}"/><a:stretch><a:fillRect/></a:stretch></p:blipFill>'
           f'<p:spPr><a:xfrm><a:off x="{E(x)}" y="{E(y)}"/><a:ext cx="{E(w)}" cy="{E(h)}"/></a:xfrm>'
           f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr></p:pic>')
    s.shapes._spTree.append(etree.fromstring(xml))
    return s.shapes[-1], 5000


def scrim(s, w=7.8, color=None, a0=88, a1=62):
    """Left-to-right dark gradient that keeps white text readable over the video."""
    color = color or SCENE_BG
    sh = rect(s, "scrim", MSO_SHAPE.RECTANGLE, 0, 0, w, SH)
    spPr = sh._element.spPr
    nf = spPr.find(qn("a:noFill"))
    grad = etree.fromstring(
        '<a:gradFill xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" rotWithShape="1"><a:gsLst>'
        f'<a:gs pos="0"><a:srgbClr val="{color}"><a:alpha val="{a0 * 1000}"/></a:srgbClr></a:gs>'
        f'<a:gs pos="55000"><a:srgbClr val="{color}"><a:alpha val="{a1 * 1000}"/></a:srgbClr></a:gs>'
        f'<a:gs pos="100000"><a:srgbClr val="{color}"><a:alpha val="0"/></a:srgbClr></a:gs>'
        '</a:gsLst><a:lin ang="0" scaled="1"/></a:gradFill>')
    if nf is not None:
        nf.addprevious(grad)
        spPr.remove(nf)
    return sh


def chrome_v2(s, dark=False):
    if dark:
        picture(s, "!!logo_d", f"{A}/logo_white.png", 0.55, 0.36, h=0.42)
    else:
        picture(s, "!!bg", f"{A}/bg_main.jpg", 0, 0, w=SW, h=SH)
        picture(s, "!!logo", f"{A}/logo.png", 0.55, 0.36, h=0.42)


def journey_bar(s, cur, dark=False, skip_current=False, y=0.36, x_left=None):
    labels = []
    for i, st in enumerate(STAGES):
        done_ = cur is not None and i < cur
        labels.append(("✓ " if done_ else f"{i + 1} ") + st[0])
    ws = [text_w(t, 11.5, "Manrope-600.ttf") + 0.46 for t in labels]
    gap = 0.12
    x = x_left if x_left is not None else 12.78 - (sum(ws) + gap * 3)
    out = []
    for i, (t, w) in enumerate(zip(labels, ws)):
        state = "cur" if i == cur else ("done" if (cur is not None and i < cur) else "next")
        if skip_current and state == "cur":
            x += w + gap
            continue
        if dark:
            fill, alpha, line, col = {"cur": (LIME, None, None, ACCENT), "done": ("FFFFFF", 22, None, "FFFFFF"),
                                      "next": ("FFFFFF", 8, "A8C9B0", "D5E8DA")}[state]
        else:
            fill, alpha, line, col = {"cur": (ACCENT, None, None, "FFFFFF"), "done": (MINT, None, None, ACCENT),
                                      "next": ("FFFFFF", None, LINE, GREY)}[state]
        chip = rect(s, f"!!jb{i}", MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, 0.42, fill=fill, alpha=alpha, line=line, line_w=1, adj=0.5)
        shape_text(chip, [(t, F_SEMI, 11.5, col)])
        out.append(chip)
        x += w + gap
    return out


def tiles(s, an, recap=False):
    for i, (verb, q, rule, _thought, icon, _scene) in enumerate(STAGES):
        x, y, w, h = 0.6 + i * 3.1, 2.45, 2.9, 4.35
        t = rect(s, f"!!jb{i}", MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h, fill=TILE, adj=0.06, shadow=(0.5, 0.08, 22))
        n_ = text_box(s, f"!!tnum{i}", x + 0.3, y + 0.22, 1.6, 0.7, [[(f"0{i + 1}", F_LIGHT, 34, LIME)]])
        v_ = text_box(s, f"!!tverb{i}", x + 0.3, y + 0.95, w - 0.5, 0.55, [[(verb, F_SEMI, 24, "FFFFFF")]])
        l_ = text_box(s, f"!!tline{i}", x + 0.3, y + 1.6, w - 0.6, 1.0, [[(rule if recap else q, F_REG, 13, WHITE_T)]])
        ih = 1.95
        im = Image.open(os.path.join(V2, icon))
        ic = picture(s, f"!!ticon{i}", os.path.join(V2, icon), x + w - ih * im.width / im.height - 0.12, y + h - ih - 0.12, h=ih)
        for k_, sh in enumerate([t, n_, v_, l_, ic]):
            an.rise(sh, 0.3 + i * 0.16 + (0 if k_ == 0 else 0.1))
        if recap:
            b = rect(s, f"done{i}", MSO_SHAPE.OVAL, x + w - 0.62, y + 0.22, 0.4, 0.4, fill=LIME)
            shape_text(b, [("✓", F_SEMI, 13, ACCENT)])
            an.fade(b, 1.1 + i * 0.12)
            an.pulse(b, 1.4 + i * 0.12, repeat=1, scale=125)


def stage_cover(n, k, first=False):
    verb, q, rule, thought, icon, scene = STAGES[k]
    s = new_slide()
    an = AnimV2(s)
    rect(s, f"!!jb{k}", MSO_SHAPE.ROUNDED_RECTANGLE, 0, 0, SW, SH, fill=SCENE_BG, adj=0.0)
    if first:
        im = Image.open(os.path.join(V2, icon))
        picture(s, f"!!ticon{k}", os.path.join(V2, icon), 7.9, 1.45, h=4.6)
    vid, dur = add_video(s, os.path.join(V2, f"{scene}.mp4"), os.path.join(V2, f"{scene}.jpg"), 0, 0, SW, SH, f"video_stage{k + 1}")
    an.fade(vid, 0.0, 0.7)
    if dur:
        an.play(vid, 0.0, dur)
    scrim(s, w=7.4, a0=70, a1=40)
    chrome_v2(s, dark=True)
    journey_bar(s, k, dark=True, skip_current=True, x_left=2.45)
    n_ = text_box(s, f"!!tnum{k}", 0.55, 0.95, 5.0, 2.5, [[(f"0{k + 1}", F_LIGHT, 130, LIME)]])
    v_ = text_box(s, f"!!tverb{k}", 0.62, 3.45, 6.6, 1.15, [[(verb, F_MED, 58, "FFFFFF")]])
    l_ = text_box(s, f"!!tline{k}", 0.65, 4.65, 5.6, 1.5, [[(thought, F_REG, 19, WHITE_T)]])
    lb = text_box(s, "stage_lbl", 0.66, 6.55, 5, 0.35, [[(f"Шаг {k + 1} из 4", F_SEMI, 13, LIME)]])
    an.rise(n_, 0.25)
    an.rise(v_, 0.4)
    an.rise(l_, 0.55)
    an.fade(lb, 0.9)
    done(s, n, an)


def content(cur, bar=True):
    s = new_slide()
    an = AnimV2(s)
    chrome_v2(s)
    if bar:
        journey_bar(s, cur)
    return s, an


# ---------------- popups (with the journey bar) ----------------
def popup_v2(n, cur, bg, client_img, client_h, client_xy, title, sub, b1, b2_lead, b2, tags, bubble, note, note_xy):
    s = new_slide()
    an = AnimV2(s)
    picture(s, "!!bg", bg, 0, 0, w=SW, h=SH)
    journey_bar(s, cur, dark=True, y=0.18)
    crd = rect(s, "!!card", MSO_SHAPE.ROUNDED_RECTANGLE, 0.8, 0.8, 11.73, 6.1, fill="FFFFFF", adj=0.04, shadow=(0.6, 0.12, 28))
    xb = rect(s, "pop_x", MSO_SHAPE.OVAL, 11.92, 1.03, 0.36, 0.36, fill="EEF1EF")
    shape_text(xb, [("✕", F_REG, 10, GREY)])
    kick = text_box(s, "pop_kick", 1.35, 1.2, 5, 0.3, [[("Ситуация в офисе", F_SEMI, 12, ACCENT)]])
    t = text_box(s, "pop_title", 1.35, 1.55, 5.9, 1.35, [[(title, F_MED, 30, INK)]])
    sb = text_box(s, "pop_sub", 1.35, 2.95, 6.0, 0.75, [[(sub, F_MED, 16, INK)]])
    p1 = text_box(s, "pop_b1", 1.35, 3.75, 6.0, 0.7, [[(b1, F_REG, 14, INK)]])
    p2 = text_box(s, "pop_b2", 1.35, 4.5, 6.0, 0.95, [[(b2_lead, F_SEMI, 14, ACCENT), (b2, F_REG, 14, INK)]])
    tg = group(s, "pop_tags")
    px = 1.35
    for i, tag in enumerate(tags):
        px += pill(tg, f"pop_tag{i}", px, 5.7, tag) + 0.12
    cl = picture(s, "pop_client", client_img, client_xy[0], client_xy[1], h=client_h)
    bub = rect(s, "pop_bubble", MSO_SHAPE.ROUNDED_RECTANGULAR_CALLOUT, 7.45, 1.05, 3.25, 0.95, fill=MINT)
    bub.adjustments[0] = 0.12
    bub.adjustments[1] = 0.80
    bub.text_frame.margin_left = bub.text_frame.margin_right = Inches(0.15)
    shape_text(bub, [(bubble, F_MED, 12.5, ACCENT)])
    nt, _, _ = hand(s, "pop_note", note, note_xy[0], note_xy[1], size=26, rot=4)
    an.fade(crd, 0.0, 0.5)
    an.fade(xb, 0.3)
    an.rise(cl, 0.25, dy=0.03)
    an.rise(bub, 0.6)
    an.stagger([kick, t, sb, p1, p2, tg], start=0.3, step=0.15)
    an.fade(nt, 1.4)
    done(s, n, an)


# ---------------- walkthrough with a zoom callout ----------------
_zoom_n = [0]


def zoom_callout(s, an, scr, rx, ry, x, y, w, h, mark=None):
    _zoom_n[0] += 1
    im = Image.open(os.path.join(SCR, f"{scr}.png")).convert("RGB")
    W, H = im.size
    cw = 640
    ch = int(cw * h / w)
    cx, cy = rx * W, ry * H
    left = int(min(max(cx - cw / 2, 0), W - cw))
    top = int(min(max(cy - ch / 2, 0), H - ch))
    path = os.path.join(BUILD, f"zoom_{_zoom_n[0]:02d}.png")
    im.crop((left, top, left + cw, top + ch)).save(path)
    lab = text_box(s, "!!zlabel", x, y - 0.38, 3, 0.3, [[("Крупно:", F_SEMI, 11.5, GREY)]])
    pic = picture(s, "!!zoom", path, x, y, w=w, h=h)
    round_picture(pic, 9000)
    add_shadow(pic, 0.45, 0.06, 20)
    ring = None
    if mark:
        mx = x + (mark[0] * W - left) / cw * w
        my = y + (mark[1] * H - top) / ch * h
        ring = rect(s, "!!zring", MSO_SHAPE.OVAL, mx - 0.36, my - 0.36, 0.72, 0.72, line=LIME, line_w=3.5)
    return lab, pic, ring


def step_v2(n, idx, scr, title, txt, taps, zoom_at, mark=None, two=None):
    s, an = content(1)
    lbl = text_box(s, "!!steplbl", 0.6, 1.1, 4, 0.32, [[(f"Шаг {idx + 1} из 5" if idx < 5 else "Готово", F_SEMI, 13, ACCENT)]])
    tt = text_box(s, "!!stepttl", 0.6, 1.48, 6.5, 1.3, [[(title, F_MED, 28, INK)]])
    tx = text_box(s, "!!steptxt", 0.6, 2.85, 6.2, 1.05, [[(txt, F_REG, 15, INK)]])
    dots = []
    for d_i in range(5):
        state = "done" if (d_i < idx or idx == 5) else ("active" if d_i == idx else "todo")
        fill = {"done": LIME, "active": ACCENT, "todo": "E3E8E4"}[state]
        tcol = {"done": ACCENT, "active": "FFFFFF", "todo": GREY}[state]
        dot = rect(s, f"!!dot{d_i}", MSO_SHAPE.OVAL, 0.62 + d_i * 0.46, 4.05, 0.32, 0.32, fill=fill)
        shape_text(dot, [(str(d_i + 1), F_SEMI, 10, tcol)])
        dots.append(dot)
    if two:
        pa = phone(s, f"{SCR}/{scr}.png", 7.25, 1.1, sw=2.3)
        ar = text_box(s, "arrow", 9.74, 3.45, 0.5, 0.6, [[{"align": PP_ALIGN.CENTER}, ("→", F_MED, 24, ACCENT)]])
        pb = phone(s, f"{SCR}/{two}.png", 10.35, 1.1, sw=2.3, suffix="B")
        pt = pa
        an.fade(ar, 1.2)
        for sh in pb.shapes:
            an.rise(sh, 1.35, dy=0.03)
    else:
        pt = phone(s, f"{SCR}/{scr}.png", 9.75, 1.05, sw=2.45)
    for sh in pt.shapes:
        an.rise(sh, 0.25, dy=0.03)
    for t_i, (rx, ry) in enumerate(taps):
        cx, cy = pt(rx, ry)
        m = tap_marker(s, "!!tap" if t_i == 0 else f"tap{t_i}", cx, cy, d=0.5)
        an.fade(m, 0.8 + t_i * 0.5, 0.4)
        an.pulse(m, 1.1 + t_i * 0.5)
    zl, zp, zr = zoom_callout(s, an, scr, zoom_at[0], zoom_at[1], 0.6, 4.95, 5.6, 1.85, mark=mark)
    an.stagger([lbl, tt, tx], start=0.15, step=0.14)
    an.stagger(dots, start=0.45, step=0.06, how="fade")
    an.fade(zl, 0.9)
    an.rise(zp, 0.95)
    if zr is not None:
        an.fade(zr, 1.35)
        an.pulse(zr, 1.6, repeat=2, scale=112)
    if idx < 5:
        an.pulse(dots[idx], 1.0, repeat=1, scale=125)
    done(s, n, an)


# =============== 1: cover (video) ===============
s = new_slide()
an = AnimV2(s)
rect(s, "cover_bg", MSO_SHAPE.RECTANGLE, 0, 0, SW, SH, fill=SCENE_BG)
vid, dur = add_video(s, os.path.join(V2, "scene_cover.mp4"), os.path.join(V2, "scene_cover.jpg"), 0, 0, SW, SH, "video_cover")
an.fade(vid, 0.0, 0.8)
if dur:
    an.play(vid, 0.0, dur)
scrim(s, w=7.6, a0=86, a1=58)
chrome_v2(s, dark=True)
k_ = text_box(s, "!!kicker", 0.62, 1.2, 6, 0.35, [[("Курс для сотрудников Розничного блока", F_SEMI, 14, LIME)]])
t_ = text_box(s, "!!title", 0.6, 1.62, 4.9, 3.25, [[("Google Pay:", F_MED, 42, "FFFFFF"), "BR", ("помогите", F_MED, 42, "FFFFFF"), "BR", ("клиенту", F_MED, 42, "FFFFFF"), "BR", ("в четыре шага", F_MED, 42, LIME)]])
s_ = text_box(s, "!!sub", 0.64, 5.0, 4.9, 0.8, [[("Проверить · Подключить · Оплатить · Защитить — прямо в офисе.", F_REG, 15, WHITE_T)]])
n_, _, _ = hand(s, "!!note", "как Apple Pay, но на Android", 0.62, 6.05, size=26, rot=3, color=LIME)
an.stagger([k_, t_, s_], start=0.4, step=0.2)
an.fade(n_, 1.3)
done(s, 1, an)

# =============== 2: same / new (no bar) ===============
s, an = content(None, bar=False)
t_ = title2(s, "Многое — как в Apple Pay,", "новое — в самом Android", size=36)
gl = group(s, "colL")
card(gl, "c_left", 0.6, 3.0, 5.95, 3.6)
text_box(gl, "c_left_h", 0.95, 3.28, 5.3, 0.45, [[("Так же, как в Apple Pay", F_SEMI, 17, INK)]])
L = [bullet_item(s, "l1", 0.95, 3.95, 5.35, "В телефоне — виртуальный номер карты, а не номер пластика"),
     bullet_item(s, "l2", 0.95, 4.8, 5.35, "При добавлении банк проверяет карту"),
     bullet_item(s, "l3", 0.95, 5.45, 5.35, "Удалить карту из телефона ≠ заблокировать её")]
gr = group(s, "colR")
card(gr, "c_right", 6.78, 3.0, 5.95, 3.6, fill=TILE)
text_box(gr, "c_right_h", 7.13, 3.28, 5.3, 0.45, [[("Новое — на Android", F_SEMI, 17, LIME)]])
R = []
for i, txt in enumerate(["Нужен NFC и сервисы Google — подходит не каждый телефон",
                         "Кошелёк — приложение для оплаты по умолчанию", "Humo и Uzcard пока не подключаются"]):
    g = group(s, f"r{i}")
    yy = [3.95, 4.8, 5.45][i]
    d_ = rect(g, f"r{i}_dot", MSO_SHAPE.OVAL, 7.13, yy + 0.03, 0.32, 0.32, fill=LIME)
    shape_text(d_, [("!", F_SEMI, 10.5, ACCENT)])
    text_box(g, f"r{i}_t", 7.61, yy, 4.87, 0.7, [[(txt, F_REG, 14.5, "FFFFFF")]])
    R.append(g)
an.rise(t_, 0.1)
an.rise(gl, 0.3)
an.stagger(L, start=0.5, step=0.15)
an.rise(gr, 1.0)
an.stagger(R, start=1.2, step=0.15)
done(s, 2, an)

# =============== 3: journey map ===============
s, an = content(None, bar=False)
t_ = title2(s, "Клиент проходит четыре шага —", "на каждом вы знаете, что делать", size=34, h=1.6)
tiles(s, an)
an.rise(t_, 0.1)
done(s, 3, an)

# =============== STAGE 1: check ===============
stage_cover(4, 0, first=True)

s, an = content(0)
t_ = title2(s, "Подойдёт ли Google Pay —", "решают три проверки", size=34, h=1.6)
cards3 = []
for i, (head, line1, line2) in enumerate([
        ("Карта", "Visa или Mastercard Ипак Йули", "Humo и Uzcard Google Pay пока не принимает"),
        ("Телефон", "Android с NFC и сервисами Google", "Нет Google Play — как на многих новых Huawei — не подойдёт"),
        ("Настройки", "NFC, блокировка экрана, Кошелёк по умолчанию", "Без блокировки экрана оплата не включится")]):
    x = 0.6 + i * 4.19
    g = group(s, f"chk{i}")
    card(g, f"chk{i}_bg", x, 2.85, 3.95, 3.95)
    text_box(g, f"chk{i}_n", x + 0.3, 2.98, 0.8, 0.6, [[(f"{i + 1}", F_LIGHT, 30, ACCENT)]])
    text_box(g, f"chk{i}_h", x + 0.95, 3.06, 2.8, 0.45, [[(head, F_SEMI, 19, INK)]])
    text_box(g, f"chk{i}_l1", x + 0.3, 5.15, 3.4, 0.62, [[(line1, F_SEMI, 13.5, INK)]])
    text_box(g, f"chk{i}_l2", x + 0.3, 5.8, 3.4, 0.85, [[(line2, F_REG, 12.5, GREY)]])
    if i == 0:
        picture(g, "chk0_c2", f"{V2}/card_mc_black.png", x + 1.25, 3.68, w=2.15)
        picture(g, "chk0_c1", f"{V2}/card_visa_lime.png", x + 0.5, 3.95, w=2.15)
    elif i == 1:
        ph = rect(g, "chk1_ph", MSO_SHAPE.ROUNDED_RECTANGLE, x + 1.42, 3.62, 0.72, 1.42, fill="121413", adj=0.12)
        scr_ = picture(g, "chk1_scr", f"{SCR}/scr_home.png", x + 1.45, 3.65, w=0.66, h=1.36)
        round_picture(scr_, 9000)
        nfc = rect(g, "chk1_nfc", MSO_SHAPE.ROUNDED_RECTANGLE, x + 2.3, 4.05, 0.75, 0.34, fill=MINT, adj=0.5)
        shape_text(nfc, [("NFC", F_SEMI, 10, ACCENT)])
    else:
        for j, lab in enumerate(["NFC", "Блокировка", "По умолч."]):
            yy = 3.65 + j * 0.47
            text_box(g, f"chk2_t{j}", x + 0.45, yy + 0.03, 1.6, 0.3, [[(lab, F_REG, 11.5, INK)]])
            tr = rect(g, f"chk2_tr{j}", MSO_SHAPE.ROUNDED_RECTANGLE, x + 2.35, yy, 0.7, 0.36, fill=ACCENT, adj=0.5)
            kn = rect(g, f"chk2_kn{j}", MSO_SHAPE.OVAL, x + 2.73, yy + 0.04, 0.28, 0.28, fill="FFFFFF")
    cards3.append(g)
an.rise(t_, 0.1)
an.stagger(cards3, start=0.35, step=0.22)
done(s, 5, an)

popup_v2(6, 0, _popup_bg("bg_popup_v2a.jpg"), f"{A}/client.png", 4.9, (8.85, 1.95), "Humo пока не добавить",
         "Google Pay сейчас принимает только Visa и Mastercard.",
         "Humo и Uzcard обещают подключить позже — даты пока нет.",
         "Что делать: ", "спросите, есть ли у клиента Visa или Mastercard Ипак Йули, — её и добавляем.",
         ["#проверка 1", "#карта"], "«Почему моя Humo не добавляется?»", "пока — нет!", (4.4, 5.5))
popup_v2(7, 0, _popup_bg("bg_popup_v2a.jpg"), f"{A}/client2_huawei.png", 4.9, (8.95, 1.95), "Кошелёк не скачался — нет сервисов Google",
         "Так бывает на многих новых Huawei.",
         "Без сервисов Google Кошелёк не установить — и Google Pay не подключить.",
         "Что делать: ", "проверьте, есть ли на телефоне Google Play. Нет — скажите клиенту, что здесь Google Pay не заработает.",
         ["#проверка 2", "#телефон"], "«Кошелёк не скачивается — что не так?»", "нет Google Play —\nнет Google Pay", (4.35, 5.4))

# =============== STAGE 2: connect ===============
stage_cover(8, 1)
step_v2(9, 0, "scr_home", "Откройте Кошелёк и нажмите «+»", "Кнопка «+» — внизу экрана, рядом с «Ещё».",
        [(0.604, 0.944)], (0.5, 0.94), mark=(0.604, 0.944))
step_v2(10, 1, "scr_addlist", "Выберите «Платежная карта»", "Первая строка в списке «Добавить в Кошелек».",
        [(0.16, 0.268)], (0.5, 0.268), mark=(0.16, 0.268))
step_v2(11, 2, "scr_payopts", "Проще всего — из Ipak Yuli Mobile",
        "Кошелёк откроет приложение банка. Нет приложения — «Новая кредитная или дебетовая карта»: данные вводит сам клиент.",
        [(0.135, 0.419), (0.115, 0.858)], (0.5, 0.419), mark=(0.135, 0.419))
step_v2(12, 3, "scr_confirm", "Подтвердите и примите оферту",
        "«Добавить в Кошелек» — и Кошелёк покажет публичную оферту банка. Клиент читает её и принимает.",
        [(0.82, 0.855)], (0.5, 0.855), mark=(0.82, 0.855), two="scr_offer")
step_v2(13, 4, "scr_default", "Нажмите «Сделать основной»",
        "Это третья проверка — настройки: Кошелёк станет приложением для оплаты по умолчанию.",
        [(0.82, 0.855)], (0.5, 0.855), mark=(0.82, 0.855))
step_v2(14, 5, "scr_done", "Готово — можно платить",
        "Бесконтактная оплата настроена. В магазине клиент подносит телефон к терминалу.", [], (0.5, 0.205))

s, an = content(1)
t_ = title2(s, "Помогаете — но данные карты", "вводит только клиент", size=34, h=1.6)
G = []
for i, rtxt in enumerate(["Номер карты и CVV клиент вводит сам", "Код из SMS клиент никому не называет — даже вам",
                          "Карту клиента — только на телефон клиента"]):
    x = 0.6 + i * 4.19
    g = group(s, f"rule{i}")
    card(g, f"rule{i}_bg", x, 2.85, 3.95, 3.1)
    text_box(g, f"rule{i}_n", x + 0.35, 3.05, 1.0, 0.8, [[(str(i + 1), F_LIGHT, 40, ACCENT)]])
    text_box(g, f"rule{i}_t", x + 0.35, 4.0, 3.3, 1.5, [[(rtxt, F_MED, 17, INK)]])
    G.append(g)
draft = rect(s, "draft", MSO_SHAPE.ROUNDED_RECTANGLE, 9.45, 6.3, 3.25, 0.36, fill="FFFFFF", line="B3261E", line_w=1, adj=0.5)
shape_text(draft, [("Черновик: согласовать с ИБ", F_REG, 10.5, "B3261E")])
an.rise(t_, 0.1)
an.stagger(G, start=0.35, step=0.2)
an.fade(draft, 1.2)
done(s, 15, an)

# =============== STAGE 3: pay ===============
stage_cover(16, 2)

s, an = content(2)
t_ = title2(s, "Платить просто —", "три движения", size=38, h=1.75)
ic = picture(s, "pay_icon", f"{V2}/icon_pay.png", 8.35, 1.45, h=5.2)
rows = []
for i, txt in enumerate(["Разблокируйте телефон", "Поднесите его задней стороной к терминалу на пару секунд", "Результат оплаты покажет терминал"]):
    y = 3.0 + i * 1.12
    g = group(s, f"pay{i}")
    c = rect(g, f"pay{i}_n", MSO_SHAPE.OVAL, 0.6, y, 0.62, 0.62, fill=ACCENT if i < 2 else LIME)
    shape_text(c, [(str(i + 1), F_SEMI, 16, "FFFFFF" if i < 2 else ACCENT)])
    text_box(g, f"pay{i}_t", 1.45, y + 0.08, 6.4, 0.85, [[(txt, F_MED, 19, INK)]])
    rows.append(g)
an.rise(t_, 0.1)
an.rise(ic, 0.3, dy=0.03)
an.stagger(rows, start=0.5, step=0.22)
done(s, 17, an)

s, an = content(2)
t_ = title2(s, "Терминал молчит — дело в телефоне,", "отказал — дело в карте", size=32, h=1.5)
gl = group(s, "colL")
card(gl, "col_l", 0.6, 2.75, 5.95, 3.55)
text_box(gl, "col_l_h", 0.95, 3.0, 5.3, 0.45, [[("Терминал молчит", F_SEMI, 18, INK), ("  → телефон", F_MED, 15, ACCENT)]])
L = [bullet_item(s, "li1", 0.95, 3.7, 5.35, "Телефон разблокирован"),
     bullet_item(s, "li2", 0.95, 4.35, 5.35, "Поднесли задней стороной на пару секунд"),
     bullet_item(s, "li3", 0.95, 5.0, 5.35, "NFC включён, Кошелёк — по умолчанию")]
gr = group(s, "colR")
card(gr, "col_r", 6.78, 2.75, 5.95, 3.55, fill=TILE)
text_box(gr, "col_r_h", 7.13, 3.0, 5.3, 0.45, [[("Терминал отказал", F_SEMI, 18, "FFFFFF"), ("  → карта", F_MED, 15, LIME)]])
R = []
for i, txt in enumerate(["Проверьте карту, как при отказе по пластику", "Баланс, лимиты и статус карты — по обычной процедуре банка"]):
    g = group(s, f"ri{i}")
    yy = [3.7, 4.5][i]
    d_ = rect(g, f"ri{i}_dot", MSO_SHAPE.OVAL, 7.13, yy + 0.03, 0.32, 0.32, fill=LIME)
    shape_text(d_, [("✓", F_SEMI, 10.5, ACCENT)])
    text_box(g, f"ri{i}_t", 7.61, yy, 4.87, 0.7, [[(txt, F_REG, 14.5, "FFFFFF")]])
    R.append(g)
bt = text_box(s, "bottom", 0.62, 6.5, 9.5, 0.35, [[("Терминал не принимает бесконтактную оплату? Поможет другой терминал.", F_REG, 12.5, GREY)]])
an.rise(t_, 0.1)
an.rise(gl, 0.3)
an.stagger(L, start=0.5, step=0.15)
an.rise(gr, 1.0)
an.stagger(R, start=1.2, step=0.15)
an.fade(bt, 1.6)
done(s, 18, an)

popup_v2(19, 2, _popup_bg("bg_popup_v2b.jpg"), f"{A}/client3_terminal.png", 4.8, (8.4, 2.0), "Терминал молчит — начните с телефона",
         "Разблокирован ли телефон? Включён ли NFC? Кошелёк — по умолчанию?",
         "Откройте настройки вместе с клиенткой: NFC включён, Кошелёк выбран для оплаты по умолчанию.",
         "Что сказать: ", "«Перед оплатой разблокируйте телефон и поднесите его задней стороной к терминалу».",
         ["#оплата", "#телефон"], "«Подношу телефон — ничего не происходит»", "сначала телефон!", (4.4, 5.55))

# =============== STAGE 4: protect ===============
stage_cover(20, 3)

s, an = content(3)
t_ = title2(s, "В чеке — виртуальный номер карты,", "поэтому цифры другие", size=32, h=1.5)
gp = group(s, "plastic")
text_box(gp, "pl_lbl", 1.2, 2.75, 4.2, 0.38, [[("Пластиковая карта", F_SEMI, 15, INK)]])
pc = picture(gp, "pl_card", f"{V2}/card_visa_lime.png", 1.2, 3.25, w=4.0)
add_shadow(pc, 0.4, 0.08, 20)
text_box(gp, "pl_d", 1.5, 4.95, 2.5, 0.4, [[("•• 4417", F_MED, 17, "FFFFFF")]])
text_box(gp, "pl_s", 1.2, 5.75, 4.3, 0.3, [[("пример цифр", F_REG, 11.5, GREY)]])
nq = text_box(s, "neq", 5.75, 3.65, 1.3, 1.3, [[{"align": PP_ALIGN.CENTER}, ("≠", F_LIGHT, 60, ACCENT)]])
gt = group(s, "token")
text_box(gt, "tk_lbl", 7.55, 2.75, 4.6, 0.38, [[("Карта в телефоне", F_SEMI, 15, INK)]])
tc = picture(gt, "tk_card", f"{V2}/card_visa_lime.png", 7.55, 3.25, w=4.0)
add_shadow(tc, 0.4, 0.08, 20)
text_box(gt, "tk_d", 7.85, 4.95, 2.5, 0.4, [[("•• 8253", F_MED, 17, "FFFFFF")]])
text_box(gt, "tk_s", 7.55, 5.75, 4.6, 0.3, [[("виртуальный номер — свой у каждого телефона", F_REG, 11.5, GREY)]])
bt = text_box(s, "bottom", 0.62, 6.4, 11.6, 0.4, [[("Последние цифры в чеке — от виртуального номера, а не от пластика. Это нормально.", F_REG, 13.5, INK)]])
an.rise(t_, 0.1)
an.rise(gp, 0.35)
an.fade(nq, 0.8)
an.pulse(nq, 1.1, repeat=1, scale=120)
an.rise(gt, 0.95)
an.fade(bt, 1.5)
done(s, 21, an)

s, an = content(3)
t_ = title2(s, "Потерян телефон — блокируем", "через «Найти устройство»", size=32, h=1.5)
G = []
for i, (t1, t2) in enumerate([("Откройте «Найти устройство» с другого телефона или компьютера", "google.com/android/find"),
                              ("Заблокируйте телефон или сотрите данные — карты удалятся вместе с ними", ""),
                              ("Пластиковая карта продолжает работать", "")]):
    x = 0.6 + i * 4.19
    g = group(s, f"lp{i}")
    card(g, f"lp{i}_bg", x, 2.75, 3.95, 3.3, fill=TILE if i == 2 else "FFFFFF")
    text_box(g, f"lp{i}_n", x + 0.35, 2.92, 1.0, 0.8, [[(str(i + 1), F_LIGHT, 40, LIME if i == 2 else ACCENT)]])
    text_box(g, f"lp{i}_t", x + 0.35, 3.85, 3.3, 1.3, [[(t1, F_MED, 16, "FFFFFF" if i == 2 else INK)]])
    if t2:
        text_box(g, f"lp{i}_u", x + 0.35, 5.45, 3.3, 0.3, [[(t2, F_REG, 12, ACCENT)]])
    G.append(g)
an.rise(t_, 0.1)
an.stagger(G, start=0.35, step=0.22)
done(s, 22, an)

popup_v2(23, 3, _popup_bg("bg_popup_v2c.jpg"), f"{A}/client4_worried.png", 4.9, (9.05, 1.95), "Удалили из Кошелька — пластик работает",
         "Удаление карты из телефона не блокирует карту.",
         "Пластиковой картой можно пользоваться как раньше.",
         "Что сказать: ", "«Захотите снова платить телефоном — просто добавьте карту заново».",
         ["#после подключения"], "«Я удалила карту из Кошелька — она заблокирована?»", "удалить ≠ заблокировать", (4.4, 5.55))

# =============== 24: recap map ===============
s, an = content(None, bar=False)
t_ = title2(s, "Четыре шага — и клиент уходит", "с работающим Google Pay", size=34, h=1.6)
tiles(s, an, recap=True)
hn, _, _ = hand(s, "hand", "сфотографируйте этот экран!", 12.75, 1.55, size=24, rot=3, anchor="right")
an.rise(t_, 0.1)
an.fade(hn, 1.9)
done(s, 24, an)

# =============== 25: test intro ===============
s, an = content(4, bar=False)
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

# =============== 26: end (dark) ===============
s = new_slide()
an = AnimV2(s)
picture(s, "end_bg", os.path.join(V2, "scene_cover.jpg"), 0, 0, w=SW, h=SH)
scrim(s, w=7.6, a0=88, a1=62)
chrome_v2(s, dark=True)
t_ = text_box(s, "end_title", 0.6, 1.9, 6.5, 1.0, [[("Курс завершён", F_MED, 52, "FFFFFF")]])
s_ = text_box(s, "end_sub", 0.64, 3.15, 5.6, 1.2, [[("На следующем приёме начните с первого шага: ", F_REG, 18, WHITE_T), ("карта, телефон, настройки.", F_SEMI, 18, LIME)]])
b = rect(s, "btn_end", MSO_SHAPE.ROUNDED_RECTANGLE, 0.64, 4.6, 2.2, 0.58, fill=LIME, adj=0.5)
shape_text(b, [("Завершить", F_SEMI, 14, ACCENT)])
an.rise(t_, 0.2)
an.rise(s_, 0.45)
an.rise(b, 0.7)
done(s, 26, an)

prs.save(OUT)
print("saved", OUT, "slides:", len(prs.slides))
