# -*- coding: utf-8 -*-
"""Reusable slide parts of the Outlook course: page chrome, glass cards, lists, buttons, quiz."""
import lib
from lib import *

MX = 0.75                 # side margin
CW = SW - 2 * MX          # content width
TOP = 2.05                # content top (below title)
BOT = 6.55                # content bottom (above footer)

COURSE = "Outlook: почта и календарь"
MODULES = [
    ("01", "Знакомство с Outlook", "Окно программы, папки и значки"),
    ("02", "Письма", "Написать, ответить, переслать"),
    ("03", "Порядок в почте", "Поиск, папки, правила, автоответ"),
    ("04", "Календарь", "Встречи, собрания, приглашения"),
    ("05", "Безопасность и этикет", "Фишинг и правила переписки"),
]

GLOWS = {   # name -> (file, x, y, w, h, rot, alpha)
    "hero": ("glow1.jpg", 0, 0, SW, SH, 0, 46),
    "hero2": ("glow1.jpg", -1.2, -0.8, SW + 2.4, SH + 1.6, 180, 40),
    "a": ("glow2.jpg", 0, 0, SW, SH, 180, 20),
    "b": ("glow2.jpg", -2.2, -1.4, SW + 3.2, SH + 2.4, 180, 20),
    "c": ("glow2.jpg", -1.6, -0.6, SW + 2.2, SH + 1.8, 180, 20),
    "d": ("glow2.jpg", -0.6, -2.0, SW + 3.0, SH + 2.6, 180, 20),
}


def ic(name, white=False):
    return "ic_%s%s.png" % (name, "_w" if white else A("suffix"))


def obj(name):
    """3D object picture for the current theme."""
    return "%s%s.png" % (name, A("suffix"))


class Kit:
    """Keeps slide numbering and builds the common page frame."""

    def __init__(self, deck, total=None):
        self.d = deck
        self.total = total
        self.mod = None       # current module index (0-based) or None
        self._g = 0

    # ---------------------------------------------------------------- frame
    def slide(self, key, title="", sub=None, notes="", glow=None, nav=True, crumb=True, logo=True, trans="morph",
              dur=1000, adv_click=True, title_w=None, title_sz=30, title_y=0.95, center=False, show_title=True):
        d = self.d
        s = d.new(key, title=title, notes=notes, trans=trans, dur=dur, adv_click=adv_click)
        no = len(d.slides)
        s.no = no
        if glow is None:
            glow = "abcd"[self._g % 4]
            self._g += 1
        fn, gx, gy, gw, gh, rot, al = GLOWS[glow]
        s.pic(fn, gx, gy, gw, gh, name="!!glow", alpha=al, rot=rot)
        if logo:
            lw = 1.25
            s.pic(A("logo") + ".png", SW - MX - lw, 0.4, w=lw, name="!!logo")
        if crumb and self.mod is not None:
            num, name, _ = MODULES[self.mod]
            s.oval(MX, 0.535, 0.1, 0.1, fill=A("ACC"), name="!!crumb-dot")
            s.text(MX + 0.22, 0.42, 6.0, 0.34, "Модуль %s · %s" % (num, name), sz=12, color=TEXT, font=FONT, anchor="ctr", name="!!crumb")
        elif crumb:
            s.oval(MX, 0.535, 0.1, 0.1, fill=A("ACC"), name="!!crumb-dot")
            s.text(MX + 0.22, 0.42, 6.0, 0.34, COURSE, sz=12, color=TEXT, anchor="ctr", name="!!crumb")
        if title and show_title:
            tw = title_w or (CW - 1.6)
            if center:
                s.shape((SW - tw) / 2, title_y, tw, 0.66, text=title, sz=title_sz, color=WHITE, font=FONT, align="ctr", anchor="t",
                        inset=(0, 0, 0, 0), ph="title", name="!!title", lnsp=0.95)
            else:
                s.shape(MX, title_y, tw, 0.66, text=title, sz=title_sz, color=WHITE, font=FONT, anchor="t", inset=(0, 0, 0, 0),
                        ph="title", name="!!title", lnsp=0.95)
        elif title:
            # keep a real (off-slide) title so the slide has a name in outlines and players
            s.shape(MX, -1.2, 8, 0.6, text=title, sz=20, color=WHITE, inset=(0, 0, 0, 0), ph="title", name="!!title", check=False)
        if sub:
            if center:
                s.text((SW - 8.6) / 2, title_y + 0.72, 8.6, 0.62, sub, sz=15, color=TEXT, font=FONT_L, align="ctr", name="!!sub", lnsp=1.0)
            else:
                s.text(MX, title_y + 0.68, title_w or 8.6, 0.36, sub, sz=15, color=TEXT, font=FONT_L, name="!!sub")
        if nav:
            mark = len(s.items)
            self.footer(s, no)
            s.tail = s.items[mark:]
            del s.items[mark:]
        return s

    def footer(self, s, no):
        total = self.total or 99
        y = 6.93
        # progress line
        s.rrect(MX, y + 0.19, 3.0, 0.04, r=0.02, fill=(WHITE, 14), name="!!prog-track")
        s.rrect(MX, y + 0.19, max(0.06, 3.0 * no / total), 0.04, r=0.02, fill=A("ACC"), name="!!prog-fill")
        s.text(MX + 3.2, y + 0.04, 1.6, 0.34, "%d / %d" % (no, total), sz=11, color=MUTED, anchor="ctr", name="!!prog-num")
        bx = SW - MX - 0.42
        nav_btn(s, bx - 0.54, y, "prev")
        nav_btn(s, bx, y, "next")


