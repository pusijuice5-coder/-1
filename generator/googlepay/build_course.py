"""Google Pay course (RU) for the Retail block: 26 slides, Morph, animations, embedded narration."""
import copy
import os
import subprocess
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
NARR = os.path.join(ROOT, "GooglePay", "ozvuchka_kurs")
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "GooglePay", "GooglePay_kurs_RU.pptx")


def _bg(name):
    p = os.path.join(A, name)
    return p if os.path.exists(p) else os.path.join(A, "bg_popup.jpg")


POPUP_BG = {7: _bg("bg_popup.jpg"), 19: _bg("bg_popup_s18.jpg"), 23: _bg("bg_popup_s22.jpg")}

INK, GREY, LIGHT, LINE = "1C1F1D", "8A918C", "B4BCB7", "DCE2DE"
ACCENT, LIME, MINT = "02691A", "4CEA4C", "E6F8E6"
F_REG, F_MED, F_SEMI, F_LIGHT, F_HAND = "Manrope", "Manrope Medium", "Manrope SemiBold", "Manrope Light", "Caveat"

def _dur(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                         capture_output=True, text=True).stdout.strip()
    return float(out)


DUR = {n: _dur(os.path.join(NARR, f"{n:02d}.mp3")) for n in range(1, 27)}

from course_text import NARR_TEXT, NOTES_EXTRA

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


# ---------- extra helpers for the course ----------
def group(container, name):
    g = container.shapes.add_group_shape()
    set_name(g, name)
    return g


def pic_alpha(pic, amt):
    blip = pic._element.blipFill.find(qn("a:blip"))
    a = etree.SubElement(blip, qn("a:alphaModFix"))
    a.set("amt", str(int(amt * 1000)))


def title2(slide, l1, l2, size=40, x=0.6, y=1.0, w=11.5, h=1.8):
    return text_box(slide, "!!title", x, y, w, h, [[(l1, F_MED, size, INK), "BR", (l2, F_MED, size, ACCENT)]])


def bullet_item(container, name, x, y, w, text, mark="✓", fill=LIME, mcol=ACCENT, size=15):
    g = group(container, name)
    c = rect(g, f"{name}_dot", MSO_SHAPE.OVAL, x, y + 0.02, 0.34, 0.34, fill=fill)
    shape_text(c, [(mark, F_SEMI, 11, mcol)])
    text_box(g, f"{name}_txt", x + 0.5, y, w - 0.5, 0.75, [[(text, F_REG, size, INK)]])
    return g


def card(container, name, x, y, w, h, fill="FFFFFF", shadow=(0.45, 0.06, 14)):
    return rect(container, name, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h, fill=fill, adj=0.06, shadow=shadow)


def popup(n, client_img, client_h, client_xy, title, sub, b1, b2_lead, b2, tags, bubble, note, t, note_xy=(4.6, 5.15)):
    """t: dict of delays: bubble, sub, b1, note, b2."""
    s = new_slide()
    picture(s, "!!bg", POPUP_BG.get(n, POPUP_BG[7]), 0, 0, w=13.333, h=7.5)
    rect(s, "!!card", MSO_SHAPE.ROUNDED_RECTANGLE, 0.8, 0.72, 11.73, 6.08, fill="FFFFFF", adj=0.04, shadow=(0.6, 0.12, 28))
    xb = rect(s, "pop_x", MSO_SHAPE.OVAL, 11.92, 0.95, 0.36, 0.36, fill="EEF1EF")
    shape_text(xb, [("✕", F_REG, 11, GREY)])
    text_box(s, "pop_title", 1.35, 1.3, 5.9, 1.3, [[(title, F_MED, 32, INK)]])
    sb = text_box(s, "pop_sub", 1.35, 2.55, 6.1, 0.8, [[(sub, F_MED, 17, INK)]])
    bb1 = text_box(s, "pop_b1", 1.35, 3.45, 6.0, 0.8, [[(b1, F_REG, 14, INK)]])
    bb2 = text_box(s, "pop_b2", 1.35, 4.25, 6.0, 1.0, [[(b2_lead, F_SEMI, 14, ACCENT), (b2, F_REG, 14, INK)]])
    tg = group(s, "pop_tags")
    px = 1.35
    for i, tag in enumerate(tags):
        px += pill(tg, f"pop_tag{i}", px, 5.45, tag) + 0.12
    picture(s, "pop_client", client_img, client_xy[0], client_xy[1], h=client_h)
    long_b = len(bubble) > 40
    bw, bh, bf = (3.3, 1.15, 19) if long_b else (2.9, 0.9, 21)
    bub = rect(s, "pop_bubble", MSO_SHAPE.ROUNDED_RECTANGULAR_CALLOUT, 7.45, 0.8, bw, bh, fill=MINT)
    bub.adjustments[0] = 0.12 if long_b else 0.19
    bub.adjustments[1] = 0.80 if long_b else 0.84
    shape_text(bub, [(bubble, F_HAND, bf, ACCENT)])
    runs = []
    for k_, part in enumerate(note.split("\n")):
        if k_:
            runs.append("BR")
        runs.append((part, F_HAND, 26, ACCENT))
    pn = text_box(s, "pop_note", note_xy[0], note_xy[1], 3.6, 1.0, [runs], rot=-5)
    tl = Timeline(s)
    tl.fade_in(bub, t["bubble"], 0.5)
    tl.fade_in(sb, t["sub"], 0.5)
    tl.fade_in(bb1, t["b1"], 0.5)
    tl.fade_in(pn, t["note"], 0.5)
    tl.fade_in(bb2, t["b2"], 0.5)
    tl.fade_in(tg, t["b2"] + 0.2, 0.4)
    finish(s, n, tl=tl)
    return s


