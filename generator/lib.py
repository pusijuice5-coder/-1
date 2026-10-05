# -*- coding: utf-8 -*-
"""Mini slide builder that writes raw PresentationML into an unpacked deck,
reusing the media and style of Agile_kurs_1.pptx."""
import os, re
from xml.sax.saxutils import escape
from PIL import ImageFont

EMU = 914400
SW, SH = 13.333, 7.5

# ---- palette (taken from the user's slides) ----
DARK = "0F2F1D"      # main dark green
G1 = "0A6A1F"        # deep green
G2 = "2E8B3E"        # accent green
G3 = "4E9F5A"
G4 = "6FB47A"
G5 = "86AB88"
LIME = "4CEA4C"      # logo green
TITLE = "173F35"
BODY = "2F3E39"
MUTED = "5C6F66"
WHITE = "FFFFFF"
MINT = "E6F2E8"      # light tint for chips
GREY = "D9E2DC"
FONT = "Tahoma"

# ---- media already present in the deck ----
IMG = {
    "logo_white": "image1.png", "logo": "image3.png", "shader": "image2.png",
    "glass": "image5.png", "team": "image7.png", "office": "image8.png",
    "present": "image4.png", "wave": "image6.png", "chest": "image10.png",
    "stand": "image11.png", "flag": "image9.png",
}
# alpha bounding boxes (fractions l,t,r,b) of the character art, with a small margin
CROP = {
    "present": (0.285, 0.035, 0.298, 0.0),
    "wave": (0.281, 0.039, 0.280, 0.0),
    "chest": (0.301, 0.039, 0.276, 0.0),
    "stand": (0.328, 0.039, 0.306, 0.0),
    "flag": (0.228, 0.091, 0.227, 0.0),
}
IMG_PX = {k: (2048, 1152) for k in CROP}

_fonts = {}
def _font(sz, bold):
    key = (sz, bold)
    if key not in _fonts:
        fn = "/usr/share/wine/fonts/tahomabd.ttf" if bold else "/usr/share/wine/fonts/tahoma.ttf"
        _fonts[key] = ImageFont.truetype(fn, int(sz * 10))  # 10x for precision; units = pt*10
    return _fonts[key]

def e(v):
    return int(round(v * EMU))

WARN = []
SHRUNK = []

# ---------------------------------------------------------------- text model
TR = {}          # source paragraph -> translation (empty = original language)
SEEN = []        # every source string that went through T(), in order
LANG = "ru-RU"


def T(s):
    """Translate one paragraph-level string (exact match), remembering what was asked for."""
    if s and re.search("[А-Яа-яЁё]", s) and s not in SEEN:
        SEEN.append(s)
    return TR.get(s, s)


def parse_runs(s):
    """'**bold** normal' -> [(text, bold)]"""
    s = T(s)
    out = []
    for i, part in enumerate(re.split(r"\*\*", s)):
        if part:
            out.append((part, i % 2 == 1))
    return out

def text_height(paras, w_in, sz, bold=False, lnsp=1.0, spc_after=0, inset=(0, 0)):
    """Estimate rendered height (inches) of paragraphs in a box of width w_in."""
    avail = (w_in - inset[0]) * 72 * 10  # in font units (pt*10)
    total = 0.0
    for p in paras:
        psz = p.get("sz", sz)
        runs = p["runs"]
        words = []
        for t, b in runs:
            for wd in re.split(r"(\s+)", t):
                if wd:
                    words.append((wd, b or p.get("b", bold), psz))
        lines, cur = 1, 0.0
        indent = p.get("marL", 0) * 72 * 10
        for wd, b, s in words:
            f = _font(s, b)
            wl = f.getlength(wd) * (1.0 if not wd.isspace() else 1.0)
            if cur + wl > avail - indent and not wd.isspace() and cur > 0:
                lines += 1
                cur = wl
            else:
                cur += wl
        line_h = psz * 1.2 * p.get("lnsp", lnsp) / 72.0
        total += lines * line_h + p.get("spcAft", spc_after) / 72.0 + p.get("spcBef", 0) / 72.0
    return total + inset[1]