def nav_btn(s, x, y, kind, d=0.42):
    """Round glass button with an arrow (like the arrow buttons of the reference cards)."""
    s.oval(x, y, d, d, fill=(WHITE, 7), line="glass2", name="!!nav-%s" % kind, link=kind,
           tip="Назад" if kind == "prev" else "Далее")
    icon = "chevron-left" if kind == "prev" else "chevron-right"
    s.pic(ic(icon, white=True), x + d * 0.22, y + d * 0.22, w=d * 0.56, name="!!nav-%s-i" % kind, link=kind)


# ---------------------------------------------------------------- basic parts
def pill(s, x, y, text, sz=12, h=0.4, name=None, fill=None, line="glass", color=TEXT, anim=None, pad=0.22, w=None, font=FONT, dot=False):
    w = w or (text_width(text, sz, font) + 2 * pad + (0.2 if dot else 0))
    if dot:
        s.begin(name or "pill")
        s.rrect(x, y, w, h, r=h / 2, fill=fill, line=line)
        s.oval(x + pad - 0.02, y + h / 2 - 0.045, 0.09, 0.09, fill=A("ACC"))
        s.text(x + pad + 0.16, y, w - pad - 0.16, h, text, sz=sz, color=color, anchor="ctr", font=font)
        s.end(anim=anim)
    else:
        s.rrect(x, y, w, h, r=h / 2, fill=fill, line=line, text=text, sz=sz, color=color, align="ctr", anchor="ctr",
                inset=(0.05, 0, 0.05, 0), name=name, anim=anim, font=font)
    return w


def button(s, x, y, w, h, text, link="next", name=None, sz=15, anim=None, primary=True):
    """Accent pill button with a hyperlink."""
    s.rrect(x, y, w, h, r=h / 2, fill="accent" if primary else (WHITE, 8), line=None if primary else "glass",
            text=text, sz=sz, color=WHITE, font=FONT_SB, align="ctr", anchor="ctr", inset=(0.1, 0, 0.1, 0.02),
            link=link, name=name, anim=anim, fx="glow_s" if primary else None)


def card(s, x, y, w, h, title=None, body=None, icon=None, num=None, tag=None, name=None, anim=None, style="glass",
         tsz=17, bsz=14, pad=0.3, img=None, img_h=0.62, divider=True, r=0.24, bullet=False, center=False, body_color=TEXT, link=None,
         inline=False):
    """Glass card: [icon | number] + title + thin divider + body text."""
    s.begin(name or "card")
    line = "glass" if style in ("glass", "glass2") else None
    s.rrect(x, y, w, h, r=r, fill=style, line=line, link=link)
    cy = y + pad
    al = "ctr" if center else "l"
    if img:
        iw = img_h * img_size(img)[0] / img_size(img)[1]
        s.pic(img, x + (w - iw) / 2 if center else x + pad - 0.04, cy - 0.04, h=img_h)
        cy += img_h + 0.1
    elif icon and inline:
        isz = 0.4
        th = text_height(title, w - 2 * pad - isz - 0.16, tsz, FONT_SB, lnsp=0.98)
        rh = max(isz, th)
        s.pic(ic(icon, white=(style == "accent")), x + pad - 0.03, cy + (rh - isz) / 2, w=isz)
        s.text(x + pad + isz + 0.13, cy, w - 2 * pad - isz - 0.13, rh, title, sz=tsz, color=WHITE, font=FONT_SB, lnsp=0.98, anchor="ctr")
        cy += rh + 0.16
        title = None
        if body and divider:
            s.line(x + pad, cy, x + w - pad, cy, color=(WHITE, 20))
            cy += 0.16
            divider = False
    elif icon:
        isz = 0.46
        s.pic(ic(icon, white=(style == "accent")), x + (w - isz) / 2 if center else x + pad - 0.03, cy, w=isz)
        cy += isz + 0.16
    elif num is not None:
        s.text(x + pad, cy - 0.08, w - 2 * pad, 0.5, str(num), sz=26, color=A("ACC") if style != "accent" else WHITE, font=FONT_L, align=al)
        cy += 0.5
    if tag:
        s.text(x + pad, cy, w - 2 * pad, 0.26, tag, sz=11, color=A("ACC_SOFT") if style != "accent" else WHITE, font=FONT_SB, align=al)
        cy += 0.3
    tw = w - 2 * pad
    if title:
        th = text_height(title, tw, tsz, FONT_SB, lnsp=0.98)
        s.text(x + pad, cy, tw, th + 0.04, title, sz=tsz, color=WHITE, font=FONT_SB, lnsp=0.98, align=al)
        cy += th + 0.14
    if body:
        if divider and title:
            s.line(x + pad, cy, x + w - pad, cy, color=(WHITE, 20))
            cy += 0.16
        s.text(x + pad, cy, tw, max(0.3, y + h - cy - pad * 0.7), body, sz=bsz, color=body_color if style != "accent" else WHITE,
               font=FONT, lnsp=1.0, spc_after=5, bullet=bullet, align=al)
    return s.end(anim=anim)