MODULES = [
    ("01", "Подойдёт ли мне Google Pay?", "три проверки", f"{A}/client.png",
     "Подойдёт ли Google Pay, решают три проверки", "«Мне подойдёт Google Pay?»"),
    ("02", "Помогите добавить карту", "пять шагов в Кошельке", f"{A}/hero.png",
     "Карта добавляется за пять шагов в Кошельке", "«Помогите добавить карту в телефон»"),
    ("03", "Оплата не прошла", "терминал молчит или отказал", f"{A}/client3_terminal.png",
     "Оплата не прошла — сначала поймите, что ответил терминал", "«Не прошла оплата телефоном»"),
    ("04", "После подключения", "чек и потерянный телефон", f"{A}/client4_worried.png",
     "Карта в телефоне живёт отдельно от пластика", "«В чеке не те цифры. А если потеряю телефон?»"),
]
GEOM = {0: (5.3, 1.2, 3.75, 5.4), 1: (9.45, 1.95, 2.95, 4.05), 2: (12.8, 2.5, 2.6, 3.6), 3: (16.5, 2.5, 2.6, 3.6),
        -1: (-4.2, 1.95, 2.95, 4.05), -2: (-7.5, 2.5, 2.6, 3.6), -3: (-10.5, 2.5, 2.6, 3.6)}


def divider(n, k):
    s = new_slide()
    chrome(s, f"{A}/bg_main.jpg")
    text_box(s, "!!divlbl", 0.6, 1.05, 4.5, 0.4, [[(f"Ситуация {k + 1} из 4", F_SEMI, 14, ACCENT)]])
    text_box(s, "!!divttl", 0.6, 1.6, 4.4, 3.0, [[(MODULES[k][4], F_MED, 30, INK)]])
    text_box(s, "!!divsub", 0.6, 4.75, 4.3, 1.0, [[(MODULES[k][5], F_HAND, 26, ACCENT)]], rot=-3)
    for i, (num, ttl, sub, img, _t, _s) in enumerate(MODULES):
        d = i - k
        x, y, w, h = GEOM[d]
        act = d == 0
        card(s, f"!!m{i}_card", x, y, w, h, shadow=(0.5, 0.08, 18 if act else 10))
        text_box(s, f"!!m{i}_num", x + 0.3, y + 0.25, 1.5, 0.7, [[(num, F_LIGHT, 40 if act else 30, ACCENT if act else LIGHT)]])
        text_box(s, f"!!m{i}_ttl", x + 0.3, y + (1.05 if act else 0.85), w - 0.6, 1.0, [[(ttl, F_SEMI, 20 if act else 15, INK if act else GREY)]])
        text_box(s, f"!!m{i}_sub", x + 0.3, y + (2.0 if act else 1.6), w - 0.6, 0.5, [[(sub, F_REG, 13 if act else 11, ACCENT if act else LIGHT)]])
        ih = h * (0.5 if act else 0.45)
        iw = ih * Image.open(img).width / Image.open(img).height
        p = picture(s, f"!!m{i}_img", img, x + w - iw - 0.25, y + h - ih - 0.15, h=ih)
        if not act:
            pic_alpha(p, 45)
    finish(s, n)


