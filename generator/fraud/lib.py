# -*- coding: utf-8 -*-
"""Small PresentationML writer for the course «Защита от мошенничества».

The package is assembled from the user's template (We_build_Products.pptx): its first slide
master (title placeholder, accent line with glow), the "Default Layout" and the theme, recoloured
to the Ipak Yuli Bank greens. Every slide is written as raw XML: shapes, pictures, entrance
animations, click triggers and fade transitions. Text is measured with Inter metrics so that
boxes are sized to their content.
"""
import os, re, shutil, zipfile
from xml.sax.saxutils import escape
from PIL import Image, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")
EMU = 914400
SW, SH = 13.333, 7.5

# ---------------------------------------------------------------- palette (logo greens + template neutrals)
GREEN = "02691A"     # logo dark green: highlight cards, icon tiles, accent line
LIME = "4CEA4C"      # logo lime: accents on dark backgrounds
DEEP = "053A18"      # dark slides
DEEP2 = "0A5424"
INK = "0F2418"       # headings
BODY = "36443C"      # body text
MUTED = "6E7C74"
CARD = "EEF3EF"      # template's light card, tinted green
LINE = "D3DED6"
WHITE = "FFFFFF"
# semantic frames from the course document
ADV_F, ADV_L, ADV_D = "E4F6E7", "37B852", "157A2C"      # green: advice to the client
SIT_F, SIT_L, SIT_D = "F1F2F4", "B4BBC2", "59636D"      # grey: situation / what you see
WARN_F, WARN_L, WARN_D = "FFF5D6", "F2C230", "8A6100"   # yellow: «Важно»
STOP_F, STOP_L, STOP_D = "FDECEC", "E5484D", "B3261E"   # red: prohibition
FONT = "Inter"

WARN = []      # overflow warnings
SHRUNK = []    # auto-shrunk boxes

_fonts = {}


def _font(sz, bold):
    key = (round(sz * 10), bold)
    if key not in _fonts:
        fn = "/usr/share/fonts/opentype/inter/Inter-%s.otf" % ("Bold" if bold else "Regular")
        _fonts[key] = ImageFont.truetype(fn, key[0])
    return _fonts[key]


def e(v):
    return int(round(v * EMU))


def parse_runs(s):
    """'**bold** normal' -> [(text, bold)]"""
    out = []
    for i, part in enumerate(re.split(r"\*\*", s)):
        if part:
            out.append((part, i % 2 == 1))
    return out


def norm_paras(text):
    if isinstance(text, str):
        return [{"t": t} for t in text.split("\n")]
    return [p if isinstance(p, dict) else {"t": p} for p in text]


def text_height(text, w_in, sz, bold=False, lnsp=1.0, spc_after=0.0, inset=(0, 0), safety=0.97):
    """Rendered height (in) of paragraphs set in a box w_in wide (Inter metrics)."""
    avail = (w_in - inset[0]) * 720 * safety
    total = 0.0
    paras = norm_paras(text)
    for n, p in enumerate(paras):
        psz = p.get("sz", sz)
        words = []
        for t, b in parse_runs(p["t"]):
            for wd in re.split(r"(\s+)", t):
                if wd:
                    words.append((wd, b or p.get("b", bold)))
        lines, cur = 1, 0.0
        indent = p.get("marL", 0.0) * 720
        for wd, b in words:
            wl = _font(psz, b).getlength(wd)
            if cur + wl > avail - indent and not wd.isspace() and cur > 0:
                lines += 1
                cur = wl
            else:
                cur += wl
        line_h = psz * 1.21 * p.get("lnsp", lnsp) / 72.0
        total += lines * line_h
        if n < len(paras) - 1:
            total += p.get("spcAft", spc_after) / 72.0
        total += p.get("spcBef", 0) / 72.0
    return total + inset[1]


def text_width(t, sz, bold=False):
    return sum(_font(sz, b or bold).getlength(x) for x, b in parse_runs(t)) / 720.0


# ---------------------------------------------------------------- icons (Lucide, ISC licence)
ICON_DIR = os.path.join(ASSETS, "icons_svg")
_icon_cache = os.path.join("/tmp", "fraud_icons_cache")


def icon_png(name, color, px=160, stroke=2.0):
    import cairosvg
    os.makedirs(_icon_cache, exist_ok=True)
    out = os.path.join(_icon_cache, "%s_%s_%s.png" % (name, color, str(stroke).replace(".", "_")))
    if not os.path.exists(out):
        svg = open(os.path.join(ICON_DIR, name + ".svg"), encoding="utf-8").read()
        svg = svg.replace('stroke="currentColor"', 'stroke="#%s"' % color).replace('stroke-width="2"', 'stroke-width="%s"' % stroke)
        cairosvg.svg2png(bytestring=svg.encode("utf-8"), write_to=out, output_width=px, output_height=px)
    return out


