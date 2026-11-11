import numpy as np
from PIL import Image
SRC = "/tmp/claude-0/w2/in_new/un/ppt/media/"
OUT = "/tmp/claude-0/w2/assets/"

def gradmap(t, stops):
    """t in 0..1 array; stops list of (pos, (r,g,b))"""
    out = np.zeros(t.shape + (3,))
    for (p0, c0), (p1, c1) in zip(stops[:-1], stops[1:]):
        m = (t >= p0) & (t <= p1)
        u = ((t - p0) / (p1 - p0))[..., None]
        out[m] = (np.array(c0) * (1 - u) + np.array(c1) * u)[m]
    return out

def hexc(h): return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

# dark cover: structure from the blue/orange fluted gradient
im = np.asarray(Image.open(SRC + "image2.png").convert("RGB")).astype(float) / 255
r, g, b = im[..., 0], im[..., 1], im[..., 2]
lum = 0.30 * r + 0.55 * g + 0.15 * b           # orange -> bright, blue -> dark
warm = np.clip(r - b + 0.5, 0, 1)              # orange highlights
t = np.clip(0.55 * lum / lum.max() + 0.45 * warm, 0, 1)
t = (t - t.min()) / (t.max() - t.min())
dark = gradmap(t, [(0, hexc("08200F")), (0.35, hexc("0F2F1D")), (0.62, hexc("0A6A1F")), (0.85, hexc("2E8B3E")), (1.0, hexc("4CEA4C"))])
Image.fromarray(dark.clip(0, 255).astype("uint8")).save(OUT + "fl_dark.png", optimize=True)

# light content: white with peach fluted streaks -> white with soft green streaks
im = np.asarray(Image.open(SRC + "image1.png").convert("RGBA")).astype(float) / 255
rgb, a = im[..., :3], im[..., 3:4]
rgb = rgb * a + (1 - a)                          # flatten on white
lum = rgb.mean(axis=2)
t = np.clip((1 - lum) / max(1e-6, (1 - lum).max()), 0, 1) ** 0.7
light = gradmap(t, [(0, hexc("FFFFFF")), (0.25, hexc("E6F4E8")), (0.6, hexc("A9DBB1")), (1.0, hexc("3E9A4E"))])
Image.fromarray(light.clip(0, 255).astype("uint8")).save(OUT + "fl_light.png", optimize=True)

# mirrored light (streaks on the left) for variety
Image.open(OUT + "fl_light.png").transpose(Image.FLIP_LEFT_RIGHT).save(OUT + "fl_light_l.png", optimize=True)
print("ok")