def phone_step(n, idx, scr, num, ttl, txt, z, taps, hand):
    s = new_slide()
    chrome(s, f"{A}/bg_main.jpg")
    text_box(s, "!!title", 0.6, 1.15, 6.6, 1.5, [[("Добавить карту —", F_MED, 40, INK), "BR", ("пять шагов в Кошельке", F_MED, 40, ACCENT)]])
    for d_i in range(5):
        state = "done" if (d_i < idx or idx == 5) else ("active" if d_i == idx else "todo")
        fill = {"done": LIME, "active": ACCENT, "todo": "E3E8E4"}[state]
        tcol = {"done": ACCENT, "active": "FFFFFF", "todo": GREY}[state]
        dot = rect(s, f"!!dot{d_i}", MSO_SHAPE.OVAL, 0.62 + d_i * 0.46, 2.82, 0.34, 0.34, fill=fill)
        shape_text(dot, [(str(d_i + 1), F_SEMI, 10.5, tcol)])
    text_box(s, "!!stepnum", 0.6, 3.3, 1.6, 1.1, [[(num, F_LIGHT, 60, ACCENT)]])
    text_box(s, "!!stepttl", 2.25, 3.42, 4.9, 1.0, [[(ttl, F_MED, 24, INK)]])
    text_box(s, "!!steptxt", 2.25, 4.35, 4.6, 1.8, [[(txt, F_REG, 15, INK)]])
    if z != 1.0:
        sx = 10.75 - 0.47 * SCR_W_IN * z
        sy = 3.0 - 0.419 * SCR_H_IN * z
    else:
        sx, sy = 8.79, 0.71
    phone(s, f"{SCR}/{scr}.png", sx, sy, z)
    tl = Timeline(s)
    markers = []
    for t_i, (rx, ry) in enumerate(taps):
        cx, cy = screen_point(sx, sy, z, rx, ry)
        markers.append(tap_marker(s, "!!tap" if t_i == 0 else f"tap{t_i}", cx, cy))
    if n == 13:
        offer = picture(s, "screen_offer", f"{SCR}/scr_offer.png", sx, sy, w=SCR_W_IN * z, h=SCR_H_IN * z)
        round_picture(offer, 5200)
        tl.fade_in(offer, 3.1, 0.6)
        tl.fade_out(markers[0], 3.0, 0.3)
    if hand:
        hx, hy, hd = hand[1]
        hn = text_box(s, "hand", hx, hy, 3.6, 0.7, [[(hand[0], F_HAND, 28, ACCENT)]], rot=-5)
        tl.fade_in(hn, hd, 0.5)
    if markers:
        tl.pulse(markers[0], 0.6 if n != 14 else 4.4)
    if n == 12 and len(markers) > 1:
        tl.fade_in(markers[1], 7.9, 0.4)
        tl.pulse(markers[1], 8.4)
    finish(s, n, tl=tl)


# =============== 1: cover ===============
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

# =============== 2: same / different ===============
s = new_slide()
chrome(s, f"{A}/bg_main.jpg")
title2(s, "Многое — как в Apple Pay,", "новое — в самом Android", size=38, y=1.0, h=1.7)
card(s, "c_left", 0.6, 3.0, 5.95, 3.55)
text_box(s, "c_left_h", 0.95, 3.3, 5.3, 0.5, [[("Так же, как в Apple Pay", F_SEMI, 18, INK)]])
L = [bullet_item(s, "l1", 0.95, 4.0, 5.3, "В телефоне — виртуальный номер карты, а не номер пластика"),
     bullet_item(s, "l2", 0.95, 4.8, 5.3, "При добавлении банк проверяет карту"),
     bullet_item(s, "l3", 0.95, 5.45, 5.3, "Удалить карту из телефона ≠ заблокировать её")]
