# -*- coding: utf-8 -*-
"""Recurring slide parts: the template's look (white page, accent line, grey rounded cards, one
highlighted card, icon tiles) in the bank's greens, plus the document's coloured frames."""
from lib import *

X0, X1 = 1.125, 12.21          # template margins
CW = X1 - X0
LOGO_C = "logo/logo_color.png"
LOGO_W = "logo/logo_white_lime.png"
BARS = "logo/bars.png"

FRAMES = {
    # kind: fill, line, dark (label/icon), icon
    "advice": (ADV_F, ADV_L, ADV_D, "message-square-quote"),
    "see": (SIT_F, SIT_L, SIT_D, "eye"),
    "situation": (SIT_F, SIT_L, SIT_D, "store"),
    "warn": (WARN_F, WARN_L, WARN_D, "triangle-alert"),
    "stop": (STOP_F, STOP_L, STOP_D, "ban"),
    "how": (CARD, None, GREEN, "workflow"),
}


# ---------------------------------------------------------------- headers
def light(d, name, kicker, title, title_w=9.35, sz=24):
    """White content slide: kicker, title (placeholder), logo, slide number. Returns (slide, content top)."""
    s = d.new(dark=False, name=name)
    s.text(X0, 0.34, 9.3, 0.24, kicker.upper(), sz=10, bold=True, color=GREEN, spc=1.2)
    th = text_height(title, title_w, sz, True, 0.95)
    s.title_ph(X0, 0.62, title_w, th + 0.04, title, sz=sz)
    s.pic(LOGO_C, X1 - 1.43, 0.3, w=1.43, name="Логотип")
    s.slidenum(X1 - 0.6, 7.06, 0.6, 0.2)
    return s, max(1.5, 0.62 + th + 0.34)


def dark(d, name):
    s = d.new(dark=True, name=name)
    s.line(1.14, 0.025, 2.85, 0.025, color=LIME, lw=4)          # the template's accent line, lime on dark
    return s


def glow(s, cx, cy, r, color=LIME, a=22):
    """Soft round light behind an illustration on dark slides."""
    s.shape(cx - r, cy - r, 2 * r, 2 * r, geom="ellipse", name="Свечение",
            grad={"path": True, "stops": [(0, color, a), (55, color, a * 0.35), (100, color, 0)]})


# ---------------------------------------------------------------- atoms
def card(s, x, y, w, h, fill=CARD, line=None, lw=1.25, r=0.16, shadow=None, name=None):
    return s.rrect(x, y, w, h, r=r, fill=fill, line=line, lw=lw, shadow=shadow, name=name)


def tile(s, x, y, d, icon, fill=GREEN, color=WHITE, r=None, stroke=2.0):
    """Template icon tile: rounded square with a white pictogram."""
    s.rrect(x, y, d, d, r=r if r is not None else d * 0.26, fill=fill, name="Плашка иконки")
    k = d * 0.56
    s.icon(icon, x + (d - k) / 2, y + (d - k) / 2, k, color=color, stroke=stroke)


def label(s, x, y, w, t, color=GREEN, sz=10, h=0.22):
    return s.text(x, y, w, h, t.upper(), sz=sz, bold=True, color=color, spc=1.0)


def num_circle(s, x, y, d, n, fill=GREEN, color=WHITE, sz=None):
    return s.shape(x, y, d, d, geom="ellipse", fill=fill, text=str(n), sz=sz or max(10, round(d * 30)), bold=True,
                   color=color, align="ctr", anchor="ctr", inset=(0, 0, 0, 0), check=False)


def h_of(text, w, sz, bold=False, lnsp=1.08, spc=0):
    return text_height(text, w, sz, bold, lnsp, spc)


def img_aspect(d, rel):
    pw, ph = d.media_size[d.media(os.path.join(ASSETS, rel))]
    return pw / ph