def card_h(title, body, w, tsz=17, bsz=14, pad=0.3, icon=False, num=False, tag=False, bullet=False, divider=True, img_h=0, inline=False):
    """Height a card needs for its content."""
    tw = w - 2 * pad
    h = pad
    if inline and icon:
        h += max(0.4, text_height(title, tw - 0.56, tsz, FONT_SB, lnsp=0.98)) + 0.16
        if body:
            h += 0.16 + text_height(body, tw, bsz, FONT, lnsp=1.0, spc_after=5, bullet=bullet)
        return h + pad * 0.85
    if img_h:
        h += img_h + 0.1
    elif icon:
        h += 0.62
    if num:
        h += 0.5
    if tag:
        h += 0.3
    if title:
        h += text_height(title, tw, tsz, FONT_SB, lnsp=0.98) + 0.14
    if body:
        if divider and title:
            h += 0.16
        h += text_height(body, tw, bsz, FONT, lnsp=1.0, spc_after=5, bullet=bullet)
    return h + pad * 0.85


def grid(s, items, x=MX, y=TOP, w=CW, cols=3, gap=0.28, h=None, anim0=150, step=110, name="c", **kw):
    """Lay cards on a grid. items: dicts passed to card()."""
    cw = (w - gap * (cols - 1)) / cols
    rows = (len(items) + cols - 1) // cols
    if h is None:
        hs = []
        for it in items:
            hs.append(card_h(it.get("title"), it.get("body"), cw, tsz=kw.get("tsz", 17), bsz=kw.get("bsz", 14), pad=kw.get("pad", 0.3),
                             icon=bool(it.get("icon")), num=it.get("num") is not None, tag=bool(it.get("tag")), bullet=kw.get("bullet", False),
                             img_h=kw.get("img_h", 0.62) if it.get("img") else 0, inline=kw.get("inline", False)))
        h = max(hs)
    for i, it in enumerate(items):
        r, c = divmod(i, cols)
        opts = dict(kw)
        opts.update(it)
        opts.setdefault("name", "%s%d" % (name, i))
        card(s, x + c * (cw + gap), y + r * (h + gap), cw, h, anim=(anim0 + i * step) if anim0 is not None else None, **opts)
    return h, rows * h + (rows - 1) * gap


def bullets(s, x, y, w, items, sz=15, gap=9, name=None, anim=None, color=TEXT, h=None):
    """Simple list with accent dots."""
    paras = [{"t": t, "spcAft": gap} for t in items]
    hh = h or text_height(paras, w, sz, FONT, lnsp=1.0, spc_after=gap, bullet=True) + 0.1
    s.text(x, y, w, hh, paras, sz=sz, color=color, bullet=True, lnsp=1.0, name=name, anim=anim)
    return hh


def note(s, x, y, w, text, icon="lightbulb", name=None, anim=None, sz=14, h=None, style="soft", color=TEXT):
    """Small hint strip with an icon."""
    tw = w - 1.05
    h = h or max(0.62, text_height(text, tw, sz, FONT, lnsp=1.0) + 0.3)
    s.begin(name or "note")
    s.rrect(x, y, w, h, r=min(0.2, h / 2), fill=style if style != "soft" else (WHITE, 6), line="glass2")
    s.pic(ic(icon), x + 0.24, y + h / 2 - 0.19, w=0.38)
    s.text(x + 0.8, y, tw, h, text, sz=sz, color=color, anchor="ctr", lnsp=1.0)
    s.end(anim=anim)
    return h


def tile3d(s, x, y, w, h, tile, name=None, anim=None, r=0.22):
    """Opaque 3D picture from the reference deck on its dark panel (as on the reference 'Quick Start' cards)."""
    s.begin(name or "tile")
    s.rrect(x, y, w, h, r=r, fill=PANEL)
    pw, ph = img_size(tile)
    ih = h * 0.96
    iw = ih * pw / ph
    if iw > w * 0.98:
        iw = w * 0.98
        ih = iw * ph / pw
    s.pic(tile, x + (w - iw) / 2, y + (h - ih) / 2, iw, ih, geom="roundRect", radius=r * 0.8)
    return s.end(anim=anim)


def keycap(s, x, y, text, sz=13, h=0.44, name=None, w=None):
    w = w or max(0.56, text_width(text, sz, FONT_SB) + 0.34)
    s.rrect(x, y, w, h, r=0.09, fill=("grad", [(0, "2A2A33", None), (100, "17171C", None)], 90), line="glass",
            text=text, sz=sz, color=WHITE, font=FONT_SB, align="ctr", anchor="ctr", inset=(0.03, 0, 0.03, 0.02), name=name)
    return w


