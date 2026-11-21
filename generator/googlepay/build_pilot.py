"""Google Pay course pilot: 11 slides, Morph, in-slide animations, embedded narration."""
import copy
import os
import sys
from lxml import etree
from PIL import Image
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn
from pptx.opc.constants import RELATIONSHIP_TYPE as RT
from pptx.media import Video
from pptx.parts.media import MediaPart

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
A = os.path.join(HERE, "assets")
SCR = os.path.join(HERE, "screens")
NARR = os.path.join(ROOT, "GooglePay", "ozvuchka")
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "GooglePay", "GooglePay_pilot.pptx")
POPUP_BG = sys.argv[2] if len(sys.argv) > 2 else os.path.join(A, "bg_popup.jpg")

INK, GREY, LIGHT, LINE = "1C1F1D", "8A918C", "B4BCB7", "DCE2DE"
ACCENT, LIME, MINT = "02691A", "4CEA4C", "E6F8E6"
F_REG, F_MED, F_SEMI, F_LIGHT, F_HAND = "Manrope", "Manrope Medium", "Manrope SemiBold", "Manrope Light", "Caveat"

DUR = {1: 21.89, 2: 12.12, 3: 11.73, 4: 12.28, 5: 19.80, 6: 6.11, 7: 3.00, 8: 13.79, 9: 11.00, 10: 9.72, 11: 6.61}

NARR_TEXT = {
    1: "Здравствуйте! Теперь клиенты Ипак Йули банка могут платить телефоном на Android — через Google Pay. Устроен он так же, как Apple Pay, который вы уже знаете. А вот сбои у него другие… и с ними клиенты придут к вам. Поэтому в этом курсе — три проверки: карта, телефон, настройки. С ними вы поможете клиенту прямо в офисе.",
    2: "Подойдёт ли клиенту Google Pay, решают три проверки. Первая — карта. Подходят карты Visa и Mastercard нашего банка. Humo и Uzcard Google Pay пока не принимает.",
    3: "Вторая — телефон. Нужен Android с модулем NFC и сервисами Google. Если сервисов Google нет — так бывает на многих новых Huawei, — Кошелёк просто не установится.",
    4: "Третья — настройки. NFC включён, на телефоне стоит блокировка экрана, а Кошелёк выбран приложением для оплаты по умолчанию. Без блокировки экрана бесконтактная оплата не включится.",
    5: "Вот как это бывает в офисе. Клиент спрашивает: «Почему моя Humo не добавляется?» Сбоя здесь нет: Google Pay пока принимает только Visa и Mastercard. Humo и Uzcard обещают подключить позже, но даты пока нет. Спросите, есть ли у клиента Visa или Mastercard нашего банка, — её и добавляем.",
    6: "Теперь — как добавить карту. Откройте Кошелёк и нажмите плюс внизу экрана.",
    7: "В списке выберите «Платёжная карта».",
    8: "Проще всего — добавить карту из приложения Ipak Yuli Mobile: номер карты вводить не нужно. Если приложения нет, нажмите «Новая кредитная или дебетовая карта» — данные карты клиент вводит сам.",
    9: "Клиент подтверждает: «Добавить в Кошелёк». Кошелёк проверяет карту и показывает условия банка — публичную оферту. Клиент читает её и принимает.",
    10: "Дальше Кошелёк предложит стать приложением для оплаты по умолчанию. Нажмите «Сделать основной» — это и есть наша третья проверка, настройки.",
    11: "Готово: бесконтактная оплата настроена. В магазине клиент просто подносит телефон к терминалу.",
}
NOTES_EXTRA = {
    2: "Факт: Visa и Mastercard Ipak Yuli Bank — в пресс-релизе ЦБ от 27.10.2026 и в п. 1.3 публичной оферты банка (экран при добавлении карты). [Сверить: все ли карточные продукты подключаются.]",
    3: "[Сверить с продуктовой командой: список марок телефонов, на которых чаще всего не работает.]",
    5: "Ситуация из Розничного блока. [Сверить: что предлагать клиенту без Visa/Mastercard — по процедуре банка.]",
    8: "[Сверить по записи экрана Ipak Yuli Mobile: путь добавления карты из приложения банка.] Экраны ввода номера карты защищены системой — их нельзя записать скриншотом.",
    9: "[Сверить: название кнопки принятия оферты — в записи её не видно.]",
}

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
BLANK = prs.slide_layouts[6]