# ---------------------------------------------------------------- blocks
def frame(s, kind, x, y, w, text, lab=None, h=None, sz=13, anim=None, pad=0.22, lnsp=1.08, spc=4, items=False,
          icon=None, title=None, title_sz=14):
    """Coloured block from the document (advice / what you see / important / prohibition / how it works).
    text: str or list of paragraphs; items=True draws them as bullets. Returns bottom y."""
    fill, ln, dk, ic = FRAMES[kind]
    icon = icon or ic
    td = 0.46
    tx = x + pad + td + 0.2
    tw = w - (tx - x) - pad
    paras = norm_paras(text)
    if items:
        paras = [dict(p, bullet=dk, marL=0.2) for p in paras]
    head = 0.0
    if lab:
        head += 0.28
    if title:
        head += h_of(title, tw, title_sz, True, 1.05) + 0.08
    body_h = h_of(paras, tw - (0.2 if items else 0), sz, False, lnsp, spc) if paras and paras[0]["t"] else 0
    need = pad + head + body_h + pad - 0.04
    h = h or max(need, td + 2 * pad)
    s.begin(lab or kind)
    s.rrect(x, y, w, h, r=0.16, fill=fill, line=ln, lw=1.25, name="Рамка " + kind)
    tile(s, x + pad, y + pad - 0.02, td, icon, fill=dk if kind != "how" else GREEN)
    yy = y + pad - 0.02
    if lab:
        label(s, tx, yy, tw, lab, color=dk)
        yy += 0.28
    if title:
        th = h_of(title, tw, title_sz, True, 1.05)
        s.text(tx, yy, tw, th + 0.02, title, sz=title_sz, bold=True, color=INK, lnsp=1.05)
        yy += th + 0.08
    if body_h:
        s.text(tx, yy, tw, h - (yy - y) - pad + 0.1, paras, sz=sz, color=BODY, lnsp=lnsp, spc_after=spc, bcolor=INK)
    s.end(anim=anim)
    return y + h


def important(s, x, y, w, text, anim=None, sz=13):
    return frame(s, "warn", x, y, w, text, lab="Важно", sz=sz, anim=anim)


def rows(s, x, y, w, items, icon="flag", fill=CARD, tile_fill=GREEN, sz=13, gap=0.12, anim0=150, step=110, pad=0.18,
         td=0.44, minh=0.62, highlight=None, numbered=False):
    """Vertical list of rounded rows with an icon tile (or number). Returns bottom y."""
    for i, t in enumerate(items):
        tw = w - pad * 2 - td - 0.22
        th = h_of(t, tw, sz, False, 1.08)
        h = max(minh, th + 2 * 0.15)
        hl = highlight == i
        s.begin("Пункт %d" % (i + 1))
        s.rrect(x, y, w, h, r=0.14, fill=GREEN if hl else fill, shadow="glow" if hl else None)
        if numbered:
            num_circle(s, x + pad, y + (h - td) / 2, td, i + 1, fill=LIME if hl else tile_fill, color=GREEN if hl else WHITE, sz=14)
        else:
            tile(s, x + pad, y + (h - td) / 2, td, icon if isinstance(icon, str) else icon[i],
                 fill=LIME if hl else tile_fill, color=GREEN if hl else WHITE)
        s.text(x + pad + td + 0.22, y + (h - th) / 2 - 0.01, tw, th + 0.04, t, sz=sz, color=WHITE if hl else BODY,
               bcolor=WHITE if hl else INK, lnsp=1.08)
        s.end(anim=anim0 + i * step)
        y += h + gap
    return y - gap


def grid_cards(s, x, y, w, items, cols, gap=0.2, sz=12.5, title_sz=14, icons=None, highlight=None, anim0=150, step=110,
               h=None, pad=0.24, td=0.5, tile_fill=GREEN):
    """Template card grid: icon tile, bold title, text. items: [(title, text)]. Returns bottom y."""
    cw = (w - gap * (cols - 1)) / cols
    tw = cw - 2 * pad
    hs = []
    for t, body in items:
        hh = pad + (td + 0.18 if icons else 0) + (h_of(t, tw, title_sz, True, 1.05) + 0.08 if t else 0) + (h_of(body, tw, sz, False, 1.08) if body else 0) + pad
        hs.append(hh)
    nrows = (len(items) + cols - 1) // cols
    row_h = [h or max(hs[r * cols:(r + 1) * cols]) for r in range(nrows)]
    yy = y
    for r in range(nrows):
        for c in range(cols):
            i = r * cols + c
            if i >= len(items):
                break
            t, body = items[i]
            cx = x + c * (cw + gap)
            hl = highlight == i or (isinstance(highlight, (list, tuple)) and i in highlight)
            s.begin("Карточка %d" % (i + 1))
            s.rrect(cx, yy, cw, row_h[r], r=0.18, fill=GREEN if hl else CARD, shadow="glow" if hl else None)
            if icons:
                tile(s, cx + pad, yy + pad, td, icons[i], fill=LIME if hl else tile_fill, color=GREEN if hl else WHITE)
            ty = yy + pad + (td + 0.18 if icons else 0)
            if t:
                th = h_of(t, tw, title_sz, True, 1.05)
                s.text(cx + pad, ty, tw, th + 0.03, t, sz=title_sz, bold=True, color=WHITE if hl else INK, lnsp=1.05)
                ty += th + 0.08
            if body:
                s.text(cx + pad, ty, tw, row_h[r] - (ty - yy) - pad + 0.12, body, sz=sz, color="E3F4E6" if hl else BODY,
                       bcolor=WHITE if hl else INK, lnsp=1.08)
            s.end(anim=anim0 + i * step)
        yy += row_h[r] + gap
    return yy - gap


