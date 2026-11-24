"""Check a pptx: every shape inside the slide frame and every text fits its box (Manrope metrics)."""
import os
import sys
from PIL import ImageFont
from pptx import Presentation
from pptx.oxml.ns import qn

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "fonts")
EMU = 914400
FILES = {"Manrope": "Manrope-400.ttf", "Manrope Medium": "Manrope-500.ttf", "Manrope SemiBold": "Manrope-600.ttf",
         "Manrope Light": "Manrope-300.ttf", "Manrope Bold": "Manrope-700.ttf"}
LINE_K = 1.366
_cache = {}


def font(name, bold):
    key = "Manrope Bold" if (bold and name == "Manrope") else name
    path = os.path.join(FONTS, FILES.get(key, "Manrope-400.ttf"))
    if path not in _cache:
        _cache[path] = ImageFont.truetype(path, 100)
    return _cache[path]


def width_pt(text, fname, bold, size):
    return font(fname, bold).getlength(text) * size / 100.0


def para_lines(p_el, avail_pt):
    """Return (height_pt, overflow_word) for one a:p."""
    tokens = []  # (text, fname, bold, size) or 'BR'
    max_size = 0
    for ch in p_el:
        if ch.tag == qn("a:r"):
            rpr = ch.find(qn("a:rPr"))
            size = int(rpr.get("sz", "1800")) / 100 if rpr is not None else 18
            latin = rpr.find(qn("a:latin")) if rpr is not None else None
            fname = latin.get("typeface") if latin is not None else "Manrope"
            bold = rpr is not None and rpr.get("b") == "1"
            text = ch.find(qn("a:t")).text or ""
            max_size = max(max_size, size)
            words = text.split(" ")
            for i, w in enumerate(words):
                tokens.append((w + (" " if i < len(words) - 1 else ""), fname, bold, size))
        elif ch.tag == qn("a:br"):
            tokens.append("BR")
    if not tokens:
        end = p_el.find(qn("a:endParaRPr"))
        size = int(end.get("sz", "1800")) / 100 if end is not None else 18
        return size * LINE_K, None
    lines, cur, bad = 1, 0.0, None
    for t in tokens:
        if t == "BR":
            lines += 1
            cur = 0.0
            continue
        w = width_pt(t[0], t[1], t[2], t[3])
        w_trim = width_pt(t[0].rstrip(), t[1], t[2], t[3])
        if cur > 0 and cur + w_trim > avail_pt:
            lines += 1
            cur = 0.0
        if w_trim > avail_pt:
            bad = t[0]
        cur += w
    spc = 0
    ppr = p_el.find(qn("a:pPr"))
    if ppr is not None:
        aft = ppr.find(qn("a:spcAft"))
        if aft is not None and aft.find(qn("a:spcPts")) is not None:
            spc = int(aft.find(qn("a:spcPts")).get("val")) / 100
    return lines * max_size * LINE_K + spc, bad


def walk(shapes):
    for sh in shapes:
        yield sh
        if sh.shape_type == 6:
            yield from walk(sh.shapes)


def check(path):
    prs = Presentation(path)
    W, H = prs.slide_width / EMU, prs.slide_height / EMU
    problems = []
    for n, s in enumerate(prs.slides, 1):
        for sh in walk(s.shapes):
            if sh.left is None:
                continue
            l, t = sh.left / EMU, sh.top / EMU
            r, b = l + sh.width / EMU, t + sh.height / EMU
            if l < -0.005 or t < -0.005 or r > W + 0.005 or b > H + 0.005:
                problems.append((n, sh.name, f"за кадром ({l:.2f},{t:.2f})–({r:.2f},{b:.2f})"))
            if not getattr(sh, "has_text_frame", False) or not sh.has_text_frame:
                continue
            if not sh.text_frame.text.strip():
                continue
            body = sh.text_frame._txBody.find(qn("a:bodyPr"))
            li = int(body.get("lIns", 91440)) / EMU
            ri = int(body.get("rIns", 91440)) / EMU
            ti = int(body.get("tIns", 45720)) / EMU
            bi = int(body.get("bIns", 45720)) / EMU
            avail_w = (sh.width / EMU - li - ri) * 72 * 0.97
            avail_h = (sh.height / EMU - ti - bi) * 72
            # shapes with geometry (pills, bubbles) have less usable room
            geom = sh._element.find(".//" + qn("a:prstGeom"))
            if geom is not None and geom.get("prst") in ("roundRect", "ellipse", "wedgeRoundRectCallout"):
                avail_w *= 0.92
            total, bad = 0.0, None
            for p in sh.text_frame._txBody.findall(qn("a:p")):
                h, b_ = para_lines(p, avail_w)
                total += h
                bad = bad or b_
            if bad:
                problems.append((n, sh.name, f"слово не влезает по ширине: «{bad.strip()}»"))
            if total > avail_h + 2:
                problems.append((n, sh.name, f"текст выше рамки: нужно {total / 72:.2f} in, есть {avail_h / 72:.2f} in"))
    return problems


if __name__ == "__main__":
    probs = check(sys.argv[1])
    for p in probs:
        print("слайд %d · %s · %s" % p)
    print("проблем:", len(probs))
