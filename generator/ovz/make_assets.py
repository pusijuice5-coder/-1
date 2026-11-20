import os, sys, math
from PIL import Image, ImageDraw, ImageFilter, ImageOps, ImageChops
SP = sys.argv[1]
G = os.path.join(SP, 'gen'); C = os.path.join(G, 'cut'); A = os.path.join(SP, 'assets'); L = os.path.join(SP, 'in', 'logo')
os.makedirs(A, exist_ok=True)

def crop_alpha(im, pad=0):
    bb = im.getchannel('A').getbbox()
    x0, y0, x1, y1 = bb
    return im.crop((max(0, x0-pad), max(0, y0-pad), min(im.width, x1+pad), min(im.height, y1+pad)))

def save_png(im, name):
    p = os.path.join(A, name); im.save(p, optimize=True); return p

# ---------- backgrounds ----------
def bg(src, name, size=(1920,1080), q=88):
    im = Image.open(os.path.join(G, src)).convert('RGB').resize(size, Image.LANCZOS)
    im.save(os.path.join(A, name), quality=q, optimize=True, progressive=True)
bg('bg_light2.png', 'ovz_bg_light_a.jpg')
bg('bg_light1.png', 'ovz_bg_light_b.jpg')
bg('bg_dark1.png',  'ovz_bg_dark.jpg')

# ---------- logos ----------
for src, name in [('logo_color.png','ovz_logo_color.png'), ('logo_onDark.png','ovz_logo_ondark.png')]:
    im = crop_alpha(Image.open(os.path.join(L, src)).convert('RGBA'))
    im = im.resize((1200, round(im.height*1200/im.width)), Image.LANCZOS)
    save_png(im, name)

# ---------- characters (with soft ground shadow) ----------
def with_shadow(im, sh_w=0.62, sh_h=0.045, alpha=70):
    im = crop_alpha(im)
    W, H = im.size
    pad_b = int(H*0.035)
    canvas = Image.new('RGBA', (W, H+pad_b), (0,0,0,0))
    sh = Image.new('L', (W, H+pad_b), 0)
    d = ImageDraw.Draw(sh)
    cx = W/2; cy = H - pad_b*0.2
    rw = W*sh_w/2; rh = H*sh_h/2
    d.ellipse([cx-rw, cy-rh, cx+rw, cy+rh], fill=alpha)
    sh = sh.filter(ImageFilter.GaussianBlur(H*0.012))
    shadow = Image.new('RGBA', (W, H+pad_b), (8, 40, 20, 0)); shadow.putalpha(sh)
    canvas.alpha_composite(shadow)
    canvas.alpha_composite(im, (0, 0))
    return canvas
for src, name in [('char_present','ovz_char_present.png'), ('char_hands','ovz_char_hands.png'),
                  ('char_point','ovz_char_point.png'), ('char_celeb','ovz_char_celeb.png')]:
    im = with_shadow(Image.open(os.path.join(C, src+'.png')).convert('RGBA'))
    im = im.resize((round(im.width*1500/im.height), 1500), Image.LANCZOS)
    save_png(im, name)

# ---------- helpers for discs ----------
MINT_C = (243, 251, 242); MINT_E = (214, 241, 211)
def radial(size, c_in, c_out, center=(0.5,0.5), radius=0.75):
    W, H = size
    # build small and upscale for speed
    s = 256
    g = Image.new('RGB', (s, s))
    px = g.load()
    for y in range(s):
        for x in range(s):
            dx = x/(s-1) - center[0]; dy = y/(s-1) - center[1]
            t = min(1.0, math.hypot(dx, dy)/radius)
            t = t*t*(3-2*t)
            px[x, y] = tuple(round(c_in[i]*(1-t) + c_out[i]*t) for i in range(3))
    return g.resize((W, H), Image.BICUBIC)

def bars_overlay(size, alpha=46, color=(255,255,255)):
    """vertical bars motif like the logo (thin/thick alternating, swelling)"""
    W, H = size
    ov = Image.new('RGBA', size, (0,0,0,0))
    d = ImageDraw.Draw(ov)
    n = 26
    step = W / n
    for i in range(n):
        x = i*step + step*0.5
        # bar widens towards the bottom with phase shift (silk thread look)
        swell_at = 0.25 + 0.5*abs(math.sin(i*0.55))
        w_thin = step*0.10; w_thick = step*0.30
        y_sw = H*swell_at
        poly = [(x-w_thin/2, 0), (x+w_thin/2, 0), (x+w_thin/2, y_sw), (x+w_thick/2, y_sw+H*0.08),
                (x+w_thick/2, H), (x-w_thick/2, H), (x-w_thick/2, y_sw+H*0.08), (x-w_thin/2, y_sw)]
        d.polygon(poly, fill=color+(alpha,))
    return ov

