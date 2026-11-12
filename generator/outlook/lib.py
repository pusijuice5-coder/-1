# -*- coding: utf-8 -*-
"""Slide builder for the Outlook course.

Writes raw PresentationML into an unpacked base package (generator/outlook/base).
Design language: black background, blurred neon glow, glass cards, Morph transitions.
Every object gets a '!!name': equal names on neighbouring slides are morphed into each other,
unique names simply fade - so nothing morphs by accident.
"""
import os, re, shutil, datetime
from xml.sax.saxutils import escape
from PIL import ImageFont, Image

EMU = 914400
SW, SH = 13.333, 7.5

# ---------------------------------------------------------------- palette / theme
THEMES = {
    "magenta": dict(ACC="FF00DB", ACC2="8A3DFF", ACC_SOFT="FF7AEB", CARD1="1B1541", CARD2="10110F",
                    HL1="A00A96", HL2="FF00DB", TINT="2A0A33", suffix="", logo="logo_white"),
    "green": dict(ACC="3DEB6C", ACC2="00C2A0", ACC_SOFT="8CF5A8", CARD1="0E3320", CARD2="0D120F",
                  HL1="0E7A36", HL2="2FD45F", TINT="0A2A18", suffix="_g", logo="logo_color"),
}
TH = dict(THEMES["magenta"])
BLACK = "000000"
WHITE = "FFFFFF"
TEXT = "D2C9D2"      # body text on dark (taken from the reference deck)
MUTED = "9C92A3"
PANEL = "151515"     # dark panel under opaque 3D tiles (reference)
OK = "3DDC84"
BAD = "FF5C7A"
WARNC = "FFC53D"

FONT = "Segoe UI"
FONT_L = "Segoe UI Light"
FONT_SB = "Segoe UI Semibold"
LANG = "ru-RU"


def set_theme(name):
    TH.clear()
    TH.update(THEMES[name])


def A(k):
    return TH[k]


ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
_IMG_SIZE = {}


def img_size(fn):
    if fn not in _IMG_SIZE:
        with Image.open(os.path.join(ASSETS, fn)) as im:
            _IMG_SIZE[fn] = im.size
    return _IMG_SIZE[fn]


# ---------------------------------------------------------------- text metrics (Inter is a slightly wider stand-in for Segoe UI)
_FDIR = "/usr/share/fonts/opentype/inter/"
_FFILE = {FONT: "Inter-Regular.otf", FONT_L: "Inter-Light.otf", FONT_SB: "Inter-SemiBold.otf", "bold": "Inter-Bold.otf"}
_fonts = {}


def _font(face, sz, bold):
    key = (face, sz, bold)
    if key not in _fonts:
        fn = _FFILE["bold"] if (bold and face == FONT) else _FFILE.get(face, "Inter-Regular.otf")
        _fonts[key] = ImageFont.truetype(_FDIR + fn, int(sz * 10))
    return _fonts[key]


def e(v):
    return int(round(v * EMU))


WARN = []
TR = {}
SEEN = []


def T(s):
    if s and re.search("[А-Яа-яЁё]", s) and s not in SEEN:
        SEEN.append(s)
    return TR.get(s, s)


def parse_runs(s):
    """'plain **white semibold** ~~accent~~' -> [(text, style)], style in '', 'b', 'a'."""
    s = T(s)
    out = []
    for part in re.split(r"(\*\*.+?\*\*|~~.+?~~)", s):
        if not part:
            continue
        if part.startswith("**"):
            out.append((part[2:-2], "b"))
        elif part.startswith("~~"):
            out.append((part[2:-2], "a"))
        else:
            out.append((part, ""))
    return out


def pitch(sz, lnsp):
    """Exact line pitch in points - makes vertical layout independent of the font actually installed."""
    return round(sz * 1.22 * lnsp * 2) / 2.0


def norm_paras(text):
    if isinstance(text, str):
        return [{"t": t} for t in text.split("\n")]
    return [({"t": p} if isinstance(p, str) else dict(p)) for p in text]


def text_lines(p, w_in, sz, font, bold, indent=0.0):
    psz = p.get("sz", sz)
    avail = (w_in - indent) * 72 * 10
    words = []
    for t, st in parse_runs(p["t"]):
        f = font
        b = bold or p.get("b", False)
        if st in ("b", "a"):
            f = FONT_SB
        for wd in re.split(r"(\s+)", t):
            if wd:
                words.append((wd, _font(p.get("font", f), psz, b)))
    lines, cur = 1, 0.0
    for wd, f in words:
        wl = f.getlength(wd)
        if cur + wl > avail and not wd.isspace() and cur > 0:
            lines += 1
            cur = wl
        else:
            cur += wl
    return lines