rg = group(s, "c_right")
card(rg, "c_right_bg", 6.78, 3.0, 5.95, 3.55)
text_box(rg, "c_right_h", 7.13, 3.3, 5.3, 0.5, [[("Новое — на Android", F_SEMI, 18, ACCENT)]])
R = [bullet_item(s, "r1", 7.13, 4.0, 5.3, "Нужен NFC и сервисы Google — подходит не каждый телефон", mark="!", fill=ACCENT, mcol="FFFFFF"),
     bullet_item(s, "r2", 7.13, 4.8, 5.3, "Кошелёк — приложение для оплаты по умолчанию", mark="!", fill=ACCENT, mcol="FFFFFF"),
     bullet_item(s, "r3", 7.13, 5.45, 5.3, "Humo и Uzcard пока не подключаются", mark="!", fill=ACCENT, mcol="FFFFFF")]
tl = Timeline(s)
for g_, d in zip(L, (2.6, 6.6, 9.1)):
    tl.fade_in(g_, d, 0.5)
tl.fade_in(rg, 12.8, 0.5)
for g_, d in zip(R, (14.8, 17.2, 20.6)):
    tl.fade_in(g_, d, 0.5)
finish(s, 2, tl=tl)

# =============== 3: divider 1 ===============
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
LX, LW = 6.95, 5.85
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
        rect(s, f"!!it{i}_line", MSO_SHAPE.RECTANGLE, LX, y, LW, 0.022 if active else 0.012, fill=INK if active else LINE)
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
        rect(s, "!!card", MSO_SHAPE.ROUNDED_RECTANGLE, 6.2, 3.45, 0.9, 0.5, fill="FFFFFF", alpha=0, adj=0.04)
    finish(s, 4 + k)

# =============== 7-8: popups ===============
popup(7, f"{A}/client.png", 5.0, (8.75, 1.8), "Humo пока не добавить",
      "Google Pay сейчас принимает только Visa и Mastercard.",
      "Humo и Uzcard обещают подключить позже — даты пока нет.",
      "Что делать: ", "спросите, есть ли у клиента Visa или Mastercard Ипак Йули, — её и добавляем.",
      ["#проверка 1", "#карта"], "«Почему моя Humo не добавляется?»", "пока — нет!",
      dict(bubble=3.05, sub=6.6, b1=9.95, note=10.4, b2=14.25))
popup(8, f"{A}/client2_huawei.png", 5.0, (8.85, 1.8), "Кошелёк не скачался — нет сервисов Google",
      "Так бывает на многих новых Huawei.",
      "Без сервисов Google Кошелёк не установить — и Google Pay не подключить.",
      "Что делать: ", "проверьте, есть ли на телефоне Google Play. Нет — скажите клиенту, что на этом телефоне Google Pay не заработает.",
      ["#проверка 2", "#телефон"], "«Кошелёк не скачивается — что не так?»", "нет Google Play —\nнет Google Pay",
      dict(bubble=1.3, sub=5.7, b1=8.7, note=9.2, b2=13.1), note_xy=(4.35, 5.15))

# =============== 9: divider 2 ===============
divider(9, 1)

# =============== 10-15: walkthrough ===============
phone_step(10, 0, "scr_home", "01", "Нажмите «+»", "Откройте Кошелёк — кнопка «+» внизу экрана.", 1.0, [(0.604, 0.944)], None)
phone_step(11, 1, "scr_addlist", "02", "Выберите «Платежная карта»", "Первая строка в списке «Добавить в Кошелек».", 1.0, [(0.16, 0.268)], None)
phone_step(12, 2, "scr_payopts", "03", "Проще — из Ipak Yuli Mobile",
           "Кошелёк откроет приложение банка. Нет приложения — «Новая кредитная или дебетовая карта»: данные вводит сам клиент.", 1.4,
           [(0.135, 0.419), (0.115, 0.858)], ("через приложение банка", (3.3, 5.95, 3.0)))
phone_step(13, 3, "scr_confirm", "04", "Подтвердите и примите оферту",
           "«Добавить в Кошелек» — Кошелёк проверит карту и покажет публичную оферту банка. Клиент читает и принимает.", 1.0,
           [(0.82, 0.855)], None)
phone_step(14, 4, "scr_default", "05", "Нажмите «Сделать основной»",
           "Это третья проверка — настройки: Кошелёк станет приложением для оплаты по умолчанию.", 1.0, [(0.82, 0.855)], None)
phone_step(15, 5, "scr_done", "✓", "Готово", "Бесконтактная оплата настроена. В магазине клиент подносит телефон к терминалу.", 1.0, [],
           ("можно платить!", (4.4, 5.6, 1.2)))