def keys(s, x, y, combo, sz=13, h=0.44):
    """'Ctrl+Shift+M' -> row of key caps with '+' between; returns total width."""
    cx = x
    parts = combo.split("+")
    for i, p in enumerate(parts):
        cx += keycap(s, cx, y, p, sz=sz, h=h)
        if i < len(parts) - 1:
            s.text(cx, y, 0.22, h, "+", sz=sz, color=MUTED, align="ctr", anchor="ctr")
            cx += 0.22
    return cx - x


def path_steps(s, x, y, steps, sz=13, h=0.46, gap=0.12, name="path", anim=None):
    """Menu path: [Файл] > [Параметры] > [Почта] - pills with chevrons."""
    s.begin(name)
    cx = x
    for i, t in enumerate(steps):
        w = text_width(t, sz, FONT_SB) + 0.44
        last = i == len(steps) - 1
        s.rrect(cx, y, w, h, r=h / 2, fill="accent" if last else (WHITE, 7), line=None if last else "glass2", text=t, sz=sz,
                color=WHITE, font=FONT_SB, align="ctr", anchor="ctr", inset=(0.04, 0, 0.04, 0.02))
        cx += w
        if not last:
            s.pic(ic("chevron-right", white=True), cx + gap - 0.04, y + h / 2 - 0.13, w=0.26, alpha=60)
            cx += gap * 2 + 0.18
    s.end(anim=anim)
    return cx - x


# ---------------------------------------------------------------- quiz
LETTERS = "ABCD"


def quiz(k, key, question, options, correct, explain, tag="Проверьте себя", situation=None, wrong=None, notes=""):
    """Question slide. Click an option -> its mark and a feedback panel appear (triggers); other feedback hides.
    options: list of str; correct: index; explain: text shown for the right answer; wrong: text for wrong ones."""
    wrong = wrong or "Не совсем. Подумайте ещё и выберите другой вариант."
    n = "Вопрос. %s%s Варианты: %s. Правильный ответ: %s. %s %s" % (
        (situation + " ") if situation else "", question, "; ".join("%s) %s" % (LETTERS[i], o) for i, o in enumerate(options)),
        LETTERS[correct], explain, notes)
    s = k.slide(key, title=tag, notes=n, adv_click=False, show_title=False)
    pill(s, MX, 0.98, tag, sz=12, name="!!qtag", dot=True)
    y = 1.56
    qw = CW
    if situation:
        sh = text_height(situation, qw, 15, FONT_L, lnsp=1.0) + 0.06
        s.text(MX, y, qw, sh, situation, sz=15, color=TEXT, font=FONT_L, lnsp=1.0, name="q-sit", anim=0)
        y += sh + 0.1
    qh = text_height(question, qw, 24, FONT, lnsp=0.98) + 0.06
    s.text(MX, y, qw, qh, question, sz=24, color=WHITE, lnsp=0.98, name="q-text", anim=0 if not situation else 80)
    y += qh + 0.3
    # options (left) + feedback panel (right)
    ow = 7.35
    fx, fw = MX + ow + 0.35, CW - ow - 0.35
    tw = ow - 1.5
    hs = [max(0.74, text_height(o, tw, 15, FONT, lnsp=1.0) + 0.34) for o in options]
    gap = 0.16
    avail = BOT - y
    tot = sum(hs) + gap * (len(hs) - 1)
    if tot > avail:
        lib.WARN.append("%s: quiz options do not fit (%.2f > %.2f)" % (key, tot, avail))
    oy = y
    rects = []
    for i, (o, oh) in enumerate(zip(options, hs)):
        s.begin("opt%d" % i)
        s.rrect(MX, oy, ow, oh, r=min(0.22, oh / 2), fill="glass", line="glass")
        s.oval(MX + 0.2, oy + oh / 2 - 0.2, 0.4, 0.4, fill=(WHITE, 8), line="glass2", text=LETTERS[i], sz=13, color=WHITE, font=FONT_SB,
               align="ctr", anchor="ctr", inset=(0, 0, 0, 0.01))
        s.text(MX + 0.82, oy, tw, oh, o, sz=15, color=WHITE, anchor="ctr", lnsp=1.0)
        s.end(anim=200 + i * 90)
        rects.append((oy, oh))
        oy += oh + gap
    # idle hint in the feedback area
    ph = oy - gap - y
    s.begin("q-hint")
    s.rrect(fx, y, fw, ph, r=0.24, fill=(WHITE, 4), line="glass2", dash="dash")
    s.pic(ic("mouse-pointer-click"), fx + fw / 2 - 0.28, y + ph / 2 - 0.62, w=0.56)
    s.text(fx + 0.3, y + ph / 2 + 0.06, fw - 0.6, 0.7, "Нажмите на вариант ответа", sz=14, color=MUTED, align="ctr", lnsp=1.0)
    hint = s.end(anim=560)
    # feedback groups
    fbs = []
    for i, (ry, rh) in enumerate(rects):
        good = i == correct
        col = OK if good else BAD
        s.begin("fb%d" % i)
        s.rrect(MX, ry, ow, rh, r=min(0.22, rh / 2), fill=(col, 10), line=col, lw=1.5)
        s.pic("ic_circle-check_ok.png" if good else "ic_circle-x_bad.png", MX + ow - 0.62, ry + rh / 2 - 0.19, w=0.38)
        s.rrect(fx, y, fw, ph, r=0.24, fill="glass", line=col, lw=1.25)
        s.pic("ic_circle-check_ok.png" if good else "ic_circle-x_bad.png", fx + 0.3, y + 0.3, w=0.5)
        s.text(fx + 0.95, y + 0.3, fw - 1.2, 0.5, "Верно!" if good else "Не совсем", sz=20, color=col, font=FONT_SB, anchor="ctr")
        body = explain if good else wrong
        s.text(fx + 0.3, y + 1.02, fw - 0.6, ph - 1.2, body, sz=14, color=TEXT, lnsp=1.02, spc_after=6)
        fbs.append(s.end())
    # transparent click areas on top
    for i, (ry, rh) in enumerate(rects):
        hit = s.rrect(MX, ry, ow, rh, r=min(0.22, rh / 2), fill="hit", name="hit%d" % i, tip="Вариант %s" % LETTERS[i])
        s.trigger(hit, show=[fbs[i]], hide=[hint] + [f for j, f in enumerate(fbs) if j != i])
    return s