# ---------------------------------------------------------------- slide
class Slide:
    def __init__(self, deck, bg="light", notes="", transition="fade"):
        self.deck = deck
        self.items = []          # xml strings at top level
        self.stack = []          # group stack
        self.rels = {}           # target -> (rId, type)
        self.nid = 2
        self.anims = []          # (spid, kind, delay)
        self.notes = notes
        self.transition = transition
        self.bg = bg
        self.video_id = None
        self._rel("../slideLayouts/slideLayout15.xml", "slideLayout")
        if bg == "video":
            self._video_bg()
        elif bg == "dark":
            self.rect(0, 0, SW, SH, fill=DARK, name="Фон")
        elif bg == "glass":
            self.pic("glass", 0, 0, SW, SH, name="Фон офис")
        elif bg == "white":
            self.rect(0, 0, SW, SH, fill="F7FAF8", name="Фон")

    # -- relationships
    def _rel(self, target, kind):
        if target in self.rels:
            return self.rels[target][0]
        rid = "rId%d" % (len(self.rels) + 1)
        types = {
            "slideLayout": "http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout",
            "image": "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image",
            "video": "http://schemas.openxmlformats.org/officeDocument/2006/relationships/video",
            "media": "http://schemas.microsoft.com/office/2007/relationships/media",
            "notesSlide": "http://schemas.openxmlformats.org/officeDocument/2006/relationships/notesSlide",
        }
        self.rels[target + "#" + kind if kind in ("video", "media") else target] = (rid, types[kind])
        return rid

    def _id(self):
        i = self.nid
        self.nid += 1
        return i

    def _add(self, xml, bbox):
        if self.stack:
            self.stack[-1]["items"].append((xml, bbox))
        else:
            self.items.append(xml)

    # -- groups
    def begin(self, name="Группа"):
        gid = self._id()
        self.stack.append({"id": gid, "name": name, "items": []})
        return gid

    def end(self, anim=None):
        g = self.stack.pop()
        if not g["items"]:
            return g["id"]
        xs = [b[0] for _, b in g["items"]]; ys = [b[1] for _, b in g["items"]]
        x2 = [b[0] + b[2] for _, b in g["items"]]; y2 = [b[1] + b[3] for _, b in g["items"]]
        x, y, w, h = min(xs), min(ys), max(x2) - min(xs), max(y2) - min(ys)
        off = '<a:off x="%d" y="%d"/><a:ext cx="%d" cy="%d"/><a:chOff x="%d" y="%d"/><a:chExt cx="%d" cy="%d"/>' % (
            e(x), e(y), e(w), e(h), e(x), e(y), e(w), e(h))
        xml = ('<p:grpSp><p:nvGrpSpPr><p:cNvPr id="%d" name="%s"/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>'
               '<p:grpSpPr><a:xfrm>%s</a:xfrm></p:grpSpPr>%s</p:grpSp>') % (
            g["id"], escape(g["name"]), off, "".join(i for i, _ in g["items"]))
        self._add(xml, (x, y, w, h))
        if anim is not None:
            self.anims.append((g["id"], "grp", anim))
        return g["id"]

    # -- primitives
    def _fill(self, fill, alpha=None, grad=None):
        if grad == "button":
            return ('<a:gradFill flip="none" rotWithShape="1"><a:gsLst>'
                    '<a:gs pos="0"><a:schemeClr val="bg1"><a:shade val="30000"/><a:satMod val="115000"/></a:schemeClr></a:gs>'
                    '<a:gs pos="50000"><a:schemeClr val="bg1"><a:shade val="67500"/><a:satMod val="115000"/></a:schemeClr></a:gs>'
                    '<a:gs pos="100000"><a:schemeClr val="bg1"><a:shade val="100000"/><a:satMod val="115000"/></a:schemeClr></a:gs>'
                    '</a:gsLst><a:lin ang="0" scaled="1"/><a:tileRect/></a:gradFill>')
        if grad:
            c1, c2, ang = grad
            return ('<a:gradFill rotWithShape="1"><a:gsLst><a:gs pos="0"><a:srgbClr val="%s"/></a:gs>'
                    '<a:gs pos="100000"><a:srgbClr val="%s"/></a:gs></a:gsLst><a:lin ang="%d" scaled="0"/></a:gradFill>') % (c1, c2, ang * 60000)
        if fill is None:
            return "<a:noFill/>"
        a = '<a:alpha val="%d"/>' % int(alpha * 1000) if alpha is not None else ""
        return '<a:solidFill><a:srgbClr val="%s">%s</a:srgbClr></a:solidFill>' % (fill, a)

    def _line(self, line, lw=1.0, dash=None):
        if not line:
            return "<a:ln><a:noFill/></a:ln>"
        d = '<a:prstDash val="%s"/>' % dash if dash else ""
        return '<a:ln w="%d"><a:solidFill><a:srgbClr val="%s"/></a:solidFill>%s</a:ln>' % (int(lw * 12700), line, d)

    def _shadow(self, shadow):
        if not shadow:
            return ""
        if shadow == "soft":
            return ('<a:effectLst><a:outerShdw blurRad="304800" dist="76200" dir="5400000" algn="t" rotWithShape="0">'
                    '<a:srgbClr val="0F2F1D"><a:alpha val="16000"/></a:srgbClr></a:outerShdw></a:effectLst>')
        if shadow == "pill":   # same family as the user's white pills (slide 6)
            return ('<a:effectLst><a:outerShdw blurRad="508000" dist="254000" dir="8100000" sx="95000" sy="95000" algn="tr" rotWithShape="0">'
                    '<a:prstClr val="black"><a:alpha val="12000"/></a:prstClr></a:outerShdw></a:effectLst>')
        if shadow == "green":  # user's dark card glow (slide 4)
            return ('<a:effectLst><a:outerShdw blurRad="381000" dist="101600" dir="5400000" algn="t" rotWithShape="0">'
                    '<a:srgbClr val="0F2F1D"><a:alpha val="30000"/></a:srgbClr></a:outerShdw></a:effectLst>')
        return ""

    def _paras(self, text, sz, color, bold, align, lnsp, spc_after, bullet, font):
        """text: str (\n = new paragraph) or list of dict paragraphs."""
        if isinstance(text, str):
            paras = [{"runs": parse_runs(t)} for t in text.split("\n")]
        else:
            paras = []
            for p in text:
                if isinstance(p, str):
                    paras.append({"runs": parse_runs(p)})
                else:
                    q = dict(p); q["runs"] = parse_runs(p["t"]); paras.append(q)
        out = []
        for p in paras:
            psz = p.get("sz", sz); pcol = p.get("color", color); pb = p.get("b", bold)
            palign = p.get("align", align); pl = p.get("lnsp", lnsp)
            pa = p.get("spcAft", spc_after); pbul = p.get("bullet", bullet)
            ppr = '<a:pPr algn="%s"%s>' % (palign, ' marL="%d" indent="%d"' % (e(0.22), -e(0.22)) if pbul else "")
            ppr += '<a:lnSpc><a:spcPct val="%d"/></a:lnSpc>' % int(pl * 100000)
            if p.get("spcBef"):
                ppr += '<a:spcBef><a:spcPts val="%d"/></a:spcBef>' % int(p["spcBef"] * 100)
            ppr += '<a:spcAft><a:spcPts val="%d"/></a:spcAft>' % int(pa * 100)
            if pbul:
                bc = pbul if isinstance(pbul, str) and len(pbul) == 6 else G2
                ppr += '<a:buClr><a:srgbClr val="%s"/></a:buClr><a:buSzPct val="110000"/><a:buFont typeface="Arial"/><a:buChar char="&#8226;"/>' % bc
            else:
                ppr += "<a:buNone/>"
            ppr += "</a:pPr>"
            runs = ""
            for t, b in p["runs"]:
                rb = b or pb
                rcol = p.get("bcolor", pcol) if b else pcol
                it = ' i="1"' if p.get("i") else ""
                f = p.get("font", font)
                runs += ('<a:r><a:rPr lang="%s" sz="%d" b="%d"%s dirty="0"><a:solidFill><a:srgbClr val="%s"/></a:solidFill>'
                         '<a:latin typeface="%s"/><a:cs typeface="%s"/></a:rPr><a:t>%s</a:t></a:r>') % (
                    LANG, int(psz * 100), 1 if rb else 0, it, rcol, f, f, escape(t))
            end = '<a:endParaRPr lang="%s" sz="%d" dirty="0"><a:latin typeface="%s"/></a:endParaRPr>' % (LANG, int(psz * 100), font)
            out.append("<a:p>%s%s%s</a:p>" % (ppr, runs, end))
        return "".join(out), paras

    def shape(self, x, y, w, h, geom="rect", fill=None, alpha=None, grad=None, line=None, lw=1.0, dash=None,
              radius=None, shadow=None, text=None, sz=14, color=BODY, bold=False, align="l", anchor="t",
              inset=(0.1, 0.05, 0.1, 0.05), lnsp=1.0, spc_after=0, bullet=False, font=FONT, name=None,
              anim=None, adj=None, rot=0, flipH=False, flipV=False, check=True, txbox=False):
        sid = self._id()
        name = name or ("TextBox %d" % sid if txbox else "Shape %d" % sid)
        av = ""
        if radius is not None and geom == "roundRect":
            av = '<a:gd name="adj" fmla="val %d"/>' % min(50000, int(radius * 100000 / min(w, h)))
        if adj:
            av += "".join('<a:gd name="%s" fmla="val %d"/>' % (k, v) for k, v in adj.items())
        attrs = (' rot="%d"' % int(rot * 60000) if rot else "") + (' flipH="1"' if flipH else "") + (' flipV="1"' if flipV else "")
        sppr = '<p:spPr><a:xfrm%s><a:off x="%d" y="%d"/><a:ext cx="%d" cy="%d"/></a:xfrm><a:prstGeom prst="%s"><a:avLst>%s</a:avLst></a:prstGeom>%s%s%s</p:spPr>' % (
            attrs, e(x), e(y), e(w), e(h), geom, av, self._fill(fill, alpha, grad), self._line(line, lw, dash), self._shadow(shadow))
        body = ""
        has_text = False
        if text is not None and text != "":
            has_text = True
            pxml, paras = self._paras(text, sz, color, bold, align, lnsp, spc_after, bullet, font)
            l, t, r, b = inset
            body = ('<p:txBody><a:bodyPr wrap="square" lIns="%d" tIns="%d" rIns="%d" bIns="%d" anchor="%s" rtlCol="0"><a:noAutofit/></a:bodyPr><a:lstStyle/>%s</p:txBody>') % (
                e(l), e(t), e(r), e(b), anchor, pxml)
            if check:
                need = text_height(paras, w, sz, bold, lnsp, spc_after, (l + r, t + b))
                sz0 = sz
                while need > h + 0.02 and sz > sz0 * 0.8:
                    sz -= 0.5
                    pxml, paras = self._paras(text, sz, color, bold, align, lnsp, spc_after, bullet, font)
                    need = text_height(paras, w, sz, bold, lnsp, spc_after, (l + r, t + b))
                if sz != sz0:
                    SHRUNK.append("slide %s: %.1f -> %.1f pt: %s" % (self.deck.cur_no, sz0, sz, str(text)[:50]))
                    body = ('<p:txBody><a:bodyPr wrap="square" lIns="%d" tIns="%d" rIns="%d" bIns="%d" anchor="%s" rtlCol="0"><a:noAutofit/></a:bodyPr><a:lstStyle/>%s</p:txBody>') % (
                        e(l), e(t), e(r), e(b), anchor, pxml)
                if need > h + 0.02:
                    WARN.append("slide %s: text overflow %.2f > %.2f in: %s" % (self.deck.cur_no, need, h, str(text)[:60]))
        else:
            body = '<p:txBody><a:bodyPr rtlCol="0" anchor="ctr"/><a:lstStyle/><a:p><a:endParaRPr lang="ru-RU" dirty="0"/></a:p></p:txBody>'
        cnv = '<p:cNvSpPr txBox="1"/>' if txbox else "<p:cNvSpPr/>"
        xml = '<p:sp><p:nvSpPr><p:cNvPr id="%d" name="%s"/>%s<p:nvPr/></p:nvSpPr>%s%s</p:sp>' % (sid, escape(name), cnv, sppr, body)
        self._add(xml, (x, y, w, h))
        if anim is not None:
            self.anims.append((sid, "sp" if has_text else "spbg", anim))
        return sid

    def rect(self, x, y, w, h, **k):
        return self.shape(x, y, w, h, geom="rect", **k)

    def rrect(self, x, y, w, h, r=0.18, **k):
        return self.shape(x, y, w, h, geom="roundRect", radius=r, **k)

    def text(self, x, y, w, h, text, **k):
        k.setdefault("inset", (0, 0, 0, 0))
        return self.shape(x, y, w, h, geom="rect", text=text, txbox=True, **k)

    def line(self, x1, y1, x2, y2, color=G2, lw=1.5, head=None, tail=None, dash=None, anim=None):
        sid = self._id()
        x, y = min(x1, x2), min(y1, y2)
        w, h = abs(x2 - x1), abs(y2 - y1)
        fl = (' flipH="1"' if x2 < x1 else "") + (' flipV="1"' if y2 < y1 else "")
        he = '<a:headEnd type="%s" w="med" len="med"/>' % head if head else ""
        te = '<a:tailEnd type="%s" w="med" len="med"/>' % tail if tail else ""
        d = '<a:prstDash val="%s"/>' % dash if dash else ""
        xml = ('<p:cxnSp><p:nvCxnSpPr><p:cNvPr id="%d" name="Connector %d"/><p:cNvCxnSpPr/><p:nvPr/></p:nvCxnSpPr>'
               '<p:spPr><a:xfrm%s><a:off x="%d" y="%d"/><a:ext cx="%d" cy="%d"/></a:xfrm><a:prstGeom prst="line"><a:avLst/></a:prstGeom>'
               '<a:ln w="%d" cap="rnd"><a:solidFill><a:srgbClr val="%s"/></a:solidFill>%s<a:round/>%s%s</a:ln></p:spPr></p:cxnSp>') % (
            sid, sid, fl, e(x), e(y), e(w), e(h), int(lw * 12700), color, d, he, te)
        self._add(xml, (x, y, max(w, 0.01), max(h, 0.01)))
        return sid

    def freeform(self, pts, x, y, w, h, color=G2, lw=3, fill=None, alpha=None, closed=False, name="Кривая"):
        """pts: list of (fx, fy) in 0..1 of the box."""
        sid = self._id()
        W, H = e(w), e(h)
        path = '<a:moveTo><a:pt x="%d" y="%d"/></a:moveTo>' % (int(pts[0][0] * W), int(pts[0][1] * H))
        for px, py in pts[1:]:
            path += '<a:lnTo><a:pt x="%d" y="%d"/></a:lnTo>' % (int(px * W), int(py * H))
        if closed:
            path += "<a:close/>"
        ln = '<a:ln w="%d" cap="rnd"><a:solidFill><a:srgbClr val="%s"/></a:solidFill><a:round/></a:ln>' % (int(lw * 12700), color) if color else "<a:ln><a:noFill/></a:ln>"
        xml = ('<p:sp><p:nvSpPr><p:cNvPr id="%d" name="%s"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x="%d" y="%d"/><a:ext cx="%d" cy="%d"/></a:xfrm>'
               '<a:custGeom><a:avLst/><a:gdLst/><a:ahLst/><a:cxnLst/><a:rect l="0" t="0" r="r" b="b"/><a:pathLst><a:path w="%d" h="%d">%s</a:path></a:pathLst></a:custGeom>%s%s</p:spPr>'
               '<p:txBody><a:bodyPr rtlCol="0" anchor="ctr"/><a:lstStyle/><a:p><a:endParaRPr lang="ru-RU" dirty="0"/></a:p></p:txBody></p:sp>') % (
            sid, escape(name), e(x), e(y), W, H, W, H, path, self._fill(fill, alpha), ln)
        self._add(xml, (x, y, w, h))
        return sid

    def pic(self, key, x, y, w=None, h=None, crop=None, name=None, anim=None, geom="rect", radius=None):
        fn = IMG[key]
        rid = self._rel("../media/" + fn, "image")
        sid = self._id()
        if crop is None and key in CROP and (w is None or h is None):
            crop = CROP[key]
        if crop is not None:
            l, t, r, b = crop
            pw, ph = IMG_PX.get(key, (2048, 1152))
            asp = (1 - l - r) * pw / ((1 - t - b) * ph)
            if w is None:
                w = h * asp
            if h is None:
                h = w / asp
        src = '<a:srcRect l="%d" t="%d" r="%d" b="%d"/>' % tuple(int(v * 100000) for v in crop) if crop else ""
        av = ""
        if geom == "roundRect" and radius:
            av = '<a:gd name="adj" fmla="val %d"/>' % min(50000, int(radius * 100000 / min(w, h)))
        xml = ('<p:pic><p:nvPicPr><p:cNvPr id="%d" name="%s"/><p:cNvPicPr><a:picLocks noChangeAspect="1"/></p:cNvPicPr><p:nvPr/></p:nvPicPr>'
               '<p:blipFill><a:blip r:embed="%s"/>%s<a:stretch><a:fillRect/></a:stretch></p:blipFill>'
               '<p:spPr><a:xfrm><a:off x="%d" y="%d"/><a:ext cx="%d" cy="%d"/></a:xfrm><a:prstGeom prst="%s"><a:avLst>%s</a:avLst></a:prstGeom></p:spPr></p:pic>') % (
            sid, escape(name or ("Рисунок %d" % sid)), rid, src, e(x), e(y), e(w), e(h), geom, av)
        self._add(xml, (x, y, w, h))
        if anim is not None:
            self.anims.append((sid, "pic", anim))
        return sid, w, h

    def ezoza(self, pose, right=None, x=None, h=7.1, bottom=SH, anim=None):
        """Place the presenter character; bottom-aligned (cut at slide bottom like in the user's slides)."""
        l, t, r, b = CROP[pose]
        asp = (1 - l - r) * 2048 / ((1 - t - b) * 1152)
        w = h * asp
        if x is None:
            x = (right if right is not None else SW) - w
        return self.pic(pose, x, bottom - h, w, h, name="Эзоза", anim=anim)

    def logo(self, dark_bg=False, x=0.46, y=0.33, w=1.55):
        return self.pic("logo_white" if dark_bg else "logo", x, y, w, w * 645 / 2214, crop=(0, 0, 0, 0), name="Логотип")

    def _video_bg(self):
        sid = self._id()
        self.video_id = sid
        r_media = self._rel("../media/media1.mp4", "media")
        r_video = self._rel("../media/media1.mp4", "video")
        r_img = self._rel("../media/image2.png", "image")
        xml = ('<p:pic><p:nvPicPr><p:cNvPr id="%d" name="720_compress_agile_green_shader_bg"><a:hlinkClick r:id="" action="ppaction://media"/></p:cNvPr>'
               '<p:cNvPicPr><a:picLocks noChangeAspect="1"/></p:cNvPicPr><p:nvPr><a:videoFile r:link="%s"/><p:extLst><p:ext uri="{DAA4B4D4-6D71-4841-9C94-3DE7FCFB9230}">'
               '<p14:media xmlns:p14="http://schemas.microsoft.com/office/powerpoint/2010/main" r:embed="%s"/></p:ext></p:extLst></p:nvPr></p:nvPicPr>'
               '<p:blipFill><a:blip r:embed="%s"/><a:stretch><a:fillRect/></a:stretch></p:blipFill>'
               '<p:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="12192000" cy="6858000"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr></p:pic>') % (
            sid, r_video, r_media, r_img)
        self.items.append(xml)

    # -- composite helpers used across the course
    def title(self, t, y=0.42, color=TITLE, sz=32, x=0.55, w=12.2, h=0.72, anim=0):
        return self.text(x, y, w, h, t, sz=sz, bold=True, color=color, anchor="t", anim=anim)

    def subtitle(self, t, y=1.12, color=BODY, sz=15, x=0.55, w=12.2, h=0.5, anim=100):
        return self.text(x, y, w, h, t, sz=sz, color=color, anim=anim)

    def hexnum(self, x, y, w, n, fill=DARK, color=WHITE, sz=None):
        h = w * 0.67
        self.shape(x, y, w, h, geom="hexagon", fill=fill, shadow="pill")
        return self.text(x, y, w, h, str(n), sz=sz or max(12, int(w * 22)), bold=True, color=color, align="ctr", anchor="ctr")

    def circle_num(self, x, y, d, n, fill=DARK, color=WHITE, sz=None, line=None):
        return self.shape(x, y, d, d, geom="ellipse", fill=fill, line=line, text=str(n), sz=sz or max(9, int(d * 26)), bold=True,
                          color=color, align="ctr", anchor="ctr", inset=(0, 0, 0, 0))

    def bubble(self, x, y, w, h, text, tail=(-60000, 30000), sz=16, flip=True, anim=0):
        """White speech bubble pointing to the character on the right (like slides 3 and 8)."""
        self.begin("Реплика")
        self.shape(x, y, w, h, geom="wedgeRoundRectCallout", fill=WHITE, flipH=flip,
                   adj={"adj1": tail[0], "adj2": tail[1], "adj3": 16667}, shadow="soft", check=False)
        self.text(x + 0.35, y + 0.28, w - 0.7, h - 0.56, text, sz=sz, color="000000", anchor="ctr", lnsp=1.05, spc_after=6)
        return self.end(anim=anim)

    def chip(self, x, y, w, h, t, fill=G2, color=WHITE, sz=10, bold=True, line=None, anim=None):
        return self.shape(x, y, w, h, geom="roundRect", radius=h / 2, fill=fill, line=line, text=t, sz=sz, bold=bold,
                          color=color, align="ctr", anchor="ctr", inset=(0.04, 0, 0.04, 0), anim=anim)

    def anim(self, sid, delay=0, kind="grp"):
        self.anims.append((sid, kind, delay))

    # -- serialisation
    def _timing(self):
        if not self.anims and self.video_id is None:
            return ""
        cid = [2]
        def nid():
            cid[0] += 1
            return cid[0]
        inner = ""
        vid = self.video_id
        cid[0] = 4  # 1 root, 2 mainSeq, 3/4 wrapper pars
        if vid is not None:
            i1, i2 = nid(), nid()
            inner += ('<p:par><p:cTn id="%d" presetID="1" presetClass="mediacall" presetSubtype="0" fill="hold" nodeType="afterEffect"><p:stCondLst><p:cond delay="0"/></p:stCondLst>'
                      '<p:childTnLst><p:cmd type="call" cmd="playFrom(0.0)"><p:cBhvr><p:cTn id="%d" dur="16000" fill="hold"/><p:tgtEl><p:spTgt spid="%d"/></p:tgtEl></p:cBhvr></p:cmd></p:childTnLst></p:cTn></p:par>') % (i1, i2, vid)
        bld = ""
        for sid, kind, delay in self.anims:
            g0 = ' grpId="0"' if kind in ("sp", "spbg") else ""
            g1 = ' grpId="1"' if kind in ("sp", "spbg") else ""
            a1, a2, a3 = nid(), nid(), nid()
            inner += ('<p:par><p:cTn id="%d" presetID="10" presetClass="entr" presetSubtype="0" fill="hold"%s nodeType="withEffect"><p:stCondLst><p:cond delay="%d"/></p:stCondLst><p:childTnLst>'
                      '<p:set><p:cBhvr><p:cTn id="%d" dur="1" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst></p:cTn><p:tgtEl><p:spTgt spid="%d"/></p:tgtEl>'
                      '<p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst></p:cBhvr><p:to><p:strVal val="visible"/></p:to></p:set>'
                      '<p:animEffect transition="in" filter="fade"><p:cBhvr><p:cTn id="%d" dur="600"/><p:tgtEl><p:spTgt spid="%d"/></p:tgtEl></p:cBhvr></p:animEffect></p:childTnLst></p:cTn></p:par>') % (
                a1, g0, delay, a2, sid, a3, sid)
            b1, b2 = nid(), nid()
            inner += ('<p:par><p:cTn id="%d" presetID="63" presetClass="path" presetSubtype="0" accel="14000" decel="86000" fill="hold"%s nodeType="withEffect"><p:stCondLst><p:cond delay="%d"/></p:stCondLst><p:childTnLst>'
                      '<p:animMotion origin="layout" path="M 0 0 L 0 0.06 " pathEditMode="relative" rAng="0" ptsTypes="AA"><p:cBhvr><p:cTn id="%d" dur="1100" spd="-100000" fill="hold"/>'
                      '<p:tgtEl><p:spTgt spid="%d"/></p:tgtEl><p:attrNameLst><p:attrName>ppt_x</p:attrName><p:attrName>ppt_y</p:attrName></p:attrNameLst></p:cBhvr><p:rCtr x="0" y="3000"/></p:animMotion></p:childTnLst></p:cTn></p:par>') % (
                b1, g1, delay, b2, sid)
            if kind == "sp":
                bld += '<p:bldP spid="%d" grpId="0"/><p:bldP spid="%d" grpId="1"/>' % (sid, sid)
            elif kind == "spbg":
                bld += '<p:bldP spid="%d" grpId="0" animBg="1"/><p:bldP spid="%d" grpId="1" animBg="1"/>' % (sid, sid)
        main = ('<p:seq concurrent="1" nextAc="seek"><p:cTn id="2" dur="indefinite" nodeType="mainSeq"><p:childTnLst>'
                '<p:par><p:cTn id="3" fill="hold"><p:stCondLst><p:cond delay="indefinite"/><p:cond evt="onBegin" delay="0"><p:tn val="2"/></p:cond></p:stCondLst><p:childTnLst>'
                '<p:par><p:cTn id="4" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>%s</p:childTnLst></p:cTn></p:par>'
                '</p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn>'
                '<p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>'
                '<p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst></p:seq>') % inner
        extra = ""
        if vid is not None:
            v1, v2, v3, v4, v5, v6 = [nid() for _ in range(6)]
            extra = ('<p:video><p:cMediaNode vol="80000"><p:cTn id="%d" fill="hold" display="0"><p:stCondLst><p:cond delay="indefinite"/></p:stCondLst></p:cTn>'
                     '<p:tgtEl><p:spTgt spid="%d"/></p:tgtEl></p:cMediaNode></p:video>'
                     '<p:seq concurrent="1" nextAc="seek"><p:cTn id="%d" restart="whenNotActive" fill="hold" evtFilter="cancelBubble" nodeType="interactiveSeq">'
                     '<p:stCondLst><p:cond evt="onClick" delay="0"><p:tgtEl><p:spTgt spid="%d"/></p:tgtEl></p:cond></p:stCondLst><p:endSync evt="end" delay="0"><p:rtn val="all"/></p:endSync>'
                     '<p:childTnLst><p:par><p:cTn id="%d" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst><p:par><p:cTn id="%d" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>'
                     '<p:par><p:cTn id="%d" presetID="2" presetClass="mediacall" presetSubtype="0" fill="hold" nodeType="clickEffect"><p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>'
                     '<p:cmd type="call" cmd="togglePause"><p:cBhvr><p:cTn id="%d" dur="1" fill="hold"/><p:tgtEl><p:spTgt spid="%d"/></p:tgtEl></p:cBhvr></p:cmd></p:childTnLst></p:cTn></p:par>'
                     '</p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn>'
                     '<p:nextCondLst><p:cond evt="onClick" delay="0"><p:tgtEl><p:spTgt spid="%d"/></p:tgtEl></p:cond></p:nextCondLst></p:seq>') % (
                v1, vid, v2, vid, v3, v4, v5, v6, vid, vid)
        t = ('<p:timing><p:tnLst><p:par><p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot"><p:childTnLst>%s%s</p:childTnLst></p:cTn></p:par></p:tnLst>%s</p:timing>') % (
            main, extra, "<p:bldLst>%s</p:bldLst>" % bld if bld else "")
        return t

    def xml(self):
        tr = ""
        if self.transition == "fade":
            tr = ('<mc:AlternateContent xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" xmlns:p14="http://schemas.microsoft.com/office/powerpoint/2010/main">'
                  '<mc:Choice Requires="p14"><p:transition spd="med" p14:dur="700"><p:fade/></p:transition></mc:Choice>'
                  '<mc:Fallback xmlns=""><p:transition spd="med"><p:fade/></p:transition></mc:Fallback></mc:AlternateContent>')
        return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
                '<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
                'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"><p:cSld><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>'
                '<p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>%s</p:spTree></p:cSld>'
                '<p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>%s%s</p:sld>') % ("".join(self.items), tr, self._timing())