# =============== 16: rules (draft, IS approval) ===============
s = new_slide()
chrome(s, f"{A}/bg_main.jpg")
title2(s, "Помогаете — но данные карты", "вводит только клиент", size=38, y=1.0, h=1.7)
RULES = ["Номер карты и CVV клиент вводит сам", "Код из SMS клиент никому не называет — даже вам", "Карту клиента — только на телефон клиента"]
G = []
for i, rtxt in enumerate(RULES):
    x = 0.6 + i * 4.19
    g = group(s, f"rule{i}")
    card(g, f"rule{i}_bg", x, 3.05, 3.95, 2.9)
    text_box(g, f"rule{i}_n", x + 0.35, 3.25, 1.0, 0.9, [[(str(i + 1), F_LIGHT, 44, ACCENT)]])
    text_box(g, f"rule{i}_t", x + 0.35, 4.25, 3.3, 1.5, [[(rtxt, F_MED, 18, INK)]])
    G.append(g)
draft = rect(s, "draft", MSO_SHAPE.ROUNDED_RECTANGLE, 9.35, 6.3, 3.35, 0.36, fill="FFFFFF", line="B3261E", line_w=1, adj=0.5)
shape_text(draft, [("Черновик: согласовать с ИБ", F_REG, 10.5, "B3261E")])
tl = Timeline(s)
for g_, d in zip(G, (3.3, 6.4, 10.0)):
    tl.fade_in(g_, d, 0.5)
finish(s, 16, tl=tl)

# =============== 17: divider 3 ===============
divider(17, 2)

# =============== 18: silent vs declined ===============
s = new_slide()
chrome(s, f"{A}/bg_main.jpg")
title2(s, "Терминал молчит — дело в телефоне,", "отказал — дело в карте", size=36, y=1.0, h=1.6)
lg = group(s, "col_l")
card(lg, "col_l_bg", 0.6, 2.95, 5.95, 3.35)
text_box(lg, "col_l_h", 0.95, 3.2, 5.3, 0.5, [[("Терминал молчит", F_SEMI, 20, INK), ("  → телефон", F_MED, 16, ACCENT)]])
li = group(s, "col_l_items")
bullet_item(li, "li1", 0.95, 3.95, 5.3, "Телефон разблокирован")
bullet_item(li, "li2", 0.95, 4.6, 5.3, "Поднесли задней стороной на пару секунд")
bullet_item(li, "li3", 0.95, 5.25, 5.3, "NFC включён, Кошелёк — по умолчанию")
rg = group(s, "col_r")
card(rg, "col_r_bg", 6.78, 2.95, 5.95, 3.35)
text_box(rg, "col_r_h", 7.13, 3.2, 5.3, 0.5, [[("Терминал отказал", F_SEMI, 20, INK), ("  → карта", F_MED, 16, ACCENT)]])
ri = group(s, "col_r_items")
bullet_item(ri, "ri1", 7.13, 3.95, 5.3, "Проверьте карту, как при отказе по пластику")
bullet_item(ri, "ri2", 7.13, 4.75, 5.3, "Баланс, лимиты и статус карты — по обычной процедуре банка")
bn = text_box(s, "bottom", 0.62, 6.5, 9.0, 0.4, [[("Терминал не принимает бесконтактную оплату? Поможет другой терминал.", F_REG, 13, GREY)]])
rect(s, "!!card", MSO_SHAPE.ROUNDED_RECTANGLE, 6.2, 3.45, 0.9, 0.5, fill="FFFFFF", alpha=0, adj=0.04)
tl = Timeline(s)
tl.fade_in(lg, 2.1, 0.5)
tl.fade_in(li, 5.9, 0.5)
tl.fade_in(rg, 13.5, 0.5)
tl.fade_in(ri, 17.0, 0.5)
tl.fade_in(bn, 20.3, 0.5)
finish(s, 18, tl=tl)