# ---------------------------------------------------------------- side panel with steps (the 'Categories' menu of the reference)
def side_steps(s, x, y, w, header, items, cur, title=None, body=None, tip=None, name="side", h_total=None, numbered=True, key=None):
    """Right-hand menu: header + items (current one highlighted) + description card under it.
    Shared names make the marker and the texts glide/crossfade between neighbouring slides (Morph)."""
    pre = "!!%s-" % name
    s.text(x, y, w, 0.36, header, sz=15, color=WHITE, anchor="ctr", name=pre + "hdr")
    ly = y + 0.47
    s.line(x, ly, x + w, ly, color=(WHITE, 30), name=pre + "ln")
    n = len(items)
    seg = w / n
    s.rrect(x + seg * max(cur, 0), ly - 0.025, seg, 0.05, r=0.025, fill=A("ACC"), name=pre + "mark")
    iy = ly + 0.2
    ih = 0.36
    for i, it in enumerate(items):
        on = i == cur
        s.oval(x + 0.02, iy + ih / 2 - 0.04, 0.08, 0.08, fill=A("ACC") if on else TEXT, name=pre + "dot%d" % i)
        s.text(x + 0.26, iy, w - 0.7, ih, it, sz=13.5, color=A("ACC") if on else TEXT, font=FONT_SB if on else FONT, anchor="ctr",
               name=pre + "it%d" % i, check=False)
        if numbered:
            s.text(x + w - 0.4, iy, 0.4, ih, str(i + 1), sz=13.5, color=A("ACC") if on else TEXT, align="r", anchor="ctr", name=pre + "n%d" % i)
        iy += ih
    cy = iy + 0.18
    if title or body:
        ch = (h_total - (cy - y)) if h_total else 2.0
        s.rrect(x - 0.12, cy, w + 0.24, ch, r=0.22, fill="glass", line="glass", name=pre + "card")
        ty = cy + 0.22
        uid = key or s.key
        if title:
            th = text_height(title, w - 0.2, 16, FONT_SB, lnsp=0.98)
            s.text(x + 0.1, ty, w - 0.2, th + 0.04, title, sz=16, color=WHITE, font=FONT_SB, lnsp=0.98, name="side-t")
            ty += th + 0.12
        if body:
            bh = cy + ch - ty - (0.62 if tip else 0.18)
            s.text(x + 0.1, ty, w - 0.2, bh, body, sz=13, color=TEXT, lnsp=1.0, spc_after=5, name="side-b")
        if tip:
            s.pic(ic("keyboard"), x + 0.1, cy + ch - 0.5, w=0.3, name="side-ki")
            s.text(x + 0.5, cy + ch - 0.56, w - 0.5, 0.42, tip, sz=12.5, color=WHITE, font=FONT_SB, anchor="ctr", name="side-k", check=False)
    return cy