def text_height(text, w_in, sz, font=FONT, bold=False, lnsp=1.0, spc_after=0, bullet=False):
    """Rendered height (inches) of paragraphs in a box w_in wide (insets excluded)."""
    total = 0.0
    paras = norm_paras(text)
    for i, p in enumerate(paras):
        psz = p.get("sz", sz)
        ind = 0.24 if p.get("bullet", bullet) else 0.0
        n = text_lines(p, w_in, sz, font, bold, ind)
        total += n * pitch(psz, p.get("lnsp", lnsp)) / 72.0
        if i < len(paras) - 1:
            total += p.get("spcAft", spc_after) / 72.0
        total += p.get("spcBef", 0) / 72.0
    return total


def text_width(s, sz, font=FONT, bold=False):
    return sum(_font(FONT_SB if st else font, sz, bold).getlength(t) for t, st in parse_runs(s)) / 720.0


# ---------------------------------------------------------------- slide
class Slide:
    def __init__(self, deck, key, title="", notes="", trans="morph", dur=1000, adv_click=True, hidden_title=False):
        self.deck = deck
        self.key = key
        self.items = []
        self.tail = []         # drawn above everything else (footer navigation)
        self.stack = []
        self.rels = {}
        self.nid = 2
        self.anims = []        # (spid, kind, delay)
        self.triggers = []     # (click_spid, [show ids], [hide ids])
        self.notes = notes
        self.trans = trans
        self.dur = dur
        self.adv_click = adv_click
        self.title_text = title
        self.links = []        # (placeholder, target key) resolved on save
        self._rel("../slideLayouts/slideLayout6.xml", "slideLayout")
        self._auto = 0

    # -- plumbing
    def _rel(self, target, kind):
        k = target + "#" + kind
        if k in self.rels:
            return self.rels[k][0]
        rid = "rId%d" % (len(self.rels) + 1)
        types = {
            "slideLayout": "http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout",
            "image": "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image",
            "slide": "http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide",
            "notesSlide": "http://schemas.openxmlformats.org/officeDocument/2006/relationships/notesSlide",
        }
        self.rels[k] = (rid, types[kind], target)
        return rid

    def _id(self):
        i = self.nid
        self.nid += 1
        return i

    def _name(self, name):
        """'!!x' names are shared between slides (morph); anything else is made unique so it only fades."""
        if name and name.startswith("!!"):
            return name
        self._auto += 1
        return "!!%s·%s·%d" % (self.key, name or "o", self._auto)

    def _add(self, xml, bbox):
        if self.stack:
            self.stack[-1]["items"].append((xml, bbox))
        else:
            self.items.append(xml)

    def _link(self, link):
        """link: 'next' | 'prev' | 'first' | 'last' | ('slide', key) -> hlinkClick xml"""
        if not link:
            return ""
        jumps = {"next": "nextslide", "prev": "previousslide", "first": "firstslide", "last": "lastslide"}
        if link in jumps:
            return '<a:hlinkClick r:id="" action="ppaction://hlinkshowjump?jump=%s"/>' % jumps[link]
        ph = "@@LINK%d@@" % len(self.links)
        self.links.append((ph, link[1]))
        return '<a:hlinkClick r:id="%s" action="ppaction://hlinksldjump"/>' % ph

    # -- groups
    def begin(self, name="grp"):
        gid = self._id()
        self.stack.append({"id": gid, "name": self._name(name), "items": []})
        return gid

    def end(self, anim=None, rot=0, link=None):
        g = self.stack.pop()
        if not g["items"]:
            return g["id"]
        xs = [b[0] for _, b in g["items"]]; ys = [b[1] for _, b in g["items"]]
        x2 = [b[0] + b[2] for _, b in g["items"]]; y2 = [b[1] + b[3] for _, b in g["items"]]
        x, y, w, h = min(xs), min(ys), max(x2) - min(xs), max(y2) - min(ys)
        off = '<a:off x="%d" y="%d"/><a:ext cx="%d" cy="%d"/><a:chOff x="%d" y="%d"/><a:chExt cx="%d" cy="%d"/>' % (
            e(x), e(y), e(w), e(h), e(x), e(y), e(w), e(h))
        xml = ('<p:grpSp><p:nvGrpSpPr><p:cNvPr id="%d" name="%s"/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>'
               '<p:grpSpPr><a:xfrm%s>%s</a:xfrm></p:grpSpPr>%s</p:grpSp>') % (
            g["id"], escape(g["name"]), ' rot="%d"' % int(rot * 60000) if rot else "", off, "".join(i for i, _ in g["items"]))
        self._add(xml, (x, y, w, h))
        if anim is not None:
            self.anims.append((g["id"], "grp", anim))
        return g["id"]

    # -- fills & lines
    def _clr(self, c, alpha=None):
        a = '<a:alpha val="%d"/>' % int(alpha * 1000) if alpha is not None else ""
        return '<a:srgbClr val="%s">%s</a:srgbClr>' % (c, a)

    def _fill(self, fill):
        """None | 'RRGGBB' | ('RRGGBB', alpha%) | ('grad', [(pos%, color, alpha%|None)], angle_deg) | 'glass' | 'accent' | 'soft' | 'hit'"""
        if fill is None:
            return "<a:noFill/>"
        if fill == "glass":
            fill = ("grad", [(0, A("CARD1"), None), (43, BLACK, None), (100, A("CARD2"), None)], 60)
        elif fill == "glass2":
            fill = ("grad", [(0, A("CARD1"), 92), (55, "0A0A10", 92), (100, A("CARD2"), 92)], 60)
        elif fill == "accent":
            fill = ("grad", [(0, A("HL1"), None), (50, A("HL2"), None), (100, A("HL1"), None)], 20)
        elif fill == "soft":
            fill = (WHITE, 6)
        elif fill == "hit":
            fill = (WHITE, 0)
        if isinstance(fill, str):
            return "<a:solidFill>%s</a:solidFill>" % self._clr(fill)
        if fill[0] == "grad":
            gs = "".join('<a:gs pos="%d">%s</a:gs>' % (p * 1000, self._clr(c, al)) for p, c, al in fill[1])
            return '<a:gradFill rotWithShape="1"><a:gsLst>%s</a:gsLst><a:lin ang="%d" scaled="0"/></a:gradFill>' % (gs, fill[2] * 60000)
        return "<a:solidFill>%s</a:solidFill>" % self._clr(fill[0], fill[1])

    def _line(self, line, lw=0.75, dash=None):
        """None | 'glass' | 'glass2' | 'RRGGBB' | ('RRGGBB', alpha%)"""
        if not line:
            return "<a:ln><a:noFill/></a:ln>"
        d = '<a:prstDash val="%s"/>' % dash if dash else ""
        if line in ("glass", "glass2"):
            a1, a2, a3 = (41, 24, 34) if line == "glass" else (26, 12, 20)
            gs = ('<a:gs pos="0">%s</a:gs><a:gs pos="45000">%s</a:gs><a:gs pos="100000">%s</a:gs>' % (
                self._clr(WHITE, a1), self._clr(WHITE, a2), self._clr(WHITE, a3)))
            return '<a:ln w="%d"><a:gradFill><a:gsLst>%s</a:gsLst><a:lin ang="5400000" scaled="1"/></a:gradFill>%s</a:ln>' % (int(lw * 12700), gs, d)
        if isinstance(line, str):
            return '<a:ln w="%d"><a:solidFill>%s</a:solidFill>%s</a:ln>' % (int(lw * 12700), self._clr(line), d)
        return '<a:ln w="%d"><a:solidFill>%s</a:solidFill>%s</a:ln>' % (int(lw * 12700), self._clr(line[0], line[1]), d)

    def _fx(self, fx):
        if fx == "glow":      # neon halo for highlighted elements
            return ('<a:effectLst><a:glow rad="139700">%s</a:glow></a:effectLst>' % self._clr(A("ACC"), 38))
        if fx == "glow_s":
            return ('<a:effectLst><a:glow rad="63500">%s</a:glow></a:effectLst>' % self._clr(A("ACC"), 45))
        if fx == "shadow":
            return ('<a:effectLst><a:outerShdw blurRad="381000" dist="127000" dir="5400000" algn="t" rotWithShape="0">'
                    '%s</a:outerShdw></a:effectLst>' % self._clr(BLACK, 60))
        return ""

    # -- text
    def _paras(self, text, sz, color, bold, align, lnsp, spc_after, bullet, font):
        out = []
        for p in norm_paras(text):
            psz = p.get("sz", sz); pcol = p.get("color", color); pb = p.get("b", bold)
            pfont = p.get("font", font)
            pbul = p.get("bullet", bullet)
            ppr = '<a:pPr algn="%s"%s>' % (p.get("align", align), ' marL="%d" indent="%d"' % (e(0.24), -e(0.24)) if pbul else "")
            ppr += '<a:lnSpc><a:spcPts val="%d"/></a:lnSpc>' % int(pitch(psz, p.get("lnsp", lnsp)) * 100)
            ppr += '<a:spcBef><a:spcPts val="%d"/></a:spcBef>' % int(p.get("spcBef", 0) * 100)
            ppr += '<a:spcAft><a:spcPts val="%d"/></a:spcAft>' % int(p.get("spcAft", spc_after) * 100)
            if pbul:
                bc = pbul if isinstance(pbul, str) and len(pbul) == 6 else A("ACC")
                ch = p.get("bchar", "&#8226;")
                ppr += '<a:buClr><a:srgbClr val="%s"/></a:buClr><a:buSzPct val="100000"/><a:buFont typeface="Arial"/><a:buChar char="%s"/>' % (bc, ch)
            else:
                ppr += "<a:buNone/>"
            ppr += "</a:pPr>"
            runs = ""
            for t, st in parse_runs(p["t"]):
                f, col, b = pfont, pcol, pb
                if st == "b":
                    f, col = FONT_SB, p.get("bcolor", WHITE)
                elif st == "a":
                    f, col = FONT_SB, A("ACC")
                runs += ('<a:r><a:rPr lang="%s" sz="%d" b="%d" i="0" dirty="0"><a:solidFill><a:srgbClr val="%s"/></a:solidFill>'
                         '<a:latin typeface="%s"/><a:ea typeface="%s"/><a:cs typeface="%s"/></a:rPr><a:t>%s</a:t></a:r>') % (
                    LANG, int(psz * 100), 1 if b else 0, col, f, f, f, escape(t))
            end = '<a:endParaRPr lang="%s" sz="%d" dirty="0"><a:latin typeface="%s"/></a:endParaRPr>' % (LANG, int(psz * 100), pfont)
            out.append("<a:p>%s%s%s</a:p>" % (ppr, runs, end))
        return "".join(out)

    def shape(self, x, y, w, h, geom="rect", fill=None, line=None, lw=0.75, dash=None, radius=None, fx=None,
              text=None, sz=14, color=TEXT, bold=False, align="l", anchor="t", inset=(0.1, 0.05, 0.1, 0.05),
              lnsp=1.0, spc_after=0, bullet=False, font=FONT, name=None, anim=None, adj=None, rot=0,
              flipH=False, flipV=False, check=True, txbox=False, link=None, ph=None, tip=None):
        sid = self._id()
        nm = self._name(name)
        av = ""
        if radius is not None and geom in ("roundRect", "round2SameRect"):
            v = min(50000, int(radius * 100000 / min(w, h)))
            av = '<a:gd name="adj" fmla="val %d"/>' % v if geom == "roundRect" else '<a:gd name="adj1" fmla="val %d"/><a:gd name="adj2" fmla="val 0"/>' % v
        if adj:
            av += "".join('<a:gd name="%s" fmla="val %d"/>' % (k, v) for k, v in adj.items())
        attrs = (' rot="%d"' % int(rot * 60000) if rot else "") + (' flipH="1"' if flipH else "") + (' flipV="1"' if flipV else "")
        sppr = '<p:spPr><a:xfrm%s><a:off x="%d" y="%d"/><a:ext cx="%d" cy="%d"/></a:xfrm><a:prstGeom prst="%s"><a:avLst>%s</a:avLst></a:prstGeom>%s%s%s</p:spPr>' % (
            attrs, e(x), e(y), e(w), e(h), geom, av, self._fill(fill), self._line(line, lw, dash), self._fx(fx))
        has_text = text is not None and text != ""
        if has_text:
            pxml = self._paras(text, sz, color, bold, align, lnsp, spc_after, bullet, font)
            l, t, r, b = inset
            body = ('<p:txBody><a:bodyPr wrap="square" lIns="%d" tIns="%d" rIns="%d" bIns="%d" anchor="%s" rtlCol="0"><a:noAutofit/></a:bodyPr><a:lstStyle/>%s</p:txBody>') % (
                e(l), e(t), e(r), e(b), anchor, pxml)
            if check:
                need = text_height(text, w - l - r, sz, font, bold, lnsp, spc_after, bullet) + t + b
                if need > h + 0.03:
                    WARN.append("%s: text overflow %.2f > %.2f in: %s" % (self.key, need, h, str(text)[:70]))
        else:
            body = '<p:txBody><a:bodyPr rtlCol="0" anchor="ctr"/><a:lstStyle/><a:p><a:endParaRPr lang="ru-RU" dirty="0"/></a:p></p:txBody>'
        cnv = '<p:cNvSpPr txBox="1"/>' if txbox else "<p:cNvSpPr/>"
        nvpr = "<p:nvPr/>"
        if ph:
            cnv = '<p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr>'
            nvpr = '<p:nvPr><p:ph type="%s"/></p:nvPr>' % ph
        descr = ' descr="%s"' % escape(tip) if tip else ""
        xml = '<p:sp><p:nvSpPr><p:cNvPr id="%d" name="%s"%s>%s</p:cNvPr>%s%s</p:nvSpPr>%s%s</p:sp>' % (
            sid, escape(nm), descr, self._link(link), cnv, nvpr, sppr, body)
        self._add(xml, (x, y, w, h))
        if anim is not None:
            self.anims.append((sid, "sp" if has_text else "spbg", anim))
        return sid

    def rect(self, x, y, w, h, **k):
        return self.shape(x, y, w, h, geom="rect", **k)

    def rrect(self, x, y, w, h, r=0.2, **k):
        return self.shape(x, y, w, h, geom="roundRect", radius=r, **k)

    def oval(self, x, y, w, h, **k):
        return self.shape(x, y, w, h, geom="ellipse", **k)

    def text(self, x, y, w, h, text, **k):
        k.setdefault("inset", (0, 0, 0, 0))
        return self.shape(x, y, w, h, geom="rect", text=text, txbox=True, **k)

    def line(self, x1, y1, x2, y2, color=(WHITE, 22), lw=0.75, dash=None, head=None, tail=None, name=None, anim=None):
        sid = self._id()
        x, y = min(x1, x2), min(y1, y2)
        w, h = abs(x2 - x1), abs(y2 - y1)
        fl = (' flipH="1"' if x2 < x1 else "") + (' flipV="1"' if y2 < y1 else "")
        he = '<a:headEnd type="%s" w="med" len="med"/>' % head if head else ""
        te = '<a:tailEnd type="%s" w="med" len="med"/>' % tail if tail else ""
        d = '<a:prstDash val="%s"/>' % dash if dash else ""
        c = self._clr(color) if isinstance(color, str) else self._clr(color[0], color[1])
        xml = ('<p:cxnSp><p:nvCxnSpPr><p:cNvPr id="%d" name="%s"/><p:cNvCxnSpPr/><p:nvPr/></p:nvCxnSpPr>'
               '<p:spPr><a:xfrm%s><a:off x="%d" y="%d"/><a:ext cx="%d" cy="%d"/></a:xfrm><a:prstGeom prst="line"><a:avLst/></a:prstGeom>'
               '<a:ln w="%d" cap="rnd"><a:solidFill>%s</a:solidFill>%s<a:round/>%s%s</a:ln></p:spPr></p:cxnSp>') % (
            sid, escape(self._name(name)), fl, e(x), e(y), e(w), e(h), int(lw * 12700), c, d, he, te)
        self._add(xml, (x, y, max(w, 0.01), max(h, 0.01)))
        if anim is not None:
            self.anims.append((sid, "cxn", anim))
        return sid

    def freeform(self, pts, x, y, w, h, color=None, lw=1.5, fill=None, closed=False, name=None, anim=None, curve=False, fx=None):
        """pts: list of (fx, fy) in 0..1 of the box; curve=True -> smooth cubic through the points."""
        sid = self._id()
        W, H = e(w), e(h)
        P = [(int(px * W), int(py * H)) for px, py in pts]
        path = '<a:moveTo><a:pt x="%d" y="%d"/></a:moveTo>' % P[0]
        if curve and len(P) > 2:
            n = len(P)
            for i in range(n - 1):
                p0 = P[i - 1] if i > 0 else P[i]; p1 = P[i]; p2 = P[i + 1]; p3 = P[i + 2] if i + 2 < n else P[i + 1]
                c1 = (p1[0] + (p2[0] - p0[0]) / 6.0, p1[1] + (p2[1] - p0[1]) / 6.0)
                c2 = (p2[0] - (p3[0] - p1[0]) / 6.0, p2[1] - (p3[1] - p1[1]) / 6.0)
                path += '<a:cubicBezTo><a:pt x="%d" y="%d"/><a:pt x="%d" y="%d"/><a:pt x="%d" y="%d"/></a:cubicBezTo>' % (
                    c1[0], c1[1], c2[0], c2[1], p2[0], p2[1])
        else:
            for px, py in P[1:]:
                path += '<a:lnTo><a:pt x="%d" y="%d"/></a:lnTo>' % (px, py)
        if closed:
            path += "<a:close/>"
        if color:
            c = self._clr(color) if isinstance(color, str) else self._clr(color[0], color[1])
            ln = '<a:ln w="%d" cap="rnd"><a:solidFill>%s</a:solidFill><a:round/></a:ln>' % (int(lw * 12700), c)
        else:
            ln = "<a:ln><a:noFill/></a:ln>"
        xml = ('<p:sp><p:nvSpPr><p:cNvPr id="%d" name="%s"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x="%d" y="%d"/><a:ext cx="%d" cy="%d"/></a:xfrm>'
               '<a:custGeom><a:avLst/><a:gdLst/><a:ahLst/><a:cxnLst/><a:rect l="0" t="0" r="r" b="b"/><a:pathLst><a:path w="%d" h="%d"%s>%s</a:path></a:pathLst></a:custGeom>%s%s%s</p:spPr>'
               '<p:txBody><a:bodyPr rtlCol="0" anchor="ctr"/><a:lstStyle/><a:p><a:endParaRPr lang="ru-RU" dirty="0"/></a:p></p:txBody></p:sp>') % (
            sid, escape(self._name(name)), e(x), e(y), W, H, W, H, "" if (fill or closed) else ' fill="none"', path, self._fill(fill), ln, self._fx(fx))
        self._add(xml, (x, y, w, h))
        if anim is not None:
            self.anims.append((sid, "spbg", anim))
        return sid

    def pic(self, fn, x, y, w=None, h=None, crop=None, name=None, anim=None, geom="rect", radius=None, alpha=None, rot=0,
            flipH=False, flipV=False, link=None):
        """fn: file in assets/. Give w or h (the other follows the aspect ratio) or both."""
        self.deck.use_media(fn)
        rid = self._rel("../media/" + fn, "image")
        sid = self._id()
        pw, ph = img_size(fn)
        l, t, r, b = crop or (0, 0, 0, 0)
        asp = (1 - l - r) * pw / ((1 - t - b) * ph)
        if w is None:
            w = h * asp
        if h is None:
            h = w / asp
        src = '<a:srcRect l="%d" t="%d" r="%d" b="%d"/>' % tuple(int(v * 100000) for v in (l, t, r, b)) if crop else ""
        am = '<a:alphaModFix amt="%d"/>' % int(alpha * 1000) if alpha is not None else ""
        av = ""
        if geom == "roundRect" and radius:
            av = '<a:gd name="adj" fmla="val %d"/>' % min(50000, int(radius * 100000 / min(w, h)))
        attrs = (' rot="%d"' % int(rot * 60000) if rot else "") + (' flipH="1"' if flipH else "") + (' flipV="1"' if flipV else "")
        xml = ('<p:pic><p:nvPicPr><p:cNvPr id="%d" name="%s">%s</p:cNvPr><p:cNvPicPr><a:picLocks noChangeAspect="1"/></p:cNvPicPr><p:nvPr/></p:nvPicPr>'
               '<p:blipFill><a:blip r:embed="%s">%s</a:blip>%s<a:stretch><a:fillRect/></a:stretch></p:blipFill>'
               '<p:spPr><a:xfrm%s><a:off x="%d" y="%d"/><a:ext cx="%d" cy="%d"/></a:xfrm><a:prstGeom prst="%s"><a:avLst>%s</a:avLst></a:prstGeom></p:spPr></p:pic>') % (
            sid, escape(self._name(name)), self._link(link), rid, am, src, attrs, e(x), e(y), e(w), e(h), geom, av)
        self._add(xml, (x, y, w, h))
        if anim is not None:
            self.anims.append((sid, "pic", anim))
        return sid

    # -- interactivity
    def trigger(self, click_sid, show=(), hide=()):
        self.triggers.append((click_sid, list(show), list(hide)))

    def anim(self, sid, delay=0, kind="grp"):
        self.anims.append((sid, kind, delay))

    # -- serialisation
    def _timing(self):
        if not self.anims and not self.triggers:
            return ""
        cid = [4]

        def nid():
            cid[0] += 1
            return cid[0]

        def entr(sid, delay, node, grp_attr=""):
            a1, a2, a3 = nid(), nid(), nid()
            return ('<p:par><p:cTn id="%d" presetID="10" presetClass="entr" presetSubtype="0" fill="hold"%s nodeType="%s"><p:stCondLst><p:cond delay="%d"/></p:stCondLst><p:childTnLst>'
                    '<p:set><p:cBhvr><p:cTn id="%d" dur="1" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst></p:cTn><p:tgtEl><p:spTgt spid="%d"/></p:tgtEl>'
                    '<p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst></p:cBhvr><p:to><p:strVal val="visible"/></p:to></p:set>'
                    '<p:animEffect transition="in" filter="fade"><p:cBhvr><p:cTn id="%d" dur="450"/><p:tgtEl><p:spTgt spid="%d"/></p:tgtEl></p:cBhvr></p:animEffect></p:childTnLst></p:cTn></p:par>') % (
                a1, grp_attr, node, delay, a2, sid, a3, sid)

        def exit_(sid, node):
            a1, a2, a3 = nid(), nid(), nid()
            return ('<p:par><p:cTn id="%d" presetID="10" presetClass="exit" presetSubtype="0" fill="hold" nodeType="%s"><p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>'
                    '<p:animEffect transition="out" filter="fade"><p:cBhvr><p:cTn id="%d" dur="200"/><p:tgtEl><p:spTgt spid="%d"/></p:tgtEl></p:cBhvr></p:animEffect>'
                    '<p:set><p:cBhvr><p:cTn id="%d" dur="1" fill="hold"><p:stCondLst><p:cond delay="199"/></p:stCondLst></p:cTn><p:tgtEl><p:spTgt spid="%d"/></p:tgtEl>'
                    '<p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst></p:cBhvr><p:to><p:strVal val="hidden"/></p:to></p:set></p:childTnLst></p:cTn></p:par>') % (
                a1, node, a2, sid, a3, sid)

        main = ""
        bld = ""
        if self.anims:
            inner = ""
            first = True
            for sid, kind, delay in self.anims:
                g0 = ' grpId="0"' if kind in ("sp", "spbg") else ""
                inner += entr(sid, delay, "withEffect", g0)
                first = False
                # gentle rise together with the fade (reverse-played short motion path)
                b1, b2 = nid(), nid()
                g1 = ' grpId="1"' if kind in ("sp", "spbg") else ""
                inner += ('<p:par><p:cTn id="%d" presetID="63" presetClass="path" presetSubtype="0" accel="14000" decel="86000" fill="hold"%s nodeType="withEffect"><p:stCondLst><p:cond delay="%d"/></p:stCondLst><p:childTnLst>'
                          '<p:animMotion origin="layout" path="M 0 0 L 0 0.04 " pathEditMode="relative" rAng="0" ptsTypes="AA"><p:cBhvr><p:cTn id="%d" dur="750" spd="-100000" fill="hold"/>'
                          '<p:tgtEl><p:spTgt spid="%d"/></p:tgtEl><p:attrNameLst><p:attrName>ppt_x</p:attrName><p:attrName>ppt_y</p:attrName></p:attrNameLst></p:cBhvr><p:rCtr x="0" y="2000"/></p:animMotion></p:childTnLst></p:cTn></p:par>') % (
                    b1, g1, delay, b2, sid)
                if kind == "sp":
                    bld += '<p:bldP spid="%d" grpId="0" animBg="1"/><p:bldP spid="%d" grpId="1" animBg="1"/>' % (sid, sid)
                elif kind == "spbg":
                    bld += '<p:bldP spid="%d" grpId="0" animBg="1"/><p:bldP spid="%d" grpId="1" animBg="1"/>' % (sid, sid)
            main = ('<p:seq concurrent="1" nextAc="seek"><p:cTn id="2" dur="indefinite" nodeType="mainSeq"><p:childTnLst>'
                    '<p:par><p:cTn id="3" fill="hold"><p:stCondLst><p:cond delay="indefinite"/><p:cond evt="onBegin" delay="0"><p:tn val="2"/></p:cond></p:stCondLst><p:childTnLst>'
                    '<p:par><p:cTn id="4" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>%s</p:childTnLst></p:cTn></p:par>'
                    '</p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn>'
                    '<p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>'
                    '<p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst></p:seq>') % inner
        inter = ""
        for click, show, hide in self.triggers:
            s1, s2, s3 = nid(), nid(), nid()
            eff = ""
            first = True
            for sid in hide:
                eff += exit_(sid, "clickEffect" if first else "withEffect")
                first = False
            for sid in show:
                eff += entr(sid, 0, "clickEffect" if first else "withEffect")
                first = False
            inter += ('<p:seq concurrent="1" nextAc="seek"><p:cTn id="%d" restart="whenNotActive" fill="hold" evtFilter="cancelBubble" nodeType="interactiveSeq">'
                      '<p:stCondLst><p:cond evt="onClick" delay="0"><p:tgtEl><p:spTgt spid="%d"/></p:tgtEl></p:cond></p:stCondLst>'
                      '<p:endSync evt="end" delay="0"><p:rtn val="all"/></p:endSync><p:childTnLst>'
                      '<p:par><p:cTn id="%d" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>'
                      '<p:par><p:cTn id="%d" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>%s</p:childTnLst></p:cTn></p:par>'
                      '</p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn>'
                      '<p:nextCondLst><p:cond evt="onClick" delay="0"><p:tgtEl><p:spTgt spid="%d"/></p:tgtEl></p:cond></p:nextCondLst></p:seq>') % (
                s1, click, s2, s3, eff, click)
        return ('<p:timing><p:tnLst><p:par><p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot"><p:childTnLst>%s%s</p:childTnLst></p:cTn></p:par></p:tnLst>%s</p:timing>') % (
            main, inter, "<p:bldLst>%s</p:bldLst>" % bld if bld else "")

    def _transition(self):
        adv = "" if self.adv_click else ' advClick="0"'
        if self.trans == "morph":
            return ('<mc:AlternateContent xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" xmlns:p159="http://schemas.microsoft.com/office/powerpoint/2015/09/main">'
                    '<mc:Choice Requires="p159"><p:transition spd="slow"%s xmlns:p14="http://schemas.microsoft.com/office/powerpoint/2010/main" p14:dur="%d"><p159:morph option="byObject"/></p:transition></mc:Choice>'
                    '<mc:Fallback xmlns=""><p:transition spd="slow"%s><p:fade/></p:transition></mc:Fallback></mc:AlternateContent>') % (adv, self.dur, adv)
        if self.trans == "fade":
            return ('<mc:AlternateContent xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" xmlns:p14="http://schemas.microsoft.com/office/powerpoint/2010/main">'
                    '<mc:Choice Requires="p14"><p:transition spd="med"%s p14:dur="700"><p:fade/></p:transition></mc:Choice>'
                    '<mc:Fallback xmlns=""><p:transition spd="med"%s><p:fade/></p:transition></mc:Fallback></mc:AlternateContent>') % (adv, adv)
        return ""

    def xml(self):
        return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
                '<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
                'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"><p:cSld><p:bg><p:bgPr><a:solidFill><a:srgbClr val="000000"/></a:solidFill><a:effectLst/></p:bgPr></p:bg>'
                '<p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>'
                '<p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>%s</p:spTree></p:cSld>'
                '<p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>%s%s</p:sld>') % ("".join(self.items + self.tail), self._transition(), self._timing())


