# -*- coding: utf-8 -*-
"""AI course: same slide types as the Agile course, on the bank's green fluted-glass backgrounds."""
import lib
from tpl import *

lib.IMG.update({"fdark": "ai_fdark.png", "flight": "ai_flight.png", "flight_l": "ai_flight_l.png", "bars": "ai_bars.png"})
BG_MAP = {"video": "flight", "dark": "fdark"}


class AIDeck(lib.Deck):
    def new(self, bg="light", notes="", replace=None, transition="fade"):
        return lib.Deck.new(self, bg=BG_MAP.get(bg, bg), notes=notes, replace=replace, transition=transition)


def quiz_wide(d, situation, question, options, correct, notes_extra=""):
    """'Проверьте себя' with long options stacked full width."""
    s = d.new(bg="flight", notes="Проверьте себя. %s %s Правильный ответ: %s. %s" % (situation, question, LETTERS[correct], notes_extra))
    s.title("Проверьте себя", anim=0)
    s.ezoza("chest", right=13.25, h=6.55)
    s.begin("Ситуация")
    paras = [{"runs": parse_runs(situation)}, {"runs": parse_runs("**" + question + "**"), "spcBef": 6}]
    th = text_height(paras, 8.6 - 1.5, 14, False, 1.05, 4)
    ch = max(1.25, th + 0.65)
    s.rrect(0.55, 1.3, 8.6, ch, r=0.22, fill=DARK, shadow="green")
    s.shape(0.8, 1.52, 0.56, 0.56, geom="ellipse", fill=LIME, text="?", sz=20, bold=True, color=DARK, align="ctr", anchor="ctr", inset=(0, 0, 0, 0))
    s.text(1.6, 1.45, 7.3, 0.3, "СИТУАЦИЯ", sz=11, bold=True, color=LIME)
    s.text(1.6, 1.78, 7.35, ch - 0.6, [{"t": situation, "spcAft": 4}, {"t": question, "b": True, "color": LIME, "spcBef": 4}],
           sz=14, color=WHITE, lnsp=1.05)
    s.end(anim=100)
    y = 1.3 + ch + 0.25
    hs = [max(0.62, text_height([{"runs": parse_runs(o)}], 7.4, 12.5, False, 1.0) + 0.22) for o in options]
    gap = 0.14
    scale = min(1.0, (6.95 - y - gap * 3) / sum(hs))
    for i, (opt, oh) in enumerate(zip(options, hs)):
        oh = oh * scale if scale < 1 else oh
        s.begin("Вариант " + LETTERS[i])
        s.rrect(0.55, y, 8.6, oh, r=min(0.3, oh / 2), grad="button", shadow="pill")
        s.circle_num(0.67, y + oh / 2 - 0.24, 0.48, LETTERS[i], fill=DARK, sz=14)
        s.text(1.32, y + 0.04, 7.65, oh - 0.08, opt, sz=12.5, color="1B2A22", anchor="ctr", lnsp=1.0)
        s.end(anim=250 + i * 120)
        y += oh + gap
    return s


def stat_cards(s, x, y, w, h, items, delay=200, dark=False):
    """Row of glass cards (idea of the user's template): big value + caption."""
    n = len(items)
    gap = 0.2
    cw = (w - gap * (n - 1)) / n
    for i, (big, cap) in enumerate(items):
        cx = x + i * (cw + gap)
        s.begin("Карточка %d" % (i + 1))
        s.rrect(cx, y, cw, h, r=0.18, fill=WHITE if not dark else "16402A", alpha=None, shadow="soft", line=None)
        s.text(cx + 0.22, y + 0.18, cw - 0.44, 0.75, big, sz=30, bold=True, color=G2 if not dark else LIME)
        s.text(cx + 0.22, y + 0.95, cw - 0.44, h - 1.1, cap, sz=12.5, color=BODY if not dark else "D8E8DC", lnsp=1.0)
        s.end(anim=delay + i * 150)


def icon_circle(s, x, y, d, glyph, fill=DARK, color=WHITE, sz=None):
    return s.shape(x, y, d, d, geom="ellipse", fill=fill, text=glyph, sz=sz or max(10, int(d * 30)), bold=True, color=color,
                   align="ctr", anchor="ctr", inset=(0, 0, 0, 0))