class Deck:
    def __init__(self, root):
        self.root = root
        self.slides = []   # (number, Slide)
        self.cur_no = None
        pres = open(os.path.join(root, "ppt/presentation.xml"), encoding="utf-8").read()
        self.max_sld_id = max(int(v) for v in re.findall(r'<p:sldId id="(\d+)"', pres))
        self.existing = len(re.findall(r'<p:sldId ', pres))

    def new(self, bg="light", notes="", replace=None, transition="fade"):
        s = Slide(self, bg=bg, notes=T(notes) if notes else notes, transition=transition)
        no = replace if replace else self.existing + len([x for x in self.slides if not x[2]]) + 1
        self.cur_no = no
        self.slides.append((no, s, bool(replace)))
        return s

    def _notes_xml(self, text, no):
        paras = "".join('<a:p><a:r><a:rPr lang="%s" dirty="0"/><a:t>%s</a:t></a:r></a:p>' % (LANG, escape(t)) for t in text.split("\n"))
        return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
                '<p:notes xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">'
                '<p:cSld><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>'
                '<p:sp><p:nvSpPr><p:cNvPr id="2" name="Slide Image Placeholder 1"/><p:cNvSpPr><a:spLocks noGrp="1" noRot="1" noChangeAspect="1"/></p:cNvSpPr><p:nvPr><p:ph type="sldImg"/></p:nvPr></p:nvSpPr><p:spPr/></p:sp>'
                '<p:sp><p:nvSpPr><p:cNvPr id="3" name="Notes Placeholder 2"/><p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr><p:nvPr><p:ph type="body" idx="1"/></p:nvPr></p:nvSpPr><p:spPr/>'
                '<p:txBody><a:bodyPr/><a:lstStyle/>%s</p:txBody></p:sp></p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:notes>') % paras

    def save(self):
        root = self.root
        ct_path = os.path.join(root, "[Content_Types].xml")
        ct = open(ct_path, encoding="utf-8").read()
        pres_path = os.path.join(root, "ppt/presentation.xml")
        pres = open(pres_path, encoding="utf-8").read()
        prels_path = os.path.join(root, "ppt/_rels/presentation.xml.rels")
        prels = open(prels_path, encoding="utf-8").read()
        notes_dir = os.path.join(root, "ppt/notesSlides")
        existing_notes = [int(m) for m in re.findall(r"notesSlide(\d+)\.xml", " ".join(os.listdir(notes_dir)))]
        next_note = max(existing_notes + [0]) + 1
        rid_nums = [int(v) for v in re.findall(r'Id="rId(\d+)"', prels)]
        next_rid = max(rid_nums) + 1
        sld_id = self.max_sld_id
        new_ids = ""
        for no, s, replaced in self.slides:
            rels = dict(s.rels)
            if s.notes:
                nfn = "notesSlide%d.xml" % next_note
                next_note += 1
                open(os.path.join(notes_dir, nfn), "w", encoding="utf-8").write(self._notes_xml(s.notes, no))
                open(os.path.join(notes_dir, "_rels", nfn + ".rels"), "w", encoding="utf-8").write(
                    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                    '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/notesMaster" Target="../notesMasters/notesMaster1.xml"/>'
                    '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="../slides/slide%d.xml"/></Relationships>' % no)
                ct = ct.replace("</Types>", '<Override PartName="/ppt/notesSlides/%s" ContentType="application/vnd.openxmlformats-officedocument.presentationml.notesSlide+xml"/></Types>' % nfn)
                rid = "rId%d" % (len(rels) + 1)
                rels["../notesSlides/" + nfn] = (rid, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/notesSlide")
            rx = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            for target, (rid, typ) in rels.items():
                target = target.split("#")[0]
                if typ.endswith("/video"):
                    rx += '<Relationship Id="%s" Type="%s" Target="%s"/>' % (rid, typ, target)
                else:
                    rx += '<Relationship Id="%s" Type="%s" Target="%s"/>' % (rid, typ, target)
            rx += "</Relationships>"
            open(os.path.join(root, "ppt/slides/slide%d.xml" % no), "w", encoding="utf-8").write(s.xml())
            open(os.path.join(root, "ppt/slides/_rels/slide%d.xml.rels" % no), "w", encoding="utf-8").write(rx)
            if not replaced:
                ct = ct.replace("</Types>", '<Override PartName="/ppt/slides/slide%d.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/></Types>' % no)
                rid = "rId%d" % next_rid
                next_rid += 1
                prels = prels.replace("</Relationships>", '<Relationship Id="%s" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide%d.xml"/></Relationships>' % (rid, no))
                sld_id += 1
                new_ids += '<p:sldId id="%d" r:id="%s"/>' % (sld_id, rid)
        pres = pres.replace("</p:sldIdLst>", new_ids + "</p:sldIdLst>")
        open(ct_path, "w", encoding="utf-8").write(ct)
        open(pres_path, "w", encoding="utf-8").write(pres)
        open(prels_path, "w", encoding="utf-8").write(prels)