class Deck:
    def __init__(self, root):
        self.root = root
        self.slides = []
        self.media = set()
        self.total = 0

    def use_media(self, fn):
        self.media.add(fn)

    def new(self, key, **k):
        s = Slide(self, key, **k)
        self.slides.append(s)
        return s

    def index(self, key):
        for i, s in enumerate(self.slides):
            if s.key == key:
                return i + 1
        raise KeyError(key)

    def _notes_xml(self, text):
        paras = "".join('<a:p><a:r><a:rPr lang="%s" dirty="0"/><a:t>%s</a:t></a:r></a:p>' % (LANG, escape(t)) for t in text.split("\n"))
        return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
                '<p:notes xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">'
                '<p:cSld><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>'
                '<p:sp><p:nvSpPr><p:cNvPr id="2" name="Slide Image Placeholder 1"/><p:cNvSpPr><a:spLocks noGrp="1" noRot="1" noChangeAspect="1"/></p:cNvSpPr><p:nvPr><p:ph type="sldImg"/></p:nvPr></p:nvSpPr><p:spPr/></p:sp>'
                '<p:sp><p:nvSpPr><p:cNvPr id="3" name="Notes Placeholder 2"/><p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr><p:nvPr><p:ph type="body" idx="1"/></p:nvPr></p:nvSpPr><p:spPr/>'
                '<p:txBody><a:bodyPr/><a:lstStyle/>%s</p:txBody></p:sp></p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:notes>') % paras

    def save(self):
        root = self.root
        for fn in sorted(self.media):
            shutil.copy(os.path.join(ASSETS, fn), os.path.join(root, "ppt/media", fn))
        ct_path = os.path.join(root, "[Content_Types].xml")
        ct = open(ct_path, encoding="utf-8").read()
        if any(f.endswith(".jpg") for f in self.media) and 'Extension="jpg"' not in ct:
            ct = ct.replace("</Types>", '<Default Extension="jpg" ContentType="image/jpeg"/></Types>')
        pres_path = os.path.join(root, "ppt/presentation.xml")
        pres = open(pres_path, encoding="utf-8").read()
        prels_path = os.path.join(root, "ppt/_rels/presentation.xml.rels")
        prels = open(prels_path, encoding="utf-8").read()
        next_rid = max(int(v) for v in re.findall(r'Id="rId(\d+)"', prels)) + 1
        ids = ""
        for no, s in enumerate(self.slides, 1):
            rels = dict(s.rels)
            xml = s.xml()
            for ph, key in s.links:
                try:
                    tgt = "slide%d.xml" % self.index(key)
                except KeyError:
                    WARN.append("%s: link target '%s' is not built" % (s.key, key))
                    tgt = "slide1.xml"
                rid = "rId%d" % (len(rels) + 1)
                rels["link" + ph] = (rid, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide", tgt)
                xml = xml.replace(ph, rid)
            if s.notes:
                nfn = "notesSlide%d.xml" % no
                open(os.path.join(root, "ppt/notesSlides", nfn), "w", encoding="utf-8").write(self._notes_xml(T(s.notes)))
                open(os.path.join(root, "ppt/notesSlides/_rels", nfn + ".rels"), "w", encoding="utf-8").write(
                    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                    '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/notesMaster" Target="../notesMasters/notesMaster1.xml"/>'
                    '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="../slides/slide%d.xml"/></Relationships>' % no)
                ct = ct.replace("</Types>", '<Override PartName="/ppt/notesSlides/%s" ContentType="application/vnd.openxmlformats-officedocument.presentationml.notesSlide+xml"/></Types>' % nfn)
                rid = "rId%d" % (len(rels) + 1)
                rels["notes"] = (rid, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/notesSlide", "../notesSlides/" + nfn)
            rx = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            for rid, typ, target in rels.values():
                rx += '<Relationship Id="%s" Type="%s" Target="%s"/>' % (rid, typ, target)
            rx += "</Relationships>"
            open(os.path.join(root, "ppt/slides/slide%d.xml" % no), "w", encoding="utf-8").write(xml)
            open(os.path.join(root, "ppt/slides/_rels/slide%d.xml.rels" % no), "w", encoding="utf-8").write(rx)
            ct = ct.replace("</Types>", '<Override PartName="/ppt/slides/slide%d.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/></Types>' % no)
            rid = "rId%d" % next_rid
            next_rid += 1
            prels = prels.replace("</Relationships>", '<Relationship Id="%s" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide%d.xml"/></Relationships>' % (rid, no))
            ids += '<p:sldId id="%d" r:id="%s"/>' % (255 + no, rid)
        pres = pres.replace("<p:sldIdLst></p:sldIdLst>", "<p:sldIdLst>%s</p:sldIdLst>" % ids)
        open(ct_path, "w", encoding="utf-8").write(ct)
        open(pres_path, "w", encoding="utf-8").write(pres)
        open(prels_path, "w", encoding="utf-8").write(prels)
        core_p = os.path.join(root, "docProps/core.xml")
        core = open(core_p, encoding="utf-8").read()
        now = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        core = re.sub(r"(<dcterms:(created|modified)[^>]*>)[^<]*", lambda m: m.group(1) + now, core)
        open(core_p, "w", encoding="utf-8").write(core)
