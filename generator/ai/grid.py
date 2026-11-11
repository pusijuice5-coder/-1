import sys, glob
from PIL import Image, ImageDraw
pat, out, cols, per = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
fs = sorted(glob.glob(pat))
for k in range(0, len(fs), per):
    chunk = fs[k:k + per]
    ims = [Image.open(f) for f in chunk]
    w, h = ims[0].size
    rows = (len(ims) + cols - 1) // cols
    g = Image.new('RGB', (cols * w, rows * h), 'white'); d = ImageDraw.Draw(g)
    for i, (f, im) in enumerate(zip(chunk, ims)):
        g.paste(im.resize((w, h)), ((i % cols) * w, (i // cols) * h))
        d.rectangle([(i % cols) * w, (i // cols) * h, (i % cols) * w + 40, (i // cols) * h + 14], fill='yellow')
        d.text(((i % cols) * w + 2, (i // cols) * h + 1), f.split('-')[-1].split('.')[0], fill='black')
    g.save(f"{out}_{k // per + 1:02d}.jpg", quality=80)
    print(f"{out}_{k // per + 1:02d}.jpg")
