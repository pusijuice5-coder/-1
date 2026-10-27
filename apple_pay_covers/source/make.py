"""Builds cover/thumbnail HTML pages from the course's original assets."""
import os

B = os.path.dirname(os.path.abspath(__file__))
A = "file://" + B + "/a/"
F = "file://" + B + "/package/files/"

LIME = "#DDE81B"
INK = "#111111"

FONTS = "".join(
    f"""@font-face{{font-family:Manrope;font-weight:{w};src:url('{F}manrope-{s}-{w}-normal.woff2') format('woff2');}}"""
    for w in (400, 500, 800) for s in ("latin", "cyrillic")
)

BASE_CSS = FONTS + f"""
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:#fff}}
.c{{position:relative;overflow:hidden;background:#fff;font-family:Manrope,sans-serif;color:{INK}}}
.vl{{position:absolute;top:0;bottom:0;width:2px;background:#EEEEEE}}
.o{{position:absolute;display:block}}
.sh{{filter:drop-shadow(0 28px 36px rgba(10,60,30,.22))}}
.pill{{position:absolute;background:{LIME};border-radius:999px;font-weight:500;line-height:1}}
.h1{{position:absolute;font-weight:800;letter-spacing:-0.02em;line-height:1.02}}
.sub{{position:absolute;font-weight:400;color:#333}}
.cap{{position:absolute;font-weight:500;color:#8a8a8a}}
"""


def img(name, x, y, w, rot=0, z=1, blur=0, shadow=True, op=1.0):
    f = []
    if shadow:
        f.append("drop-shadow(0 28px 36px rgba(10,60,30,.22))")
    if blur:
        f.append(f"blur({blur}px)")
    style = (f"left:{x}px;top:{y}px;width:{w}px;z-index:{z};transform:rotate({rot}deg);"
             f"filter:{' '.join(f) or 'none'};opacity:{op}")
    return f'<img class="o" src="{A}{name}" style="{style}">'


def bokeh(x, y, d, op=0.85):
    return (f'<div class="o" style="left:{x}px;top:{y}px;width:{d}px;height:{d}px;border-radius:50%;'
            f'background:#1E5A3A;filter:blur({d//6}px);opacity:{op};z-index:0"></div>')


def lines(xs):
    return "".join(f'<div class="vl" style="left:{x}px"></div>' for x in xs)


def page(w, h, body):
    return (f"<!doctype html><html><head><meta charset='utf-8'><style>{BASE_CSS}</style></head>"
            f"<body><div class='c' style='width:{w}px;height:{h}px'>{body}</div></body></html>")


def cover_text(part, subtitle):
    return f"""
<img class="o" src="{A}logo.png" style="left:110px;top:92px;height:62px;z-index:5">
<div class="pill" style="left:110px;top:300px;padding:14px 32px;font-size:30px;z-index:5">Часть {part}</div>
<div class="h1" style="left:106px;top:380px;font-size:84px;z-index:5">Apple Pay<br>для банка-эмитента</div>
<div class="sub" style="left:110px;top:590px;font-size:34px;z-index:5">{subtitle}</div>
<div class="cap" style="left:110px;bottom:84px;font-size:22px;z-index:5">Курс «Структура взаимодействия банка-эмитента с Apple Pay»</div>
"""


COVER_LINES = lines([104, 527, 950, 1373, 1796])

cover1 = page(1920, 1080, COVER_LINES + cover_text(1, "Apple Wallet и добавление карты") + "".join([
    bokeh(420, -170, 320),
    bokeh(820, 900, 300),
    img("phone.png", 1340, 120, 430, z=2),
    img("card.png", 1080, 470, 470, rot=-16, z=3),
    img("wallet.png", 1020, 600, 440, z=4),
    img("apple_logo.png", 1690, 40, 190, rot=10, z=5),
    img("apple_logo.png", 1180, 150, 150, rot=-14, z=5),
    img("apple_logo.png", 1640, 800, 230, rot=18, z=5),
]))

cover2 = page(1920, 1080, COVER_LINES + cover_text(2, "Платежи и управление картой") + "".join([
    bokeh(420, -170, 320),
    bokeh(820, 900, 300),
    img("phone.png", 1340, 120, 430, z=2),
    img("watch_black.png", 1150, 430, 300, rot=-12, z=4),
    img("ic15_5.png", 1060, 250, 170, rot=-6, z=5),
    img("ic15_4.png", 1250, 140, 120, rot=12, z=5),
    img("ic15_2.png", 1080, 860, 150, rot=-20, z=5),
    img("apple_logo.png", 1700, 40, 190, rot=10, z=5),
    img("apple_logo.png", 1650, 800, 230, rot=18, z=5),
]))

THUMB_LINES = lines([270, 540, 810])


def thumb(part, digit, extra):
    return page(1080, 1080, THUMB_LINES + f"""
<img class="o" src="{A}logo.png" style="left:72px;top:72px;height:54px;z-index:5">
<div class="pill" style="left:72px;top:158px;padding:12px 28px;font-size:28px;z-index:5">Часть {part}</div>
""" + "".join([
        bokeh(-110, 860, 300),
        bokeh(860, -120, 260),
        img(digit, 250, 300, 500, z=3),
    ]) + extra)


thumb1 = thumb(1, "digit_1.png", img("wallet.png", 640, 560, 340, rot=8, z=4))
thumb2 = thumb(2, "digit_2.png", img("ic15_5.png", 720, 720, 220, rot=-8, z=4))

for name, html in [("cover1", cover1), ("cover2", cover2), ("thumb1", thumb1), ("thumb2", thumb2)]:
    with open(os.path.join(B, name + ".html"), "w", encoding="utf-8") as fh:
        fh.write(html)
print("ok")