MORPH = ('<mc:AlternateContent xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" '
         'xmlns:p159="http://schemas.microsoft.com/office/powerpoint/2015/09/main">'
         '<mc:Choice Requires="p159"><p:transition xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" '
         'xmlns:p14="http://schemas.microsoft.com/office/powerpoint/2010/main" spd="slow" p14:dur="{dur}" advTm="{adv}">'
         '<p159:morph option="byObject"/></p:transition></mc:Choice>'
         '<mc:Fallback><p:transition xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" spd="slow" advTm="{adv}"><p:fade/></p:transition></mc:Fallback>'
         '</mc:AlternateContent>')


# ---------- helpers ----------
def rgb(h):
    return RGBColor.from_string(h)


def set_name(shape, name):
    shape._element.xpath("./*[1]/p:cNvPr")[0].set("name", name)


def text_box(slide, name, x, y, w, h, paras, anchor=MSO_ANCHOR.TOP, rot=0):
    """paras: list of list of (text, font, size, color, bold) runs; a run may be 'BR'."""
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    set_name(tb, name)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    for i, runs in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        align = None
        spacing = None
        for r in runs:
            if r == "BR":
                p.add_line_break()
                continue
            if isinstance(r, dict):
                align = r.get("align", align)
                spacing = r.get("space", spacing)
                continue
            text, font, size, color = r[:4]
            run = p.add_run()
            run.text = text
            run.font.name = font
            run.font.size = Pt(size)
            run.font.color.rgb = rgb(color)
            if len(r) > 4 and r[4]:
                run.font.bold = True
        if align:
            p.alignment = align
        if spacing:
            p.space_after = Pt(spacing)
        p.line_spacing = 1.0
    if rot:
        tb.rotation = rot
    return tb


def rect(slide, name, kind, x, y, w, h, fill=None, line=None, line_w=None, alpha=None, adj=None, shadow=None):
    sh = slide.shapes.add_shape(kind, Inches(x), Inches(y), Inches(w), Inches(h))
    set_name(sh, name)
    if fill:
        sh.fill.solid()
        sh.fill.fore_color.rgb = rgb(fill)
        if alpha is not None:
            clr = sh.fill._xPr.find(qn("a:solidFill"))[0]
            a = etree.SubElement(clr, qn("a:alpha"))
            a.set("val", str(int(alpha * 1000)))
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
    sh.text_frame.margin_left = sh.text_frame.margin_right = 0
    return sh


def add_shadow(shape, blur=0.35, dist=0.06, alpha=18):
    spPr = shape._element.spPr
    eff = etree.SubElement(spPr, qn("a:effectLst"))
    sh = etree.SubElement(eff, qn("a:outerShdw"))
    sh.set("blurRad", str(int(Inches(blur))))
    sh.set("dist", str(int(Inches(dist))))
    sh.set("dir", "5400000")
    sh.set("algn", "t")
    sh.set("rotWithShape", "0")
    c = etree.SubElement(sh, qn("a:srgbClr"))
    c.set("val", "000000")
    a = etree.SubElement(c, qn("a:alpha"))
    a.set("val", str(alpha * 1000))


def shape_text(sh, runs, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE):
    tf = sh.text_frame
    tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    for text, font, size, color in runs:
        r = p.add_run()
        r.text = text
        r.font.name, r.font.size, r.font.color.rgb = font, Pt(size), rgb(color)


def picture(slide, name, path, x, y, h=None, w=None):
    im = Image.open(path)
    ar = im.width / im.height
    if h is not None and w is None:
        w = h * ar
    if w is not None and h is None:
        h = w / ar
    pic = slide.shapes.add_picture(path, Inches(x), Inches(y), Inches(w), Inches(h))
    set_name(pic, name)
    return pic