def drop_shadow_under(ill, strength=60):
    W, H = ill.size
    a = ill.getchannel('A')
    sh = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(sh)
    bb = a.getbbox()
    cx = (bb[0]+bb[2])/2; bw = (bb[2]-bb[0])*0.42; by = bb[3]-H*0.01; bh = H*0.035
    d.ellipse([cx-bw, by-bh, cx+bw, by+bh], fill=strength)
    sh = sh.filter(ImageFilter.GaussianBlur(H*0.02))
    out = Image.new('RGBA', (W, H), (10, 60, 25, 0)); out.putalpha(sh)
    return out

def gray_version(ill):
    rgb = ill.convert('RGB'); a = ill.getchannel('A')
    g = ImageOps.grayscale(rgb)
    g = ImageOps.autocontrast(g, cutoff=1)
    # lighten a bit
    g = g.point(lambda v: int(70 + v*0.72))
    out = Image.merge('RGBA', (g, g, g, a))
    return out

def place(base, ill, cx, cy, bw, bh=None):
    ill = crop_alpha(ill)
    bh = bh or bw
    k = min(bw/ill.width, bh/ill.height)
    ill = ill.resize((round(ill.width*k), round(ill.height*k)), Image.LANCZOS)
    x = round(cx - ill.width/2); y = round(cy - ill.height/2)
    layer = Image.new('RGBA', base.size, (0,0,0,0))
    layer.alpha_composite(ill, (max(0,x), max(0,y)) if x>=0 and y>=0 else (0,0)) if (x>=0 and y>=0) else None
    if x < 0 or y < 0:
        layer = Image.new('RGBA', base.size, (0,0,0,0)); layer.paste(ill, (x, y), ill)
    sh = drop_shadow_under(layer)
    base.alpha_composite(sh); base.alpha_composite(layer)
    return base

def small_disc(ill_path, name, size=640, scale=0.70, gray=False):
    ill = Image.open(ill_path).convert('RGBA')
    if gray:
        base = radial((size, size), (246, 247, 246), (226, 229, 227)).convert('RGBA')
        ill = gray_version(ill)
    else:
        base = radial((size, size), MINT_C, MINT_E).convert('RGBA')
    base = place(base, ill, size*0.5, size*0.5, size*scale)
    base.convert('RGB').save(os.path.join(A, name), quality=90, optimize=True)

def big_disc(ill_path, name, size=1800, u=0.63, v=0.47, scale=0.56, hscale=0.60):
    ill = Image.open(ill_path).convert('RGBA')
    base = radial((size, size), MINT_C, MINT_E, center=(u, v), radius=0.62).convert('RGBA')
    base.alpha_composite(bars_overlay((size, size), alpha=40))
    base = place(base, ill, size*u, size*v, size*scale, size*hscale)
    base.convert('RGB').save(os.path.join(A, name), quality=90, optimize=True)

subjects = {
  'step1':'step1', 'step2':'step2', 'step3':'step3', 'step4':'step4', 'step5':'step5', 'step6':'step6',
  'funds':'op_funds', 'transfer':'op_transfer', 'close':'op_close', 'currency':'op_currency', 'storage':'op_storage',
}
for key, src in subjects.items():
    p = os.path.join(C, src+'.png')
    sc = 0.70 if key == 'step1' else 0.64
    small_disc(p, f'ovz_disc_{key}.jpg', scale=sc)
    small_disc(p, f'ovz_disc_{key}_bw.jpg', scale=sc, gray=True)
    big_disc(p, f'ovz_big_{key}.jpg', scale=0.56, hscale=0.62 if key=='step1' else 0.56)

# ---------- standalone illustrations ----------
for src, name, w in [('contents','ovz_contents.png',1400), ('globe_lang','ovz_globe.png',1000),
                     ('residents','ovz_residents.png',1000), ('op_sanctions','ovz_sanctions.png',1000),
                     ('icon_important','ovz_icon_important.png',256)]:
    im = crop_alpha(Image.open(os.path.join(C, src+'.png')).convert('RGBA'))
    im = im.resize((w, round(im.height*w/im.width)), Image.LANCZOS)
    save_png(im, name)

for f in sorted(os.listdir(A)):
    p = os.path.join(A, f); im = Image.open(p)
    print(f'{f:28s} {str(im.size):14s} {os.path.getsize(p)//1024} KB')