def opener(k, key, num, title, lead, points, visual, minutes, notes="", tile=False):
    """Module title slide: one big glass card (the 'Quick Start' card of the reference) with a 3D object."""
    s = k.slide(key, title="Модуль %s. %s" % (num, title), glow="hero", notes=notes, crumb=False, show_title=False, dur=1250)
    x, y, w, h = MX, 1.25, CW, 5.25
    s.rrect(x, y, w, h, r=0.36, fill="glass", line="glass", name="!!open-card")
    th = text_height(title, 6.2, 38, FONT, lnsp=0.92)
    lh = text_height(lead, 6.0, 16, FONT_L, lnsp=1.0)
    ph_ = text_height([{"t": t, "spcAft": 5} for t in points], 6.0, 14.5, FONT, lnsp=1.0, spc_after=5, bullet=True)
    total = 0.42 + 0.3 + th + 0.18 + lh + 0.34 + 0.36 + ph_
    cy = y + (h - total) / 2
    pill(s, x + 0.5, cy, "Модуль %s из 05  ·  %s" % (num, minutes), sz=12.5, h=0.42, name="open-pill", dot=True, anim=100)
    cy += 0.42 + 0.3
    s.shape(x + 0.5, cy, 6.2, th + 0.1, text=title, sz=38, color=WHITE, font=FONT, lnsp=0.92, inset=(0, 0, 0, 0), ph="title",
            name="!!title", anchor="t")
    cy += th + 0.18
    s.text(x + 0.5, cy, 6.0, lh + 0.05, lead, sz=16, color=TEXT, font=FONT_L, lnsp=1.0, name="open-lead", anim=200)
    cy += lh + 0.34
    s.text(x + 0.5, cy, 3, 0.3, "Вы узнаете", sz=12, color=A("ACC_SOFT"), font=FONT_SB, name="open-h", anim=300)
    bullets(s, x + 0.5, cy + 0.36, 6.0, points, sz=14.5, gap=5, name="open-pts", anim=380)
    vx, vw = x + 7.25, w - 7.25 - 0.42
    if tile:
        tile3d(s, vx, y + 0.42, vw, h - 0.84, visual, name="!!open-vis", anim=None)
    else:
        s.rrect(vx, y + 0.42, vw, h - 0.84, r=0.26, fill=PANEL, name="!!open-panel")
        pw, ph = img_size(visual)
        ih = min(h - 1.7, (vw - 0.7) * ph / pw)
        iw = ih * pw / ph
        s.pic(visual, vx + (vw - iw) / 2, y + (h - ih) / 2, iw, ih, name="!!open-obj", anim=250)
    return s


def tour(k, key, title, mock_fn, zone, header, items, cur, dtitle, dbody, tip=None, notes="", sub=None, side_name="tour", mock_kw=None,
         hl=True, mx=MX, my=1.78, mk=0.925, glow=None, side_x=None, hl_pad=0.05):
    """Window mock on the left + step menu on the right; the highlight frame morphs from zone to zone."""
    import mock
    s = k.slide(key, title=title, notes=notes, glow=glow, dur=900)
    z = mock_fn(s, mx, my, k=mk, **(mock_kw or {}))
    if hl and zone and z.get(zone):
        mock.highlight(s, z[zone], pad=hl_pad)
    wx, wy, ww, wh = z["win"]
    sx = side_x or (wx + ww + 0.48)
    side_steps(s, sx, my - 0.02, SW - MX - sx, header, items, cur, dtitle, dbody, tip=tip, name=side_name, h_total=wh + 0.04)
    return s, z


# ---------------------------------------------------------------- comparison / process / rows
def compare(s, y, bad, good, h=None, bad_title="Так не стоит", good_title="Так лучше", x=MX, w=CW, sz=15, gap=0.3, anim0=150, mono=False):
    """Two glass cards side by side: what to avoid (red mark) and what to do (green mark)."""
    cw = (w - gap) / 2
    font = FONT
    hs = []
    for items in (bad, good):
        hh = 0.95
        for t in items:
            hh += max(0.5, text_height(t, cw - 1.3, sz, font, lnsp=1.0) + 0.2) + 0.1
        hs.append(hh + 0.2)
    h = h or max(hs)
    for side, (items, title, col, icon) in enumerate(((bad, bad_title, BAD, "ic_circle-x_bad.png"), (good, good_title, OK, "ic_circle-check_ok.png"))):
        cx = x + side * (cw + gap)
        s.begin("cmp%d" % side)
        s.rrect(cx, y, cw, h, r=0.26, fill="glass", line="glass")
        s.rrect(cx + 0.3, y + 0.3, text_width(title, 12.5, FONT_SB) + 0.5, 0.4, r=0.2, fill=(col, 14), line=(col, 70), text=title, sz=12.5,
                color=col, font=FONT_SB, align="ctr", anchor="ctr", inset=(0.05, 0, 0.05, 0.01))
        ry = y + 0.92
        for t in items:
            rh = max(0.5, text_height(t, cw - 1.3, sz, font, lnsp=1.0) + 0.2)
            s.rrect(cx + 0.3, ry, cw - 0.6, rh, r=0.12, fill=(WHITE, 5), line="glass2")
            s.pic(icon, cx + 0.44, ry + rh / 2 - 0.15, w=0.3)
            s.text(cx + 0.9, ry, cw - 1.3, rh, t, sz=sz, color=WHITE if side else TEXT, anchor="ctr", lnsp=1.0)
            ry += rh + 0.1
        s.end(anim=anim0 + side * 160)
    return h