def round_picture(pic, adj):
    pic.auto_shape_type = MSO_SHAPE.ROUNDED_RECTANGLE
    geom = pic._element.spPr.find(qn("a:prstGeom"))
    av = geom.find(qn("a:avLst"))
    for g in list(av):
        av.remove(g)
    gd = etree.SubElement(av, qn("a:gd"))
    gd.set("name", "adj")
    gd.set("fmla", f"val {adj}")


def chrome(slide, bg):
    picture(slide, "!!bg", bg, 0, 0, w=13.333, h=7.5)
    picture(slide, "!!logo", f"{A}/logo.png", 0.55, 0.36, h=0.42)
    text_box(slide, "!!hdr", 8.6, 0.42, 4.2, 0.3, [[{"align": PP_ALIGN.RIGHT}, ("Курс · Google Pay", F_REG, 10, GREY)]])
    text_box(slide, "!!ftrL", 0.55, 6.98, 4, 0.3, [[("Розничный блок", F_REG, 10, GREY)]])
    text_box(slide, "!!ftrR", 8.6, 6.98, 4.2, 0.3, [[{"align": PP_ALIGN.RIGHT}, ("Ipak Yuli Bank", F_REG, 10, GREY)]])


def pill(slide, name, x, y, text, color=ACCENT):
    w = 0.22 + 0.085 * len(text)
    sh = rect(slide, name, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, 0.3, fill="FFFFFF", line=color, line_w=1, adj=0.5)
    shape_text(sh, [(text, F_REG, 10.5, color)])
    return w


def tap_marker(slide, name, cx, cy, d=0.62):
    sh = rect(slide, name, MSO_SHAPE.OVAL, cx - d / 2, cy - d / 2, d, d, fill=LIME, alpha=45, line="FFFFFF", line_w=2.5,
              shadow=(0.18, 0.02, 25))
    return sh


def notes(slide, n):
    tf = slide.notes_slide.notes_text_frame
    tf.text = "Озвучка: " + NARR_TEXT[n]
    if n in NOTES_EXTRA:
        tf.add_paragraph().text = NOTES_EXTRA[n]


# ---------- animation / media XML ----------
P_NS = "http://schemas.openxmlformats.org/presentationml/2006/main"