# ---------------------------------------------------------------- slide
class Slide:
    def __init__(self, deck, dark=False, name="", transition="fade"):
        self.deck = deck
        self.dark = dark
        self.name = name
        self.items = []
        self.stack = []
        self.rels = {}
        self.nid = 2
        self.anims = []          # (spid, kind, delay, effect, dur)
        self.triggers = []       # (button spid, [(spid, kind, effect, delay)])
        self.transition = transition
        self._rel("../slideLayouts/slideLayout1.xml", "slideLayout")

    # -- relationships
    def _rel(self, target, kind):
        if target in self.rels:
            return self.rels[target][0]
        rid = "rId%d" % (len(self.rels) + 1)
        types = {
            "slideLayout": "http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout",
            "image": "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image",
        }
        self.rels[target] = (rid, types[kind])
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

    def end(self, anim=None, effect="rise", dur=None):
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
            self.anims.append((g["id"], "grp", anim, effect, dur))
        return g["id"]

    # -- fills, lines, effects
    def _fill(self, fill, alpha=None, grad=None):
        if grad:
            stops = "".join('<a:gs pos="%d"><a:srgbClr val="%s">%s</a:srgbClr></a:gs>' % (
                int(p * 1000), c, '<a:alpha val="%d"/>' % int(a * 1000) if a is not None else "") for p, c, a in grad["stops"])
            if grad.get("path"):
                return ('<a:gradFill rotWithShape="1"><a:gsLst>%s</a:gsLst><a:path path="circle">'
                        '<a:fillToRect l="50000" t="50000" r="50000" b="50000"/></a:path></a:gradFill>') % stops
            return '<a:gradFill rotWithShape="1"><a:gsLst>%s</a:gsLst><a:lin ang="%d" scaled="0"/></a:gradFill>' % (
                stops, int(grad.get("ang", 90) * 60000))
        if fill is None:
            return "<a:noFill/>"
        a = '<a:alpha val="%d"/>' % int(alpha * 1000) if alpha is not None else ""
        return '<a:solidFill><a:srgbClr val="%s">%s</a:srgbClr></a:solidFill>' % (fill, a)

    def _line(self, line, lw=1.0, dash=None):
        if not line:
            return "<a:ln><a:noFill/></a:ln>"
        d = '<a:prstDash val="%s"/>' % dash if dash else ""
        return '<a:ln w="%d"><a:solidFill><a:srgbClr val="%s"/></a:solidFill>%s</a:ln>' % (int(lw * 12700), line, d)

    def _effects(self, shadow):
        if not shadow:
            return ""
        if shadow == "soft":
            return ('<a:effectLst><a:outerShdw blurRad="254000" dist="63500" dir="5400000" algn="t" rotWithShape="0">'
                    '<a:srgbClr val="0F2418"><a:alpha val="10000"/></a:srgbClr></a:outerShdw></a:effectLst>')
        if shadow == "glow":      # the template's highlighted card: coloured blur under the card
            return ('<a:effectLst><a:outerShdw blurRad="381000" dist="127000" dir="5400000" algn="t" rotWithShape="0">'
                    '<a:srgbClr val="%s"><a:alpha val="32000"/></a:srgbClr></a:outerShdw></a:effectLst>' % GREEN)
        if shadow == "lime":
            return ('<a:effectLst><a:outerShdw blurRad="381000" dist="76200" dir="5400000" algn="t" rotWithShape="0">'
                    '<a:srgbClr val="%s"><a:alpha val="35000"/></a:srgbClr></a:outerShdw></a:effectLst>' % LIME)
        if shadow == "red":
            return ('<a:effectLst><a:outerShdw blurRad="381000" dist="101600" dir="5400000" algn="t" rotWithShape="0">'
                    '<a:srgbClr val="%s"><a:alpha val="28000"/></a:srgbClr></a:outerShdw></a:effectLst>' % STOP_L)
        if shadow == "soften":
            return '<a:effectLst><a:softEdge rad="508000"/></a:effectLst>'
        return ""

    def _paras(self, text, sz, color, bold, align, lnsp, spc_after, font, spc=0, bcolor=None):
        out = []
        paras = norm_paras(text)
        for p in paras:
            psz = p.get("sz", sz); pcol = p.get("color", color); pb = p.get("b", bold)
            palign = p.get("align", align); pl = p.get("lnsp", lnsp)
            pa = p.get("spcAft", spc_after)
            bul = p.get("bullet")
            mar = ""
            if bul:
                mar = ' marL="%d" indent="%d"' % (e(p.get("marL", 0.24)), -e(p.get("marL", 0.24)))
            ppr = '<a:pPr algn="%s"%s>' % (palign, mar)
            ppr += '<a:lnSpc><a:spcPct val="%d"/></a:lnSpc>' % int(pl * 100000)
            if p.get("spcBef"):
                ppr += '<a:spcBef><a:spcPts val="%d"/></a:spcBef>' % int(p["spcBef"] * 100)
            ppr += '<a:spcAft><a:spcPts val="%d"/></a:spcAft>' % int(pa * 100)
            if bul:
                bc = bul if isinstance(bul, str) and len(bul) == 6 else GREEN
                ppr += '<a:buClr><a:srgbClr val="%s"/></a:buClr><a:buSzPct val="100000"/><a:buFont typeface="Arial"/><a:buChar char="&#8226;"/>' % bc
            else:
                ppr += "<a:buNone/>"
            ppr += "</a:pPr>"
            runs = ""
            for t, b in parse_runs(p["t"]):
                rb = b or pb
                rcol = (p.get("bcolor") or bcolor or pcol) if b else pcol
                sp = ' spc="%d"' % int(p.get("spc", spc) * 100) if p.get("spc", spc) else ""
                it = ' i="1"' if p.get("i") else ""
                runs += ('<a:r><a:rPr lang="ru-RU" sz="%d" b="%d"%s%s dirty="0"><a:solidFill><a:srgbClr val="%s"/></a:solidFill>'
                         '<a:latin typeface="%s"/><a:cs typeface="%s"/></a:rPr><a:t>%s</a:t></a:r>') % (
                    int(round(psz * 100)), 1 if rb else 0, it, sp, rcol, font, font, escape(t))
            end = '<a:endParaRPr lang="ru-RU" sz="%d" dirty="0"><a:latin typeface="%s"/></a:endParaRPr>' % (int(round(psz * 100)), font)
            out.append("<a:p>%s%s%s</a:p>" % (ppr, runs, end))
        return "".join(out)

    def shape(self, x, y, w, h, geom="rect", fill=None, alpha=None, grad=None, line=None, lw=1.0, dash=None,
              radius=None, shadow=None, text=None, sz=14, color=BODY, bold=False, align="l", anchor="t",
              inset=(0.1, 0.05, 0.1, 0.05), lnsp=1.0, spc_after=0, font=FONT, name=None, spc=0, bcolor=None,
              anim=None, effect="rise", dur=None, adj=None, rot=0, flipH=False, flipV=False, check=True,
              txbox=False, link=None, minsz=None, wrap=True):
        sid = self._id()
        name = name or ("TextBox %d" % sid if txbox else "Shape %d" % sid)
        av = ""
        if radius is not None and geom == "roundRect":
            av = '<a:gd name="adj" fmla="val %d"/>' % min(50000, int(radius * 100000 / max(0.01, min(w, h))))
        if adj:
            av += "".join('<a:gd name="%s" fmla="val %d"/>' % (k, v) for k, v in adj.items())
        attrs = (' rot="%d"' % int(rot * 60000) if rot else "") + (' flipH="1"' if flipH else "") + (' flipV="1"' if flipV else "")
        sppr = ('<p:spPr><a:xfrm%s><a:off x="%d" y="%d"/><a:ext cx="%d" cy="%d"/></a:xfrm><a:prstGeom prst="%s"><a:avLst>%s</a:avLst>'
                '</a:prstGeom>%s%s%s</p:spPr>') % (attrs, e(x), e(y), e(w), e(h), geom, av, self._fill(fill, alpha, grad),
                                                   self._line(line, lw, dash), self._effects(shadow))
        has_text = text is not None and text != ""
        if has_text:
            l, t, r, b = inset
            sz0 = sz
            if check:
                need = text_height(text, w, sz, bold, lnsp, spc_after, (l + r, t + b))
                lo = minsz or sz0 * 0.85
                while need > h + 0.01 and sz > lo:
                    sz = round(sz - 0.5, 1)
                    text = [dict(p, sz=sz * p["sz"] / sz0) if "sz" in p else p for p in norm_paras(text)] if not isinstance(text, str) else text
                    need = text_height(text, w, sz, bold, lnsp, spc_after, (l + r, t + b))
                if sz != sz0:
                    SHRUNK.append("slide %s: %.1f -> %.1f pt: %s" % (self.deck.cur_no, sz0, sz, str(text)[:60]))
                if need > h + 0.02:
                    WARN.append("slide %s: text overflow %.2f > %.2f in: %s" % (self.deck.cur_no, need, h, str(text)[:70]))
            pxml = self._paras(text, sz, color, bold, align, lnsp, spc_after, font, spc, bcolor)
            body = ('<p:txBody><a:bodyPr wrap="%s" lIns="%d" tIns="%d" rIns="%d" bIns="%d" anchor="%s" rtlCol="0">'
                    '<a:noAutofit/></a:bodyPr><a:lstStyle/>%s</p:txBody>') % ("square" if wrap else "none", e(l), e(t), e(r), e(b), anchor, pxml)
        else:
            body = '<p:txBody><a:bodyPr rtlCol="0" anchor="ctr"/><a:lstStyle/><a:p><a:endParaRPr lang="ru-RU" dirty="0"/></a:p></p:txBody>'
        cnv = '<p:cNvSpPr txBox="1"/>' if txbox else "<p:cNvSpPr/>"
        hl = ""
        if link == "next":
            hl = '<a:hlinkClick r:id="" action="ppaction://hlinkshowjump?jump=nextslide"/>'
        xml = '<p:sp><p:nvSpPr><p:cNvPr id="%d" name="%s">%s</p:cNvPr>%s<p:nvPr/></p:nvSpPr>%s%s</p:sp>' % (
            sid, escape(name), hl, cnv, sppr, body)
        self._add(xml, (x, y, w, h))
        if anim is not None:
            self.anims.append((sid, "sp" if has_text else "spbg", anim, effect, dur))
        return sid

    def rect(self, x, y, w, h, **k):
        return self.shape(x, y, w, h, geom="rect", **k)

    def rrect(self, x, y, w, h, r=0.16, **k):
        return self.shape(x, y, w, h, geom="roundRect", radius=r, **k)

    def text(self, x, y, w, h, text, **k):
        k.setdefault("inset", (0, 0, 0, 0))
        return self.shape(x, y, w, h, geom="rect", text=text, txbox=True, **k)

    def title_ph(self, x, y, w, h, text, sz=24, color=INK, lnsp=0.95, anim=None):
        """Slide title in the layout's title placeholder: LMS players and the outline read it."""
        sid = self._id()
        pxml = self._paras(text, sz, color, True, "l", lnsp, 0, FONT)
        need = text_height(text, w, sz, True, lnsp)
        if need > h + 0.02:
            WARN.append("slide %s: TITLE overflow %.2f > %.2f: %s" % (self.deck.cur_no, need, h, text[:60]))
        xml = ('<p:sp><p:nvSpPr><p:cNvPr id="%d" name="Заголовок %d"/><p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr>'
               '<p:nvPr><p:ph type="title"/></p:nvPr></p:nvSpPr><p:spPr><a:xfrm><a:off x="%d" y="%d"/><a:ext cx="%d" cy="%d"/></a:xfrm></p:spPr>'
               '<p:txBody><a:bodyPr vert="horz" wrap="square" lIns="0" tIns="0" rIns="0" bIns="0" rtlCol="0" anchor="t"><a:noAutofit/></a:bodyPr>'
               '<a:lstStyle/>%s</p:txBody></p:sp>') % (sid, sid, e(x), e(y), e(w), e(h), pxml)
        self._add(xml, (x, y, w, h))
        if anim is not None:
            self.anims.append((sid, "sp", anim, "rise", None))
        return sid

    def slidenum(self, x, y, w, h, color=MUTED, sz=9):
        sid = self._id()
        xml = ('<p:sp><p:nvSpPr><p:cNvPr id="%d" name="Номер слайда"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>'
               '<p:spPr><a:xfrm><a:off x="%d" y="%d"/><a:ext cx="%d" cy="%d"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/></p:spPr>'
               '<p:txBody><a:bodyPr wrap="none" lIns="0" tIns="0" rIns="0" bIns="0" anchor="ctr"><a:noAutofit/></a:bodyPr><a:lstStyle/>'
               '<a:p><a:pPr algn="r"/><a:fld id="{B6F15528-21DE-4FAA-801E-634DDDAF4B2B}" type="slidenum"><a:rPr lang="ru-RU" sz="%d" dirty="0">'
               '<a:solidFill><a:srgbClr val="%s"/></a:solidFill><a:latin typeface="%s"/></a:rPr><a:t>%d</a:t></a:fld></a:p></p:txBody></p:sp>') % (
            sid, e(x), e(y), e(w), e(h), int(sz * 100), color, FONT, self.deck.cur_no)
        self.items.append(xml)

    def line(self, x1, y1, x2, y2, color=GREEN, lw=1.5, head=None, tail=None, dash=None, anim=None, effect="wipe", dur=None):
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
        if anim is not None:
            self.anims.append((sid, "pic", anim, effect, dur))
        return sid

    def pic(self, path, x, y, w=None, h=None, crop=None, name=None, anim=None, effect="rise", dur=None,
            alpha=None, geom="rect", radius=None):
        if not os.path.isabs(path):
            path = os.path.join(ASSETS, path)
        tgt = self.deck.media(path)
        rid = self._rel("../media/" + tgt, "image")
        pw, ph = self.deck.media_size[tgt]
        l, t, r, b = crop or (0, 0, 0, 0)
        asp = (1 - l - r) * pw / ((1 - t - b) * ph)
        if w is None:
            w = h * asp
        if h is None:
            h = w / asp
        sid = self._id()
        src = '<a:srcRect l="%d" t="%d" r="%d" b="%d"/>' % tuple(int(v * 100000) for v in (l, t, r, b)) if crop else ""
        am = '<a:alphaModFix amt="%d"/>' % int(alpha * 1000) if alpha is not None else ""
        av = ""
        if geom == "roundRect" and radius:
            av = '<a:gd name="adj" fmla="val %d"/>' % min(50000, int(radius * 100000 / min(w, h)))
        xml = ('<p:pic><p:nvPicPr><p:cNvPr id="%d" name="%s"/><p:cNvPicPr><a:picLocks noChangeAspect="1"/></p:cNvPicPr><p:nvPr/></p:nvPicPr>'
               '<p:blipFill><a:blip r:embed="%s">%s</a:blip>%s<a:stretch><a:fillRect/></a:stretch></p:blipFill>'
               '<p:spPr><a:xfrm><a:off x="%d" y="%d"/><a:ext cx="%d" cy="%d"/></a:xfrm><a:prstGeom prst="%s"><a:avLst>%s</a:avLst></a:prstGeom></p:spPr></p:pic>') % (
            sid, escape(name or ("Рисунок %d" % sid)), rid, am, src, e(x), e(y), e(w), e(h), geom, av)
        self._add(xml, (x, y, w, h))
        if anim is not None:
            self.anims.append((sid, "pic", anim, effect, dur))
        return sid, w, h

    def icon(self, name, x, y, d, color=WHITE, stroke=2.0, anim=None):
        return self.pic(icon_png(name, color, stroke=stroke), x, y, d, d, name="Иконка " + name, anim=anim)

    # -- interactivity
    def trigger(self, button_sid, targets):
        """targets: [(spid, kind, effect, delay)] appear when the button is clicked."""
        self.triggers.append((button_sid, targets))

    # -- serialisation of animations
    def _effect_xml(self, nid, sid, kind, delay, effect, dur, node="withEffect"):
        g0 = ' grpId="0"' if kind in ("sp", "spbg") else ""
        vis = ('<p:set><p:cBhvr><p:cTn id="%d" dur="1" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst></p:cTn>'
               '<p:tgtEl><p:spTgt spid="%d"/></p:tgtEl><p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst></p:cBhvr>'
               '<p:to><p:strVal val="visible"/></p:to></p:set>')
        out = ""
        if effect in ("rise", "fade"):
            d = dur or 600
            a1, a2, a3 = nid(), nid(), nid()
            out += ('<p:par><p:cTn id="%d" presetID="10" presetClass="entr" presetSubtype="0" fill="hold"%s nodeType="%s">'
                    '<p:stCondLst><p:cond delay="%d"/></p:stCondLst><p:childTnLst>' + vis +
                    '<p:animEffect transition="in" filter="fade"><p:cBhvr><p:cTn id="%d" dur="%d"/><p:tgtEl><p:spTgt spid="%d"/></p:tgtEl>'
                    '</p:cBhvr></p:animEffect></p:childTnLst></p:cTn></p:par>') % (a1, g0, node, delay, a2, sid, a3, d, sid)
            if effect == "rise":
                g1 = ' grpId="1"' if kind in ("sp", "spbg") else ""
                b1, b2 = nid(), nid()
                out += ('<p:par><p:cTn id="%d" presetID="63" presetClass="path" presetSubtype="0" accel="14000" decel="86000" fill="hold"%s nodeType="withEffect">'
                        '<p:stCondLst><p:cond delay="%d"/></p:stCondLst><p:childTnLst>'
                        '<p:animMotion origin="layout" path="M 0 0.04 L 0 0 E" pathEditMode="relative" rAng="0" ptsTypes="AA"><p:cBhvr>'
                        '<p:cTn id="%d" dur="%d" fill="hold"/><p:tgtEl><p:spTgt spid="%d"/></p:tgtEl><p:attrNameLst><p:attrName>ppt_x</p:attrName>'
                        '<p:attrName>ppt_y</p:attrName></p:attrNameLst></p:cBhvr><p:rCtr x="0" y="-2000"/></p:animMotion></p:childTnLst></p:cTn></p:par>') % (
                    b1, g1, delay, b2, max(700, d + 200), sid)
        elif effect == "zoom":
            d = dur or 500
            a1, a2, a3, a4, a5 = nid(), nid(), nid(), nid(), nid()
            out += ('<p:par><p:cTn id="%d" presetID="53" presetClass="entr" presetSubtype="16" fill="hold"%s nodeType="%s">'
                    '<p:stCondLst><p:cond delay="%d"/></p:stCondLst><p:childTnLst>' + vis +
                    '<p:anim calcmode="lin" valueType="num"><p:cBhvr><p:cTn id="%d" dur="%d" fill="hold"/><p:tgtEl><p:spTgt spid="%d"/></p:tgtEl>'
                    '<p:attrNameLst><p:attrName>ppt_w</p:attrName></p:attrNameLst></p:cBhvr><p:tavLst><p:tav tm="0"><p:val><p:fltVal val="0"/></p:val></p:tav>'
                    '<p:tav tm="100000"><p:val><p:strVal val="#ppt_w"/></p:val></p:tav></p:tavLst></p:anim>'
                    '<p:anim calcmode="lin" valueType="num"><p:cBhvr><p:cTn id="%d" dur="%d" fill="hold"/><p:tgtEl><p:spTgt spid="%d"/></p:tgtEl>'
                    '<p:attrNameLst><p:attrName>ppt_h</p:attrName></p:attrNameLst></p:cBhvr><p:tavLst><p:tav tm="0"><p:val><p:fltVal val="0"/></p:val></p:tav>'
                    '<p:tav tm="100000"><p:val><p:strVal val="#ppt_h"/></p:val></p:tav></p:tavLst></p:anim>'
                    '<p:animEffect transition="in" filter="fade"><p:cBhvr><p:cTn id="%d" dur="%d"/><p:tgtEl><p:spTgt spid="%d"/></p:tgtEl></p:cBhvr></p:animEffect>'
                    '</p:childTnLst></p:cTn></p:par>') % (a1, g0, node, delay, a2, sid, a3, d, sid, a4, d, sid, a5, d, sid)
        elif effect in ("wipe", "wipe_down"):
            d = dur or 500
            sub, flt = ("8", "wipe(left)") if effect == "wipe" else ("1", "wipe(up)")
            a1, a2, a3 = nid(), nid(), nid()
            out += ('<p:par><p:cTn id="%d" presetID="22" presetClass="entr" presetSubtype="%s" fill="hold"%s nodeType="%s">'
                    '<p:stCondLst><p:cond delay="%d"/></p:stCondLst><p:childTnLst>' + vis +
                    '<p:animEffect transition="in" filter="%s"><p:cBhvr><p:cTn id="%d" dur="%d"/><p:tgtEl><p:spTgt spid="%d"/></p:tgtEl>'
                    '</p:cBhvr></p:animEffect></p:childTnLst></p:cTn></p:par>') % (a1, sub, g0, node, delay, a2, sid, flt, a3, d, sid)
        return out

    def _bld(self, sid, kind, effect):
        if kind not in ("sp", "spbg"):
            return ""
        bg = ' animBg="1"' if kind == "spbg" else ""
        out = '<p:bldP spid="%d" grpId="0"%s/>' % (sid, bg)
        if effect == "rise":
            out += '<p:bldP spid="%d" grpId="1"%s/>' % (sid, bg)
        return out

    def _timing(self):
        if not self.anims and not self.triggers:
            return ""
        cid = [4]   # 1 root, 2 main sequence, 3/4 wrappers

        def nid():
            cid[0] += 1
            return cid[0]
        inner = ""
        bld = ""
        for sid, kind, delay, effect, dur in self.anims:
            inner += self._effect_xml(nid, sid, kind, delay, effect, dur)
            bld += self._bld(sid, kind, effect)
        main = ""
        if self.anims:
            main = ('<p:seq concurrent="1" nextAc="seek"><p:cTn id="2" dur="indefinite" nodeType="mainSeq"><p:childTnLst>'
                    '<p:par><p:cTn id="3" fill="hold"><p:stCondLst><p:cond delay="indefinite"/><p:cond evt="onBegin" delay="0"><p:tn val="2"/></p:cond>'
                    '</p:stCondLst><p:childTnLst><p:par><p:cTn id="4" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>%s'
                    '</p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn>'
                    '<p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>'
                    '<p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst></p:seq>') % inner
        inter = ""
        for btn, targets in self.triggers:
            s1, s2, s3 = nid(), nid(), nid()
            effs = ""
            for i, (sid, kind, effect, delay) in enumerate(targets):
                effs += self._effect_xml(nid, sid, kind, delay, effect, None, node="clickEffect" if i == 0 else "withEffect")
                bld += self._bld(sid, kind, effect)
            inter += ('<p:seq concurrent="1" nextAc="seek"><p:cTn id="%d" restart="whenNotActive" fill="hold" evtFilter="cancelBubble" nodeType="interactiveSeq">'
                      '<p:stCondLst><p:cond evt="onClick" delay="0"><p:tgtEl><p:spTgt spid="%d"/></p:tgtEl></p:cond></p:stCondLst>'
                      '<p:endSync evt="end" delay="0"><p:rtn val="all"/></p:endSync><p:childTnLst>'
                      '<p:par><p:cTn id="%d" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>'
                      '<p:par><p:cTn id="%d" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>%s'
                      '</p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn>'
                      '<p:nextCondLst><p:cond evt="onClick" delay="0"><p:tgtEl><p:spTgt spid="%d"/></p:tgtEl></p:cond></p:nextCondLst></p:seq>') % (
                s1, btn, s2, s3, effs, btn)
        return ('<p:timing><p:tnLst><p:par><p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot"><p:childTnLst>%s%s'
                '</p:childTnLst></p:cTn></p:par></p:tnLst>%s</p:timing>') % (main, inter, "<p:bldLst>%s</p:bldLst>" % bld if bld else "")

    def xml(self):
        tr = ""
        if self.transition == "fade":
            tr = ('<mc:AlternateContent xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" xmlns:p14="http://schemas.microsoft.com/office/powerpoint/2010/main">'
                  '<mc:Choice Requires="p14"><p:transition spd="med" p14:dur="600"><p:fade/></p:transition></mc:Choice>'
                  '<mc:Fallback><p:transition spd="med"><p:fade/></p:transition></mc:Fallback></mc:AlternateContent>')
        show = ' showMasterSp="0"' if self.dark else ""
        bg = ""
        if self.dark:
            bg = ('<p:bg><p:bgPr><a:gradFill rotWithShape="1"><a:gsLst><a:gs pos="0"><a:srgbClr val="%s"/></a:gs>'
                  '<a:gs pos="100000"><a:srgbClr val="%s"/></a:gs></a:gsLst><a:lin ang="2700000" scaled="0"/></a:gradFill>'
                  '<a:effectLst/></p:bgPr></p:bg>') % (DEEP2, DEEP)
        return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
                '<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
                'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"%s><p:cSld name="%s">%s<p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>'
                '<p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>%s</p:spTree></p:cSld>'
                '<p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>%s%s</p:sld>') % (
            show, escape(self.name, {'"': "&quot;"}), bg, "".join(self.items), tr, self._timing())