def process(s, y, items, x=MX, w=CW, anim0=150, d=0.74, tsz=17, bsz=14, card_h=None):
    """Numbered steps on a line (process templates): big number circles joined by a line, a card under each."""
    n = len(items)
    gap = 0.26
    cw = (w - gap * (n - 1)) / n
    cy = y + d / 2
    s.line(x + cw / 2, cy, x + w - cw / 2, cy, color=(WHITE, 26), lw=1.25, dash="sysDash", name="proc-line", anim=anim0)
    hs = [card_h_(t, b, cw, tsz, bsz) for t, b in items]
    ch = card_h or max(hs)
    for i, (t, b) in enumerate(items):
        cx = x + i * (cw + gap)
        s.begin("proc%d" % i)
        s.oval(cx + cw / 2 - d / 2, y, d, d, fill=("grad", [(0, A("CARD1"), None), (100, "0A0A10", None)], 60), line=A("ACC"), lw=1.5,
               text=str(i + 1), sz=22, color=WHITE, font=FONT_L, align="ctr", anchor="ctr", inset=(0, 0, 0, 0.02))
        card(s, cx, y + d + 0.24, cw, ch, title=t, body=b, tsz=tsz, bsz=bsz, name="proc-card%d" % i, center=False)
        s.end(anim=anim0 + 120 + i * 130)
    return d + 0.24 + ch


def card_h_(title, body, w, tsz, bsz):
    return card_h(title, body, w, tsz=tsz, bsz=bsz)


def rows(s, x, y, w, items, rh=0.62, name="rows", anim0=150, tsz=15, bsz=13.5, tw=3.0, icon_white=False, step=70):
    """List of rows: [icon] title | text. Each row is its own strip, so rows can appear one after another."""
    for i, it in enumerate(items):
        icon, title, text = it
        ry = y + i * (rh + 0.1)
        s.begin("%s%d" % (name, i))
        s.rrect(x, ry, w, rh, r=min(0.18, rh / 2), fill="glass", line="glass2")
        s.pic(ic(icon, white=icon_white), x + 0.22, ry + rh / 2 - 0.17, w=0.34)
        s.text(x + 0.74, ry, tw, rh, title, sz=tsz, color=WHITE, font=FONT_SB, anchor="ctr", lnsp=0.98)
        s.text(x + 0.74 + tw + 0.1, ry, w - tw - 1.1, rh, text, sz=bsz, color=TEXT, anchor="ctr", lnsp=1.0)
        s.end(anim=(anim0 + i * step) if anim0 is not None else None)
    return len(items) * (rh + 0.1) - 0.1


def letter(s, x, y, w, h, sender, addr, subject, paras, attach=None, name="letter", sz=12.5, anim=None, danger=False, rpad=0.3):
    """A message drawn as a glass card. Returns anchor points {'from','subject','p0'..,'attach'} -> (x, y) for number badges."""
    s.begin(name)
    s.rrect(x, y, w, h, r=0.24, fill="0B0A10", line="glass", fx="shadow")
    pts = {}
    s.oval(x + 0.3, y + 0.3, 0.52, 0.52, fill=((BAD if danger else A("ACC2")), 45), text=sender[:1], sz=14, color=WHITE, font=FONT_SB,
           align="ctr", anchor="ctr", inset=(0, 0, 0, 0.01))
    s.text(x + 0.98, y + 0.26, w - 1.3, 0.3, sender, sz=13.5, color=WHITE, font=FONT_SB, anchor="ctr")
    s.text(x + 0.98, y + 0.56, w - 1.3, 0.28, addr, sz=11.5, color=BAD if danger else MUTED, anchor="ctr")
    pts["from"] = (x + 0.98 + min(w - 1.7, text_width(addr, 11.5) + 0.12), y + 0.52)
    s.line(x + 0.3, y + 0.98, x + w - 0.3, y + 0.98, color=(WHITE, 16))
    sh = text_height(subject, w - 0.3 - rpad, 15, FONT_SB, lnsp=0.98)
    s.text(x + 0.3, y + 1.1, w - 0.3 - rpad, sh + 0.04, subject, sz=15, color=WHITE, font=FONT_SB, lnsp=0.98)
    pts["subject"] = (x + 0.3 + min(w - 1.0, text_width(subject, 15, FONT_SB) + 0.12), y + 1.08)
    cy = y + 1.1 + sh + 0.16
    for i, p in enumerate(paras):
        ph = text_height(p, w - 0.3 - rpad, sz, FONT, lnsp=1.0)
        s.text(x + 0.3, cy, w - 0.3 - rpad, ph + 0.03, p, sz=sz, color=TEXT, lnsp=1.0)
        pts["p%d" % i] = (x + w - 0.56, cy + ph / 2 - 0.16)
        pts["p%dy" % i] = (cy, ph)
        cy += ph + 0.13
    if attach:
        aw = text_width(attach, 11.5) + 0.95
        s.rrect(x + 0.3, cy + 0.02, aw, 0.4, r=0.1, fill=(WHITE, 6), line="glass2")
        s.pic(ic("paperclip"), x + 0.4, cy + 0.11, w=0.22)
        s.text(x + 0.7, cy + 0.02, aw - 0.75, 0.4, attach, sz=11.5, color=TEXT, anchor="ctr")
        pts["attach"] = (x + 0.3 + aw + 0.1, cy + 0.04)
        cy += 0.5
    pts["end"] = (x, cy)
    s.end(anim=anim)
    return pts