def arrow(s, x1, y, x2, color=GREEN, lw=2.0, anim=None, dash=None):
    return s.line(x1, y, x2, y, color=color, lw=lw, tail="triangle", anim=anim, effect="wipe", dash=dash)


def chip(s, x, y, w, h, t, fill=CARD, color=INK, sz=11, bold=True, line=None, anim=None):
    return s.shape(x, y, w, h, geom="roundRect", radius=h / 2, fill=fill, line=line, text=t, sz=sz, bold=bold,
                   color=color, align="ctr", anchor="ctr", inset=(0.04, 0, 0.04, 0), anim=anim, check=False, wrap=False)


def chip_w(t, sz=11, bold=True, padx=0.22):
    return text_width(t, sz, bold) + 2 * padx


# ---------------------------------------------------------------- module cover
def module_cover(d, n, name, thought, items, img, img_h=4.5, note=None):
    s = dark(d, "Модуль %d. %s" % (n, name))
    s.text(6.2, 0.35, 7.0, 6.9, "%02d" % n, sz=330, bold=True, color=WHITE, align="r", check=False, name="Номер модуля",
           lnsp=0.85)
    # the big number is a watermark: make it translucent
    s.items[-1] = s.items[-1].replace('<a:srgbClr val="FFFFFF"/></a:solidFill><a:latin', '<a:srgbClr val="FFFFFF"><a:alpha val="6000"/></a:srgbClr></a:solidFill><a:latin')
    s.pic(LOGO_W, 0.75, 0.55, w=1.75, name="Логотип")
    s.text(0.75, 1.62, 6.6, 0.26, "МОДУЛЬ %d ИЗ 8" % n, sz=12, bold=True, color=LIME, spc=1.5, anim=0)
    s.text(0.75, 1.95, 6.6, 0.3, name, sz=13, color="B9D8C0", anim=0)
    th = text_height(thought, 6.6, 28, True, 0.98)
    s.title_ph(0.75, 2.38, 6.6, th + 0.05, thought, sz=28, color=WHITE, lnsp=0.98, anim=120)
    y = 2.38 + th + 0.4
    if note:
        nh = h_of(note, 6.4, 13.5, False, 1.1)
        s.text(0.75, y, 6.4, nh + 0.05, note, sz=13.5, color="D6EBDA", lnsp=1.1, anim=250)
        y += nh + 0.3
    if items:
        label(s, 0.75, y, 6.6, "В этом модуле", color=LIME, sz=11)
        y += 0.38
        for i, t in enumerate(items):
            ih = h_of(t, 6.0, 13.5, False, 1.05)
            s.begin("Пункт %d" % (i + 1))
            s.shape(0.75, y + 0.03, 0.3, 0.3, geom="ellipse", fill=None, line=LIME, lw=1.25, text=str(i + 1), sz=10, bold=True,
                    color=LIME, align="ctr", anchor="ctr", inset=(0, 0, 0, 0), check=False)
            s.text(1.2, y + 0.01, 6.0, ih + 0.04, t, sz=13.5, color=WHITE, lnsp=1.05)
            s.end(anim=350 + i * 110)
            y += max(ih, 0.3) + 0.14
    if y > 7.1:
        WARN.append("cover %d too tall: %.2f" % (n, y))
    # illustration
    glow(s, 10.05, 3.95, 3.0, a=26)
    pw, ph = d.media_size[d.media(os.path.join(ASSETS, "img", img))]
    h = img_h
    w = h * pw / ph
    if w > 5.4:
        w = 5.4
        h = w * ph / pw
    s.pic("img/" + img, 10.05 - w / 2, 3.95 - h / 2, w, h, name="Иллюстрация", anim=200, effect="zoom", dur=700)
    s.slidenum(X1 - 0.6, 7.06, 0.6, 0.2, color="9CC4A6")
    return s