class Timeline:
    def __init__(self, slide):
        self.slide = slide
        self.effects = []  # xml strings with placeholders
        self.bld = []
        self.next_id = 5
        self.audio_spid = None

    def _id(self):
        self.next_id += 1
        return self.next_id

    def fade_in(self, shape, delay_s, dur=0.5):
        sp = shape.shape_id
        i1, i2, i3 = self._id(), self._id(), self._id()
        is_sp = shape._element.tag == qn("p:sp")
        grp = ' grpId="0"' if is_sp else ""
        self.effects.append(
            f'<p:par><p:cTn id="{i1}" presetID="10" presetClass="entr" presetSubtype="0" fill="hold"{grp} nodeType="withEffect">'
            f'<p:stCondLst><p:cond delay="{int(delay_s*1000)}"/></p:stCondLst><p:childTnLst>'
            f'<p:set><p:cBhvr><p:cTn id="{i2}" dur="1" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst></p:cTn>'
            f'<p:tgtEl><p:spTgt spid="{sp}"/></p:tgtEl><p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst></p:cBhvr>'
            f'<p:to><p:strVal val="visible"/></p:to></p:set>'
            f'<p:animEffect transition="in" filter="fade"><p:cBhvr><p:cTn id="{i3}" dur="{int(dur*1000)}"/>'
            f'<p:tgtEl><p:spTgt spid="{sp}"/></p:tgtEl></p:cBhvr></p:animEffect></p:childTnLst></p:cTn></p:par>')
        if is_sp:
            self.bld.append((sp, 0))

    def fade_out(self, shape, delay_s, dur=0.4, grp_id=2):
        sp = shape.shape_id
        i1, i2, i3 = self._id(), self._id(), self._id()
        is_sp = shape._element.tag == qn("p:sp")
        grp = f' grpId="{grp_id}"' if is_sp else ""
        d = int(dur * 1000)
        self.effects.append(
            f'<p:par><p:cTn id="{i1}" presetID="10" presetClass="exit" presetSubtype="0" fill="hold"{grp} nodeType="withEffect">'
            f'<p:stCondLst><p:cond delay="{int(delay_s*1000)}"/></p:stCondLst><p:childTnLst>'
            f'<p:animEffect transition="out" filter="fade"><p:cBhvr><p:cTn id="{i2}" dur="{d}"/>'
            f'<p:tgtEl><p:spTgt spid="{sp}"/></p:tgtEl></p:cBhvr></p:animEffect>'
            f'<p:set><p:cBhvr><p:cTn id="{i3}" dur="1" fill="hold"><p:stCondLst><p:cond delay="{d-1}"/></p:stCondLst></p:cTn>'
            f'<p:tgtEl><p:spTgt spid="{sp}"/></p:tgtEl><p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst></p:cBhvr>'
            f'<p:to><p:strVal val="hidden"/></p:to></p:set></p:childTnLst></p:cTn></p:par>')
        if is_sp:
            self.bld.append((sp, grp_id))

    def pulse(self, shape, delay_s, repeat=3, scale=118, grp_id=1):
        sp = shape.shape_id
        i1, i2 = self._id(), self._id()
        self.effects.append(
            f'<p:par><p:cTn id="{i1}" presetID="6" presetClass="emph" presetSubtype="0" repeatCount="{repeat*1000}" '
            f'accel="50000" decel="50000" autoRev="1" fill="hold" grpId="{grp_id}" nodeType="withEffect">'
            f'<p:stCondLst><p:cond delay="{int(delay_s*1000)}"/></p:stCondLst><p:childTnLst>'
            f'<p:animScale><p:cBhvr><p:cTn id="{i2}" dur="450" fill="hold"/><p:tgtEl><p:spTgt spid="{sp}"/></p:tgtEl></p:cBhvr>'
            f'<p:by x="{scale*1000}" y="{scale*1000}"/></p:animScale></p:childTnLst></p:cTn></p:par>')
        self.bld.append((sp, grp_id))

    def audio(self, mp3_path, label="narration"):
        slide = self.slide
        video = Video.from_path_or_file_like(mp3_path, "audio/mpeg")
        media_part = MediaPart.new(slide.part.package, video)
        r_media = slide.part.relate_to(media_part, RT.MEDIA)
        r_audio = slide.part.relate_to(media_part, RT.AUDIO)
        _, r_img = slide.part.get_or_add_image_part(f"{A}/speaker.png")
        spid = max(int(e.get("id")) for e in slide.shapes._spTree.iter(qn("p:cNvPr"))) + 1
        xml = (
            f'<p:pic xmlns:p="{P_NS}" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
            f'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
            f'<p:nvPicPr><p:cNvPr id="{spid}" name="{label}"><a:hlinkClick r:id="" action="ppaction://media"/></p:cNvPr>'
            f'<p:cNvPicPr><a:picLocks noChangeAspect="1"/></p:cNvPicPr>'
            f'<p:nvPr><a:audioFile r:link="{r_audio}"/><p:extLst><p:ext uri="{{DAA4B4D4-6D71-4841-9C94-3DE7FCFB9230}}">'
            f'<p14:media xmlns:p14="http://schemas.microsoft.com/office/powerpoint/2010/main" r:embed="{r_media}"/></p:ext></p:extLst></p:nvPr></p:nvPicPr>'
            f'<p:blipFill><a:blip r:embed="{r_img}"/><a:stretch><a:fillRect/></a:stretch></p:blipFill>'
            f'<p:spPr><a:xfrm><a:off x="{-int(Inches(1.2))}" y="{int(Inches(0.2))}"/><a:ext cx="{int(Inches(0.5))}" cy="{int(Inches(0.5))}"/></a:xfrm>'
            f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr></p:pic>')
        slide.shapes._spTree.append(etree.fromstring(xml))
        self.audio_spid = spid

    def write(self, audio_ms):
        inner = ""
        if self.audio_spid:
            inner += (f'<p:par><p:cTn id="5" presetID="1" presetClass="mediacall" presetSubtype="0" fill="hold" nodeType="afterEffect">'
                      f'<p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst><p:cmd type="call" cmd="playFrom(0.0)">'
                      f'<p:cBhvr><p:cTn id="{self._id()}" dur="{audio_ms}" fill="hold"/><p:tgtEl><p:spTgt spid="{self.audio_spid}"/></p:tgtEl>'
                      f'</p:cBhvr></p:cmd></p:childTnLst></p:cTn></p:par>')
        inner += "".join(self.effects)
        media_node = ""
        if self.audio_spid:
            media_node = (f'<p:audio><p:cMediaNode vol="80000"><p:cTn id="{self._id()}" fill="hold" display="0">'
                          f'<p:stCondLst><p:cond delay="indefinite"/></p:stCondLst></p:cTn>'
                          f'<p:tgtEl><p:spTgt spid="{self.audio_spid}"/></p:tgtEl></p:cMediaNode></p:audio>')
        bld = ""
        if self.bld:
            seen = []
            for b in self.bld:
                if b not in seen:
                    seen.append(b)
            bld = "<p:bldLst>" + "".join(f'<p:bldP spid="{s}" grpId="{g}" animBg="1"/>' for s, g in seen) + "</p:bldLst>"
        xml = (f'<p:timing xmlns:p="{P_NS}"><p:tnLst><p:par><p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot"><p:childTnLst>'
               f'<p:seq concurrent="1" nextAc="seek"><p:cTn id="2" dur="indefinite" nodeType="mainSeq"><p:childTnLst>'
               f'<p:par><p:cTn id="3" fill="hold"><p:stCondLst><p:cond delay="indefinite"/><p:cond evt="onBegin" delay="0"><p:tn val="2"/></p:cond></p:stCondLst><p:childTnLst>'
               f'<p:par><p:cTn id="4" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>'
               f'{inner}</p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn></p:par>'
               f'</p:childTnLst></p:cTn><p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>'
               f'<p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst></p:seq>'
               f'{media_node}</p:childTnLst></p:cTn></p:par></p:tnLst>{bld}</p:timing>')
        el = etree.fromstring(xml)
        for k, ctn in enumerate(el.iter(qn("p:cTn")), start=1):
            ctn.set("id", str(k))
        sld = self.slide._element
        # order: cSld, clrMapOvr, transition, timing
        sld.append(el)


def finish(slide, n, morph=True, tl=None):
    notes(slide, n)
    adv = int((DUR[n] + 0.8) * 1000)
    clr = slide._element.find(qn("p:clrMapOvr"))
    trans = etree.fromstring(MORPH.format(dur=1400 if morph else 700, adv=adv))
    if clr is not None:
        clr.addnext(trans)
    else:
        slide._element.find(qn("p:cSld")).addnext(trans)
    tl = tl or Timeline(slide)
    tl.audio(f"{NARR}/{n:02d}.mp3", label=f"narration_slide{n}")
    tl.write(int(DUR[n] * 1000))


def new_slide():
    return prs.slides.add_slide(BLANK)


# ---------- phone ----------
SCR_W_IN, SCR_H_IN = 2.716, 6.05
BEZ = 0.09


def phone(slide, screen_path, x, y, z=1.0, screen_name="!!screen"):
    """x,y = top-left of SCREEN; z = zoom factor."""
    sw, sh_ = SCR_W_IN * z, SCR_H_IN * z
    b = BEZ * z
    body = rect(slide, "!!phone", MSO_SHAPE.ROUNDED_RECTANGLE, x - b, y - b, sw + 2 * b, sh_ + 2 * b, fill="121413",
                adj=0.075, shadow=(0.45, 0.10, 22))
    pic = picture(slide, screen_name, screen_path, x, y, w=sw, h=sh_)
    round_picture(pic, 5200)
    return body, pic


def screen_point(x, y, z, rx, ry):
    return x + rx * SCR_W_IN * z, y + ry * SCR_H_IN * z


# =============== SLIDE 1: cover ===============
s = new_slide()
chrome(s, f"{A}/bg_cover.jpg")
text_box(s, "!!title", 0.6, 1.75, 7.9, 2.3, [[("Google Pay", F_MED, 54, INK), "BR", ("за три проверки", F_MED, 54, ACCENT)]])
note = text_box(s, "!!note", 5.05, 1.32, 3.4, 1.15, [[("— как Apple Pay,", F_HAND, 30, ACCENT), "BR", ("но на Android", F_HAND, 30, ACCENT)]], rot=-6)
sub = text_box(s, "!!sub", 0.62, 4.15, 5.3, 1.3, [[("Карта, телефон, настройки — так вы поможете клиенту прямо в офисе. Устроен Google Pay как Apple Pay, а сбои у него другие.", F_REG, 16, INK)]])
picture(s, "!!hero", f"{A}/hero.png", 9.05, 0.45, h=7.05)
tl = Timeline(s)
tl.fade_in(note, 6.9, 0.6)
tl.fade_in(sub, 16.2, 0.6)
finish(s, 1, morph=False, tl=tl)

# =============== SLIDES 2-4: three checks ===============
ITEMS = [
    ("01", "Карта", "проверка 1 из 3", "Visa или Mastercard Ипак Йули",
     "Humo и Uzcard Google Pay пока не принимает — их обещают подключить позже.", ["#тип карты"]),
    ("02", "Телефон", "проверка 2 из 3", "Android с NFC и сервисами Google",
     "Нет сервисов Google — как на многих новых Huawei — Кошелёк не установится.", ["#NFC", "#Google Play"]),
    ("03", "Настройки", "проверка 3 из 3", "NFC, блокировка экрана, Кошелёк по умолчанию",
     "Без блокировки экрана бесконтактная оплата не включится.", ["#по умолчанию"]),
]
LX, LW = 6.95, 5.85
popup_card_seed = None
for k in range(3):
    s = new_slide()
    chrome(s, f"{A}/bg_main.jpg")
    text_box(s, "!!title", 0.6, 1.3, 5.9, 2.8, [[("Подойдёт ли", F_MED, 40, INK), "BR", ("Google Pay —", F_MED, 40, INK), "BR",
                                                  ("решают", F_MED, 40, ACCENT), "BR", ("три проверки", F_MED, 40, ACCENT)]])
    text_box(s, "!!note", 3.25, 3.95, 3.0, 0.7, [[("до подключения!", F_HAND, 28, ACCENT)]], rot=-5)
    text_box(s, "!!sum", 0.62, 5.7, 5.2, 0.7, [[("Все три — до того, как клиент начнёт добавлять карту.", F_REG, 14, INK)]])
    y = 1.35
    for i, (num, ttl, lbl, head, txt, tags) in enumerate(ITEMS):
        active = (i == k)
        h = 2.45 if active else 0.78
        ln = rect(s, f"!!it{i}_line", MSO_SHAPE.RECTANGLE, LX, y, LW, 0.022 if active else 0.012,
                  fill=INK if active else LINE)
        col = INK if active else LIGHT
        text_box(s, f"!!it{i}_num", LX, y + 0.22, 0.6, 0.4, [[(num, F_REG, 15, col)]])
        text_box(s, f"!!it{i}_ttl", LX + 0.62, y + 0.18, 3.6, 0.5, [[(ttl, F_MED, 20 if active else 17, col)]])
        text_box(s, f"!!it{i}_lbl", LX + LW - 2.0, y + 0.24, 2.0, 0.35, [[{"align": PP_ALIGN.RIGHT}, (lbl, F_REG, 10.5, GREY if active else LIGHT)]])
        if active:
            text_box(s, f"!!it{i}_head", LX + 0.62, y + 0.82, 5.1, 0.45, [[(head, F_SEMI, 15, INK)]])
            text_box(s, f"!!it{i}_txt", LX + 0.62, y + 1.25, 4.9, 0.7, [[(txt, F_REG, 13, INK)]])
            px = LX + 0.62
            for t_i, t in enumerate(tags):
                px += pill(s, f"!!it{i}_tag{t_i}", px, y + 1.95, t) + 0.12
        y += h
    rect(s, "!!list_end", MSO_SHAPE.RECTANGLE, LX, y, LW, 0.012, fill=LINE)
    if k == 2:
        # invisible seed for popup zoom
        rect(s, "!!card", MSO_SHAPE.ROUNDED_RECTANGLE, 6.2, 3.45, 0.9, 0.5, fill="FFFFFF", alpha=0, adj=0.04)
    finish(s, 2 + k)

# =============== SLIDE 5: popup situation ===============
s = new_slide()
picture(s, "!!bg", POPUP_BG or f"{A}/bg_main.jpg", 0, 0, w=13.333, h=7.5)
card = rect(s, "!!card", MSO_SHAPE.ROUNDED_RECTANGLE, 0.8, 0.72, 11.73, 6.08, fill="FFFFFF", adj=0.04, shadow=(0.6, 0.12, 28))
xbtn = rect(s, "pop_x", MSO_SHAPE.OVAL, 11.92, 0.95, 0.36, 0.36, fill="EEF1EF")
shape_text(xbtn, [("✕", F_REG, 11, GREY)])
text_box(s, "pop_title", 1.35, 1.3, 6.2, 0.9, [[("Humo пока не добавить", F_MED, 36, INK)]])
sub5 = text_box(s, "pop_sub", 1.35, 2.25, 6.3, 0.8, [[("Google Pay сейчас принимает только Visa и Mastercard.", F_MED, 18, INK)]])
b1 = text_box(s, "pop_b1", 1.35, 3.25, 6.0, 0.8, [[("Humo и Uzcard обещают подключить позже — даты пока нет.", F_REG, 14, INK)]])
b2 = text_box(s, "pop_b2", 1.35, 4.0, 6.0, 1.0, [[("Что делать: ", F_SEMI, 14, ACCENT), ("спросите, есть ли у клиента Visa или Mastercard Ипак Йули, — её и добавляем.", F_REG, 14, INK)]])
tg1 = rect(s, "pop_tag1", MSO_SHAPE.ROUNDED_RECTANGLE, 1.35, 5.3, 1.32, 0.3, fill="FFFFFF", line=ACCENT, line_w=1, adj=0.5)
shape_text(tg1, [("#проверка 1", F_REG, 10.5, ACCENT)])
tg2 = rect(s, "pop_tag2", MSO_SHAPE.ROUNDED_RECTANGLE, 2.79, 5.3, 0.88, 0.3, fill="FFFFFF", line=ACCENT, line_w=1, adj=0.5)
shape_text(tg2, [("#карта", F_REG, 10.5, ACCENT)])
cl = picture(s, "pop_client", f"{A}/client.png", 8.75, 1.8, h=5.0)
bub = rect(s, "pop_bubble", MSO_SHAPE.ROUNDED_RECTANGULAR_CALLOUT, 7.65, 0.86, 2.75, 0.85, fill=MINT)
bub.adjustments[0] = 0.19
bub.adjustments[1] = 0.84
shape_text(bub, [("«Почему моя Humo не добавляется?»", F_HAND, 22, ACCENT)])
pn = text_box(s, "pop_note", 4.05, 5.15, 2.6, 0.6, [[("пока — нет!", F_HAND, 28, ACCENT)]], rot=-6)
tl = Timeline(s)
tl.fade_in(bub, 3.05, 0.5)
tl.fade_in(sub5, 6.6, 0.5)
tl.fade_in(b1, 9.95, 0.5)
tl.fade_in(pn, 10.4, 0.5)
tl.fade_in(b2, 14.25, 0.5)
tl.fade_in(tg1, 14.5, 0.4)
tl.fade_in(tg2, 14.6, 0.4)
finish(s, 5, tl=tl)

# =============== SLIDES 6-11: walkthrough ===============
STEPS = [
    # n, screen, num, title, text, zoom, taps(list of rel points), note
    (6, "scr_home", "01", "Нажмите «+»", "Откройте Кошелёк — кнопка «+» внизу экрана.", 1.0, [(0.604, 0.944)], None),
    (7, "scr_addlist", "02", "Выберите «Платежная карта»", "Первая строка в списке «Добавить в Кошелек».", 1.0, [(0.16, 0.268)], None),
    (8, "scr_payopts", "03", "Проще — из Ipak Yuli Mobile",
     "Номер карты вводить не нужно. Нет приложения — «Новая кредитная или дебетовая карта»: данные вводит сам клиент.", 1.4,
     [(0.135, 0.419), (0.115, 0.858)], "без ввода номера!"),
    (9, "scr_confirm", "04", "Подтвердите и примите оферту",
     "«Добавить в Кошелек» — Кошелёк проверит карту и покажет публичную оферту банка. Клиент читает и принимает.", 1.0,
     [(0.82, 0.855)], None),
    (10, "scr_default", "05", "Нажмите «Сделать основной»",
     "Это третья проверка — настройки: Кошелёк станет приложением для оплаты по умолчанию.", 1.0, [(0.82, 0.855)], None),
    (11, "scr_done", "✓", "Готово", "Бесконтактная оплата настроена. В магазине клиент подносит телефон к терминалу.", 1.0, [], "можно платить!"),
]
PX, PY = 8.79, 0.71  # screen top-left at zoom 1
for idx, (n, scr, num, ttl, txt, z, taps, hand) in enumerate(STEPS):
    s = new_slide()
    chrome(s, f"{A}/bg_main.jpg")
    text_box(s, "!!title", 0.6, 1.15, 6.6, 1.5, [[("Добавить карту —", F_MED, 40, INK), "BR", ("пять шагов в Кошельке", F_MED, 40, ACCENT)]])
    for d_i in range(5):
        state = "done" if (d_i < idx or n == 11) else ("active" if d_i == idx else "todo")
        fill = {"done": LIME, "active": ACCENT, "todo": "E3E8E4"}[state]
        tcol = {"done": ACCENT, "active": "FFFFFF", "todo": GREY}[state]
        dot = rect(s, f"!!dot{d_i}", MSO_SHAPE.OVAL, 0.62 + d_i * 0.46, 2.82, 0.34, 0.34, fill=fill)
        shape_text(dot, [(str(d_i + 1), F_SEMI, 10.5, tcol)])
    text_box(s, "!!stepnum", 0.6, 3.3, 1.6, 1.1, [[(num, F_LIGHT, 60, ACCENT)]])
    text_box(s, "!!stepttl", 2.25, 3.42, 4.9, 1.0, [[(ttl, F_MED, 24, INK)]])
    text_box(s, "!!steptxt", 2.25, 4.35, 4.6, 1.8, [[(txt, F_REG, 15, INK)]])
    if z != 1.0:
        tx, ty = 10.75, 3.0
        rx, ry = taps[0][0] if False else 0.47, 0.419
        sx = tx - rx * SCR_W_IN * z
        sy = ty - ry * SCR_H_IN * z
    else:
        sx, sy = PX, PY
    body, pic = phone(s, f"{SCR}/{scr}.png", sx, sy, z)
    tl = Timeline(s)
    markers = []
    for t_i, (rx, ry) in enumerate(taps):
        cx, cy = screen_point(sx, sy, z, rx, ry)
        m = tap_marker(s, "!!tap" if t_i == 0 else f"tap{t_i}", cx, cy)
        markers.append(m)
    if n == 9:
        offer = picture(s, "screen_offer", f"{SCR}/scr_offer.png", sx, sy, w=SCR_W_IN * z, h=SCR_H_IN * z)
        round_picture(offer, 5200)
        tl.fade_in(offer, 3.1, 0.6)
        tl.fade_out(markers[0], 3.0, 0.3)
    if hand:
        hn = text_box(s, "hand", 3.6 if n == 8 else 4.4, 5.85 if n == 8 else 5.6, 3.2, 0.7, [[(hand, F_HAND, 28, ACCENT)]], rot=-5)
        tl.fade_in(hn, 4.2 if n == 8 else 1.2, 0.5)
    if markers:
        tl.pulse(markers[0], 0.6 if n != 10 else 4.4)
    if n == 8 and len(markers) > 1:
        tl.fade_in(markers[1], 6.7, 0.4)
        tl.pulse(markers[1], 7.2)
    finish(s, n, tl=tl)

prs.save(OUT)
print("saved", OUT, "slides:", len(prs.slides))