def num_badge(s, x, y, n, d=0.34, name=None, anim=None, color=None):
    s.oval(x, y, d, d, fill="accent" if not color else color, text=str(n), sz=11.5 * d / 0.34, color=WHITE, font=FONT_SB, align="ctr",
           anchor="ctr", inset=(0, 0, 0, 0.01), name=name, anim=anim, fx="glow_s")


def num_list(s, x, y, w, items, sz=14, gap=0.14, name="nl", anim0=200, d=0.34, tsz=None, title_color=WHITE):
    """Numbered explanations: (title, text) with accent number badges. Returns used height."""
    cy = y
    for i, it in enumerate(items):
        title, text = it if isinstance(it, tuple) else (it, None)
        paras = [{"t": title, "font": FONT_SB, "color": title_color, "sz": tsz or sz + 1}]
        if text:
            paras.append({"t": text, "spcBef": 2})
        hh = text_height(paras, w - d - 0.2, sz, FONT, lnsp=1.0)
        s.begin("%s%d" % (name, i))
        num_badge(s, x, cy + 0.02, i + 1, d=d)
        s.text(x + d + 0.2, cy, w - d - 0.2, hh + 0.04, paras, sz=sz, color=TEXT, lnsp=1.0)
        s.end(anim=(anim0 + i * 100) if anim0 is not None else None)
        cy += max(hh, d) + gap
    return cy - y - gap


def side_stepper(s, x, y, w, items, cur, title, body, tip=None, name="stp", h_total=4.4, tsz=20, bsz=14.5):
    """Right-hand panel for step-by-step tours: 'Шаг N из M', a row of numbered dots (current one glows) and a description card."""
    pre = "!!%s-" % name
    n = len(items)
    s.text(x, y, w, 0.34, "Шаг %d из %d" % (cur + 1, n), sz=13, color=A("ACC_SOFT"), font=FONT_SB, anchor="ctr", name=pre + "hdr")
    d = 0.42
    cy = y + 0.5
    stepw = (w - d) / (n - 1)
    s.line(x + d / 2, cy + d / 2, x + w - d / 2, cy + d / 2, color=(WHITE, 22), lw=1.0, name=pre + "ln")
    if cur > 0:
        s.line(x + d / 2, cy + d / 2, x + d / 2 + stepw * cur, cy + d / 2, color=A("ACC"), lw=1.5, name=pre + "ln2")
    for i in range(n):
        cx = x + i * stepw
        if i == cur:
            s.oval(cx - 0.04, cy - 0.04, d + 0.08, d + 0.08, fill="accent", text=str(i + 1), sz=14, color=WHITE, font=FONT_SB, align="ctr",
                   anchor="ctr", inset=(0, 0, 0, 0.01), name=pre + "c%d" % i, fx="glow_s")
        elif i < cur:
            s.oval(cx, cy, d, d, fill=A("TINT"), line=A("ACC"), lw=1.25, text=str(i + 1), sz=12.5, color=WHITE, font=FONT_SB, align="ctr",
                   anchor="ctr", inset=(0, 0, 0, 0.01), name=pre + "c%d" % i)
        else:
            s.oval(cx, cy, d, d, fill="16141C", line="glass", text=str(i + 1), sz=12.5, color=MUTED, font=FONT_SB, align="ctr",
                   anchor="ctr", inset=(0, 0, 0, 0.01), name=pre + "c%d" % i)
    ky = cy + d + 0.36
    ch = y + h_total - ky
    s.rrect(x, ky, w, ch, r=0.26, fill="glass", line="glass", name=pre + "card")
    ty = ky + 0.32
    th = text_height(title, w - 0.7, tsz, FONT_SB, lnsp=0.98)
    s.text(x + 0.35, ty, w - 0.7, th + 0.05, title, sz=tsz, color=WHITE, font=FONT_SB, lnsp=0.98, name="stp-t")
    ty += th + 0.14
    s.line(x + 0.35, ty, x + w - 0.35, ty, color=(WHITE, 20), name=pre + "cl")
    ty += 0.18
    bh = ky + ch - ty - (0.78 if tip else 0.2)
    s.text(x + 0.35, ty, w - 0.7, bh, body, sz=bsz, color=TEXT, lnsp=1.02, spc_after=6, name="stp-b")
    if tip:
        s.text(x + 0.35, ky + ch - 0.74, 1.6, 0.44, "Быстрее с клавиатуры:", sz=11.5, color=MUTED, anchor="ctr", name="stp-kl", check=False, lnsp=0.95)
        keys(s, x + 2.0, ky + ch - 0.74, tip.replace(" ", ""))
    return ky