# =============== 19: popup terminal ===============
popup(19, f"{A}/client3_terminal.png", 4.9, (8.35, 1.85), "Терминал молчит — начните с телефона",
      "Разблокирован ли телефон? Включён ли NFC? Кошелёк — по умолчанию?",
      "Откройте настройки вместе с клиенткой: NFC включён, Кошелёк выбран для оплаты по умолчанию.",
      "Что сказать: ", "«Перед оплатой разблокируйте телефон и поднесите его задней стороной к терминалу».",
      ["#оплата", "#телефон"], "«Подношу телефон — ничего не происходит»", "сначала телефон!",
      dict(bubble=1.7, sub=4.6, b1=8.1, note=8.5, b2=14.9))

# =============== 20: divider 4 ===============
divider(20, 3)

# =============== 21: virtual number ===============
s = new_slide()
chrome(s, f"{A}/bg_main.jpg")
title2(s, "В чеке — виртуальный номер карты,", "поэтому цифры другие", size=36, y=1.0, h=1.6)


def bank_card(container, name, x, y, fill, digits, label, sub):
    g = group(container, name)
    text_box(g, f"{name}_lbl", x, y - 0.55, 4.2, 0.45, [[(label, F_SEMI, 16, INK)]])
    c = rect(g, f"{name}_c", MSO_SHAPE.ROUNDED_RECTANGLE, x, y, 3.9, 2.45, fill=fill, adj=0.08, shadow=(0.4, 0.08, 20))
    picture(g, f"{name}_logo", f"{A}/logo_white.png", x + 0.3, y + 0.28, h=0.45)
    text_box(g, f"{name}_d", x + 0.3, y + 1.75, 3.2, 0.5, [[(digits, F_MED, 20, "FFFFFF")]])
    text_box(g, f"{name}_s", x, y + 2.6, 4.4, 0.5, [[(sub, F_REG, 12.5, GREY)]])
    return g


bank_card(s, "plastic", 1.6, 3.35, ACCENT, "•• 4417", "Пластиковая карта", "пример цифр")
eq = text_box(s, "neq", 6.0, 3.85, 1.2, 1.2, [[{"align": PP_ALIGN.CENTER}, ("≠", F_LIGHT, 66, ACCENT)]])
ph = bank_card(s, "token", 7.65, 3.35, "8CC63F", "•• 8253", "Карта в телефоне", "виртуальный номер — свой у каждого телефона")
bt = text_box(s, "bottom", 0.62, 6.45, 11.5, 0.45, [[("Последние цифры в чеке — от виртуального номера, а не от пластика. Это нормально.", F_REG, 14, INK)]])
tl = Timeline(s)
tl.fade_in(ph, 4.8, 0.6)
tl.fade_in(eq, 9.4, 0.5)
tl.fade_in(bt, 9.8, 0.5)
finish(s, 21, tl=tl)

# =============== 22: lost phone ===============
s = new_slide()
chrome(s, f"{A}/bg_main.jpg")
title2(s, "Потерян телефон — блокируем", "через «Найти устройство»", size=36, y=1.0, h=1.6)
STEPS3 = [("Откройте «Найти устройство» с другого телефона или компьютера", "google.com/android/find"),
          ("Заблокируйте телефон или сотрите данные — карты удалятся вместе с ними", ""),
          ("Пластиковая карта продолжает работать", "")]
G = []
for i, (t1, t2) in enumerate(STEPS3):
    x = 0.6 + i * 4.19
    g = group(s, f"lp{i}")
    card(g, f"lp{i}_bg", x, 2.95, 3.95, 3.1)
    text_box(g, f"lp{i}_n", x + 0.35, 3.15, 1.0, 0.9, [[(str(i + 1), F_LIGHT, 44, ACCENT)]])
    text_box(g, f"lp{i}_t", x + 0.35, 4.1, 3.3, 1.3, [[(t1, F_MED, 17, INK)]])
    if t2:
        text_box(g, f"lp{i}_u", x + 0.35, 5.45, 3.3, 0.4, [[(t2, F_REG, 12.5, ACCENT)]])
    G.append(g)
rect(s, "!!card", MSO_SHAPE.ROUNDED_RECTANGLE, 6.2, 3.45, 0.9, 0.5, fill="FFFFFF", alpha=0, adj=0.04)
tl = Timeline(s)
for g_, d in zip(G, (0.3, 4.6, 12.9)):
    tl.fade_in(g_, d, 0.5)
finish(s, 22, tl=tl)