# ---------------------------------------------------------------- package
CT_MAIN = "application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"
R_DOC = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"


def make_base(template_pptx, root, theme_colors, title):
    """Unpacks only master 1, its 'Default Layout' and theme from the template into `root`."""
    if os.path.exists(root):
        shutil.rmtree(root)
    if os.path.isdir(template_pptx):          # parts extracted from the template (see extract_base.py)
        def rd(n):
            return open(os.path.join(template_pptx, n), encoding="utf-8").read()
    else:
        z = zipfile.ZipFile(template_pptx)

        def rd(n):
            return z.read(n).decode("utf-8")
    for d in ("_rels", "docProps", "ppt/_rels", "ppt/slides/_rels", "ppt/slideMasters/_rels", "ppt/slideLayouts/_rels", "ppt/theme", "ppt/media"):
        os.makedirs(os.path.join(root, d), exist_ok=True)

    def wr(n, s):
        open(os.path.join(root, n), "w", encoding="utf-8").write(s)
    # master: keep one layout
    m = rd("ppt/slideMasters/slideMaster1.xml")
    m = re.sub(r"<p:sldLayoutIdLst>.*?</p:sldLayoutIdLst>", '<p:sldLayoutIdLst><p:sldLayoutId id="2147483649" r:id="rId1"/></p:sldLayoutIdLst>', m, flags=re.S)
    wr("ppt/slideMasters/slideMaster1.xml", m)
    wr("ppt/slideMasters/_rels/slideMaster1.xml.rels",
       '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
       '<Relationship Id="rId1" Type="%s/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>'
       '<Relationship Id="rId2" Type="%s/theme" Target="../theme/theme1.xml"/></Relationships>' % (R_DOC, R_DOC))
    lay = rd("ppt/slideLayouts/slideLayout2.xml").replace('<p:cSld name="Default Layout">', '<p:cSld name="Слайд курса">')
    wr("ppt/slideLayouts/slideLayout1.xml", lay)
    wr("ppt/slideLayouts/_rels/slideLayout1.xml.rels",
       '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
       '<Relationship Id="rId1" Type="%s/slideMaster" Target="../slideMasters/slideMaster1.xml"/></Relationships>' % R_DOC)
    th = rd("ppt/theme/theme1.xml")
    for tag, val in theme_colors.items():
        th = re.sub(r"(<a:%s>)<a:(?:srgbClr|sysClr)[^>]*/>" % tag, r'\1<a:srgbClr val="%s"/>' % val, th, count=1)
    th = th.replace('<a:clrScheme name="X Theme Light Color">', '<a:clrScheme name="Ipak Yuli Bank">')
    th = th.replace('<a:latin typeface="Inter Bold"', '<a:latin typeface="Inter"')
    wr("ppt/theme/theme1.xml", th)
    for n in ("ppt/presProps.xml", "ppt/viewProps.xml", "ppt/tableStyles.xml"):
        wr(n, rd(n))
    pres = rd("ppt/presentation.xml")
    dts = re.search(r"<p:defaultTextStyle>.*?</p:defaultTextStyle>", pres, re.S).group(0)
    wr("ppt/presentation.xml",
       '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
       'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" saveSubsetFonts="1">'
       '<p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId1"/></p:sldMasterIdLst><p:sldIdLst></p:sldIdLst>'
       '<p:sldSz cx="12192000" cy="6858000"/><p:notesSz cx="6858000" cy="9144000"/>%s</p:presentation>' % dts)
    wr("_rels/.rels",
       '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
       '<Relationship Id="rId1" Type="%s/officeDocument" Target="ppt/presentation.xml"/>'
       '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>'
       '<Relationship Id="rId3" Type="%s/extended-properties" Target="docProps/app.xml"/></Relationships>' % (R_DOC, R_DOC))
    wr("docProps/core.xml",
       '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
       'xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:dcmitype="http://purl.org/dc/dcmitype/" '
       'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><dc:title>%s</dc:title><dc:creator>Ipak Yuli Bank</dc:creator><dc:language>ru-RU</dc:language></cp:coreProperties>' % escape(title))
    wr("docProps/app.xml",
       '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" '
       'xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes"><Application>Microsoft Office PowerPoint</Application><PresentationFormat>Широкоэкранный</PresentationFormat></Properties>')