# =============== 23: popup deleted card ===============
popup(23, f"{A}/client4_worried.png", 5.0, (9.0, 1.8), "Удалили из Кошелька — пластик работает",
      "Удаление карты из телефона не блокирует карту.",
      "Пластиковой картой можно пользоваться как раньше.",
      "Что сказать: ", "«Захотите снова платить телефоном — просто добавьте карту заново».",
      ["#после подключения"], "«Я удалила карту из Кошелька — она заблокирована?»", "удалить ≠ заблокировать",
      dict(bubble=1.5, sub=5.4, b1=6.3, note=6.6, b2=11.4))

# =============== 24: final cheat sheet ===============
s = new_slide()
chrome(s, f"{A}/bg_main.jpg")
title2(s, "Сначала три проверки,", "потом пять шагов", size=40, y=1.0, h=1.7)
CH = [("Карта", 5.6), ("Телефон", 6.3), ("Настройки", 7.0), ("5 шагов в Кошельке", 8.7)]
tl = Timeline(s)
x = 0.6
for i, (txt, d) in enumerate(CH):
    w = 0.5 + 0.13 * len(txt)
    g = group(s, f"chip{i}")
    c = rect(g, f"chip{i}_bg", MSO_SHAPE.ROUNDED_RECTANGLE, x, 3.0, w, 0.62, fill=ACCENT if i == 3 else "FFFFFF",
             line=None if i == 3 else ACCENT, line_w=1.25, adj=0.5)
    shape_text(c, [(txt, F_SEMI, 15, "FFFFFF" if i == 3 else ACCENT)])
    if i < 3:
        text_box(g, f"chip{i}_ar", x + w + 0.12, 3.02, 0.4, 0.55, [[("→", F_MED, 20, GREY)]])
    tl.fade_in(g, d, 0.4)
    x += w + 0.62
LINES3 = [("Терминал молчит — дело в телефоне", 10.2), ("Терминал отказал — дело в карте", 12.7), ("Телефон потерян — «Найти устройство»", 14.5)]
for i, (txt, d) in enumerate(LINES3):
    g = bullet_item(s, f"fl{i}", 0.6, 4.15 + i * 0.68, 8.5, txt, mark=str(i + 1), fill=MINT, size=17)
    tl.fade_in(g, d, 0.4)
hn = text_box(s, "hand", 8.2, 5.6, 4.9, 0.8, [[("сфотографируйте этот экран!", F_HAND, 28, ACCENT)]], rot=-5)
tl.fade_in(hn, 17.7, 0.5)
finish(s, 24, tl=tl)

# =============== 25: test intro ===============
s = new_slide()
chrome(s, f"{A}/bg_cover.jpg")
text_box(s, "!!title", 0.6, 1.75, 8.0, 2.3, [[("Проверьте себя:", F_MED, 50, INK), "BR", ("шесть ситуаций", F_MED, 50, ACCENT), "BR", ("из офиса", F_MED, 50, ACCENT)]])
text_box(s, "!!sub", 0.62, 4.75, 5.6, 0.8, [[("Выберите, что вы сделаете в каждой ситуации.", F_REG, 16, INK)]])
b = rect(s, "btn", MSO_SHAPE.ROUNDED_RECTANGLE, 0.62, 5.6, 2.4, 0.6, fill=ACCENT, adj=0.5)
shape_text(b, [("Начать тест", F_SEMI, 15, "FFFFFF")])
picture(s, "!!hero", f"{A}/hero.png", 9.05, 0.45, h=7.05)
finish(s, 25)

# =============== 26: end ===============
s = new_slide()
chrome(s, f"{A}/bg_cover.jpg")
text_box(s, "!!title", 0.6, 1.75, 8.0, 1.3, [[("Курс завершён", F_MED, 54, INK)]])
text_box(s, "!!sub", 0.62, 3.2, 5.8, 1.2, [[("На следующем приёме начните с трёх проверок: ", F_REG, 18, INK), ("карта, телефон, настройки.", F_SEMI, 18, ACCENT)]])
b = rect(s, "btn", MSO_SHAPE.ROUNDED_RECTANGLE, 0.62, 4.6, 2.2, 0.6, fill=ACCENT, adj=0.5)
shape_text(b, [("Завершить", F_SEMI, 15, "FFFFFF")])
picture(s, "!!hero", f"{A}/hero.png", 9.05, 0.45, h=7.05)
finish(s, 26)

prs.save(OUT)
print("saved", OUT, "slides:", len(prs.slides))