class Deck:
    def __init__(self, root):
        self.root = root
        self.slides = []
        self.cur_no = 0
        self.media_map = {}      # abs path -> file name in ppt/media
        self.media_size = {}

    def new(self, dark=False, name="", transition="fade"):
        s = Slide(self, dark=dark, name=name, transition=transition)
        self.slides.append(s)
        self.cur_no = len(self.slides)
        s.no = self.cur_no
        return s

    def media(self, path):
        path = os.path.abspath(path)
        if path not in self.media_map:
            ext = os.path.splitext(path)[1].lower()
            fn = "image%d%s" % (len(self.media_map) + 1, ext)
            shutil.copyfile(path, os.path.join(self.root, "ppt/media", fn))
            self.media_map[path] = fn
            self.media_size[fn] = Image.open(path).size
        return self.media_map[path]

    def save(self, out_pptx):
        root = self.root
        sld_ids, prels = "", ""
        ct_over = ""
        for i, s in enumerate(self.slides, 1):
            open(os.path.join(root, "ppt/slides/slide%d.xml" % i), "w", encoding="utf-8").write(s.xml())
            rx = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            for target, (rid, typ) in s.rels.items():
                rx += '<Relationship Id="%s" Type="%s" Target="%s"/>' % (rid, typ, target)
            rx += "</Relationships>"
            open(os.path.join(root, "ppt/slides/_rels/slide%d.xml.rels" % i), "w", encoding="utf-8").write(rx)
            sld_ids += '<p:sldId id="%d" r:id="rId%d"/>' % (255 + i, 100 + i)
            prels += '<Relationship Id="rId%d" Type="%s/slide" Target="slides/slide%d.xml"/>' % (100 + i, R_DOC, i)
            ct_over += '<Override PartName="/ppt/slides/slide%d.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>' % i
        p = os.path.join(root, "ppt/presentation.xml")
        pres = open(p, encoding="utf-8").read().replace("<p:sldIdLst></p:sldIdLst>", "<p:sldIdLst>%s</p:sldIdLst>" % sld_ids)
        open(p, "w", encoding="utf-8").write(pres)
        open(os.path.join(root, "ppt/_rels/presentation.xml.rels"), "w", encoding="utf-8").write(
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="%s/slideMaster" Target="slideMasters/slideMaster1.xml"/>'
            '<Relationship Id="rId2" Type="%s/presProps" Target="presProps.xml"/>'
            '<Relationship Id="rId3" Type="%s/viewProps" Target="viewProps.xml"/>'
            '<Relationship Id="rId4" Type="%s/theme" Target="theme/theme1.xml"/>'
            '<Relationship Id="rId5" Type="%s/tableStyles" Target="tableStyles.xml"/>%s</Relationships>' % (R_DOC, R_DOC, R_DOC, R_DOC, R_DOC, prels))
        open(os.path.join(root, "[Content_Types].xml"), "w", encoding="utf-8").write(
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="png" ContentType="image/png"/><Default Extension="jpeg" ContentType="image/jpeg"/>'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/ppt/presentation.xml" ContentType="%s"/>'
            '<Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>'
            '<Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>'
            '<Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>'
            '<Override PartName="/ppt/presProps.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presProps+xml"/>'
            '<Override PartName="/ppt/viewProps.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.viewProps+xml"/>'
            '<Override PartName="/ppt/tableStyles.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.tableStyles+xml"/>'
            '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>'
            '<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>'
            '%s</Types>' % (CT_MAIN, ct_over))
        if os.path.exists(out_pptx):
            os.remove(out_pptx)
        with zipfile.ZipFile(out_pptx, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.write(os.path.join(root, "[Content_Types].xml"), "[Content_Types].xml")
            for base, _, files in os.walk(root):
                for f in sorted(files):
                    full = os.path.join(base, f)
                    arc = os.path.relpath(full, root)
                    if arc == "[Content_Types].xml":
                        continue
                    zf.write(full, arc)
